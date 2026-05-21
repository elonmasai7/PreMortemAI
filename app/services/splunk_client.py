import time
from typing import Any

import httpx

from app.config import Settings
from app.exceptions import ConfigurationError, SplunkAuthenticationError, SplunkConnectionError, SplunkSearchError
from app.services.validation_service import validate_spl_query


class SplunkClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.splunk_base_url
        self.timeout = settings.splunk_timeout_seconds
        if not self.base_url:
            return
        self._client = httpx.Client(verify=settings.splunk_verify_ssl, timeout=self.timeout)

    def _ensure_config(self) -> None:
        if not self.settings.splunk_base_url:
            raise ConfigurationError("Splunk base URL is missing. Set SPLUNK_BASE_URL.")
        if not self.settings.splunk_auth_configured():
            raise ConfigurationError(
                "Splunk authentication is missing. Set SPLUNK_TOKEN or SPLUNK_USERNAME/SPLUNK_PASSWORD."
            )

    def _auth(self) -> tuple[dict[str, str], tuple[str, str] | None]:
        if self.settings.splunk_token:
            return {"Authorization": f"Bearer {self.settings.splunk_token}"}, None
        return {}, (self.settings.splunk_username or "", self.settings.splunk_password or "")

    def _request(self, method: str, path: str, data: dict[str, Any] | None = None, params: dict[str, Any] | None = None):
        self._ensure_config()
        headers, auth = self._auth()
        url = f"{self.settings.splunk_base_url}{path}"
        try:
            resp = self._client.request(method, url, data=data, params=params, headers=headers, auth=auth)
        except httpx.HTTPError as exc:
            raise SplunkConnectionError(f"Unable to connect to Splunk API: {exc}") from exc
        if resp.status_code in (401, 403):
            raise SplunkAuthenticationError(
                "Splunk authentication failed. Check SPLUNK_TOKEN or SPLUNK_USERNAME/SPLUNK_PASSWORD."
            )
        if resp.status_code >= 400:
            raise SplunkSearchError(f"Splunk API request failed: HTTP {resp.status_code} - {resp.text[:200]}")
        return resp

    def test_connection(self) -> dict[str, Any]:
        resp = self._request("GET", "/services/server/info", params={"output_mode": "json"})
        payload = resp.json()
        return {
            "status": "ok",
            "server": payload.get("entry", [{}])[0].get("name", "unknown"),
        }

    def list_indexes(self) -> list[str]:
        resp = self._request("GET", "/services/data/indexes", params={"count": 0, "output_mode": "json"})
        return [entry.get("name", "") for entry in resp.json().get("entry", []) if entry.get("name")]

    def list_saved_searches(self) -> list[str]:
        resp = self._request(
            "GET",
            "/servicesNS/-/-/saved/searches",
            params={"count": 0, "output_mode": "json"},
        )
        return [entry.get("name", "") for entry in resp.json().get("entry", []) if entry.get("name")]

    def run_search(self, query: str, max_count: int = 100) -> dict[str, Any]:
        validate_spl_query(query, self.settings)
        resp = self._request(
            "POST",
            "/services/search/jobs",
            data={"search": query, "output_mode": "json", "exec_mode": "normal"},
        )
        sid = resp.json().get("sid")
        if not sid:
            raise SplunkSearchError("Splunk did not return a search job ID.")
        results = self.get_search_results(sid=sid, max_count=max_count)
        return {"job_id": sid, "status": "done", "rows": results}

    def get_search_results(self, sid: str, max_count: int = 100) -> list[dict[str, Any]]:
        deadline = time.time() + self.settings.splunk_timeout_seconds
        while time.time() < deadline:
            status_resp = self._request(
                "GET",
                f"/services/search/jobs/{sid}",
                params={"output_mode": "json"},
            )
            entry = status_resp.json().get("entry", [{}])[0]
            content = entry.get("content", {})
            if content.get("isFailed"):
                raise SplunkSearchError("Splunk search job failed.")
            if content.get("isDone"):
                break
            time.sleep(1)
        else:
            raise SplunkSearchError("Timed out waiting for Splunk search job completion.")

        result_resp = self._request(
            "GET",
            f"/services/search/jobs/{sid}/results",
            params={"output_mode": "json", "count": max_count},
        )
        payload = result_resp.json()
        return payload.get("results", [])

    def validate_spl(self, query: str) -> dict[str, Any]:
        validate_spl_query(query, self.settings)
        resp = self._request(
            "POST",
            "/services/search/parser",
            data={"q": query, "output_mode": "json"},
        )
        return {"valid": True, "details": resp.json()}

    def run_oneshot_search(self, query: str, max_count: int = 100) -> list[dict[str, Any]]:
        validate_spl_query(query, self.settings)
        resp = self._request(
            "POST",
            "/services/search/jobs/export",
            data={
                "search": query,
                "output_mode": "json",
                "exec_mode": "oneshot",
                "count": max_count,
            },
        )
        lines = [line for line in resp.text.splitlines() if line.strip()]
        rows: list[dict[str, Any]] = []
        for line in lines:
            try:
                parsed = httpx.Response(200, text=line).json()
            except ValueError:
                continue
            result = parsed.get("result")
            if result:
                rows.append(result)
        return rows
