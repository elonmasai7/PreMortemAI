import pytest

from app.config import Settings
from app.exceptions import ConfigurationError
from app.services.splunk_client import SplunkClient


def test_splunk_client_requires_base_url():
    settings = Settings(SPLUNK_BASE_URL=None, SPLUNK_TOKEN="abc")
    client = SplunkClient(settings)
    with pytest.raises(ConfigurationError):
        client.test_connection()


def test_splunk_validate_rejects_disallowed_spl():
    settings = Settings(SPLUNK_BASE_URL="https://localhost:8089", SPLUNK_TOKEN="abc")
    client = SplunkClient(settings)
    with pytest.raises(Exception):
        client.validate_spl("search index=main | script")
