from fastapi.testclient import TestClient

from app.dependencies import get_splunk_client
from app.main import _rate_limit_windows, app


class FakeSplunk:
    def run_search(self, query, max_count=100):
        return {"job_id": "sid", "status": "done", "rows": []}


def test_request_id_header_added():
    with TestClient(app) as client:
        response = client.get("/api/health/liveness")
        assert response.status_code == 200
        assert response.headers.get("x-request-id")


def test_splunk_search_rate_limit():
    _rate_limit_windows.clear()
    app.dependency_overrides[get_splunk_client] = lambda: FakeSplunk()
    with TestClient(app) as client:
        for _ in range(30):
            ok_response = client.post("/api/splunk/search", json={"query": "search index=main", "max_count": 1})
            assert ok_response.status_code == 200
        limited = client.post("/api/splunk/search", json={"query": "search index=main", "max_count": 1})
        assert limited.status_code == 429
    app.dependency_overrides.clear()
    _rate_limit_windows.clear()
