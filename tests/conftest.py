from dataclasses import replace
import pandas as pd
import pytest
from config import get_settings
from database import StockRepository, create_database

@pytest.fixture
def repository(tmp_path): return StockRepository(create_database(f"sqlite:///{tmp_path/'test.db'}"))

@pytest.fixture
def settings(tmp_path):
    for name in ["raw","extracted","processed"]: (tmp_path/"data"/name).mkdir(parents=True)
    (tmp_path/"logs").mkdir()
    return replace(get_settings(),database_url=f"sqlite:///{tmp_path/'db.sqlite'}",root=tmp_path,source_url="dummy")

@pytest.fixture
def prices():
    days=pd.date_range("2026-01-01",periods=70)
    return pd.DataFrame({"ticker":"FPT","exchange":"HOSE","trading_date":days,"open":range(100,170),"high":range(102,172),"low":range(99,169),"close":range(101,171),"volume":[1000+i*20 for i in range(70)]})
