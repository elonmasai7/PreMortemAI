from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_db, get_mcp_client, get_settings_dep, get_splunk_client
from app.models import Investigation, RemediationRecommendation

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings_dep), splunk_client=Depends(get_splunk_client)):
    investigations = db.query(Investigation).order_by(Investigation.updated_at.desc()).limit(10).all()
    avg_risk = db.query(func.avg(Investigation.risk_score)).scalar() or 0.0
    pending_actions = (
        db.query(RemediationRecommendation)
        .filter(RemediationRecommendation.status == "pending")
        .order_by(RemediationRecommendation.created_at.desc())
        .limit(10)
        .all()
    )
    services_at_risk = sorted({inv.service_name for inv in investigations if inv.risk_score >= 25})
    anomaly_signals = [inv.forecast_summary for inv in investigations if inv.forecast_summary][:5]
    splunk_status = "setup_required"
    no_data_message = None
    if settings.splunk_config_complete():
        try:
            splunk_client.test_connection()
            splunk_status = "connected"
            if not investigations:
                no_data_message = (
                    "Splunk is connected, but no matching operational telemetry was found for the configured indexes. "
                    "Configure SPL queries or indexes in settings."
                )
        except Exception:
            splunk_status = "error"
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "investigations": investigations,
            "avg_risk": round(float(avg_risk), 2),
            "pending_actions": pending_actions,
            "splunk_status": splunk_status,
            "ai_status": settings.ai_provider,
            "no_data_message": no_data_message,
            "services_at_risk": services_at_risk,
            "anomaly_signals": anomaly_signals,
        },
    )


@router.get("/setup", response_class=HTMLResponse)
def setup_page(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    mcp_client=Depends(get_mcp_client),
):
    missing = []
    if not settings.splunk_base_url:
        missing.append("SPLUNK_BASE_URL")
    if not settings.splunk_auth_configured():
        missing.append("SPLUNK_TOKEN or SPLUNK_USERNAME/SPLUNK_PASSWORD")
    if settings.ai_provider != "disabled" and not settings.ai_config_complete():
        missing.append("AI provider variables")
    splunk_check = {"status": "setup_required", "detail": "Missing configuration."}
    if settings.splunk_config_complete():
        try:
            splunk_check = splunk_client.test_connection()
        except Exception as exc:
            splunk_check = {"status": "error", "detail": str(exc)}
    mcp_status = mcp_client.status()
    return templates.TemplateResponse(
        "setup.html",
        {
            "request": request,
            "title": "Setup",
            "settings": settings,
            "missing": missing,
            "splunk_check": splunk_check,
            "mcp_status": mcp_status,
            "database_status": "ok",
        },
    )
