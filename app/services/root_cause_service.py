from typing import Any


def rank_root_causes_from_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return [
            {
                "cause": "No correlated events found in selected time range",
                "confidence": 0.2,
                "evidence_summary": "Splunk returned zero rows for the investigation queries.",
                "rank": 1,
            }
        ]
    joined = " ".join(str(r) for r in rows[:20]).lower()
    candidates = []
    if "deploy" in joined or "release" in joined:
        candidates.append(
            {
                "cause": "Recent deployment or release event correlates with service degradation",
                "confidence": 0.7,
                "evidence_summary": "Deployment/release keywords appear near error patterns.",
                "rank": len(candidates) + 1,
            }
        )
    if "timeout" in joined or "upstream" in joined:
        candidates.append(
            {
                "cause": "Upstream dependency timeout is likely propagating failures",
                "confidence": 0.65,
                "evidence_summary": "Timeout and dependency terms appear in evidence set.",
                "rank": len(candidates) + 1,
            }
        )
    if not candidates:
        candidates.append(
            {
                "cause": "Service-side error rate increase",
                "confidence": 0.5,
                "evidence_summary": "Generic error trend detected but no direct dependency marker.",
                "rank": 1,
            }
        )
    return candidates
