"""SQLAlchemy engine/session construction."""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import get_settings
from .models import Base


def create_database(url: str | None = None) -> Engine:
    """Create an engine and all tables; SQLite is the safe local default."""
    database_url = url or get_settings().database_url
    kwargs = {"connect_args": {"check_same_thread": False}} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, future=True, pool_pre_ping=True, **kwargs)
    Base.metadata.create_all(engine)
    return engine
