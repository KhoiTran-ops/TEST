"""Plotly financial charts."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def stock_chart(data):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, row_heights=[.5,.2,.15,.15], vertical_spacing=.03)
    fig.add_trace(go.Candlestick(x=data.trading_date, open=data.open, high=data.high, low=data.low, close=data.close, name="Price"), row=1, col=1)
    for col in ["sma20", "sma50", "ema20", "bollinger_upper", "bollinger_lower"]:
        fig.add_trace(go.Scatter(x=data.trading_date, y=data[col], name=col.upper()), row=1, col=1)
    fig.add_trace(go.Bar(x=data.trading_date, y=data.volume, name="Volume"), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.trading_date, y=data.volume_ma20, name="Volume MA20"), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.trading_date, y=data.rsi14, name="RSI14"), row=3, col=1)
    fig.add_trace(go.Scatter(x=data.trading_date, y=data.macd, name="MACD"), row=4, col=1)
    fig.add_trace(go.Scatter(x=data.trading_date, y=data.macd_signal, name="MACD Signal"), row=4, col=1)
    fig.update_layout(height=850, xaxis_rangeslider_visible=False); return fig
