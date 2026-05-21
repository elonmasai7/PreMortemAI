from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.agents.report_agent import ReportAgent
from app.dependencies import get_ai_provider, get_db
from app.models import HumanDecision, Investigation, Report

router = APIRouter(prefix="/api/reports", tags=["reports"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
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
def generate_report(investigation_id: int, db: Session = Depends(get_db), ai_provider=Depends(get_ai_provider)):
    investigation = db.get(Investigation, investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    decisions = db.query(HumanDecision).filter(HumanDecision.investigation_id == investigation_id).all()
    decision_lines = [f"{d.decided_at.isoformat()} {d.decision}: {d.note or ''}" for d in decisions]
    report_agent = ReportAgent(ai_provider)
    markdown = report_agent.run(
        investigation,
        investigation.root_cause_summary or "",
        investigation.blast_radius_summary or "",
        decision_lines,
    )
    report = Report(investigation_id=investigation.id, title=f"Postmortem #{investigation.id}", markdown_body=markdown)
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "investigation_id": report.investigation_id, "title": report.title}


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {
        "id": report.id,
        "investigation_id": report.investigation_id,
        "title": report.title,
        "markdown_body": report.markdown_body,
        "created_at": report.created_at.isoformat(),
    }


@router.get("/{report_id}/markdown")
def get_report_markdown(report_id: int, db: Session = Depends(get_db)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return PlainTextResponse(report.markdown_body)


@page_router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return templates.TemplateResponse("reports.html", {"request": request, "title": "Reports", "reports": reports})
