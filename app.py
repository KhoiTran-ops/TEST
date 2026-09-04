"""Streamlit entry point; reads only precomputed database data."""
import streamlit as st
from config import get_settings
from database import StockRepository, create_database
from dashboard.pages import overview, pipeline_monitor, stock_analysis, stock_screener
from dashboard.styles import CSS

st.set_page_config(page_title="Vietnam Stock Analytics",page_icon="📈",layout="wide"); st.markdown(CSS,unsafe_allow_html=True)
repository=StockRepository(create_database()); st.sidebar.title("Vietnam Stock Analytics")
page=st.sidebar.radio("Page",["Market Overview","Stock Analysis","Stock Screener","Pipeline Monitor"])
st.sidebar.caption(f"Data cache TTL: {get_settings().refresh_seconds}s")
{"Market Overview":overview.render,"Stock Analysis":stock_analysis.render,"Stock Screener":stock_screener.render,"Pipeline Monitor":pipeline_monitor.render}[page](repository)
