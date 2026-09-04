"""Deterministic signal generation and explanations."""
import pandas as pd


def generate_signals(frame: pd.DataFrame, volume_multiplier: float = 1.2) -> pd.DataFrame:
    result = frame.copy()
    buy = (result.close > result.sma50) & result.rsi14.between(40, 70) & (result.macd > result.macd_signal) & (result.volume > volume_multiplier * result.volume_ma20)
    sell = (result.close < result.sma50) & (result.macd < result.macd_signal) & (result.rsi14 > 70)
    result["signal"] = "HOLD"; result.loc[buy, "signal"] = "BUY"; result.loc[sell, "signal"] = "SELL"
    return result


def explain_signal(row: dict, volume_multiplier: float = 1.2) -> list[str]:
    return [f"Close {'>' if row['close'] > row['sma50'] else '≤'} SMA50", f"RSI14 = {row['rsi14']:.1f}",
            f"MACD {'>' if row['macd'] > row['macd_signal'] else '≤'} Signal", f"Volume {'>' if row['volume'] > volume_multiplier * row['volume_ma20'] else '≤'} {volume_multiplier} × Volume MA20"]
