from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import Settings
from app.dependencies import get_db, get_settings_dep, get_splunk_client
from app.exceptions import ValidationError
from app.models import AppSetting
from app.schemas.splunk import SplunkSearchRequest, SplunkValidateRequest

router = APIRouter(prefix="/api/splunk", tags=["splunk"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/status")
def status(settings: Settings = Depends(get_settings_dep), splunk_client=Depends(get_splunk_client)):
    if not settings.splunk_config_complete():
        return {"status": "setup_required", "message": "Splunk settings incomplete."}
    return splunk_client.test_connection()


@router.post("/search")
def search(payload: SplunkSearchRequest, splunk_client=Depends(get_splunk_client)):
    return splunk_client.run_search(payload.query, max_count=payload.max_count)


@router.get("/indexes")
def indexes(splunk_client=Depends(get_splunk_client)):
    return {"indexes": splunk_client.list_indexes()}


@router.get("/saved-searches")
def saved_searches(splunk_client=Depends(get_splunk_client)):
    return {"saved_searches": splunk_client.list_saved_searches()}


@router.post("/validate-query")
def validate_query(payload: SplunkValidateRequest, splunk_client=Depends(get_splunk_client)):
    try:
        return splunk_client.validate_spl(payload.query)
    except Exception as exc:
        raise ValidationError(str(exc)) from exc


@page_router.get("/splunk/search", response_class=HTMLResponse)
def search_page(request: Request, db: Session = Depends(get_db)):
    saved = db.query(AppSetting).filter(AppSetting.key.like("spl_template::%")).order_by(AppSetting.key).all()
    return templates.TemplateResponse(
        "splunk_search.html",
        {"request": request, "title": "Splunk Search", "rows": [], "error": None, "query": "", "saved": saved},
    )


@page_router.post("/splunk/search", response_class=HTMLResponse)
def run_search_page(
    request: Request,
    query: str = Form(...),
    save_template_name: str | None = Form(default=None),
    splunk_client=Depends(get_splunk_client),
    db: Session = Depends(get_db),
):
    rows = []
    error = None
    try:
        result = splunk_client.run_search(query, max_count=100)
        rows = result.get("rows", [])
        if save_template_name:
            key = f"spl_template::{save_template_name.strip()}"
            existing = db.query(AppSetting).filter(AppSetting.key == key).first()
            if existing:
                existing.value = query
                db.add(existing)
            else:
                db.add(AppSetting(key=key, value=query))
            db.commit()
    except Exception as exc:
        error = str(exc)
    saved = db.query(AppSetting).filter(AppSetting.key.like("spl_template::%")).order_by(AppSetting.key).all()
    return templates.TemplateResponse(
        "splunk_search.html",
        {"request": request, "title": "Splunk Search", "rows": rows, "error": error, "query": query, "saved": saved},
    )
