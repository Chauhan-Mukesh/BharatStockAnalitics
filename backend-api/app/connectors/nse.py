"""NSE data connector.

Fetches quote and metadata from NSE public endpoints.
Uses cache-first strategy and exponential back-off retries.

NOTE: NSE has aggressive bot protections. This connector uses realistic
browser-like headers and adds random delays. For production use, consider
an official data vendor or a licensed data API.
"""
from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

_NSE_BASE = "https://www.nseindia.com"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}


class NseConnector:
    """Async HTTP client for NSE public data endpoints."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._session_cookies: dict = {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=_NSE_BASE,
                headers=_HEADERS,
                follow_redirects=True,
                timeout=15.0,
            )
            # Warm-up: visit the homepage to get session cookies
            try:
                resp = await self._client.get("/", timeout=10.0)
                self._session_cookies = dict(resp.cookies)
                await asyncio.sleep(random.uniform(0.5, 1.5))
            except Exception as exc:
                logger.warning("NSE warm-up failed: %s", exc)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _get(self, path: str) -> dict | list:
        client = await self._get_client()
        await asyncio.sleep(random.uniform(0.2, 0.8))
        resp = await client.get(path, cookies=self._session_cookies)
        resp.raise_for_status()
        return resp.json()

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Fetch live quote for a symbol from NSE."""
        try:
            data = await self._get(f"/api/quote-equity?symbol={symbol.upper()}")
            price_info = data.get("priceInfo", {})
            industry_info = data.get("industryInfo", {})
            metadata = data.get("metadata", {})
            live_volume = (
                price_info.get("totalTradedVolume")
                or metadata.get("totalTradedVolume")
                or data.get("securityWiseDP", {}).get("quantityTraded")
                or data.get("preOpenMarket", {}).get("totalTradedVolume", 0)
            )
            return {
                "symbol": symbol.upper(),
                "company_name": metadata.get("companyName", ""),
                "exchange": "NSE",
                "price": price_info.get("lastPrice", 0.0),
                "open": price_info.get("open", 0.0),
                "high": price_info.get("intraDayHighLow", {}).get("max", 0.0),
                "low": price_info.get("intraDayHighLow", {}).get("min", 0.0),
                "prev_close": price_info.get("previousClose", 0.0),
                "change": price_info.get("change", 0.0),
                "change_pct": price_info.get("pChange", 0.0),
                "volume": live_volume,
                "week52_high": price_info.get("weekHighLow", {}).get("max", None),
                "week52_low": price_info.get("weekHighLow", {}).get("min", None),
                "vwap": price_info.get("vwap", None),
                "sector": industry_info.get("sector", None),
                "industry": industry_info.get("industry", None),
            }
        except Exception as exc:
            logger.error("NSE get_quote failed symbol=%s err=%s", symbol, exc)
            raise

    async def search(self, query: str) -> list[dict[str, Any]]:
        """Search stocks by name or symbol."""
        try:
            data = await self._get(f"/api/search/autocomplete?q={query}")
            results = []
            for item in data.get("symbols", []):
                results.append({
                    "symbol": item.get("symbol", ""),
                    "company_name": item.get("symbol_info", item.get("symbol", "")),
                    "exchange": "NSE",
                    "isin": item.get("isin", None),
                })
            return results
        except Exception as exc:
            logger.error("NSE search failed query=%s err=%s", query, exc)
            return []

    async def get_historical(self, symbol: str, series: str = "EQ",
                             from_date: str = "01-01-2020",
                             to_date: str = "31-12-2024") -> list[dict]:
        """Fetch historical OHLCV data."""
        try:
            path = (
                f"/api/historical/cm/equity"
                f"?symbol={symbol.upper()}&series=[%22{series}%22]"
                f"&from={from_date}&to={to_date}&csv=false"
            )
            data = await self._get(path)
            records = []
            for row in data.get("data", []):
                records.append({
                    "date": row.get("CH_TIMESTAMP"),
                    "open": row.get("CH_OPENING_PRICE"),
                    "high": row.get("CH_TRADE_HIGH_PRICE"),
                    "low": row.get("CH_TRADE_LOW_PRICE"),
                    "close": row.get("CH_CLOSING_PRICE"),
                    "volume": row.get("CH_TOT_TRADED_QTY"),
                })
            return records
        except Exception as exc:
            logger.error("NSE historical failed symbol=%s err=%s", symbol, exc)
            return []

    async def get_shareholding(self, symbol: str) -> list[dict]:
        """Fetch shareholding pattern."""
        try:
            data = await self._get(
                f"/api/corporate-share-holding-aggregate?index=equities&symbol={symbol.upper()}"
            )
            results = []
            for item in data.get("data", []):
                results.append({
                    "period": item.get("date", ""),
                    "promoter_pct": item.get("promoterAndPromoterGroupTotal", None),
                    "fii_pct": item.get("foreignPortfolioInvestors", None),
                    "dii_pct": item.get("dii", None),
                    "public_pct": item.get("publicTotal", None),
                })
            return results
        except Exception as exc:
            logger.error("NSE shareholding failed symbol=%s err=%s", symbol, exc)
            return []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
