
from sqlalchemy.orm import Query

from app.services.auth_service import AuthContext

ROLE_RANK = {"viewer": 10, "analyst": 20, "admin": 30, "owner": 40}


def has_role(context: AuthContext, required_role: str) -> bool:
    return ROLE_RANK.get(context.role, 0) >= ROLE_RANK.get(required_role, 0)


def has_any_role(context: AuthContext, required_roles: tuple[str, ...]) -> bool:
    return any(has_role(context, role) for role in required_roles)


def scope_query_to_tenant(query: Query, model, context: AuthContext):
    return query.filter(model.tenant_id == context.tenant_id)


def tenant_match_or_raise(resource_tenant_id: int, context: AuthContext) -> None:
    if resource_tenant_id != context.tenant_id:
        from app.exceptions import ValidationError

        raise ValidationError("Cross-tenant access is not allowed.")
