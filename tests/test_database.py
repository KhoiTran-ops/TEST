def test_incremental_upsert_is_idempotent(repository, prices):
    first=repository.upsert_prices(prices); second=repository.upsert_prices(prices)
    assert first["inserted"]==70
    assert second=={"inserted":0,"updated":0,"skipped":70}
    assert repository.health_counts()==(1,70)

def test_latest_trading_date_query(repository, prices):
    repository.upsert_prices(prices)
    assert str(repository.latest_trading_date())=="2026-03-11"
