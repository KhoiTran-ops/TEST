"""Bounded, transactional database operations used by pipeline and dashboard."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any

import pandas as pd
from sqlalchemy import Engine, func, select, text
from sqlalchemy.orm import Session

from .models import PipelineRun, StockPrice, StockSignal, TechnicalIndicator


class StockRepository:
    def __init__(self, engine: Engine): self.engine = engine

    def upsert_prices(self, frame: pd.DataFrame) -> dict[str, int]:
        inserted = updated = skipped = 0
        with Session(self.engine) as session:
            for row in frame.to_dict("records"):
                key = {"ticker": row["ticker"], "trading_date": pd.Timestamp(row["trading_date"]).date()}
                obj = session.scalar(select(StockPrice).filter_by(**key))
                values = {k: row[k] for k in ("exchange", "open", "high", "low", "close", "volume")}
                if obj is None: session.add(StockPrice(**key, **values)); inserted += 1
                elif any(getattr(obj, k) != v for k, v in values.items()):
                    for k, v in values.items(): setattr(obj, k, v)
                    updated += 1
                else: skipped += 1
            session.commit()
        return {"inserted": inserted, "updated": updated, "skipped": skipped}

    def all_prices(self) -> pd.DataFrame:
        return pd.read_sql(select(StockPrice), self.engine)

    def replace_analytics(self, frame: pd.DataFrame) -> None:
        indicator_cols = ["sma20", "sma50", "ema20", "rsi14", "macd", "macd_signal", "bollinger_upper", "bollinger_lower", "atr14", "volume_ma20"]
        with Session(self.engine) as session:
            for row in frame.to_dict("records"):
                day = pd.Timestamp(row["trading_date"]).date(); key = {"ticker": row["ticker"], "trading_date": day}
                ind = session.scalar(select(TechnicalIndicator).filter_by(**key)) or TechnicalIndicator(**key)
                for col in indicator_cols: setattr(ind, col, None if pd.isna(row[col]) else float(row[col]))
                session.add(ind)
                signal_key = {"ticker": row["ticker"], "signal_date": day}
                sig = session.scalar(select(StockSignal).filter_by(**signal_key)) or StockSignal(**signal_key)
                for col in ["exchange", "close", "signal", "sma20", "sma50", "rsi14", "macd", "macd_signal", "volume", "volume_ma20"]:
                    value = row[col]; setattr(sig, col, None if pd.isna(value) else value)
                session.add(sig)
            session.commit()

    def history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        query = text("""SELECT p.*, i.sma20,i.sma50,i.ema20,i.rsi14,i.macd,i.macd_signal,i.bollinger_upper,i.bollinger_lower,i.atr14,i.volume_ma20,s.signal
            FROM stock_prices p LEFT JOIN technical_indicators i ON p.ticker=i.ticker AND p.trading_date=i.trading_date
            LEFT JOIN stock_signals s ON p.ticker=s.ticker AND p.trading_date=s.signal_date
            WHERE p.ticker=:ticker AND p.trading_date BETWEEN :start AND :end ORDER BY p.trading_date""")
        return pd.read_sql(query, self.engine, params={"ticker": ticker, "start": start, "end": end})

    def latest_trading_date(self):
        with Session(self.engine) as session: return session.scalar(select(func.max(StockPrice.trading_date)))

    def tickers(self, exchange: str = "ALL") -> list[str]:
        with Session(self.engine) as session:
            q = select(StockPrice.ticker).distinct().order_by(StockPrice.ticker)
            if exchange != "ALL": q = q.where(StockPrice.exchange == exchange)
            return list(session.scalars(q))

    def screener(self, exchange="ALL", signal="ALL", rsi=(0, 100), price=(0, 10**9), min_volume_ratio=0.0, limit=500) -> pd.DataFrame:
        latest = self.latest_trading_date()
        if latest is None: return pd.DataFrame()
        clauses = ["s.signal_date=:day", "s.close BETWEEN :pmin AND :pmax", "COALESCE(s.rsi14,0) BETWEEN :rmin AND :rmax", "s.volume >= :ratio * COALESCE(s.volume_ma20,1)"]
        params: dict[str, Any] = {"day": latest, "pmin": price[0], "pmax": price[1], "rmin": rsi[0], "rmax": rsi[1], "ratio": min_volume_ratio, "limit": limit}
        if exchange != "ALL": clauses.append("s.exchange=:exchange"); params["exchange"] = exchange
        if signal != "ALL": clauses.append("s.signal=:signal"); params["signal"] = signal
        query = text(f"SELECT s.* FROM stock_signals s WHERE {' AND '.join(clauses)} ORDER BY s.signal,ticker LIMIT :limit")
        return pd.read_sql(query, self.engine, params=params)

    def overview(self) -> dict:
        day = self.latest_trading_date()
        with self.engine.connect() as con:
            exchanges = dict(con.execute(text("SELECT exchange,COUNT(DISTINCT ticker) FROM stock_prices WHERE trading_date=:d GROUP BY exchange"), {"d": day}).all()) if day else {}
            signals = dict(con.execute(text("SELECT signal,COUNT(*) FROM stock_signals WHERE signal_date=:d GROUP BY signal"), {"d": day}).all()) if day else {}
        return {"latest_trading_date": day, "total_stocks": sum(exchanges.values()), "exchanges": exchanges, "signals": signals}

    def start_run(self, run_id: str) -> None:
        with Session(self.engine) as s: s.add(PipelineRun(run_id=run_id, started_at=datetime.utcnow(), status="RUNNING")); s.commit()

    def finish_run(self, run_id: str, **values) -> None:
        with Session(self.engine) as s:
            run = s.scalar(select(PipelineRun).where(PipelineRun.run_id == run_id))
            for key, value in values.items(): setattr(run, key, value)
            run.finished_at = datetime.utcnow(); run.duration_seconds = (run.finished_at-run.started_at).total_seconds(); s.commit()

    def running(self) -> bool:
        with Session(self.engine) as s: return bool(s.scalar(select(func.count()).select_from(PipelineRun).where(PipelineRun.status == "RUNNING")))

    def latest_run(self, successful=False):
        with Session(self.engine) as s:
            q = select(PipelineRun).order_by(PipelineRun.started_at.desc())
            if successful: q = q.where(PipelineRun.status.in_(["SUCCESS", "NO_NEW_DATA"]))
            return s.scalar(q.limit(1))

    def health_counts(self) -> tuple[int, int]:
        with Session(self.engine) as s: return s.scalar(select(func.count(func.distinct(StockPrice.ticker)))), s.scalar(select(func.count()).select_from(StockPrice))
