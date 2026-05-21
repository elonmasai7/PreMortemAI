from typing import Any


def detect_anomalies(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    for row in rows:
        for key, value in row.items():
            if "error" in key.lower():
                try:
                    numeric = float(value)
                except (TypeError, ValueError):
                    continue
                if numeric > 0:
                    anomalies.append({"signal": key, "value": numeric, "reason": "Non-zero error signal"})
    return anomalies[:20]
