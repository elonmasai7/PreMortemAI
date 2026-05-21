from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.config import Settings
from app.dependencies import get_auth_context, get_settings_dep
from app.services.metrics_service import SLO_TRACKER

try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
except ImportError:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"

    def generate_latest():
        return b"# prometheus-client not installed\n"

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@router.get("/slo")
def slo_summary(settings: Settings = Depends(get_settings_dep), context=Depends(get_auth_context)):
    summary = SLO_TRACKER.summary(
        success_target_percent=settings.slo_success_target_percent,
        latency_target_ms=settings.slo_latency_target_ms,
    )
    return summary
