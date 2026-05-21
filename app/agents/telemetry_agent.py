from app.services.splunk_search_service import SPL_TEMPLATES, SplunkSearchService


class TelemetryAgent:
    def __init__(self, search_service: SplunkSearchService):
        self.search_service = search_service

    def collect(self, service_name: str) -> list[dict]:
        rows: list[dict] = []
        for template_name in SPL_TEMPLATES:
            result = self.search_service.run_template(template_name, service_name, max_count=50)
            query = result.get("query")
            for row in result.get("rows", []):
                row_copy = dict(row)
                row_copy["__spl_query"] = query
                row_copy["__template_name"] = template_name
                rows.append(row_copy)
        return rows
