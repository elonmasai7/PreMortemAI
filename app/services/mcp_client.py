import httpx

from app.config import Settings


class MCPClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def status(self) -> dict[str, str]:
        if not self.settings.mcp_enabled:
            return {"status": "disabled", "detail": "MCP integration disabled by configuration."}
        if not self.settings.mcp_server_url:
            return {"status": "error", "detail": "MCP_ENABLED is true but MCP_SERVER_URL is missing."}
        try:
            resp = httpx.get(self.settings.mcp_server_url, timeout=5)
            if resp.status_code < 400:
                return {"status": "ok", "detail": f"MCP server reachable: {self.settings.mcp_server_url}"}
            return {"status": "error", "detail": f"MCP server returned HTTP {resp.status_code}."}
        except httpx.HTTPError as exc:
            return {"status": "error", "detail": f"MCP server unreachable: {exc}"}
