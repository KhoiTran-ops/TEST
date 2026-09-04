# Automated Stock Analytics — Phase 4

An end-to-end Vietnamese stock analytics pipeline for HOSE, HNX and UPCOM. The automation layer downloads a configured CafeF CSV/ZIP export, validates and incrementally upserts prices, then precomputes indicators and algorithmic signals. Streamlit only performs bounded database queries—it never contacts CafeF or recomputes market history.

## Installation

Python 3.11+ is required.

```bash
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Environment variables can be loaded by your shell/service. Set `CAFEF_DATASET_URL` to a direct CSV/ZIP URL or a local export path. Accepted columns are `ticker, exchange, trading_date, open, high, low, close, volume`; common CafeF aliases are normalized. SQLite (`data/stocks.db`) is the default. To retain an existing PostgreSQL deployment, set `DATABASE_URL=postgresql+psycopg://user:password@host/database` and install its driver. Never commit `.env`.

## Running

```bash
python main.py --mode pipeline
python main.py --mode health-check
python main.py --mode scheduler
streamlit run app.py
pytest -q
```

The first pipeline run inserts all unique ticker/date pairs. Re-running the same file reports `NO_NEW_DATA`, inserts zero rows, and counts unchanged rows as skipped. A corrected OHLCV row is updated in place. Unique constraints provide an additional database-level duplicate guarantee. Invalid rows are logged and tolerated up to the configurable threshold; fatal source, validation, database, or analytics errors are persisted as `FAILED`.

The scheduler uses `Asia/Ho_Chi_Minh`, weekdays at 18:00 by default, with coalescing and a single APScheduler instance. A database `RUNNING` guard also protects manual/dashboard execution. Change schedule, thresholds and analysis settings in `config/config.yaml`.

## Dashboard

Run `streamlit run app.py` and choose Market Overview, Stock Analysis, Stock Screener, or Pipeline Monitor. The monitor offers a confirmation-gated manual run. Dashboard data is already persisted by the pipeline; history queries require ticker and date bounds, while overview/screener queries use only the latest trading date.

## Windows Task Scheduler

1. Choose **Create Task**, select **Run whether user is logged on or not**, and enable **Restart on failure** (for example every 5 minutes, three attempts).
2. Add a weekly trigger for Monday–Friday at 18:00.
3. Set **Program/script** to the absolute interpreter, e.g. `C:\Projects\stocks\.venv\Scripts\python.exe`.
4. Set **Arguments** to `main.py --mode pipeline`.
5. Set **Start in** to the absolute project directory, e.g. `C:\Projects\stocks`.

No terminal needs to remain open. Store environment variables in the task account/system environment. The database guard makes an accidental overlapping trigger safe.

## Linux cron alternative

```cron
0 18 * * 1-5 cd /opt/automated-stock-analytics && .venv/bin/python main.py --mode pipeline >> logs/cron.log 2>&1
```

Cron's timezone should be configured as `Asia/Ho_Chi_Minh`; the application scheduler already handles this itself. A weekday trigger does not imply a trading day: unchanged CafeF input becomes successful `NO_NEW_DATA` rather than a failure.

## Architecture and operations

`pipeline/` owns source access, orchestration, logging, health checks and scheduling. `database/` owns SQLAlchemy models and bounded queries. `analysis/` owns indicators and deterministic BUY/SELL/HOLD rules. `dashboard/` is presentation-only. Logs rotate at `logs/pipeline.log`; pipeline audit rows capture timings, counts and errors.

To test incremental behavior manually, point `CAFEF_DATASET_URL` to a sample CSV, run the pipeline twice, verify the second run has zero inserts, then append one later trading-date row and run again. The dashboard will immediately query that new latest date.
