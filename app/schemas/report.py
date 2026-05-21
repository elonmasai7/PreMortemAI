from datetime import datetime

from pydantic import BaseModel


class ReportRead(BaseModel):
    id: int
    investigation_id: int
    title: str
    markdown_body: str
    created_at: datetime

    model_config = {"from_attributes": True}
