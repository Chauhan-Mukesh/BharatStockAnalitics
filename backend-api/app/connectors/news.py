"""News aggregator connector.

Fetches financial news from publicly accessible RSS/API sources.
Uses Google News RSS and Economic Times RSS as open/free sources.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BharatStocks/1.0)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}


def _rss_items(xml_text: str) -> list[dict[str, Any]]:
    """Parse RSS/Atom feed and return list of item dicts."""
    items = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        channel = root.find("channel")
        entries = channel.findall("item") if channel is not None else root.findall("atom:entry", ns)
        for entry in entries:
            title_el = entry.find("title")
            link_el = entry.find("link")
            pubdate_el = entry.find("pubDate") or entry.find("atom:published", ns)
            desc_el = entry.find("description") or entry.find("atom:summary", ns)

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else (link_el.get("href") if link_el is not None else "")
            pub = pubdate_el.text if pubdate_el is not None else None
            desc = desc_el.text if desc_el is not None else None

            items.append({"headline": title, "url": link, "published_at": pub, "summary": desc})
    except Exception as exc:
        logger.warning("RSS parse error: %s", exc)
    return items


class NewsConnector:
    """Fetches news from open RSS sources."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers=_HEADERS,
            follow_redirects=True,
            timeout=10.0,
        )

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    async def _fetch_rss(self, url: str) -> str:
        resp = await self._client.get(url)
        resp.raise_for_status()
        return resp.text

    async def get_news_for_stock(self, symbol: str, company_name: str) -> list[dict[str, Any]]:
        """Fetch news articles for a stock from Google News RSS."""
        query = f"{company_name} stock NSE BSE"
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        items = []
        try:
            xml_text = await self._fetch_rss(rss_url)
            raw_items = _rss_items(xml_text)
            for item in raw_items[:20]:
                items.append({
                    **item,
                    "source": "Google News",
                    "sentiment": None,  # enriched later by AI layer
                })
        except Exception as exc:
            logger.error("NewsConnector failed symbol=%s err=%s", symbol, exc)
        return items

    async def get_market_news(self) -> list[dict[str, Any]]:
        """Fetch general Indian market news."""
        urls = [
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "https://www.business-standard.com/rss/markets-106.rss",
        ]
        items = []
        for url in urls:
            try:
                xml_text = await self._fetch_rss(url)
                raw = _rss_items(xml_text)
                for item in raw[:10]:
                    items.append({**item, "source": url.split("/")[2]})
            except Exception as exc:
                logger.warning("Market news fetch failed url=%s err=%s", url, exc)
        return items

    async def close(self) -> None:
        await self._client.aclose()
