from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.agents.report_agent import ReportAgent
from app.dependencies import get_ai_provider, get_auth_context, get_db, require_roles
from app.models import HumanDecision, Investigation, Report
from app.services.audit_service import write_audit_for_context

router = APIRouter(prefix="/api/reports", tags=["reports"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_reports(
    db: Session = Depends(get_db),
    context=Depends(get_auth_context),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    investigation_id: int | None = Query(default=None),
):
    query = db.query(Report).filter(Report.tenant_id == context.tenant_id)
    if investigation_id is not None:
        query = query.filter(Report.investigation_id == investigation_id)
    reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": report.id,
            "investigation_id": report.investigation_id,
            "title": report.title,
            "created_at": report.created_at.isoformat(),
        }
        for report in reports
    ]


@router.post("/{investigation_id}/generate")
def generate_report(
    investigation_id: int,
    db: Session = Depends(get_db),
    ai_provider=Depends(get_ai_provider),
    context=Depends(require_roles("analyst", "admin", "owner")),
):
    investigation = db.get(Investigation, investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    if investigation.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    decisions = (
        db.query(HumanDecision)
        .filter(HumanDecision.investigation_id == investigation_id, HumanDecision.tenant_id == context.tenant_id)
        .all()
    )
    decision_lines = [f"{d.decided_at.isoformat()} {d.decision}: {d.note or ''}" for d in decisions]
    report_agent = ReportAgent(ai_provider)
    markdown = report_agent.run(
        investigation,
        investigation.root_cause_summary or "",
        investigation.blast_radius_summary or "",
        decision_lines,
    )
    report = Report(
        tenant_id=context.tenant_id,
        investigation_id=investigation.id,
        title=f"Postmortem #{investigation.id}",
        markdown_body=markdown,
    )
    db.add(report)
    write_audit_for_context(
        db,
        context,
        action="report.generate",
        resource_type="report",
        metadata={"investigation_id": investigation_id},
    )
    db.commit()
    db.refresh(report)
    return {"id": report.id, "investigation_id": report.investigation_id, "title": report.title}


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), context=Depends(get_auth_context)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {
        "id": report.id,
        "investigation_id": report.investigation_id,
        "title": report.title,
        "markdown_body": report.markdown_body,
        "created_at": report.created_at.isoformat(),
    }


@router.get("/{report_id}/markdown")
def get_report_markdown(report_id: int, db: Session = Depends(get_db), context=Depends(get_auth_context)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.tenant_id != context.tenant_id:
        raise HTTPException(status_code=404, detail="Report not found.")
    return PlainTextResponse(report.markdown_body)


@page_router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, db: Session = Depends(get_db), context=Depends(get_auth_context)):
    reports = db.query(Report).filter(Report.tenant_id == context.tenant_id).order_by(Report.created_at.desc()).all()
    return templates.TemplateResponse("reports.html", {"request": request, "title": "Reports", "reports": reports})
