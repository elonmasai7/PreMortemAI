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
