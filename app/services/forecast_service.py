from typing import Any


def forecast_risk(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "method": "transparent_fallback",
            "risk_score": 0.0,
            "risk_level": "low",
            "summary": "No telemetry rows returned; unable to infer imminent breach risk.",
        }
    error_values: list[float] = []
    for row in rows:
        for key, value in row.items():
            if "error" in key.lower() or "p95" in key.lower() or "latency" in key.lower():
                try:
                    error_values.append(float(value))
                except (ValueError, TypeError):
                    continue
    if not error_values:
        score = 25.0
    else:
        baseline = sum(error_values) / len(error_values)
        score = min(100.0, baseline)
    if score >= 75:
        level = "critical"
    elif score >= 50:
        level = "high"
    elif score >= 25:
        level = "medium"
    else:
        level = "low"
    return {
        "method": "transparent_fallback",
        "risk_score": round(score, 2),
        "risk_level": level,
        "summary": f"Forecasted risk level {level} based on recent telemetry trends.",
    }
