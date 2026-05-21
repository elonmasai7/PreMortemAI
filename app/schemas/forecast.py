from pydantic import BaseModel


class ForecastSummary(BaseModel):
    method: str
    risk_score: float
    risk_level: str
    summary: str
