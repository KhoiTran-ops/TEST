import pandas as pd
import plotly.express as px
import streamlit as st

def render(repository):
    st.header("Market Overview"); info = repository.overview(); exchanges, signals = info["exchanges"], info["signals"]
    cols = st.columns(4); cols[0].metric("Last Trading Date", str(info["latest_trading_date"] or "N/A")); cols[1].metric("Total Stocks", info["total_stocks"]); cols[2].metric("BUY Signals", signals.get("BUY",0)); cols[3].metric("SELL Signals", signals.get("SELL",0))
    cols = st.columns(4)
    for col, name in zip(cols, ["HOSE","HNX","UPCOM","HOLD"]): col.metric(f"{name} Stocks" if name != "HOLD" else "HOLD Signals", exchanges.get(name,0) if name != "HOLD" else signals.get(name,0))
    if signals: st.plotly_chart(px.pie(pd.DataFrame({"signal": signals.keys(), "count": signals.values()}), names="signal", values="count", title="Signal distribution"), use_container_width=True)
    latest = repository.screener(limit=20)
    if not latest.empty: st.subheader("Latest market activity"); st.dataframe(latest, use_container_width=True, hide_index=True)
