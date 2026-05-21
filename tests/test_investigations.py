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
            "rows": [{"service": "checkout", "error_count": 42, "message": "timeout upstream"}],
        }


def test_create_and_run_investigation():
    app.dependency_overrides[get_splunk_client] = lambda: FakeSplunk()
    with TestClient(app) as client:
        created = client.post("/api/investigations", json={"title": "Checkout risk", "service_name": "checkout"})
        assert created.status_code == 201
        inv_id = created.json()["id"]

        run_resp = client.post(f"/api/investigations/{inv_id}/run")
        assert run_resp.status_code == 200
        assert run_resp.json()["status"] in {"analyzed", "failed"}

        list_resp = client.get("/api/investigations")
        assert list_resp.status_code == 200
        assert isinstance(list_resp.json(), list)

        paged_resp = client.get("/api/investigations?limit=1&offset=0")
        assert paged_resp.status_code == 200
        assert len(paged_resp.json()) <= 1
