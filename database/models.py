"""Relational data model for prices, derived analytics and pipeline audit."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class StockPrice(Base):
    __tablename__ = "stock_prices"
    __table_args__ = (UniqueConstraint("ticker", "trading_date"), Index("ix_price_exchange", "exchange"))
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    exchange: Mapped[str] = mapped_column(String(10), index=True)
    trading_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float); high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float); close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    __table_args__ = (UniqueConstraint("ticker", "trading_date"),)
    id: Mapped[int] = mapped_column(primary_key=True); ticker: Mapped[str] = mapped_column(String(20), index=True)
    trading_date: Mapped[date] = mapped_column(Date, index=True)
    sma20: Mapped[Optional[float]] = mapped_column(Float); sma50: Mapped[Optional[float]] = mapped_column(Float)
    ema20: Mapped[Optional[float]] = mapped_column(Float); rsi14: Mapped[Optional[float]] = mapped_column(Float)
    macd: Mapped[Optional[float]] = mapped_column(Float); macd_signal: Mapped[Optional[float]] = mapped_column(Float)
    bollinger_upper: Mapped[Optional[float]] = mapped_column(Float); bollinger_lower: Mapped[Optional[float]] = mapped_column(Float)
    atr14: Mapped[Optional[float]] = mapped_column(Float); volume_ma20: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockSignal(Base):
    __tablename__ = "stock_signals"
    __table_args__ = (UniqueConstraint("ticker", "signal_date"), Index("ix_signal_date_signal", "signal_date", "signal"))
    id: Mapped[int] = mapped_column(primary_key=True); ticker: Mapped[str] = mapped_column(String(20), index=True)
    exchange: Mapped[str] = mapped_column(String(10)); signal_date: Mapped[date] = mapped_column(Date, index=True)
    close: Mapped[float] = mapped_column(Float); signal: Mapped[str] = mapped_column(String(4), index=True)
    sma20: Mapped[Optional[float]] = mapped_column(Float); sma50: Mapped[Optional[float]] = mapped_column(Float)
    rsi14: Mapped[Optional[float]] = mapped_column(Float); macd: Mapped[Optional[float]] = mapped_column(Float)
    macd_signal: Mapped[Optional[float]] = mapped_column(Float); volume: Mapped[float] = mapped_column(Float)
    volume_ma20: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id: Mapped[int] = mapped_column(primary_key=True); run_id: Mapped[str] = mapped_column(String(36), unique=True)
    started_at: Mapped[datetime] = mapped_column(DateTime); finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), index=True); dataset_date: Mapped[Optional[date]] = mapped_column(Date)
    records_downloaded: Mapped[int] = mapped_column(Integer, default=0); records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0); records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0); errors: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text); duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
