from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.agents.blast_radius_agent import BlastRadiusAgent
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.forecast_agent import ForecastAgent
from app.agents.remediation_agent import RemediationAgent
from app.agents.report_agent import ReportAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.telemetry_agent import TelemetryAgent
from app.config import Settings
from app.dependencies import get_ai_provider, get_db, get_settings_dep, get_splunk_client
from app.models import Investigation
from app.schemas.investigation import InvestigationCreate, InvestigationRead
from app.services.splunk_search_service import SplunkSearchService

router = APIRouter(prefix="/api/investigations", tags=["investigations"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def get_investigation_or_404(db: Session, investigation_id: int) -> Investigation:
    item = db.get(Investigation, investigation_id)
    if not item:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return item


def build_coordinator(settings: Settings, splunk_client, ai_provider) -> CoordinatorAgent:
    search_service = SplunkSearchService(splunk_client, settings)
    return CoordinatorAgent(
        telemetry_agent=TelemetryAgent(search_service),
        forecast_agent=ForecastAgent(),
        root_cause_agent=RootCauseAgent(),
        blast_radius_agent=BlastRadiusAgent(),
        remediation_agent=RemediationAgent(ai_provider),
        report_agent=ReportAgent(ai_provider),
    )


@router.get("", response_model=list[InvestigationRead])
def list_investigations(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    service_name: str | None = Query(default=None),
):
    query = db.query(Investigation)
    if status:
        query = query.filter(Investigation.status == status)
    if service_name:
        query = query.filter(Investigation.service_name == service_name)
    return query.order_by(Investigation.created_at.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=InvestigationRead, status_code=201)
def create_investigation(payload: InvestigationCreate, db: Session = Depends(get_db)):
    item = Investigation(title=payload.title, service_name=payload.service_name, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{investigation_id}", response_model=InvestigationRead)
def get_investigation(investigation_id: int, db: Session = Depends(get_db)):
    return get_investigation_or_404(db, investigation_id)


@router.post("/{investigation_id}/run", response_model=InvestigationRead)
def run_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    ai_provider=Depends(get_ai_provider),
):
    item = get_investigation_or_404(db, investigation_id)
    coordinator = build_coordinator(settings, splunk_client, ai_provider)
    try:
        return coordinator.run(db, item)
    except Exception as exc:
        item.status = "failed"
        db.add(item)
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{investigation_id}/refresh", response_model=InvestigationRead)
def refresh_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    ai_provider=Depends(get_ai_provider),
):
    return run_investigation(investigation_id, db, settings, splunk_client, ai_provider)


@router.delete("/{investigation_id}", status_code=204)
def delete_investigation(investigation_id: int, db: Session = Depends(get_db)):
    item = get_investigation_or_404(db, investigation_id)
    db.delete(item)
    db.commit()
    return None


@page_router.get("/investigations", response_class=HTMLResponse)
def investigations_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(Investigation).order_by(Investigation.created_at.desc()).all()
    return templates.TemplateResponse("investigations.html", {"request": request, "title": "Investigations", "items": items})


@page_router.post("/investigations/new", response_class=HTMLResponse)
def create_from_page(
    request: Request,
    title: str = Form(...),
    service_name: str = Form(...),
    db: Session = Depends(get_db),
):
    item = Investigation(title=title, service_name=service_name, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)
    return RedirectResponse(url=f"/investigations/{item.id}", status_code=303)


@page_router.get("/investigations/{investigation_id}", response_class=HTMLResponse)
def investigation_detail_page(request: Request, investigation_id: int, db: Session = Depends(get_db)):
    item = get_investigation_or_404(db, investigation_id)
    return templates.TemplateResponse(
        "investigation_detail.html",
        {
            "request": request,
            "title": "Investigation Detail",
            "item": item,
            "evidence": item.evidences,
            "root_causes": item.root_causes,
            "recommendations": item.recommendations,
            "decisions": item.decisions,
            "reports": item.reports,
        },
    )
