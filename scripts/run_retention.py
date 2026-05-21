#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.config import get_settings
from app.database import SessionLocal
from app.models import AuditEvent, Evidence, Report


def main() -> None:
    settings = get_settings()
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.compliance_retention_days)

    db = SessionLocal()
    try:
        audit_deleted = db.execute(delete(AuditEvent).where(AuditEvent.created_at < cutoff)).rowcount or 0
        evidence_deleted = db.execute(delete(Evidence).where(Evidence.created_at < cutoff)).rowcount or 0
        report_deleted = db.execute(delete(Report).where(Report.created_at < cutoff)).rowcount or 0
        db.commit()
        print(
            {
                "cutoff": cutoff.isoformat(),
                "audit_events_deleted": int(audit_deleted),
                "evidence_deleted": int(evidence_deleted),
                "reports_deleted": int(report_deleted),
            }
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
