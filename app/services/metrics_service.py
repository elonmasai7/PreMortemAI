try:
    from prometheus_client import Counter, Histogram
except ImportError:  # pragma: no cover
    class _NoopMetric:
        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            return None

        def observe(self, *args, **kwargs):
            return None

    def Counter(*args, **kwargs):  # type: ignore
        return _NoopMetric()

    def Histogram(*args, **kwargs):  # type: ignore
        return _NoopMetric()

REQUEST_COUNT = Counter(
    "premortem_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "premortem_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)
