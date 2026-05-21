from datetime import datetime

from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    service_name: str = Field(min_length=1, max_length=200)


class InvestigationRead(BaseModel):
    id: int
    title: str
    service_name: str
    status: str
    risk_score: float
    risk_level: str
    forecast_summary: str | None
    root_cause_summary: str | None
    blast_radius_summary: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
