import logging

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

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_bytes:
        return JSONResponse(status_code=413, content={"detail": "Request body too large."})
    return await call_next(request)


@app.on_event("startup")
def startup() -> None:
    init_db()
    logger.info("Application started")


@app.exception_handler(ConfigurationError)
@app.exception_handler(SplunkConnectionError)
@app.exception_handler(SplunkAuthenticationError)
@app.exception_handler(SplunkSearchError)
@app.exception_handler(AIProviderError)
@app.exception_handler(InvestigationNotFoundError)
@app.exception_handler(ValidationError)
async def controlled_exception_handler(request: Request, exc: Exception):
    logger.warning("Handled application error: %s", exc)
    return JSONResponse(status_code=400, content={"detail": str(exc), "next_step": "Check setup page and route input values."})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Request validation error: %s", exc)
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
