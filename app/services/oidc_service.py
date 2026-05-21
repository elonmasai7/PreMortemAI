from urllib.parse import urlencode

import httpx

from app.config import Settings
from app.exceptions import ConfigurationError


class OIDCService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def is_enabled(self) -> bool:
        return bool(self.settings.auth_oidc_enabled)

    def _assert_configured(self) -> None:
        required = [
            self.settings.auth_oidc_client_id,
            self.settings.auth_oidc_client_secret,
            self.settings.auth_oidc_discovery_url,
            self.settings.auth_oidc_redirect_uri,
        ]
        if not all(required):
            raise ConfigurationError(
                "OIDC is enabled but configuration is incomplete. Set AUTH_OIDC_CLIENT_ID, AUTH_OIDC_CLIENT_SECRET, AUTH_OIDC_DISCOVERY_URL, and AUTH_OIDC_REDIRECT_URI."
            )

    def discovery(self) -> dict:
        self._assert_configured()
        response = httpx.get(self.settings.auth_oidc_discovery_url, timeout=15)
        response.raise_for_status()
        return response.json()

    def build_authorize_url(self, state: str, nonce: str) -> str:
        discovery = self.discovery()
        authorization_endpoint = discovery.get("authorization_endpoint")
        if not authorization_endpoint:
            raise ConfigurationError("OIDC discovery document missing authorization_endpoint.")
        query = {
            "client_id": self.settings.auth_oidc_client_id,
            "redirect_uri": self.settings.auth_oidc_redirect_uri,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
            "nonce": nonce,
        }
        return f"{authorization_endpoint}?{urlencode(query)}"

    def exchange_code(self, code: str) -> dict:
        discovery = self.discovery()
        token_endpoint = discovery.get("token_endpoint")
        if not token_endpoint:
            raise ConfigurationError("OIDC discovery document missing token_endpoint.")
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.settings.auth_oidc_client_id,
            "client_secret": self.settings.auth_oidc_client_secret,
            "redirect_uri": self.settings.auth_oidc_redirect_uri,
        }
        response = httpx.post(token_endpoint, data=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    def fetch_userinfo(self, access_token: str) -> dict:
        discovery = self.discovery()
        userinfo_endpoint = discovery.get("userinfo_endpoint")
        if not userinfo_endpoint:
            raise ConfigurationError("OIDC discovery document missing userinfo_endpoint.")
        response = httpx.get(userinfo_endpoint, headers={"Authorization": f"Bearer {access_token}"}, timeout=15)
        response.raise_for_status()
        return response.json()
