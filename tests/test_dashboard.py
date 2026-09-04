def test_screener_reads_latest_only(repository,prices):
    from analysis.indicators import calculate_indicators
    from analysis.strategy import generate_signals
    repository.upsert_prices(prices); repository.replace_analytics(generate_signals(calculate_indicators(repository.all_prices())))
    result=repository.screener()
    assert len(result)==1 and str(result.iloc[0].signal_date).startswith("2026-03-11")
