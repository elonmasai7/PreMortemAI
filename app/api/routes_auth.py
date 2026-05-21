from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_auth_context, get_db, get_settings_dep, require_roles
from app.models import APIKey, Tenant, User
from app.schemas.auth import APIKeyCreateRequest, APIKeyRead, LoginRequest, LoginResponse
from app.services.auth_service import create_access_token, create_api_key_record, hash_password, verify_password

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
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "role": user.role}
