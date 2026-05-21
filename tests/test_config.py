from app.config import Settings


def test_splunk_config_validation():
    settings = Settings(
        SPLUNK_BASE_URL="https://localhost:8089",
        SPLUNK_TOKEN="token",
    )
    assert settings.splunk_config_complete() is True


def test_missing_splunk_auth():
    settings = Settings(SPLUNK_BASE_URL="https://localhost:8089")
    assert settings.splunk_config_complete() is False
