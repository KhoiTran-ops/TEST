"""Operational health summary used by CLI and presentation layer."""
from sqlalchemy import text

from config import get_settings
from database import StockRepository, create_database
from .source import CafeFSource


def check_health(repository=None, source=None) -> dict:
    settings = get_settings(); repo = repository or StockRepository(create_database())
    db = "OK"
    try:
        with repo.engine.connect() as con: con.execute(text("SELECT 1"))
        stocks, records = repo.health_counts()
    except Exception:
        db, stocks, records = "ERROR", 0, 0
    src = source or CafeFSource(settings.source_url, settings.root/"data/raw", settings.root/"data/extracted")
    last, success = repo.latest_run(), repo.latest_run(successful=True)
    return {"database": db, "source": "OK" if src.available() else "UNAVAILABLE", "latest_dataset": settings.source_url,
            "latest_trading_date": repo.latest_trading_date(), "number_of_stocks": stocks, "number_of_records": records,
            "last_pipeline_execution": last.started_at if last else None, "last_pipeline_status": last.status if last else "NEVER",
            "last_successful_execution": success.started_at if success else None}
