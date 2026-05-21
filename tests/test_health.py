from fastapi.testclient import TestClient

from app.dependencies import get_splunk_client
from app.main import app


class FakeSplunk:
    def test_connection(self):
        return {"status": "ok", "server": "fake"}


def test_health_routes():
    app.dependency_overrides[get_splunk_client] = lambda: FakeSplunk()
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["app"]["status"] == "ok"

    live = client.get("/api/health/liveness")
    assert live.status_code == 200
    assert live.json()["alive"] is True

    ready = client.get("/api/health/readiness")
    assert ready.status_code == 200
    assert "components" in ready.json()
