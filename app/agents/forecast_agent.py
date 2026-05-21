from app.services.forecast_service import forecast_risk


class ForecastAgent:
    def run(self, rows: list[dict]) -> dict:
        return forecast_risk(rows)
