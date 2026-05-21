from sqlalchemy.orm import Session

from app.agents.blast_radius_agent import BlastRadiusAgent
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.forecast_agent import ForecastAgent
from app.agents.remediation_agent import RemediationAgent
from app.agents.report_agent import ReportAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.telemetry_agent import TelemetryAgent
from app.config import Settings
from app.models import Investigation
from app.services.splunk_search_service import SplunkSearchService


def build_coordinator(settings: Settings, splunk_client, ai_provider) -> CoordinatorAgent:
    search_service = SplunkSearchService(splunk_client, settings)
    return CoordinatorAgent(
        telemetry_agent=TelemetryAgent(search_service),
        forecast_agent=ForecastAgent(),
        root_cause_agent=RootCauseAgent(),
        blast_radius_agent=BlastRadiusAgent(),
        remediation_agent=RemediationAgent(ai_provider),
        report_agent=ReportAgent(ai_provider),
    )


def run_investigation_pipeline(db: Session, investigation: Investigation, settings: Settings, splunk_client, ai_provider):
    coordinator = build_coordinator(settings, splunk_client, ai_provider)
    return coordinator.run(db, investigation)
