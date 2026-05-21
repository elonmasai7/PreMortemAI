from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_ai_provider, get_db, get_mcp_client, get_settings_dep, get_splunk_client
from app.schemas.health import ComponentStatus, HealthResponse

router = APIRouter(prefix="/api/health", tags=["health"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def build_health_status(db: Session, settings: Settings, splunk_client, ai_provider, mcp_client) -> HealthResponse:
    db_status = ComponentStatus(status="ok", detail="SQLite reachable")
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = ComponentStatus(status="error", detail=f"Database unreachable: {exc}")

    if not settings.splunk_config_complete():
        splunk_status = ComponentStatus(status="setup_required", detail="Set SPLUNK_BASE_URL and credentials.")
    else:
        try:
            splunk_client.test_connection()
            splunk_status = ComponentStatus(status="ok", detail="Splunk API reachable")
        except Exception as exc:
            splunk_status = ComponentStatus(status="error", detail=str(exc))

    if settings.ai_provider == "disabled":
        ai_status = ComponentStatus(status="disabled", detail="AI provider disabled by configuration.")
    elif not settings.ai_config_complete():
        ai_status = ComponentStatus(status="setup_required", detail="AI provider configuration incomplete.")
    else:
        ai_status = ComponentStatus(status="ok", detail=f"AI provider configured: {settings.ai_provider}")

    mcp = mcp_client.status()
    mcp_status = ComponentStatus(status=mcp["status"], detail=mcp["detail"])

    return HealthResponse(
        app=ComponentStatus(status="ok", detail="Application running"),
        database=db_status,
        splunk=splunk_status,
        ai_provider=ai_status,
        mcp=mcp_status,
        configuration_complete=(db_status.status == "ok" and splunk_status.status in {"ok", "setup_required"}),
    )


@router.get("", response_model=HealthResponse)
def health(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    ai_provider=Depends(get_ai_provider),
    mcp_client=Depends(get_mcp_client),
):
    return build_health_status(db, settings, splunk_client, ai_provider, mcp_client)


@router.get("/readiness")
def readiness(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    ai_provider=Depends(get_ai_provider),
    mcp_client=Depends(get_mcp_client),
):
    result = build_health_status(db, settings, splunk_client, ai_provider, mcp_client)
    return {"ready": result.database.status == "ok", "components": result.model_dump()}


@router.get("/liveness")
def liveness():
    return {"alive": True}


@page_router.get("/health", response_class=HTMLResponse)
def health_page(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    ai_provider=Depends(get_ai_provider),
    mcp_client=Depends(get_mcp_client),
):
    payload = build_health_status(db, settings, splunk_client, ai_provider, mcp_client)
    return templates.TemplateResponse("error.html", {"request": request, "title": "Health", "health": payload.model_dump()})
