"""Typed application configuration loaded from YAML and environment variables."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str
    source_url: str | None
    timezone: str
    schedule_hour: int
    schedule_minute: int
    weekdays: tuple[str, ...]
    refresh_seconds: int
    volume_multiplier: float
    invalid_record_threshold: float
    root: Path = ROOT


@lru_cache
def get_settings() -> Settings:
    path = Path(os.getenv("CONFIG_FILE", ROOT / "config/config.yaml"))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    automation, dashboard, analysis, pipeline = (
        raw["automation"], raw["dashboard"], raw["analysis"], raw["pipeline"]
    )
    return Settings(
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'data/stocks.db'}"),
        source_url=os.getenv("CAFEF_DATASET_URL") or raw.get("source", {}).get("dataset_url"),
        timezone=automation["timezone"], schedule_hour=automation["schedule_hour"],
        schedule_minute=automation["schedule_minute"], weekdays=tuple(automation["weekdays"]),
        refresh_seconds=dashboard["refresh_interval_seconds"],
        volume_multiplier=analysis["volume_multiplier"],
        invalid_record_threshold=pipeline["invalid_record_threshold"],
    )
