#!/usr/bin/env python3
from app.config import get_settings


def main() -> None:
    settings = get_settings()
    checks = {
        "APP_NAME": bool(settings.app_name),
        "DATABASE_URL": bool(settings.database_url),
        "SPLUNK_BASE_URL": bool(settings.splunk_base_url),
        "SPLUNK_AUTH": settings.splunk_auth_configured(),
        "AI_PROVIDER": bool(settings.ai_provider),
    }
    for key, ok in checks.items():
        print(f"{key}: {'OK' if ok else 'MISSING'}")


if __name__ == "__main__":
    main()
