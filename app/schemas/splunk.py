from typing import Any

from pydantic import BaseModel, Field


class SplunkSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    max_count: int = Field(default=100, ge=1, le=1000)


class SplunkSearchResponse(BaseModel):
    job_id: str | None
    status: str
    rows: list[dict[str, Any]]
    message: str


class SplunkValidateRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
