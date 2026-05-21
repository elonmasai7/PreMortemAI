from app.config import Settings
from app.services.ai_client import build_ai_provider


def test_disabled_ai_mode():
    settings = Settings(AI_PROVIDER="disabled")
    provider = build_ai_provider(settings)
    output = provider.summarize_evidence([{"event": "error spike"}])
    assert "summary" in output
    assert output["human_approval_required"] is True
