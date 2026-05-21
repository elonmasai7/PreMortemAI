from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="PreMortem AI", alias="APP_NAME")
    app_env: Literal["development", "test", "production"] = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    database_url: str = Field(default="sqlite:///./premortem.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    splunk_base_url: str | None = Field(default=None, alias="SPLUNK_BASE_URL")
    splunk_username: str | None = Field(default=None, alias="SPLUNK_USERNAME")
    splunk_password: str | None = Field(default=None, alias="SPLUNK_PASSWORD")
    splunk_token: str | None = Field(default=None, alias="SPLUNK_TOKEN")
    splunk_verify_ssl: bool = Field(default=True, alias="SPLUNK_VERIFY_SSL")
    splunk_default_index: str | None = Field(default=None, alias="SPLUNK_DEFAULT_INDEX")
    splunk_timeout_seconds: int = Field(default=60, alias="SPLUNK_TIMEOUT_SECONDS")

    mcp_server_url: str | None = Field(default=None, alias="MCP_SERVER_URL")
    mcp_enabled: bool = Field(default=False, alias="MCP_ENABLED")

    ai_provider: Literal["disabled", "openai_compatible", "local"] = Field(default="disabled", alias="AI_PROVIDER")
    ai_base_url: str | None = Field(default=None, alias="AI_BASE_URL")
    ai_api_key: str | None = Field(default=None, alias="AI_API_KEY")
    ai_model: str | None = Field(default=None, alias="AI_MODEL")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    auth_required: bool = Field(default=False, alias="AUTH_REQUIRED")
    auth_secret_key: str = Field(default="change-me-in-production", alias="AUTH_SECRET_KEY")
    auth_access_token_minutes: int = Field(default=60, alias="AUTH_ACCESS_TOKEN_MINUTES")
    auth_bootstrap_admin_username: str = Field(default="admin", alias="AUTH_BOOTSTRAP_ADMIN_USERNAME")
    auth_bootstrap_admin_password: str = Field(default="admin12345", alias="AUTH_BOOTSTRAP_ADMIN_PASSWORD")
    auth_oidc_enabled: bool = Field(default=False, alias="AUTH_OIDC_ENABLED")
    auth_oidc_client_id: str | None = Field(default=None, alias="AUTH_OIDC_CLIENT_ID")
    auth_oidc_client_secret: str | None = Field(default=None, alias="AUTH_OIDC_CLIENT_SECRET")
    auth_oidc_discovery_url: str | None = Field(default=None, alias="AUTH_OIDC_DISCOVERY_URL")
    auth_oidc_redirect_uri: str | None = Field(default=None, alias="AUTH_OIDC_REDIRECT_URI")
    auth_oidc_default_role: str = Field(default="viewer", alias="AUTH_OIDC_DEFAULT_ROLE")

    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    queue_enabled: bool = Field(default=False, alias="QUEUE_ENABLED")
    queue_name: str = Field(default="investigations", alias="QUEUE_NAME")
    cache_ttl_seconds: int = Field(default=60, alias="CACHE_TTL_SECONDS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")
    tenant_usage_quota_per_minute: int = Field(default=600, alias="TENANT_USAGE_QUOTA_PER_MINUTE")

    remediation_min_evidence_for_approval: int = Field(default=1, alias="REMEDIATION_MIN_EVIDENCE_FOR_APPROVAL")
    remediation_restricted_keywords: str = Field(default="drop database,terraform destroy,rm -rf", alias="REMEDIATION_RESTRICTED_KEYWORDS")

    compliance_retention_days: int = Field(default=90, alias="COMPLIANCE_RETENTION_DAYS")
    compliance_enable_audit_export: bool = Field(default=True, alias="COMPLIANCE_ENABLE_AUDIT_EXPORT")
    kms_provider: str | None = Field(default=None, alias="KMS_PROVIDER")
    kms_key_id: str | None = Field(default=None, alias="KMS_KEY_ID")

    tracing_enabled: bool = Field(default=True, alias="TRACING_ENABLED")
    tracing_exporter: Literal["none", "otlp"] = Field(default="none", alias="TRACING_EXPORTER")
    slo_success_target_percent: float = Field(default=99.5, alias="SLO_SUCCESS_TARGET_PERCENT")
    slo_latency_target_ms: int = Field(default=1500, alias="SLO_LATENCY_TARGET_MS")

    max_spl_query_length: int = 4000
    max_request_body_bytes: int = 1_000_000

    @field_validator("splunk_base_url")
    @classmethod
    def normalize_splunk_url(cls, value: str | None) -> str | None:
        if value:
            return value.rstrip("/")
        return value

    def splunk_auth_configured(self) -> bool:
        return bool(self.splunk_token or (self.splunk_username and self.splunk_password))

    def splunk_config_complete(self) -> bool:
        return bool(self.splunk_base_url and self.splunk_auth_configured())

    def ai_config_complete(self) -> bool:
        if self.ai_provider == "disabled":
            return True
        if self.ai_provider == "local":
            return bool(self.ai_base_url and self.ai_model)
        return bool(self.ai_base_url and self.ai_model and self.ai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
