from fastapi.testclient import TestClient

from app.main import app


def test_auth_login_and_me():
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"tenant_slug": "default", "username": "admin", "password": "admin12345"},
        )
        assert login.status_code == 200
        payload = login.json()
        assert payload.get("access_token")

        me = client.get("/api/auth/me")
        assert me.status_code == 200
        assert me.json().get("tenant_id") == 1
