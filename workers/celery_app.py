"""Celery application factory for BharatStocks workers."""
import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "bharatstocks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "tasks.quotes",
        "tasks.filings",
        "tasks.news",
        "tasks.metrics",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # Periodic task schedule
    beat_schedule={
        # Refresh quotes for all watchlisted stocks every 5 minutes during market hours
        "refresh-quotes": {
            "task": "tasks.quotes.refresh_all_quotes",
            "schedule": 300,  # 5 minutes
        },
        # Ingest new filings every hour
        "ingest-filings": {
            "task": "tasks.filings.ingest_recent_filings",
            "schedule": crontab(minute=0),  # hourly
        },
        # Refresh news every 15 minutes
        "refresh-news": {
            "task": "tasks.news.refresh_all_news",
            "schedule": 900,  # 15 minutes
        },
        # Recalculate financial metrics daily at midnight IST
        "refresh-metrics": {
            "task": "tasks.metrics.recalculate_all_metrics",
            "schedule": crontab(hour=0, minute=30),
        },
    },
)
