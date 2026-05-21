from sqlalchemy.orm import Session

from app.agents.blast_radius_agent import BlastRadiusAgent
from app.agents.forecast_agent import ForecastAgent
from app.agents.remediation_agent import RemediationAgent
from app.agents.report_agent import ReportAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.telemetry_agent import TelemetryAgent
from app.models import Evidence, Investigation, RemediationRecommendation, Report, RootCauseCandidate
from app.time_utils import utc_now


class CoordinatorAgent:
    def __init__(
        self,
        telemetry_agent: TelemetryAgent,
        forecast_agent: ForecastAgent,
        root_cause_agent: RootCauseAgent,
        blast_radius_agent: BlastRadiusAgent,
        remediation_agent: RemediationAgent,
        report_agent: ReportAgent,
    ):
        self.telemetry_agent = telemetry_agent
        self.forecast_agent = forecast_agent
        self.root_cause_agent = root_cause_agent
        self.blast_radius_agent = blast_radius_agent
        self.remediation_agent = remediation_agent
        self.report_agent = report_agent

    def run(self, db: Session, investigation: Investigation) -> Investigation:
        rows = self.telemetry_agent.collect(investigation.service_name)
        for row in rows[:200]:
            spl_query = row.get("__spl_query")
            safe_row = {k: v for k, v in row.items() if not k.startswith("__")}
            db.add(
                Evidence(
                    tenant_id=investigation.tenant_id,
                    investigation_id=investigation.id,
                    source="splunk",
                    spl_query=spl_query,
                    event_time=utc_now(),
                    evidence_type="telemetry",
                    content=str(safe_row),
                    confidence=0.6,
                )
            )

        forecast = self.forecast_agent.run(rows)
        investigation.risk_score = forecast["risk_score"]
        investigation.risk_level = forecast["risk_level"]
        investigation.forecast_summary = forecast["summary"]

        candidates = self.root_cause_agent.run(rows)
        investigation.root_cause_summary = candidates[0]["cause"] if candidates else None
        for candidate in candidates:
            db.add(
                RootCauseCandidate(
                    tenant_id=investigation.tenant_id,
                    investigation_id=investigation.id,
                    cause=candidate["cause"],
                    confidence=float(candidate["confidence"]),
                    evidence_summary=candidate["evidence_summary"],
                    rank=int(candidate["rank"]),
                )
            )

        blast = self.blast_radius_agent.run(rows, investigation.service_name)
        investigation.blast_radius_summary = str(blast)

        remediation = self.remediation_agent.run(rows)
        db.add(
            RemediationRecommendation(
                tenant_id=investigation.tenant_id,
                investigation_id=investigation.id,
                action_type=remediation["action_type"],
                action_summary=remediation["action_summary"],
                risk_of_action=remediation["risk_of_action"],
                risk_of_inaction=remediation["risk_of_inaction"],
                confidence=float(remediation["confidence"]),
                status="pending",
            )
        )

        report_md = self.report_agent.run(
            investigation,
            investigation.root_cause_summary or "",
            investigation.blast_radius_summary or "",
            [],
        )
        db.add(
            Report(
                tenant_id=investigation.tenant_id,
                investigation_id=investigation.id,
                title=f"Report for {investigation.title}",
                markdown_body=report_md,
            )
        )

        investigation.status = "analyzed"
        db.add(investigation)
        db.commit()
        db.refresh(investigation)
        return investigation
