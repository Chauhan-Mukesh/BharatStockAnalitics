"""Technical analysis indicators.

Implements RSI, MACD, SMA, EMA, Bollinger Bands, ATR, Supertrend,
Stochastic Oscillator, ADX from raw OHLCV data using only numpy/pandas.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(window=period).mean()


def ema(close: pd.Series, period: int) -> pd.Series:
    return close.ewm(span=period, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns (macd_line, signal_line, histogram)."""
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(close: pd.Series, period: int = 20, std_dev: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns (upper, middle, lower)."""
    middle = sma(close, period)
    std = close.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, adjust=True, min_periods=period).mean()


def supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
               period: int = 10, multiplier: float = 3.0) -> tuple[pd.Series, pd.Series]:
    """Returns (supertrend_line, direction) where direction: 1=up, -1=down."""
    atr_series = atr(high, low, close, period)
    hl2 = (high + low) / 2
    upper_band = hl2 + multiplier * atr_series
    lower_band = hl2 - multiplier * atr_series

    supertrend_vals = pd.Series(index=close.index, dtype=float)
    direction = pd.Series(index=close.index, dtype=int)

    for i in range(period, len(close)):
        if i == period:
            supertrend_vals.iloc[i] = lower_band.iloc[i]
            direction.iloc[i] = 1
            continue
        prev_st = supertrend_vals.iloc[i - 1]
        prev_dir = direction.iloc[i - 1]

        curr_upper = upper_band.iloc[i]
        curr_lower = lower_band.iloc[i]
        prev_close = close.iloc[i - 1]

        if prev_dir == 1:
            curr_lower = max(curr_lower, lower_band.iloc[i - 1]) if not pd.isna(lower_band.iloc[i - 1]) else curr_lower
            supertrend_vals.iloc[i] = curr_lower
            direction.iloc[i] = 1 if close.iloc[i] > curr_lower else -1
        else:
            curr_upper = min(curr_upper, upper_band.iloc[i - 1]) if not pd.isna(upper_band.iloc[i - 1]) else curr_upper
            supertrend_vals.iloc[i] = curr_upper
            direction.iloc[i] = -1 if close.iloc[i] < curr_upper else 1

    return supertrend_vals, direction


def stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
               k_period: int = 14, d_period: int = 3) -> tuple[pd.Series, pd.Series]:
    """Returns (%K, %D)."""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan) * 100
    d = k.rolling(window=d_period).mean()
    return k, d


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average Directional Index."""
    tr = atr(high, low, close, period)

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    atr_smooth = tr.ewm(com=period - 1, adjust=True, min_periods=period).mean()
    plus_di = 100 * plus_dm.ewm(com=period - 1, adjust=True, min_periods=period).mean() / atr_smooth
    minus_di = 100 * minus_dm.ewm(com=period - 1, adjust=True, min_periods=period).mean() / atr_smooth
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(com=period - 1, adjust=True, min_periods=period).mean()


def compute_all_indicators(ohlcv: list[dict]) -> dict:
    """Compute all indicators from OHLCV list.

    Each item must have: date, open, high, low, close, volume.
    Returns dict with latest indicator values.
    """
    if len(ohlcv) < 30:
        return {}

    df = pd.DataFrame(ohlcv).sort_values("date")
    df = df.dropna(subset=["close", "high", "low", "open"])

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    result: dict = {}

    # RSI
    rsi_series = rsi(close, 14)
    result["rsi_14"] = round(float(rsi_series.iloc[-1]), 2) if not pd.isna(rsi_series.iloc[-1]) else None

    # MACD
    macd_line, signal_line, histogram = macd(close)
    result["macd"] = round(float(macd_line.iloc[-1]), 4) if not pd.isna(macd_line.iloc[-1]) else None
    result["macd_signal"] = round(float(signal_line.iloc[-1]), 4) if not pd.isna(signal_line.iloc[-1]) else None
    result["macd_hist"] = round(float(histogram.iloc[-1]), 4) if not pd.isna(histogram.iloc[-1]) else None

    # SMAs
    for p in (20, 50, 200):
        s = sma(close, p)
        result[f"sma_{p}"] = round(float(s.iloc[-1]), 2) if len(s.dropna()) > 0 and not pd.isna(s.iloc[-1]) else None

    # EMAs
    for p in (20, 50):
        e = ema(close, p)
        result[f"ema_{p}"] = round(float(e.iloc[-1]), 2) if not pd.isna(e.iloc[-1]) else None

    # Bollinger Bands
    bb_upper, bb_mid, bb_lower = bollinger_bands(close)
    result["bb_upper"] = round(float(bb_upper.iloc[-1]), 2) if not pd.isna(bb_upper.iloc[-1]) else None
    result["bb_middle"] = round(float(bb_mid.iloc[-1]), 2) if not pd.isna(bb_mid.iloc[-1]) else None
    result["bb_lower"] = round(float(bb_lower.iloc[-1]), 2) if not pd.isna(bb_lower.iloc[-1]) else None

    # ATR
    atr_series = atr(high, low, close, 14)
    result["atr_14"] = round(float(atr_series.iloc[-1]), 2) if not pd.isna(atr_series.iloc[-1]) else None

    # ADX
    adx_series = adx(high, low, close, 14)
    result["adx_14"] = round(float(adx_series.iloc[-1]), 2) if not pd.isna(adx_series.iloc[-1]) else None

    # Stochastic
    stoch_k, stoch_d = stochastic(high, low, close)
    result["stoch_k"] = round(float(stoch_k.iloc[-1]), 2) if not pd.isna(stoch_k.iloc[-1]) else None
    result["stoch_d"] = round(float(stoch_d.iloc[-1]), 2) if not pd.isna(stoch_d.iloc[-1]) else None

    # Supertrend
    if len(df) >= 20:
        st_vals, st_dir = supertrend(high, low, close)
        last_st = st_vals.dropna()
        last_dir = st_dir.dropna()
        if len(last_st) > 0:
            result["supertrend"] = round(float(last_st.iloc[-1]), 2)
            result["supertrend_direction"] = "up" if int(last_dir.iloc[-1]) == 1 else "down"

    # Support / Resistance (simple 20-period high/low)
    recent = df.tail(20)
    result["support"] = round(float(recent["low"].min()), 2)
    result["resistance"] = round(float(recent["high"].max()), 2)

    return result
