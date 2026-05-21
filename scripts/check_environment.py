#!/usr/bin/env python3
from app.config import get_settings


def main() -> None:
    settings = get_settings()
    checks = {
        "APP_NAME": bool(settings.app_name),
        "DATABASE_URL": bool(settings.database_url),
        "AUTH_SECRET_KEY": bool(settings.auth_secret_key),
        "SPLUNK_BASE_URL": bool(settings.splunk_base_url),
        "SPLUNK_AUTH": settings.splunk_auth_configured(),
        "AI_PROVIDER": bool(settings.ai_provider),
        "REDIS_URL": bool(settings.redis_url),
        "OIDC_CONFIG": (not settings.auth_oidc_enabled)
        or bool(
            settings.auth_oidc_client_id
            and settings.auth_oidc_client_secret
            and settings.auth_oidc_discovery_url
            and settings.auth_oidc_redirect_uri
        ),
        "KMS_CONFIG": (not settings.kms_provider and not settings.kms_key_id)
        or bool(settings.kms_provider and settings.kms_key_id),
    }
    for key, ok in checks.items():
        print(f"{key}: {'OK' if ok else 'MISSING'}")


if __name__ == "__main__":
    main()
