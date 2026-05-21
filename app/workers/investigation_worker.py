from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Investigation
from app.services.ai_client import build_ai_provider
from app.services.investigation_pipeline import run_investigation_pipeline
from app.services.splunk_client import SplunkClient


def process_investigation_job(investigation_id: int, tenant_id: int) -> dict:
    settings = get_settings()
    splunk_client = SplunkClient(settings)
    ai_provider = build_ai_provider(settings)

    db: Session = SessionLocal()
    try:
        investigation = (
            db.query(Investigation)
            .filter(Investigation.id == investigation_id, Investigation.tenant_id == tenant_id)
            .first()
        )
        if not investigation:
            return {"status": "not_found", "investigation_id": investigation_id}
        investigation.status = "running"
        db.add(investigation)
        db.commit()
        run_investigation_pipeline(db, investigation, settings, splunk_client, ai_provider)
        return {"status": "completed", "investigation_id": investigation_id}
    finally:
        db.close()
