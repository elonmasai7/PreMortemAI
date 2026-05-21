from app.services.root_cause_service import rank_root_causes_from_rows


class RootCauseAgent:
    def run(self, rows: list[dict]) -> list[dict]:
        return rank_root_causes_from_rows(rows)
