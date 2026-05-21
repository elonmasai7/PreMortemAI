from fastapi.testclient import TestClient

from app.dependencies import get_splunk_client
from app.main import app


class FakeSplunk:
    def test_connection(self):
        return {"status": "ok", "server": "fake"}

    def run_search(self, query, max_count=100):
        return {
            "job_id": "sid123",
            "status": "done",
            "rows": [{"service": "payments", "error_count": 10}],
        }


def test_remediation_approve_reject():
    app.dependency_overrides[get_splunk_client] = lambda: FakeSplunk()
    with TestClient(app) as client:
        created = client.post("/api/investigations", json={"title": "Payment risk", "service_name": "payments"}).json()
        inv_id = created["id"]
        client.post(f"/api/investigations/{inv_id}/run")

        approve = client.post(f"/api/remediation/{inv_id}/approve", json={"note": "Looks safe"})
        assert approve.status_code == 200
        assert approve.json()["status"] == "approved"

        reject = client.post(f"/api/remediation/{inv_id}/reject", json={"note": "Changed decision"})
        assert reject.status_code == 200
        assert reject.json()["status"] == "rejected"
