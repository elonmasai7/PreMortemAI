from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db_session
from app.models import User
from app.services.ai_client import build_ai_provider
from app.services.auth_service import AuthContext, decode_access_token, resolve_api_key
from app.services.authz import has_any_role
from app.services.cache_service import RedisCache
from app.services.mcp_client import MCPClient
from app.services.rate_limiter import RedisRateLimiter
from app.services.redis_client import build_redis_client
from app.services.splunk_client import SplunkClient


def get_settings_dep() -> Settings:
    return get_settings()


def get_db(dep: Session = Depends(get_db_session)) -> Session:
    return dep


def get_splunk_client(settings: Settings = Depends(get_settings_dep)) -> SplunkClient:
    return SplunkClient(settings)


def get_mcp_client(settings: Settings = Depends(get_settings_dep)) -> MCPClient:
    return MCPClient(settings)


def get_ai_provider(settings: Settings = Depends(get_settings_dep)):
    return build_ai_provider(settings)


def get_redis(settings: Settings = Depends(get_settings_dep)):
    return build_redis_client(settings)


def get_cache(settings: Settings = Depends(get_settings_dep), redis_client=Depends(get_redis)):
    if not redis_client:
        return None
    return RedisCache(redis_client, ttl_seconds=settings.cache_ttl_seconds)


def get_auth_context(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> AuthContext:
    redis_client = build_redis_client(settings)
    limiter = RedisRateLimiter(redis_client, window_seconds=settings.rate_limit_window_seconds) if redis_client else None

    def _enforce_tenant_quota(tenant_id: int):
        if limiter and limiter.is_limited(f"tenant:{tenant_id}:quota", settings.tenant_usage_quota_per_minute):
            raise HTTPException(status_code=429, detail="Tenant usage quota exceeded for current window.")

    if not settings.auth_required:
        _enforce_tenant_quota(1)
        return AuthContext(user_id=1, tenant_id=1, role="owner", auth_type="dev")

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        payload = decode_access_token(token, settings)
        user_id = int(payload.get("sub", 0))
        tenant_id = int(payload.get("tenant_id", 0))
        role = str(payload.get("role", "viewer"))
        if user_id <= 0 or tenant_id <= 0:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
        user = db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User account is inactive.")
        if user.tenant_id != tenant_id:
            raise HTTPException(status_code=401, detail="Token tenant mismatch.")
        _enforce_tenant_quota(tenant_id)
        return AuthContext(user_id=user_id, tenant_id=tenant_id, role=role, auth_type="bearer")

    if x_api_key:
        record = resolve_api_key(db, x_api_key)
        if not record:
            raise HTTPException(status_code=401, detail="Invalid API key.")
        role = record.role_override or "viewer"
        _enforce_tenant_quota(record.tenant_id)
        return AuthContext(user_id=record.user_id, tenant_id=record.tenant_id, role=role, auth_type="api_key")

    raise HTTPException(status_code=401, detail="Authentication required.")


def require_roles(*roles: str):
    def _dependency(context: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if not has_any_role(context, roles):
            raise HTTPException(status_code=403, detail="Insufficient role for this action.")
        return context

    return _dependency
