import csv
import io
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_auth_context, get_db, get_settings_dep, require_roles
from app.models import AuditEvent

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/audit-export")
def export_audit(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    context=Depends(require_roles("admin", "owner")),
    format: str = Query(default="json", pattern="^(json|csv)$"),
    days: int = Query(default=30, ge=1, le=365),
):
    if not settings.compliance_enable_audit_export:
        raise HTTPException(status_code=403, detail="Audit export is disabled by configuration.")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.tenant_id == context.tenant_id, AuditEvent.created_at >= since)
        .order_by(AuditEvent.created_at.desc())
        .all()
    )

    rows = [
        {
            "id": ev.id,
            "tenant_id": ev.tenant_id,
            "actor_user_id": ev.actor_user_id,
            "actor_type": ev.actor_type,
            "action": ev.action,
            "resource_type": ev.resource_type,
            "resource_id": ev.resource_id,
            "metadata": ev.metadata_json,
            "created_at": ev.created_at.isoformat(),
        }
        for ev in events
    ]

    if format == "json":
        return {"count": len(rows), "events": rows}

    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=["id", "tenant_id", "actor_user_id", "actor_type", "action", "resource_type", "resource_id", "metadata", "created_at"],
    )
    writer.writeheader()
    writer.writerows(rows)
    return PlainTextResponse(out.getvalue(), media_type="text/csv")


@router.get("/retention/status")
def retention_status(settings: Settings = Depends(get_settings_dep), context=Depends(get_auth_context)):
    return {
        "retention_days": settings.compliance_retention_days,
        "audit_export_enabled": settings.compliance_enable_audit_export,
    }


@router.get("/kms/status")
def kms_status(settings: Settings = Depends(get_settings_dep), context=Depends(get_auth_context)):
    return {
        "kms_provider": settings.kms_provider,
        "kms_key_id": settings.kms_key_id,
        "configured": bool(settings.kms_provider and settings.kms_key_id),
    }
