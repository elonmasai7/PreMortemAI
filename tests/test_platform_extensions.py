from fastapi.testclient import TestClient

from app.main import app


def test_slo_and_queue_and_compliance_endpoints():
    with TestClient(app) as client:
        slo = client.get("/api/metrics/slo")
        assert slo.status_code == 200
        assert "success_rate_percent" in slo.json()

        queue = client.get("/api/queue/metrics")
        assert queue.status_code == 200
        assert "queue_enabled" in queue.json()

        retention = client.get("/api/compliance/retention/status")
        assert retention.status_code == 200
        assert "retention_days" in retention.json()
