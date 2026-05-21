import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_auth_context, get_db, get_settings_dep, require_roles
from app.models import APIKey, Tenant, User
from app.schemas.auth import APIKeyCreateRequest, APIKeyRead, LoginRequest, LoginResponse
from app.services.audit_service import write_audit_event, write_audit_for_context
from app.services.auth_service import create_access_token, create_api_key_record, hash_password, verify_password
from app.services.oidc_service import OIDCService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), settings: Settings = Depends(get_settings_dep)):
    tenant = db.query(Tenant).filter(Tenant.slug == payload.tenant_slug, Tenant.is_active.is_(True)).first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    user = (
        db.query(User)
        .filter(User.tenant_id == tenant.id, User.username == payload.username, User.is_active.is_(True))
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_access_token(user.id, tenant.id, user.role, settings)
    write_audit_event(
        db,
        tenant_id=tenant.id,
        actor_user_id=user.id,
        actor_type="password",
        action="auth.login",
        resource_type="user",
        resource_id=str(user.id),
        metadata={"username": user.username},
    )
    db.commit()
    return LoginResponse(access_token=token, tenant_id=tenant.id, role=user.role)


@router.get("/oidc/start")
def oidc_start(settings: Settings = Depends(get_settings_dep)):
    oidc = OIDCService(settings)
    if not oidc.is_enabled():
        raise HTTPException(status_code=400, detail="OIDC login is disabled.")
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    try:
        authorize_url = oidc.build_authorize_url(state=state, nonce=nonce)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"authorize_url": authorize_url, "state": state, "nonce": nonce}


@router.get("/oidc/callback", response_model=LoginResponse)
def oidc_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    oidc = OIDCService(settings)
    if not oidc.is_enabled():
        raise HTTPException(status_code=400, detail="OIDC login is disabled.")
    try:
        token_payload = oidc.exchange_code(code)
        userinfo = oidc.fetch_userinfo(token_payload.get("access_token", ""))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"OIDC callback failed: {exc}") from exc

    email = (userinfo.get("email") or "").lower()
    preferred_username = userinfo.get("preferred_username") or userinfo.get("name") or email
    issuer = userinfo.get("iss")
    if not email:
        raise HTTPException(status_code=400, detail="OIDC userinfo did not include an email claim.")

    domain = email.split("@")[-1]
    tenant = (
        db.query(Tenant)
        .filter(
            Tenant.is_active.is_(True),
            (Tenant.oidc_domain == domain) | (Tenant.oidc_issuer == issuer),
        )
        .first()
    )
    if not tenant:
        tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
    if not tenant:
        raise HTTPException(status_code=500, detail="No tenant mapping available for OIDC login.")

    user = db.query(User).filter(User.tenant_id == tenant.id, User.username == preferred_username).first()
    if not user:
        user = User(
            tenant_id=tenant.id,
            username=preferred_username,
            password_hash=hash_password(secrets.token_urlsafe(24)),
            role=settings.auth_oidc_default_role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id, tenant.id, user.role, settings)
    write_audit_event(
        db,
        tenant_id=tenant.id,
        actor_user_id=user.id,
        actor_type="oidc",
        action="auth.oidc_login",
        resource_type="user",
        resource_id=str(user.id),
        metadata={"email": email, "state": state},
    )
    db.commit()
    return LoginResponse(access_token=token, tenant_id=tenant.id, role=user.role)


@router.get("/me")
def me(context=Depends(get_auth_context)):
    return {
        "user_id": context.user_id,
        "tenant_id": context.tenant_id,
        "role": context.role,
        "auth_type": context.auth_type,
    }


@router.get("/api-keys", response_model=list[APIKeyRead])
def list_api_keys(
    db: Session = Depends(get_db),
    context=Depends(require_roles("admin", "owner")),
):
    keys = db.query(APIKey).filter(APIKey.tenant_id == context.tenant_id).order_by(APIKey.created_at.desc()).all()
    return keys


@router.post("/api-keys")
def create_api_key(
    payload: APIKeyCreateRequest,
    db: Session = Depends(get_db),
    context=Depends(require_roles("admin", "owner")),
):
    record, raw = create_api_key_record(
        db,
        tenant_id=context.tenant_id,
        user_id=context.user_id or 1,
        role=payload.role_override,
    )
    write_audit_for_context(
        db,
        context,
        action="auth.api_key_create",
        resource_type="api_key",
        resource_id=str(record.id),
        metadata={"role_override": payload.role_override},
    )
    db.commit()
    return {
        "id": record.id,
        "key_prefix": record.key_prefix,
        "role_override": record.role_override,
        "api_key": raw,
    }


@router.post("/users")
def create_user(
    username: str,
    password: str,
    role: str = "viewer",
    db: Session = Depends(get_db),
    context=Depends(require_roles("admin", "owner")),
):
    existing = db.query(User).filter(User.tenant_id == context.tenant_id, User.username == username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists in tenant.")
    user = User(
        tenant_id=context.tenant_id,
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    write_audit_for_context(
        db,
        context,
        action="auth.user_create",
        resource_type="user",
        metadata={"username": username, "role": role},
    )
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role}
