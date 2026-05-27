"""Celery tasks: quote refresh."""
from __future__ import annotations

import asyncio
import logging
import os

import httpx
import redis
from celery_app import celery_app

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_BASE = os.getenv("API_BASE_URL", "http://backend-api:8000")

_redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def _get_tracked_symbols() -> list[tuple[str, str]]:
    """Return list of (exchange, symbol) from watchlist:* keys in Redis."""
    symbols = set()
    for key in _redis_client.scan_iter("watchlist_items:*"):
        parts = key.split(":")
        if len(parts) == 3:
            symbols.add((parts[1], parts[2]))
    # Also add a default set for POC
    symbols.update([
        ("NSE", "BEL"), ("NSE", "INFY"), ("NSE", "RELIANCE"),
        ("NSE", "TCS"), ("NSE", "HDFCBANK"), ("NSE", "TATAMOTORS"),
    ])
    return list(symbols)


@celery_app.task(name="tasks.quotes.refresh_all_quotes", bind=True, max_retries=3)
def refresh_all_quotes(self):
    """Refresh quotes for all tracked symbols and update Redis cache."""
    symbols = _get_tracked_symbols()
    logger.info("Refreshing quotes for %d symbols", len(symbols))

    results = {"success": 0, "failed": 0}
    for exchange, symbol in symbols:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{API_BASE}/api/stocks/{exchange}/{symbol}/quote")
                if resp.status_code == 200:
                    results["success"] += 1
                else:
                    logger.warning("Quote refresh failed %s/%s: HTTP %d", exchange, symbol, resp.status_code)
                    results["failed"] += 1
        except Exception as exc:
            logger.error("Quote refresh error %s/%s: %s", exchange, symbol, exc)
            results["failed"] += 1

    logger.info("Quote refresh complete: %s", results)
    return results


@celery_app.task(name="tasks.quotes.refresh_single_quote")
def refresh_single_quote(exchange: str, symbol: str):
    """Refresh quote for a single symbol."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{API_BASE}/api/stocks/{exchange}/{symbol}/quote")
            return {"status": resp.status_code, "symbol": symbol}
    except Exception as exc:
        logger.error("Single quote refresh failed %s/%s: %s", exchange, symbol, exc)
        return {"status": "error", "symbol": symbol, "error": str(exc)}
