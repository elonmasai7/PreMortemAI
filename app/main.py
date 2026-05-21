import logging
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_ai import router as ai_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_health import page_router as health_page_router
from app.api.routes_health import router as health_router
from app.api.routes_investigations import page_router as investigations_page_router
from app.api.routes_investigations import router as investigations_router
from app.api.routes_remediation import page_router as remediation_page_router
from app.api.routes_remediation import router as remediation_router
from app.api.routes_reports import page_router as reports_page_router
from app.api.routes_reports import router as reports_router
from app.api.routes_splunk import page_router as splunk_page_router
from app.api.routes_splunk import router as splunk_router
from app.config import get_settings
from app.database import init_db
from app.exceptions import (
    AIProviderError,
    ConfigurationError,
    InvestigationNotFoundError,
    SplunkAuthenticationError,
    SplunkConnectionError,
    SplunkSearchError,
    ValidationError,
)
from app.logging_config import setup_logging

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

_rate_limit_lock = Lock()
_rate_limit_windows: dict[tuple[str, str], deque[float]] = defaultdict(deque)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("Application started")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def _is_rate_limited(ip: str, bucket: str, limit: int, window_seconds: int = 60) -> bool:
    now = time.monotonic()
    key = (ip, bucket)
    with _rate_limit_lock:
        hits = _rate_limit_windows[key]
        while hits and (now - hits[0]) > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            return True
        hits.append(now)
    return False


def _rate_limit_bucket(path: str) -> tuple[str, int] | None:
    if path == "/api/splunk/search":
        return ("splunk-search", 30)
    if path.startswith("/api/investigations/") and (path.endswith("/run") or path.endswith("/refresh")):
        return ("investigation-run", 30)
    if path.startswith("/api/ai/"):
        return ("ai-api", 60)
    return None


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_bytes:
        return JSONResponse(status_code=413, content={"detail": "Request body too large."})
    return await call_next(request)


@app.middleware("http")
async def write_api_rate_limit(request: Request, call_next):
    bucket_config = _rate_limit_bucket(request.url.path)
    if bucket_config:
        bucket, limit = bucket_config
        client_ip = request.client.host if request.client else "unknown"
        if _is_rate_limited(client_ip, bucket, limit):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded for this endpoint.",
                    "next_step": "Retry after one minute or reduce request frequency.",
                },
                headers={"Retry-After": "60"},
            )
    return await call_next(request)


@app.exception_handler(ConfigurationError)
@app.exception_handler(SplunkConnectionError)
@app.exception_handler(SplunkAuthenticationError)
@app.exception_handler(SplunkSearchError)
@app.exception_handler(AIProviderError)
@app.exception_handler(InvestigationNotFoundError)
@app.exception_handler(ValidationError)
async def controlled_exception_handler(request: Request, exc: Exception):
    logger.warning("Handled application error: %s [request_id=%s]", exc, getattr(request.state, "request_id", "n/a"))
    return JSONResponse(status_code=400, content={"detail": str(exc), "next_step": "Check setup page and route input values."})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Request validation error: %s [request_id=%s]", exc, getattr(request.state, "request_id", "n/a"))
    return JSONResponse(status_code=422, content={"detail": "Invalid request payload.", "errors": exc.errors()})


app.include_router(dashboard_router)
app.include_router(health_page_router)
app.include_router(splunk_page_router)
app.include_router(investigations_page_router)
app.include_router(remediation_page_router)
app.include_router(reports_page_router)

app.include_router(health_router)
app.include_router(splunk_router)
app.include_router(investigations_router)
app.include_router(ai_router)
app.include_router(remediation_router)
app.include_router(reports_router)
