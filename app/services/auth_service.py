import hashlib
import hmac
import json
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import Settings
from app.exceptions import ValidationError
from app.models import APIKey, Tenant, User


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"pbkdf2_sha256${salt}${dk.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, digest = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return hmac.compare_digest(candidate, digest)


def create_access_token(user_id: int, tenant_id: int, role: str, settings: Settings) -> str:
    now = _utc_now()
    payload = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.auth_access_token_minutes)).timestamp()),
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")
    signature = hmac.new(settings.auth_secret_key.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def decode_access_token(token: str, settings: Settings) -> dict:
    try:
        payload_part, signature = token.rsplit(".", 1)
        expected = hmac.new(settings.auth_secret_key.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValidationError("Invalid token signature.")
        padded = payload_part + "=" * (-len(payload_part) % 4)
        payload = json.loads(urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(_utc_now().timestamp()):
            raise ValidationError("Access token has expired.")
        return payload
    except ValueError as exc:
        raise ValidationError("Invalid or expired access token.") from exc
    except (json.JSONDecodeError, ValidationError):
        raise
    except Exception as exc:
        raise ValidationError("Invalid or expired access token.") from exc


@dataclass
class AuthContext:
    user_id: int | None
    tenant_id: int
    role: str
    auth_type: str


def generate_api_key() -> str:
    return f"pm_{secrets.token_urlsafe(32)}"


def create_api_key_record(db: Session, tenant_id: int, user_id: int, role: str | None = None) -> tuple[APIKey, str]:
    raw = generate_api_key()
    record = APIKey(
        tenant_id=tenant_id,
        user_id=user_id,
        role_override=role,
        key_prefix=raw[:10],
        key_hash=_hash_secret(raw),
        is_active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record, raw


def resolve_api_key(db: Session, raw_key: str) -> APIKey | None:
    key_hash = _hash_secret(raw_key)
    record = db.query(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active.is_(True)).first()
    if not record:
        return None
    if record.expires_at and record.expires_at < _utc_now():
        return None
    return record


def bootstrap_auth_entities(db: Session, settings: Settings) -> None:
    tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
    if not tenant:
        tenant = Tenant(name="Default Tenant", slug="default", is_active=True)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    admin = db.query(User).filter(User.tenant_id == tenant.id, User.username == settings.auth_bootstrap_admin_username).first()
    if not admin:
        admin = User(
            tenant_id=tenant.id,
            username=settings.auth_bootstrap_admin_username,
            password_hash=hash_password(settings.auth_bootstrap_admin_password),
            role="owner",
            is_active=True,
        )
        db.add(admin)
        db.commit()
