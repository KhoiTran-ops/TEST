"""End-to-end, auditable and idempotent pipeline orchestration."""
from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import uuid

import pandas as pd

from analysis.indicators import calculate_indicators
from analysis.strategy import generate_signals
from config import Settings, get_settings
from database import StockRepository, create_database
from .source import CafeFSource


def configure_logging(settings: Settings) -> logging.Logger:
    log = logging.getLogger("pipeline")
    log_path = settings.root / "logs/pipeline.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    has_current_file = False
    for handler in tuple(log.handlers):
        if isinstance(handler, RotatingFileHandler):
            if Path(handler.baseFilename).resolve() == log_path.resolve():
                has_current_file = True
            else:
                log.removeHandler(handler)
                handler.close()
    if not has_current_file:
        handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        log.addHandler(handler)
    if not any(type(handler) is logging.StreamHandler for handler in log.handlers):
        log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    return log


class PipelineOrchestrator:
    def __init__(self, repository=None, source=None, settings=None):
        self.settings = settings or get_settings(); self.repository = repository or StockRepository(create_database(self.settings.database_url))
        self.source = source or CafeFSource(self.settings.source_url, self.settings.root/"data/raw", self.settings.root/"data/extracted"); self.log = configure_logging(self.settings)

    @staticmethod
    def clean(files: list) -> tuple[pd.DataFrame, int]:
        data = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)
        data.columns = [c.strip().lower().replace("<", "").replace(">", "") for c in data.columns]
        aliases = {"date": "trading_date", "symbol": "ticker", "market": "exchange", "openprice": "open", "highprice": "high", "lowprice": "low", "closeprice": "close", "totalvolume": "volume"}
        data = data.rename(columns={k: v for k, v in aliases.items() if k in data})
        required = ["ticker", "exchange", "trading_date", "open", "high", "low", "close", "volume"]
        missing = set(required)-set(data.columns)
        if missing: raise ValueError(f"Invalid dataset; missing columns: {sorted(missing)}")
        before = len(data); data["trading_date"] = pd.to_datetime(data.trading_date, errors="coerce")
        for col in ["open", "high", "low", "close", "volume"]: data[col] = pd.to_numeric(data[col], errors="coerce")
        data["ticker"] = data.ticker.astype(str).str.upper().str.strip(); data["exchange"] = data.exchange.astype(str).str.upper().str.strip()
        valid = data.dropna(subset=required); valid = valid[(valid.high >= valid.low) & (valid.volume >= 0) & valid.exchange.isin(["HOSE", "HNX", "UPCOM"])]
        return valid.drop_duplicates(["ticker", "trading_date"], keep="last"), before-len(valid)

    def run(self) -> dict:
        if self.repository.running(): return {"status": "ALREADY_RUNNING", "message": "Pipeline already running. Please wait."}
        run_id = str(uuid.uuid4()); self.repository.start_run(run_id); self.log.info("Pipeline started")
        stats = {"status": "FAILED", "records_downloaded": 0, "records_processed": 0, "records_inserted": 0, "records_updated": 0, "records_skipped": 0, "errors": 0}
        try:
            self.log.info("Detecting latest CafeF dataset")
            if not self.source.available(): raise RuntimeError("SOURCE_UNAVAILABLE")
            path = self.source.download(); self.log.info("Download completed")
            files = self.source.extract(path); self.log.info("Extraction completed")
            frame, invalid = self.clean(files); stats.update(records_downloaded=len(frame)+invalid, records_processed=len(frame), errors=invalid)
            if len(frame) and invalid/(len(frame)+invalid) > self.settings.invalid_record_threshold: raise ValueError("Invalid record threshold exceeded")
            dataset_date = frame.trading_date.max().date() if len(frame) else None
            counts = self.repository.upsert_prices(frame); stats.update({f"records_{k}": v for k, v in counts.items()})
            if not counts["inserted"] and not counts["updated"]:
                stats["status"] = "NO_NEW_DATA"; self.log.info("No new data")
            else:
                enriched = generate_signals(calculate_indicators(self.repository.all_prices()), self.settings.volume_multiplier)
                self.repository.replace_analytics(enriched); stats["status"] = "SUCCESS"; self.log.info("Indicators calculated; signals generated")
            self.repository.finish_run(run_id, dataset_date=dataset_date, **stats); self.log.info("Pipeline completed: %s", stats["status"]); return {"run_id": run_id, **stats}
        except Exception as exc:
            stats["errors"] += 1; self.log.exception("Pipeline failed: %s", exc)
            self.repository.finish_run(run_id, error_message=str(exc), **stats); return {"run_id": run_id, "error_message": str(exc), **stats}
