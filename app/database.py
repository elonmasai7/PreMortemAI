from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from app import models  # noqa: F401
    from app.services.auth_service import bootstrap_auth_entities

    Base.metadata.create_all(bind=engine)

    if settings.database_url.startswith("sqlite"):
        with engine.connect() as connection:
            columns = [row[1] for row in connection.execute(text("PRAGMA table_info(investigations)"))]
        if columns and "tenant_id" not in columns:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        bootstrap_auth_entities(db, settings)
    finally:
        db.close()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
