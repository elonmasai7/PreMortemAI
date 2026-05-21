from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import Settings
from app.exceptions import AIProviderError


class AIProvider(ABC):
    @abstractmethod
    def summarize_evidence(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def rank_root_causes(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_remediation_plan(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_postmortem(self, investigation: dict[str, Any]) -> str:
        raise NotImplementedError


class DisabledAIProvider(AIProvider):
    def summarize_evidence(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "summary": "AI provider disabled. Using rule-based summary from Splunk evidence.",
            "evidence_used": evidence[:5],
            "confidence": 0.5,
            "assumptions": ["No model inference available."],
            "missing_data": ["Enable AI_PROVIDER for model-generated narrative."],
            "human_approval_required": True,
        }

    def rank_root_causes(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        first = evidence[0] if evidence else {"message": "No evidence returned by Splunk search."}
        return {
            "candidates": [
                {
                    "cause": "Potential service degradation inferred from recent error/latency patterns",
                    "confidence": 0.4,
                    "evidence_summary": str(first)[:400],
                    "rank": 1,
                }
            ],
            "assumptions": ["Limited to deterministic analysis."],
            "missing_data": ["Enable AI provider for richer correlation."],
            "human_approval_required": True,
        }

    def create_remediation_plan(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "action_type": "investigate",
            "action_summary": "Review latest failing service logs and compare with deployment events before rollback decision.",
            "risk_of_action": "Low operational risk, moderate engineering effort.",
            "risk_of_inaction": "Potential outage escalation if degradation trend continues.",
            "confidence": 0.45,
            "evidence_used": evidence[:5],
            "assumptions": ["No automated rollback allowed."],
            "missing_data": ["Service topology metadata may improve plan quality."],
            "human_approval_required": True,
            "suggested_alert_rule": "Create Splunk alert for error_count trend acceleration over 3 consecutive 5m buckets.",
            "suggested_dashboard_panel": "Plot p95 latency and error_count by service over last 60 minutes.",
        }

    def generate_postmortem(self, investigation: dict[str, Any]) -> str:
        return (
            f"# Post-Incident Report\n\n"
            f"## Incident Summary\nInvestigation {investigation.get('id')} for service {investigation.get('service_name')}\n\n"
            "## Notes\nAI provider is disabled. Report generated from stored evidence and decisions.\n"
        )


class OpenAICompatibleProvider(AIProvider):
    def __init__(self, settings: Settings):
        self.settings = settings

    def _chat(self, prompt: str) -> str:
        if not (self.settings.ai_base_url and self.settings.ai_model and self.settings.ai_api_key):
            raise AIProviderError("AI provider is not fully configured. Check AI_BASE_URL, AI_MODEL, and AI_API_KEY.")
        headers = {"Authorization": f"Bearer {self.settings.ai_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.settings.ai_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an incident prevention assistant. Never invent facts. Always cite provided evidence.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
        try:
            resp = httpx.post(f"{self.settings.ai_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise AIProviderError(f"AI provider request failed: {exc}") from exc
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise AIProviderError("AI provider response format was invalid.") from exc

    def summarize_evidence(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        content = self._chat(f"Summarize this Splunk evidence and include assumptions and missing data:\n{evidence[:20]}")
        return {"summary": content, "confidence": 0.7, "human_approval_required": True, "evidence_used": evidence[:10]}

    def rank_root_causes(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        content = self._chat(f"Rank likely root causes with confidence and evidence:\n{evidence[:20]}")
        return {
            "candidates": [{"cause": content[:280], "confidence": 0.65, "evidence_summary": content[:600], "rank": 1}],
            "human_approval_required": True,
        }

    def create_remediation_plan(self, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        content = self._chat(f"Create safe remediation plan. Must require human approval. Evidence:\n{evidence[:20]}")
        return {
            "action_type": "human_review",
            "action_summary": content[:800],
            "risk_of_action": "Requires operator validation before production change.",
            "risk_of_inaction": "Risk may escalate to outage.",
            "confidence": 0.6,
            "evidence_used": evidence[:10],
            "assumptions": ["Model output reviewed by engineer."],
            "missing_data": [],
            "human_approval_required": True,
            "suggested_alert_rule": "Tune threshold-based alert from observed error growth.",
            "suggested_dashboard_panel": "Service-level latency and error trend panel.",
        }

    def generate_postmortem(self, investigation: dict[str, Any]) -> str:
        return self._chat(f"Generate concise markdown postmortem from: {investigation}")


class LocalModelProvider(OpenAICompatibleProvider):
    pass


def build_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "disabled":
        return DisabledAIProvider()
    if settings.ai_provider == "local":
        return LocalModelProvider(settings)
    if settings.ai_provider == "openai_compatible":
        return OpenAICompatibleProvider(settings)
    raise AIProviderError(f"Unsupported AI provider: {settings.ai_provider}")
