"""Redis cache layer with JSON serialisation helpers."""
from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _pool


async def cache_get(key: str) -> Any | None:
    try:
        raw = await get_redis().get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("cache_get failed key=%s err=%s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    try:
        await get_redis().setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.warning("cache_set failed key=%s err=%s", key, exc)


async def cache_delete(key: str) -> None:
    try:
        await get_redis().delete(key)
    except Exception as exc:
        logger.warning("cache_delete failed key=%s err=%s", key, exc)
