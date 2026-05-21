from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_ai_provider, get_auth_context

router = APIRouter(prefix="/api/ai", tags=["ai"])


class EvidencePayload(BaseModel):
    evidence: list[dict] = Field(default_factory=list)


class PostmortemPayload(BaseModel):
    investigation: dict


@router.post("/summarize")
def summarize(payload: EvidencePayload, ai_provider=Depends(get_ai_provider), context=Depends(get_auth_context)):
    return ai_provider.summarize_evidence(payload.evidence)


@router.post("/root-cause")
def root_cause(payload: EvidencePayload, ai_provider=Depends(get_ai_provider), context=Depends(get_auth_context)):
    return ai_provider.rank_root_causes(payload.evidence)


@router.post("/remediation-plan")
def remediation_plan(payload: EvidencePayload, ai_provider=Depends(get_ai_provider), context=Depends(get_auth_context)):
    return ai_provider.create_remediation_plan(payload.evidence)


@router.post("/postmortem")
def postmortem(payload: PostmortemPayload, ai_provider=Depends(get_ai_provider), context=Depends(get_auth_context)):
    return {"markdown": ai_provider.generate_postmortem(payload.investigation)}
