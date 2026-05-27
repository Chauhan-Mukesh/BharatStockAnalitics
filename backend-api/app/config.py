"""Application configuration via environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "BharatStocks API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "******localhost:5432/bharatstocks"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Quote cache TTL (seconds)
    quote_cache_ttl: int = 60
    news_cache_ttl: int = 900   # 15 min
    financials_cache_ttl: int = 86400  # 1 day
    technicals_cache_ttl: int = 300    # 5 min

    # NSE / BSE base URLs
    nse_base_url: str = "https://www.nseindia.com"
    bse_base_url: str = "https://api.bseindia.com"

    # Yahoo Finance (fallback)
    yahoo_finance_base: str = "https://query1.finance.yahoo.com"

    # Ollama AI
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2:7b"

    # API rate limits (requests per minute per IP)
    rate_limit_per_minute: int = 60

    # CORS
    allowed_origins: list[str] = ["*"]

    # Secret key for JWT (change in production!)
    secret_key: str = "changeme-super-secret-key"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
