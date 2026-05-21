from app.models import HumanDecision, RemediationRecommendation


def apply_decision(recommendation: RemediationRecommendation, decision: str) -> None:
    if decision == "approve":
        recommendation.status = "approved"
    elif decision == "reject":
        recommendation.status = "rejected"


def build_decision_audit(recommendation_id: int, investigation_id: int, decision: str, note: str | None) -> HumanDecision:
    return HumanDecision(
        recommendation_id=recommendation_id,
        investigation_id=investigation_id,
        decision=decision,
        note=note,
    )
