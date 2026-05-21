from app.services.blast_radius_service import estimate_blast_radius


class BlastRadiusAgent:
    def run(self, rows: list[dict], service_name: str) -> dict:
        return estimate_blast_radius(rows, service_name)
