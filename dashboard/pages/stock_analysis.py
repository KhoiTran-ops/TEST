from datetime import date, timedelta
import streamlit as st
from dashboard.components.charts import stock_chart
from dashboard.components.metrics import compact_number

def render(repository):
    st.header("Stock Analysis"); exchange = st.selectbox("Exchange", ["ALL","HOSE","HNX","UPCOM"]); tickers = repository.tickers(exchange)
    if not tickers: st.info("Run the pipeline to load market data."); return
    ticker = st.selectbox("Ticker", tickers); end = st.date_input("End date", date.today()); start = st.date_input("Start date", end-timedelta(days=365))
    data = repository.history(ticker, start, end)
    if data.empty: st.warning("No data in this date range."); return
    last = data.iloc[-1]; previous = data.iloc[-2].close if len(data)>1 else last.close; change = (last.close/previous-1)*100 if previous else 0
    values = [("Latest Price",f"{last.close:,.2f}"),("Daily Change",f"{change:+.2f}%"),("Volume",compact_number(last.volume)),("Period High",f"{data.high.max():,.2f}"),("Period Low",f"{data.low.min():,.2f}"),("RSI",f"{last.rsi14:.1f}"),("MACD",f"{last.macd:.2f}"),("Signal",last.signal)]
    for col, item in zip(st.columns(8), values): col.metric(*item)
    st.plotly_chart(stock_chart(data), use_container_width=True)
