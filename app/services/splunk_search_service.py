from typing import Any

from app.config import Settings
from app.services.splunk_client import SplunkClient

SPL_TEMPLATES = {
    "service_error_trend": (
        'search index={default_index} service="{service_name}" (error OR exception OR timeout) '
        "| timechart span=5m count as error_count"
    ),
    "latency_trend": (
        'search index={default_index} service="{service_name}" '
        "| timechart span=5m avg(latency_ms) as avg_latency p95(latency_ms) as p95_latency"
    ),
    "deployment_correlation": (
        'search index={default_index} (deployment OR deploy OR version OR release) service="{service_name}" '
        "| table _time service version release actor message"
    ),
    "dependency_timeout": (
        'search index={default_index} service="{service_name}" (timeout OR retry OR upstream OR downstream) '
        "| table _time service message trace_id span_id status"
    ),
    "business_impact": (
        "search index={default_index} (checkout OR payment OR order OR transaction OR revenue) "
        "| stats count as event_count sum(revenue) as revenue_sum by status"
    ),
}


class SplunkSearchService:
    def __init__(self, client: SplunkClient, settings: Settings):
        self.client = client
        self.settings = settings

    def render_template(self, name: str, service_name: str) -> str:
        template = SPL_TEMPLATES[name]
        return template.format(default_index=self.settings.splunk_default_index or "*", service_name=service_name)

    def run_template(self, name: str, service_name: str, max_count: int = 100) -> dict[str, Any]:
        query = self.render_template(name, service_name)
        payload = self.client.run_search(query, max_count=max_count)
        payload["query"] = query
        payload["template_name"] = name
        return payload
