"""Celery tasks: news refresh."""
from __future__ import annotations

import json
import logging
import os
import xml.etree.ElementTree as ET

import httpx
import redis
from celery_app import celery_app

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis = redis.from_url(REDIS_URL, decode_responses=True)

TRACKED_STOCKS = [
    ("NSE", "BEL", "Bharat Electronics"),
    ("NSE", "INFY", "Infosys"),
    ("NSE", "RELIANCE", "Reliance Industries"),
    ("NSE", "TCS", "Tata Consultancy Services"),
    ("NSE", "HDFCBANK", "HDFC Bank"),
    ("NSE", "TATAMOTORS", "Tata Motors"),
]


def _fetch_google_news_rss(query: str) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; BharatStocks/1.0)"})
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            channel = root.find("channel")
            items = []
            for item in (channel.findall("item") if channel is not None else [])[:15]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub = item.findtext("pubDate", "")
                items.append({"headline": title, "url": link, "published_at": pub, "source": "Google News"})
            return items
    except Exception as exc:
        logger.warning("RSS fetch failed query=%s: %s", query, exc)
        return []


@celery_app.task(name="tasks.news.refresh_all_news", bind=True)
def refresh_all_news(self):
    """Refresh news for all tracked stocks and cache in Redis."""
    logger.info("Starting news refresh for %d stocks", len(TRACKED_STOCKS))
    results = {"refreshed": 0, "failed": 0}

    for exchange, symbol, company_name in TRACKED_STOCKS:
        try:
            query = f"{company_name} stock NSE BSE"
            news_items = _fetch_google_news_rss(query)
            cache_key = f"news:{exchange}:{symbol}"
            # Assign temp IDs and neutral sentiment (AI enrichment done on read)
            for i, item in enumerate(news_items):
                item["id"] = i + 1
                item.setdefault("sentiment", "neutral")
            _redis.setex(cache_key, 900, json.dumps(news_items, default=str))  # 15 min TTL
            results["refreshed"] += 1
            logger.info("Refreshed %d news items for %s/%s", len(news_items), exchange, symbol)
        except Exception as exc:
            logger.error("News refresh failed %s/%s: %s", exchange, symbol, exc)
            results["failed"] += 1

    logger.info("News refresh complete: %s", results)
    return results


@celery_app.task(name="tasks.news.refresh_for_symbol")
def refresh_news_for_symbol(exchange: str, symbol: str, company_name: str):
    """On-demand news refresh for a single stock."""
    try:
        query = f"{company_name} stock"
        items = _fetch_google_news_rss(query)
        cache_key = f"news:{exchange.upper()}:{symbol.upper()}"
        for i, item in enumerate(items):
            item["id"] = i + 1
            item.setdefault("sentiment", "neutral")
        _redis.setex(cache_key, 900, json.dumps(items, default=str))
        return {"status": "ok", "count": len(items)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
