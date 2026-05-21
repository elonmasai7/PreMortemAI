from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db_session
from app.services.ai_client import build_ai_provider
from app.services.mcp_client import MCPClient
from app.services.splunk_client import SplunkClient


def get_settings_dep() -> Settings:
    return get_settings()


def get_db(dep: Session = Depends(get_db_session)) -> Session:
    return dep


def get_splunk_client(settings: Settings = Depends(get_settings_dep)) -> SplunkClient:
    return SplunkClient(settings)


def get_mcp_client(settings: Settings = Depends(get_settings_dep)) -> MCPClient:
    return MCPClient(settings)


def get_ai_provider(settings: Settings = Depends(get_settings_dep)):
    return build_ai_provider(settings)
