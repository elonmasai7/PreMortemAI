from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    tenant_slug: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: int
    role: str


class APIKeyCreateRequest(BaseModel):
    role_override: str | None = Field(default=None, max_length=32)


class APIKeyRead(BaseModel):
    id: int
    key_prefix: str
    role_override: str | None
    is_active: bool
    expires_at: datetime | None
    created_at: datetime
