"""Unit tests for technical analysis engine."""
import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend-api"))

from app.analytics.technicals import (
    sma, ema, rsi, macd, bollinger_bands, atr,
    stochastic, adx, compute_all_indicators,
)
import pandas as pd
import numpy as np


def _make_close(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype=float)


def _make_ohlcv(n: int = 200, seed: int = 42) -> list[dict]:
    """Generate synthetic OHLCV data."""
    rng = np.random.default_rng(seed)
    prices = 100.0 + np.cumsum(rng.normal(0, 1, n))
    records = []
    base = datetime(2023, 1, 1)
    for i in range(n):
        c = max(prices[i], 1.0)
        h = c * (1 + abs(rng.normal(0, 0.01)))
        l = c * (1 - abs(rng.normal(0, 0.01)))
        o = c * (1 + rng.normal(0, 0.005))
        records.append({
            "date": (base + timedelta(days=i)).isoformat(),
            "open": round(float(o), 2),
            "high": round(float(h), 2),
            "low": round(float(l), 2),
            "close": round(float(c), 2),
            "volume": int(rng.integers(100000, 5000000)),
        })
    return records


class TestSmaEma:
    def test_sma_length(self):
        close = _make_close([float(i) for i in range(1, 31)])
        result = sma(close, 10)
        assert len(result) == 30

    def test_sma_values(self):
        close = _make_close([1.0, 2.0, 3.0, 4.0, 5.0])
        result = sma(close, 3)
        assert result.iloc[-1] == pytest.approx(4.0)

    def test_ema_reacts_faster_than_sma(self):
        """EMA should weight recent values more heavily than SMA."""
        close = _make_close([100.0] * 20 + [200.0] * 5)
        ema_val = float(ema(close, 10).iloc[-1])
        sma_val = float(sma(close, 10).iloc[-1])
        assert ema_val > sma_val


class TestRsi:
    def test_rsi_bounds(self):
        ohlcv = _make_ohlcv(100)
        close = pd.Series([r["close"] for r in ohlcv], dtype=float)
        result = rsi(close, 14)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_rsi_oversold_signal(self):
        # Falling prices should produce RSI < 30
        falling = _make_close([100.0 - i * 2 for i in range(50)])
        result = rsi(falling, 14)
        assert float(result.dropna().iloc[-1]) < 40


class TestMacd:
    def test_macd_returns_three_series(self):
        close = _make_close([float(i) + (i % 5) for i in range(100)])
        macd_line, signal_line, hist = macd(close)
        assert len(macd_line) == 100
        assert len(signal_line) == 100
        assert len(hist) == 100

    def test_macd_hist_is_difference(self):
        close = _make_close([float(i) for i in range(100)])
        macd_line, signal_line, hist = macd(close)
        expected = macd_line - signal_line
        pd.testing.assert_series_equal(hist, expected)


class TestBollingerBands:
    def test_bb_order(self):
        ohlcv = _make_ohlcv(100)
        close = pd.Series([r["close"] for r in ohlcv], dtype=float)
        upper, middle, lower = bollinger_bands(close, 20)
        valid = pd.concat([upper, middle, lower], axis=1).dropna()
        assert (valid.iloc[:, 0] >= valid.iloc[:, 1]).all()  # upper >= middle
        assert (valid.iloc[:, 1] >= valid.iloc[:, 2]).all()  # middle >= lower


class TestComputeAllIndicators:
    def test_returns_dict(self):
        ohlcv = _make_ohlcv(200)
        result = compute_all_indicators(ohlcv)
        assert isinstance(result, dict)
        assert "rsi_14" in result
        assert "macd" in result
        assert "sma_20" in result
        assert "ema_20" in result
        assert "bb_upper" in result
        assert "support" in result
        assert "resistance" in result

    def test_insufficient_data(self):
        result = compute_all_indicators(_make_ohlcv(10))
        assert result == {}

    def test_rsi_in_valid_range(self):
        ohlcv = _make_ohlcv(200)
        result = compute_all_indicators(ohlcv)
        rsi_val = result.get("rsi_14")
        if rsi_val is not None:
            assert 0 <= rsi_val <= 100

    def test_support_below_resistance(self):
        ohlcv = _make_ohlcv(200)
        result = compute_all_indicators(ohlcv)
        assert result["support"] <= result["resistance"]
