from app.models import Investigation
from app.services.ai_client import AIProvider
from app.services.report_service import generate_markdown_report


class ReportAgent:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    def run(
        self,
        investigation: Investigation,
        root_cause_summary: str,
        blast_radius_summary: str,
        decision_history: list[str],
    ) -> str:
        if self.ai_provider.__class__.__name__ == "DisabledAIProvider":
            return generate_markdown_report(investigation, root_cause_summary, blast_radius_summary, decision_history)
        return self.ai_provider.generate_postmortem(
            {
                "id": investigation.id,
                "title": investigation.title,
                "service_name": investigation.service_name,
                "risk_score": investigation.risk_score,
                "risk_level": investigation.risk_level,
                "root_cause": root_cause_summary,
                "impact": blast_radius_summary,
                "decisions": decision_history,
            }
        )
