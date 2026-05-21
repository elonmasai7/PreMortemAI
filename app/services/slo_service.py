from collections import deque
from threading import Lock


class SLOTracker:
    def __init__(self, max_points: int = 20000):
        self.max_points = max_points
        self._records: deque[tuple[float, int]] = deque(maxlen=max_points)
        self._lock = Lock()

    def record(self, latency_seconds: float, status_code: int) -> None:
        with self._lock:
            self._records.append((latency_seconds, status_code))

    def summary(self, success_target_percent: float, latency_target_ms: int) -> dict:
        with self._lock:
            points = list(self._records)
        total = len(points)
        if total == 0:
            return {
                "window_requests": 0,
                "success_rate_percent": 100.0,
                "latency_p95_ms": 0.0,
                "error_budget_remaining_percent": 100.0,
                "slo_target_success_percent": success_target_percent,
                "slo_target_latency_ms": latency_target_ms,
            }

        successes = sum(1 for _, status in points if status < 500)
        success_rate = (successes / total) * 100.0

        latencies_ms = sorted(latency * 1000.0 for latency, _ in points)
        p95_index = int(max(0, min(len(latencies_ms) - 1, round(0.95 * (len(latencies_ms) - 1)))))
        p95 = latencies_ms[p95_index]

        allowed_error_rate = max(0.0, 100.0 - success_target_percent)
        current_error_rate = max(0.0, 100.0 - success_rate)
        if allowed_error_rate <= 0:
            remaining = 100.0 if current_error_rate == 0 else 0.0
        else:
            remaining = max(0.0, min(100.0, ((allowed_error_rate - current_error_rate) / allowed_error_rate) * 100.0))

        return {
            "window_requests": total,
            "success_rate_percent": round(success_rate, 3),
            "latency_p95_ms": round(p95, 2),
            "error_budget_remaining_percent": round(remaining, 2),
            "slo_target_success_percent": success_target_percent,
            "slo_target_latency_ms": latency_target_ms,
        }
