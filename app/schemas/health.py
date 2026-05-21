from pydantic import BaseModel


class ComponentStatus(BaseModel):
    status: str
    detail: str


class HealthResponse(BaseModel):
    app: ComponentStatus
    database: ComponentStatus
    splunk: ComponentStatus
    ai_provider: ComponentStatus
    mcp: ComponentStatus
    configuration_complete: bool
