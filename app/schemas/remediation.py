from datetime import datetime

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=2000)


class RecommendationRead(BaseModel):
    id: int
    investigation_id: int
    action_type: str
    action_summary: str
    risk_of_action: str
    risk_of_inaction: str
    confidence: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
