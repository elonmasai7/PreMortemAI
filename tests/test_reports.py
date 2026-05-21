from fastapi.testclient import TestClient

from app.dependencies import get_splunk_client
from app.main import app


class FakeSplunk:
    def test_connection(self):
        return {"status": "ok", "server": "fake"}

    def run_search(self, query, max_count=100):
        return {"job_id": "sid123", "status": "done", "rows": [{"service": "api", "error_count": 5}]}


def test_report_generation_flow():
    app.dependency_overrides[get_splunk_client] = lambda: FakeSplunk()
    with TestClient(app) as client:
        created = client.post("/api/investigations", json={"title": "API risk", "service_name": "api"}).json()
        inv_id = created["id"]
        client.post(f"/api/investigations/{inv_id}/run")

        generated = client.post(f"/api/reports/{inv_id}/generate")
        assert generated.status_code == 200
        report_id = generated.json()["id"]

        report = client.get(f"/api/reports/{report_id}")
        assert report.status_code == 200
        assert "markdown_body" in report.json()
