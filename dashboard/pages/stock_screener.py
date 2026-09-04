import streamlit as st
from analysis.strategy import explain_signal

def render(repository):
    st.header("Stock Screener"); c1,c2=st.columns(2); exchange=c1.selectbox("Exchange",["ALL","HOSE","HNX","UPCOM"],key="sx"); signal=c2.selectbox("Signal",["ALL","BUY","SELL","HOLD"])
    rsi=st.slider("RSI range",0,100,(0,100)); price=st.slider("Price range",0,500_000,(0,500_000)); ratio=st.number_input("Minimum volume ratio",0.0,10.0,0.0,.1)
    frame=repository.screener(exchange,signal,rsi,price,ratio)
    if frame.empty: st.info("No matching stocks."); return
    sort=st.selectbox("Sort by",["rsi14","volume","close","signal"]); frame=frame.sort_values(sort,ascending=False); st.dataframe(frame,use_container_width=True,hide_index=True)
    ticker=st.selectbox("Explain signal",frame.ticker.tolist()); row=frame[frame.ticker==ticker].iloc[0].to_dict(); st.subheader(f"{ticker} — {row['signal']}")
    for reason in explain_signal(row): st.write(f"✓ {reason}")
    st.success(f"Result: {row['signal']}")
