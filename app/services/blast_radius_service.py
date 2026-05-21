from typing import Any


def estimate_blast_radius(rows: list[dict[str, Any]], service_name: str) -> dict[str, Any]:
    impacted_services = {service_name}
    for row in rows[:200]:
        for key in ("service", "upstream_service", "downstream_service"):
            val = row.get(key)
            if val:
                impacted_services.add(str(val))
    user_count = None
    for row in rows:
        if "user_count" in row:
            try:
                user_count = int(float(row["user_count"]))
            except (TypeError, ValueError):
                user_count = None
            break
    return {
        "services": sorted(impacted_services),
        "affected_transactions_estimate": len(rows),
        "affected_users_estimate": user_count,
        "revenue_at_risk": None,
        "summary": "Revenue impact is omitted unless explicit business telemetry is present.",
    }
