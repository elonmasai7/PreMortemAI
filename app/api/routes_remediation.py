from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import HumanDecision, Investigation, RemediationRecommendation
from app.schemas.remediation import DecisionRequest
from app.services.remediation_service import apply_decision, build_decision_audit

router = APIRouter(prefix="/api/remediation", tags=["remediation"])
page_router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def _get_recommendation(db: Session, investigation_id: int) -> RemediationRecommendation:
    recommendation = (
        db.query(RemediationRecommendation)
        .filter(RemediationRecommendation.investigation_id == investigation_id)
        .order_by(RemediationRecommendation.created_at.desc())
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="No remediation recommendation found for investigation.")
    return recommendation


@router.get("/{investigation_id}")
def get_remediation(investigation_id: int, db: Session = Depends(get_db)):
    recommendation = _get_recommendation(db, investigation_id)
    decisions = (
        db.query(HumanDecision)
        .filter(HumanDecision.recommendation_id == recommendation.id)
        .order_by(HumanDecision.decided_at.desc())
        .all()
    )
    return {
        "recommendation": {
            "id": recommendation.id,
            "action_type": recommendation.action_type,
            "action_summary": recommendation.action_summary,
            "risk_of_action": recommendation.risk_of_action,
            "risk_of_inaction": recommendation.risk_of_inaction,
            "confidence": recommendation.confidence,
            "status": recommendation.status,
        },
        "decisions": [
            {"decision": d.decision, "note": d.note, "decided_at": d.decided_at.isoformat()} for d in decisions
        ],
    }


@router.post("/{investigation_id}/approve")
def approve(investigation_id: int, payload: DecisionRequest, db: Session = Depends(get_db)):
    recommendation = _get_recommendation(db, investigation_id)
    apply_decision(recommendation, "approve")
    db.add(build_decision_audit(recommendation.id, investigation_id, "approve", payload.note))
    db.add(recommendation)
    db.commit()
    return {"status": "approved", "recommendation_id": recommendation.id}


@router.post("/{investigation_id}/reject")
def reject(investigation_id: int, payload: DecisionRequest, db: Session = Depends(get_db)):
    recommendation = _get_recommendation(db, investigation_id)
    apply_decision(recommendation, "reject")
    db.add(build_decision_audit(recommendation.id, investigation_id, "reject", payload.note))
    db.add(recommendation)
    db.commit()
    return {"status": "rejected", "recommendation_id": recommendation.id}


@page_router.get("/remediation/{investigation_id}", response_class=HTMLResponse)
def remediation_page(request: Request, investigation_id: int, db: Session = Depends(get_db)):
    investigation = db.get(Investigation, investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    recommendation = _get_recommendation(db, investigation_id)
    decisions = (
        db.query(HumanDecision)
        .filter(HumanDecision.recommendation_id == recommendation.id)
        .order_by(HumanDecision.decided_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "remediation.html",
        {
            "request": request,
            "title": "Remediation",
            "investigation": investigation,
            "recommendation": recommendation,
            "decisions": decisions,
        },
    )


@page_router.post("/remediation/{investigation_id}/approve")
def remediation_approve_page(investigation_id: int, note: str | None = Form(default=None), db: Session = Depends(get_db)):
    approve(investigation_id, DecisionRequest(note=note), db)
    return RedirectResponse(url=f"/remediation/{investigation_id}", status_code=303)


@page_router.post("/remediation/{investigation_id}/reject")
def remediation_reject_page(investigation_id: int, note: str | None = Form(default=None), db: Session = Depends(get_db)):
    reject(investigation_id, DecisionRequest(note=note), db)
    return RedirectResponse(url=f"/remediation/{investigation_id}", status_code=303)
