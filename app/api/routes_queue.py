from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import get_settings_dep, require_roles
from app.services.queue_service import get_queue

router = APIRouter(prefix="/api/queue", tags=["queue"])


@router.get("/metrics")
def queue_metrics(settings: Settings = Depends(get_settings_dep), context=Depends(require_roles("admin", "owner"))):
    queue = get_queue(settings)
    if not queue:
        return {"queue_enabled": False, "detail": "Queue is disabled or Redis is not configured."}
    try:
        jobs = queue.jobs
        oldest_seconds = 0
        if jobs:
            oldest = min(job.enqueued_at.timestamp() for job in jobs if job.enqueued_at)
            import time

            oldest_seconds = max(0, int(time.time() - oldest))
        return {
            "queue_enabled": True,
            "queue_name": settings.queue_name,
            "depth": len(jobs),
            "failed_count": queue.failed_job_registry.count,
            "oldest_job_age_seconds": oldest_seconds,
        }
    except Exception as exc:
        return {"queue_enabled": True, "error": str(exc)}
