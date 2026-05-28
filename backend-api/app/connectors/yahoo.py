"""Yahoo Finance connector (fallback / supplement).

Used when NSE/BSE connectors fail or return incomplete data.
Yahoo Finance provides Indian stock data with suffix:
  NSE stocks → SYMBOL.NS
  BSE stocks → SYMBOL.BO
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

_YF_BASE = "https://query1.finance.yahoo.com"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BharatStocks/1.0)",
    "Accept": "application/json",
}

_EXCHANGE_SUFFIX = {"NSE": ".NS", "BSE": ".BO"}


def _yf_symbol(symbol: str, exchange: str) -> str:
    suffix = _EXCHANGE_SUFFIX.get(exchange.upper(), ".NS")
    return f"{symbol.upper()}{suffix}"


class YahooFinanceConnector:
    """Async Yahoo Finance v8/v10 client."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=_YF_BASE,
            headers=_HEADERS,
            follow_redirects=True,
            timeout=15.0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _get(self, path: str, params: dict | None = None) -> dict:
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_quote(self, symbol: str, exchange: str) -> dict[str, Any]:
        """Fetch live quote via Yahoo Finance v8 quoteSummary."""
        yf_sym = _yf_symbol(symbol, exchange)
        try:
            data = await self._get(
                f"/v8/finance/quote",
                params={"symbols": yf_sym, "fields": "regularMarketPrice,regularMarketOpen,regularMarketDayHigh,regularMarketDayLow,regularMarketPreviousClose,regularMarketVolume,marketCap,fiftyTwoWeekHigh,fiftyTwoWeekLow,regularMarketChange,regularMarketChangePercent,shortName"},
            )
            result = data.get("quoteResponse", {}).get("result", [])
            if not result:
                return {}
            r = result[0]
            return {
                "symbol": symbol.upper(),
                "company_name": r.get("shortName", symbol),
                "exchange": exchange.upper(),
                "price": r.get("regularMarketPrice", 0.0),
                "open": r.get("regularMarketOpen", 0.0),
                "high": r.get("regularMarketDayHigh", 0.0),
                "low": r.get("regularMarketDayLow", 0.0),
                "prev_close": r.get("regularMarketPreviousClose", 0.0),
                "change": r.get("regularMarketChange", 0.0),
                "change_pct": r.get("regularMarketChangePercent", 0.0),
                "volume": r.get("regularMarketVolume", 0),
                "market_cap": r.get("marketCap", None),
                "week52_high": r.get("fiftyTwoWeekHigh", None),
                "week52_low": r.get("fiftyTwoWeekLow", None),
            }
        except Exception as exc:
            logger.error("Yahoo get_quote failed symbol=%s err=%s", yf_sym, exc)
            raise

    async def get_financial_summary(self, symbol: str, exchange: str) -> dict[str, Any]:
        """Fetch key stats and financial data."""
        yf_sym = _yf_symbol(symbol, exchange)
        try:
            data = await self._get(
                f"/v10/finance/quoteSummary/{yf_sym}",
                params={"modules": "defaultKeyStatistics,financialData,summaryDetail,assetProfile"},
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            stats = result.get("defaultKeyStatistics", {})
            fin = result.get("financialData", {})
            summary = result.get("summaryDetail", {})
            profile = result.get("assetProfile", {})

            def _val(obj: dict, key: str) -> float | None:
                v = obj.get(key)
                if isinstance(v, dict):
                    return v.get("raw")
                return v

            return {
                "pe": _val(summary, "trailingPE"),
                "forward_pe": _val(summary, "forwardPE"),
                "pb": _val(stats, "priceToBook"),
                "peg": _val(stats, "pegRatio"),
                "ev_ebitda": _val(stats, "enterpriseToEbitda"),
                "ev_sales": _val(stats, "enterpriseToRevenue"),
                "price_sales": _val(summary, "priceToSalesTrailing12Months"),
                "dividend_yield": _val(summary, "dividendYield"),
                "market_cap": _val(summary, "marketCap"),
                "enterprise_value": _val(stats, "enterpriseValue"),
                "roe": _val(fin, "returnOnEquity"),
                "roa": _val(fin, "returnOnAssets"),
                "debt_to_equity": _val(fin, "debtToEquity"),
                "current_ratio": _val(fin, "currentRatio"),
                "gross_margin": _val(fin, "grossMargins"),
                "operating_margin": _val(fin, "operatingMargins"),
                "net_margin": _val(fin, "profitMargins"),
                "description": profile.get("longBusinessSummary", ""),
                "sector": profile.get("sector", ""),
                "industry": profile.get("industry", ""),
                "website": profile.get("website", ""),
                "headquarters": f"{profile.get('city', '')}, {profile.get('country', '')}".strip(", "),
                "employee_count": profile.get("fullTimeEmployees", None),
            }
        except Exception as exc:
            logger.error("Yahoo financial_summary failed symbol=%s err=%s", yf_sym, exc)
            return {}

    async def get_historical(self, symbol: str, exchange: str,
                             period: str = "5y", interval: str = "1d") -> list[dict]:
        """Fetch historical OHLCV data."""
        yf_sym = _yf_symbol(symbol, exchange)
        try:
            data = await self._get(
                f"/v8/finance/chart/{yf_sym}",
                params={"range": period, "interval": interval},
            )
            chart = data.get("chart", {}).get("result", [{}])[0]
            timestamps = chart.get("timestamp", [])
            indicators = chart.get("indicators", {}).get("quote", [{}])[0]
            records = []
            for i, ts in enumerate(timestamps):
                records.append({
                    "date": datetime.fromtimestamp(ts).isoformat(),
                    "open": (indicators.get("open") or [None])[i],
                    "high": (indicators.get("high") or [None])[i],
                    "low": (indicators.get("low") or [None])[i],
                    "close": (indicators.get("close") or [None])[i],
                    "volume": (indicators.get("volume") or [0])[i] or 0,
                })
            return [r for r in records if r["close"] is not None]
        except Exception as exc:
            logger.error("Yahoo historical failed symbol=%s err=%s", yf_sym, exc)
            return []

    async def close(self) -> None:
        await self._client.aclose()
