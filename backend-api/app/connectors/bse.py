"""BSE data connector.

Uses BSE's public API endpoints for quote, company data, and filings.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

_BSE_API = "https://api.bseindia.com/BseIndiaAPI/api"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.bseindia.com",
    "Referer": "https://www.bseindia.com/",
}


class BseConnector:
    """Async HTTP client for BSE public data endpoints."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers=_HEADERS,
            follow_redirects=True,
            timeout=15.0,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        resp = await self._client.get(f"{_BSE_API}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_quote(self, scrip_code: str) -> dict[str, Any]:
        """Fetch live quote for a BSE scrip code."""
        try:
            data = await self._get(f"/getScripHeaderData/w", params={"Debtflag": "", "scripcode": scrip_code, "seriesid": ""})
            return {
                "symbol": data.get("Scripcode", scrip_code),
                "company_name": data.get("Longname", ""),
                "exchange": "BSE",
                "price": float(data.get("Currentvalue", 0) or 0),
                "open": float(data.get("Open", 0) or 0),
                "high": float(data.get("High52", 0) or 0),
                "low": float(data.get("Low52", 0) or 0),
                "prev_close": float(data.get("Prevclose", 0) or 0),
                "change": float(data.get("Chg", 0) or 0),
                "change_pct": float(data.get("Chgp", 0) or 0),
                "volume": int(data.get("Ttlqty", 0) or 0),
                "week52_high": float(data.get("High52", 0) or 0),
                "week52_low": float(data.get("Low52", 0) or 0),
                "market_cap": float(data.get("Mktcap", 0) or 0),
            }
        except Exception as exc:
            logger.error("BSE get_quote failed scrip=%s err=%s", scrip_code, exc)
            raise

    async def search(self, query: str) -> list[dict[str, Any]]:
        """Search BSE stocks by name."""
        try:
            data = await self._get("/getScripSearch/w", params={"strScrip": query, "strType": "Q"})
            results = []
            for item in (data if isinstance(data, list) else data.get("Table", [])):
                results.append({
                    "symbol": str(item.get("SCRIP_CD", "")),
                    "company_name": item.get("Issuer_Name", ""),
                    "exchange": "BSE",
                    "isin": item.get("ISIN_NUMBER", None),
                })
            return results
        except Exception as exc:
            logger.error("BSE search failed query=%s err=%s", query, exc)
            return []

    async def get_company_overview(self, scrip_code: str) -> dict[str, Any]:
        """Fetch company details."""
        try:
            data = await self._get("/CompanyHeader/w", params={"scripcode": scrip_code, "flag": "C", "mktcap": "", "pagetype": ""})
            return {
                "company_name": data.get("CMP_NAME", ""),
                "sector": data.get("SECTOR", None),
                "industry": data.get("INDUSTRY", None),
                "isin": data.get("ISIN_CODE", None),
                "website": data.get("WEBSITE", None),
                "description": data.get("ABOUT_US", None),
            }
        except Exception as exc:
            logger.error("BSE overview failed scrip=%s err=%s", scrip_code, exc)
            return {}

    async def get_filings(self, scrip_code: str, category: str = "-1", subcategory: str = "-1") -> list[dict]:
        """Fetch corporate filings list (links only — no document content)."""
        try:
            data = await self._get(
                "/AnnualReports/w",
                params={"scripcode": scrip_code, "Category": category, "Subcategory": subcategory},
            )
            results = []
            for item in (data if isinstance(data, list) else data.get("Table", [])):
                results.append({
                    "title": item.get("NEWSSUB", item.get("HEADLINE", "Untitled")),
                    "source_url": item.get("ATTACHMENTNAME", item.get("URL", "")),
                    "filing_date": item.get("NEWS_DT", item.get("DT_TM", None)),
                    "filing_type": "annual_report",
                    "source": "BSE",
                })
            return results
        except Exception as exc:
            logger.error("BSE filings failed scrip=%s err=%s", scrip_code, exc)
            return []

    async def close(self) -> None:
        await self._client.aclose()
