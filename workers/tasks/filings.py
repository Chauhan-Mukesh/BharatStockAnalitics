"""Celery tasks: filings ingestion."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta

import httpx
import redis
from celery_app import celery_app

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_BASE = os.getenv("API_BASE_URL", "http://backend-api:8000")
BSE_FILINGS_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnualReports/w"

_redis = redis.from_url(REDIS_URL, decode_responses=True)

# Symbols to track for filings (POC list — production fetches from DB)
TRACKED_SYMBOLS = [
    ("BSE", "500325"),   # Reliance
    ("BSE", "532174"),   # ICICI Bank
    ("BSE", "532978"),   # BEL
    ("BSE", "500209"),   # Infosys
]


@celery_app.task(name="tasks.filings.ingest_recent_filings", bind=True, max_retries=2)
def ingest_recent_filings(self):
    """Fetch latest filings from BSE and cache them."""
    logger.info("Starting filings ingestion")
    results = {"ingested": 0, "failed": 0}

    for exchange, scrip_code in TRACKED_SYMBOLS:
        try:
            with httpx.Client(timeout=15.0, headers={"Referer": "https://www.bseindia.com/"}) as client:
                resp = client.get(
                    BSE_FILINGS_URL,
                    params={"scripcode": scrip_code, "Category": "-1", "Subcategory": "-1"},
                )
                if resp.status_code == 200:
                    filings = resp.json()
                    cache_key = f"filings_raw:{exchange}:{scrip_code}"
                    _redis.setex(cache_key, 86400, json.dumps(filings, default=str))
                    results["ingested"] += 1
                    logger.info("Ingested %d filings for %s/%s",
                                len(filings) if isinstance(filings, list) else 0,
                                exchange, scrip_code)
        except Exception as exc:
            logger.error("Filing ingestion failed %s/%s: %s", exchange, scrip_code, exc)
            results["failed"] += 1

    logger.info("Filing ingestion complete: %s", results)
    return results


@celery_app.task(name="tasks.filings.ingest_for_symbol")
def ingest_filings_for_symbol(exchange: str, scrip_code: str):
    """On-demand filing ingestion for a specific symbol."""
    try:
        with httpx.Client(timeout=15.0, headers={"Referer": "https://www.bseindia.com/"}) as client:
            resp = client.get(
                BSE_FILINGS_URL,
                params={"scripcode": scrip_code, "Category": "-1", "Subcategory": "-1"},
            )
            resp.raise_for_status()
            filings = resp.json()
            cache_key = f"filings_raw:{exchange}:{scrip_code}"
            _redis.setex(cache_key, 86400, json.dumps(filings, default=str))
            return {"status": "ok", "count": len(filings) if isinstance(filings, list) else 0}
    except Exception as exc:
        logger.error("On-demand filing ingestion failed: %s", exc)
        return {"status": "error", "error": str(exc)}
