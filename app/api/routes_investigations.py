from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_ai_provider, get_auth_context, get_db, get_settings_dep, get_splunk_client, require_roles
from app.models import Investigation
from app.schemas.investigation import InvestigationCreate, InvestigationRead
from app.services.investigation_pipeline import run_investigation_pipeline
from app.services.queue_service import enqueue_investigation_run

router = APIRouter(prefix="/api/investigations", tags=["investigations"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def get_investigation_or_404(db: Session, investigation_id: int) -> Investigation:
    item = db.get(Investigation, investigation_id)
    if not item:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return item


@router.get("", response_model=list[InvestigationRead])
def list_investigations(
    db: Session = Depends(get_db),
    context=Depends(get_auth_context),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    service_name: str | None = Query(default=None),
):
    query = db.query(Investigation).filter(Investigation.tenant_id == context.tenant_id)
    if status:
        query = query.filter(Investigation.status == status)
    if service_name:
        query = query.filter(Investigation.service_name == service_name)
    return query.order_by(Investigation.created_at.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=InvestigationRead, status_code=201)
def create_investigation(
    payload: InvestigationCreate,
    db: Session = Depends(get_db),
    context=Depends(require_roles("analyst", "admin", "owner")),
):
    item = Investigation(tenant_id=context.tenant_id, title=payload.title, service_name=payload.service_name, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{investigation_id}", response_model=InvestigationRead)
def get_investigation(investigation_id: int, db: Session = Depends(get_db), context=Depends(get_auth_context)):
    item = get_investigation_or_404(db, investigation_id)
    if item.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return item


@router.post("/{investigation_id}/run", response_model=InvestigationRead)
def run_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
    splunk_client=Depends(get_splunk_client),
    ai_provider=Depends(get_ai_provider),
    context=Depends(require_roles("analyst", "admin", "owner")),
):
    item = get_investigation_or_404(db, investigation_id)
    if item.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    job_id = enqueue_investigation_run(settings, investigation_id=item.id, tenant_id=context.tenant_id)
    if job_id:
        item.status = "queued"
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    try:
        return run_investigation_pipeline(db, item, settings, splunk_client, ai_provider)
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
    context=Depends(require_roles("analyst", "admin", "owner")),
):
    return run_investigation(investigation_id, db, settings, splunk_client, ai_provider, context)


@router.delete("/{investigation_id}", status_code=204)
def delete_investigation(
    investigation_id: int,
    db: Session = Depends(get_db),
    context=Depends(require_roles("admin", "owner")),
):
    item = get_investigation_or_404(db, investigation_id)
    if item.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    db.delete(item)
    db.commit()
    return None


@page_router.get("/investigations", response_class=HTMLResponse)
def investigations_page(request: Request, db: Session = Depends(get_db), context=Depends(get_auth_context)):
    items = db.query(Investigation).filter(Investigation.tenant_id == context.tenant_id).order_by(Investigation.created_at.desc()).all()
    return templates.TemplateResponse("investigations.html", {"request": request, "title": "Investigations", "items": items})


@page_router.post("/investigations/new", response_class=HTMLResponse)
def create_from_page(
    request: Request,
    title: str = Form(...),
    service_name: str = Form(...),
    db: Session = Depends(get_db),
    context=Depends(get_auth_context),
):
    item = Investigation(tenant_id=context.tenant_id, title=title, service_name=service_name, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)
    return RedirectResponse(url=f"/investigations/{item.id}", status_code=303)


@page_router.get("/investigations/{investigation_id}", response_class=HTMLResponse)
def investigation_detail_page(request: Request, investigation_id: int, db: Session = Depends(get_db), context=Depends(get_auth_context)):
    item = get_investigation_or_404(db, investigation_id)
    if item.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Investigation not found.")
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
