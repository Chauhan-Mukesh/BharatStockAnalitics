"""Celery tasks: financial metric recalculation."""
from __future__ import annotations

import json
import logging
import os

import httpx
import redis
from celery_app import celery_app

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_BASE = os.getenv("API_BASE_URL", "http://backend-api:8000")
_redis = redis.from_url(REDIS_URL, decode_responses=True)

TRACKED_SYMBOLS = [
    ("NSE", "BEL"), ("NSE", "INFY"), ("NSE", "RELIANCE"),
    ("NSE", "TCS"), ("NSE", "HDFCBANK"), ("NSE", "TATAMOTORS"),
    ("NSE", "HAL"), ("NSE", "WIPRO"), ("NSE", "HCLTECH"),
]


@celery_app.task(name="tasks.metrics.recalculate_all_metrics", bind=True)
def recalculate_all_metrics(self):
    """Invalidate financial/technicals cache so next request fetches fresh data."""
    logger.info("Recalculating metrics for %d symbols", len(TRACKED_SYMBOLS))
    invalidated = 0

    for exchange, symbol in TRACKED_SYMBOLS:
        keys_to_delete = [
            f"financials:{exchange}:{symbol}",
            f"technicals:{exchange}:{symbol}:1y",
            f"technicals:{exchange}:{symbol}:3y",
            f"risk:{exchange}:{symbol}",
            f"ai_summary:{exchange}:{symbol}",
        ]
        for key in keys_to_delete:
            deleted = _redis.delete(key)
            if deleted:
                invalidated += 1

    logger.info("Cache invalidation complete: %d keys removed", invalidated)
    return {"invalidated": invalidated}


@celery_app.task(name="tasks.metrics.precompute_for_symbol")
def precompute_for_symbol(exchange: str, symbol: str):
    """Trigger pre-computation by calling API endpoints (warms cache)."""
    endpoints = [
        f"/api/stocks/{exchange}/{symbol}/financials",
        f"/api/stocks/{exchange}/{symbol}/technicals",
        f"/api/stocks/{exchange}/{symbol}/risk",
    ]
    results = {}
    with httpx.Client(base_url=API_BASE, timeout=30.0) as client:
        for endpoint in endpoints:
            try:
                resp = client.get(endpoint)
                results[endpoint] = resp.status_code
            except Exception as exc:
                results[endpoint] = f"error: {exc}"
    return results
