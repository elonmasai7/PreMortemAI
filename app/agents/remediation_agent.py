from app.services.ai_client import AIProvider


class RemediationAgent:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    def run(self, rows: list[dict]) -> dict:
        return self.ai_provider.create_remediation_plan(rows)
