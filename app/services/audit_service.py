import json

from sqlalchemy.orm import Session

from app.models import AuditEvent
from app.services.auth_service import AuthContext


def write_audit_event(
    db: Session,
    *,
    tenant_id: int,
    actor_user_id: int | None,
    actor_type: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        actor_type=actor_type,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata or {}, default=str),
    )
    db.add(event)
    return event


def write_audit_for_context(
    db: Session,
    context: AuthContext,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    metadata: dict | None = None,
) -> AuditEvent:
    return write_audit_event(
        db,
        tenant_id=context.tenant_id,
        actor_user_id=context.user_id,
        actor_type=context.auth_type,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata,
    )
