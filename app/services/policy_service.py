from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import Settings
from app.exceptions import ValidationError
from app.models import Evidence, RemediationRecommendation
from app.services.auth_service import AuthContext
from app.services.authz import has_role


@dataclass
class PolicyDecision:
    allowed: bool
    violations: list[str]


def _restricted_keywords(settings: Settings) -> list[str]:
    return [part.strip().lower() for part in settings.remediation_restricted_keywords.split(",") if part.strip()]


def evaluate_remediation_approval_policy(
    db: Session,
    context: AuthContext,
    recommendation: RemediationRecommendation,
    settings: Settings,
) -> PolicyDecision:
    violations: list[str] = []

    evidence_count = (
        db.query(Evidence)
        .filter(Evidence.tenant_id == context.tenant_id, Evidence.investigation_id == recommendation.investigation_id)
        .count()
    )
    if evidence_count < settings.remediation_min_evidence_for_approval:
        violations.append(
            f"Insufficient evidence for approval. Minimum required: {settings.remediation_min_evidence_for_approval}."
        )

    summary_lower = recommendation.action_summary.lower()
    for keyword in _restricted_keywords(settings):
        if keyword and keyword in summary_lower:
            violations.append(f"Action summary contains restricted remediation keyword: '{keyword}'.")

    if recommendation.confidence < 0.4 and not has_role(context, "admin"):
        violations.append("Low confidence recommendations require admin or owner approval.")

    risk_text = (recommendation.risk_of_action or "").lower()
    if "high" in risk_text and not has_role(context, "admin"):
        violations.append("High-risk actions require admin or owner approval.")

    return PolicyDecision(allowed=(len(violations) == 0), violations=violations)


def enforce_remediation_approval_policy(
    db: Session,
    context: AuthContext,
    recommendation: RemediationRecommendation,
    settings: Settings,
) -> None:
    decision = evaluate_remediation_approval_policy(db, context, recommendation, settings)
    if not decision.allowed:
        raise ValidationError("Remediation policy blocked approval. " + " ".join(decision.violations))
