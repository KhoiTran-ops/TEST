"""Vectorized technical indicator calculation."""
import numpy as np
import pandas as pd


def calculate_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate indicators independently for each ticker in date order."""
    def one(group: pd.DataFrame) -> pd.DataFrame:
        g = group.sort_values("trading_date").copy(); close = g["close"]
        g["sma20"] = close.rolling(20).mean(); g["sma50"] = close.rolling(50).mean()
        g["ema20"] = close.ewm(span=20, adjust=False).mean()
        delta = close.diff(); gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(); loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        g["rsi14"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
        g["macd"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        g["macd_signal"] = g["macd"].ewm(span=9, adjust=False).mean()
        std = close.rolling(20).std(); g["bollinger_upper"] = g["sma20"] + 2 * std; g["bollinger_lower"] = g["sma20"] - 2 * std
        previous = close.shift(); true_range = pd.concat([(g.high-g.low), (g.high-previous).abs(), (g.low-previous).abs()], axis=1).max(axis=1)
        g["atr14"] = true_range.rolling(14).mean(); g["volume_ma20"] = g.volume.rolling(20).mean()
        return g
    return frame.groupby("ticker", group_keys=False).apply(one, include_groups=True).reset_index(drop=True)
