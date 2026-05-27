"""Stocks API router — search, quote, overview, financials, technicals,
shareholding, filings, news, risk, peers, AI summary.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.ai.ollama import OllamaClient, DISCLAIMER
from app.analytics.financials import compute_all_ratios
from app.analytics.technicals import compute_all_indicators
from app.analytics.risk import analyse_risk
from app.cache.redis import cache_get, cache_set
from app.config import get_settings, Settings
from app.connectors.nse import NseConnector
from app.connectors.bse import BseConnector
from app.connectors.yahoo import YahooFinanceConnector
from app.connectors.news import NewsConnector
from app.schemas.stock import (
    AiSummaryResponse,
    FilingItem,
    FinancialsResponse,
    NewsItem,
    OverviewResponse,
    PeerItem,
    QuoteResponse,
    RiskFlag,
    RiskResponse,
    RatiosSnapshot,
    ShareholdingResponse,
    StockSearchResult,
    TechnicalsResponse,
    TechnicalIndicators,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stocks", tags=["stocks"])

# ---------------------------------------------------------------------------
# Shared connector instances (singleton per process)
# ---------------------------------------------------------------------------
_nse = NseConnector()
_bse = BseConnector()
_yahoo = YahooFinanceConnector()
_news = NewsConnector()
_ai = OllamaClient()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@router.get("/search", response_model=list[StockSearchResult])
async def search_stocks(
    q: str = Query(..., min_length=1, max_length=64, description="Symbol, name, or ISIN prefix"),
    exchange: Optional[str] = Query(None, description="NSE or BSE filter"),
):
    """Search stocks by symbol, name, or ISIN. Returns merged NSE + BSE results."""
    cache_key = f"search:{q.lower()}:{(exchange or '').upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    results: list[dict] = []
    if not exchange or exchange.upper() == "NSE":
        results.extend(await _nse.search(q))
    if not exchange or exchange.upper() == "BSE":
        results.extend(await _bse.search(q))

    # Deduplicate by ISIN when available
    seen_isins: set[str] = set()
    deduped = []
    for r in results:
        isin = r.get("isin")
        if isin and isin in seen_isins:
            continue
        if isin:
            seen_isins.add(isin)
        deduped.append(r)

    await cache_set(cache_key, deduped, ttl=300)
    return deduped


# ---------------------------------------------------------------------------
# Quote
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/quote", response_model=QuoteResponse)
async def get_quote(exchange: str, symbol: str):
    """Live market quote with cache-first (60 s TTL)."""
    settings = get_settings()
    cache_key = f"quote:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    data: dict = {}
    try:
        if exchange.upper() == "NSE":
            data = await _nse.get_quote(symbol)
        else:
            data = await _bse.get_quote(symbol)
    except Exception:
        logger.warning("Primary connector failed for %s/%s, falling back to Yahoo", exchange, symbol)

    if not data.get("price"):
        try:
            data = await _yahoo.get_quote(symbol, exchange)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Data unavailable: {exc}") from exc

    await cache_set(cache_key, data, ttl=settings.quote_cache_ttl)
    return data


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/overview", response_model=OverviewResponse)
async def get_overview(exchange: str, symbol: str):
    """Company overview — description, sector, management, website."""
    cache_key = f"overview:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    data = await _yahoo.get_financial_summary(symbol, exchange)
    result = {
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "company_name": data.get("company_name", symbol.upper()),
        "isin": None,
        "sector": data.get("sector"),
        "industry": data.get("industry"),
        "description": data.get("description"),
        "website": data.get("website"),
        "headquarters": data.get("headquarters"),
        "employee_count": data.get("employee_count"),
        "management": [],
        "logo_url": f"https://logo.clearbit.com/{_clean_domain(data.get('website', ''))}",
    }
    await cache_set(cache_key, result, ttl=86400)
    return result


def _clean_domain(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").rstrip("/").split("/")[0]


# ---------------------------------------------------------------------------
# Financials
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/financials", response_model=FinancialsResponse)
async def get_financials(exchange: str, symbol: str):
    """Key financial ratios and statement history."""
    settings = get_settings()
    cache_key = f"financials:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    # Fetch current quote for price
    try:
        quote = await get_quote(exchange, symbol)
        price = quote.get("price") if isinstance(quote, dict) else quote.price
    except Exception:
        price = None

    yf_data = await _yahoo.get_financial_summary(symbol, exchange)
    flat = {**yf_data, "price": price}
    ratios_dict = compute_all_ratios(flat)

    result = {
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "ratios": ratios_dict,
        "income_statement": [],
        "balance_sheet": [],
        "cash_flow": [],
    }
    await cache_set(cache_key, result, ttl=settings.financials_cache_ttl)
    return result


# ---------------------------------------------------------------------------
# Technicals
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/technicals", response_model=TechnicalsResponse)
async def get_technicals(
    exchange: str,
    symbol: str,
    period: str = Query("1y", description="Data range: 1y, 3y, 5y, max"),
):
    """Technical indicators computed from OHLCV history."""
    settings = get_settings()
    cache_key = f"technicals:{exchange.upper()}:{symbol.upper()}:{period}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    ohlcv = await _yahoo.get_historical(symbol, exchange, period=period)
    indicators = compute_all_indicators(ohlcv) if ohlcv else {}

    result = {
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "indicators": indicators,
        "ohlcv": ohlcv[-365:],  # cap to last 365 points for response size
    }
    await cache_set(cache_key, result, ttl=settings.technicals_cache_ttl)
    return result


# ---------------------------------------------------------------------------
# Shareholding
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/shareholding", response_model=ShareholdingResponse)
async def get_shareholding(exchange: str, symbol: str):
    """Promoter/FII/DII shareholding pattern history."""
    cache_key = f"shareholding:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    history = []
    if exchange.upper() == "NSE":
        history = await _nse.get_shareholding(symbol)

    result = {
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "history": history,
    }
    await cache_set(cache_key, result, ttl=86400)
    return result


# ---------------------------------------------------------------------------
# Filings
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/filings", response_model=list[FilingItem])
async def get_filings(exchange: str, symbol: str):
    """Exchange filings — annual reports, investor presentations (links only)."""
    cache_key = f"filings:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    filings: list[dict] = []
    if exchange.upper() == "BSE":
        filings = await _bse.get_filings(symbol)
    # NSE filings endpoint returns paginated XML — left for workers to ingest
    # Here we return whatever was persisted by workers (from DB ideally; empty for POC)

    # Add sequential IDs
    for i, f in enumerate(filings):
        f.setdefault("id", i + 1)

    await cache_set(cache_key, filings, ttl=3600)
    return filings


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/news", response_model=list[NewsItem])
async def get_news(exchange: str, symbol: str):
    """Aggregated news with AI sentiment tags."""
    settings = get_settings()
    cache_key = f"news:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    raw_news = await _news.get_news_for_stock(symbol, symbol)

    # Classify sentiment via AI (best-effort)
    headlines = [n["headline"] for n in raw_news]
    try:
        sentiments = await _ai.classify_sentiment(headlines)
    except Exception:
        sentiments = ["neutral"] * len(headlines)

    result = []
    for i, (item, sentiment) in enumerate(zip(raw_news, sentiments)):
        result.append({
            "id": i + 1,
            "headline": item.get("headline", ""),
            "summary": item.get("summary"),
            "url": item.get("url"),
            "source": item.get("source"),
            "sentiment": sentiment,
            "published_at": item.get("published_at"),
        })

    await cache_set(cache_key, result, ttl=settings.news_cache_ttl)
    return result


# ---------------------------------------------------------------------------
# Risk
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/risk", response_model=RiskResponse)
async def get_risk(exchange: str, symbol: str):
    """Risk analysis — red flags with severity levels."""
    cache_key = f"risk:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    yf_data = await _yahoo.get_financial_summary(symbol, exchange)
    try:
        quote = await get_quote(exchange, symbol)
        price = quote.get("price") if isinstance(quote, dict) else quote.price
    except Exception:
        price = None

    flat = {**yf_data, "price": price}
    ratios_dict = compute_all_ratios(flat)

    # Fetch shareholding for trend analysis
    holding_history: list[dict] = []
    if exchange.upper() == "NSE":
        holding_history = await _nse.get_shareholding(symbol)

    overall, flags = analyse_risk(ratios_dict, shareholding_history=holding_history)

    result = {
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "overall_risk": overall,
        "flags": [
            {
                "key": f.key,
                "label": f.label,
                "severity": f.severity,
                "description": f.description,
            }
            for f in flags
        ],
    }
    await cache_set(cache_key, result, ttl=3600)
    return result


# ---------------------------------------------------------------------------
# Peers
# ---------------------------------------------------------------------------

# Hardcoded peer mapping for POC — production would use sector clustering
_PEERS_MAP: dict[str, list[tuple[str, str]]] = {
    "BEL": [("HAL", "NSE"), ("BDL", "NSE"), ("DATAPATTNS", "NSE"), ("PARAS", "NSE")],
    "INFY": [("TCS", "NSE"), ("WIPRO", "NSE"), ("HCLTECH", "NSE"), ("TECHM", "NSE")],
    "RELIANCE": [("ONGC", "NSE"), ("IOC", "NSE"), ("BPCL", "NSE")],
    "TATAMOTORS": [("M&M", "NSE"), ("MARUTI", "NSE"), ("BAJAJ-AUTO", "NSE")],
}


@router.get("/{exchange}/{symbol}/peers", response_model=list[PeerItem])
async def get_peers(exchange: str, symbol: str):
    """Peer comparison — key ratios side by side."""
    cache_key = f"peers:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    peers_list = _PEERS_MAP.get(symbol.upper(), [])
    results = []
    for peer_sym, peer_exch in peers_list:
        try:
            yf_data = await _yahoo.get_financial_summary(peer_sym, peer_exch)
            pq = await _yahoo.get_quote(peer_sym, peer_exch)
            flat = {**yf_data, "price": pq.get("price")}
            ratios_dict = compute_all_ratios(flat)
            results.append({
                "symbol": peer_sym,
                "company_name": yf_data.get("company_name", peer_sym),
                "exchange": peer_exch,
                "market_cap": pq.get("market_cap"),
                "pe": ratios_dict.get("pe"),
                "pb": ratios_dict.get("pb"),
                "roe": ratios_dict.get("roe"),
                "roce": ratios_dict.get("roce"),
                "revenue_growth": ratios_dict.get("revenue_cagr_3y"),
                "debt_to_equity": ratios_dict.get("debt_to_equity"),
            })
        except Exception as exc:
            logger.warning("Peer fetch failed %s: %s", peer_sym, exc)

    await cache_set(cache_key, results, ttl=3600)
    return results


# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------

@router.get("/{exchange}/{symbol}/ai-summary", response_model=AiSummaryResponse)
async def get_ai_summary(exchange: str, symbol: str):
    """AI-generated investment summary using local Ollama model."""
    cache_key = f"ai_summary:{exchange.upper()}:{symbol.upper()}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    yf_data = await _yahoo.get_financial_summary(symbol, exchange)
    try:
        quote = await get_quote(exchange, symbol)
        price = quote.get("price") if isinstance(quote, dict) else quote.price
    except Exception:
        price = None

    flat = {**yf_data, "price": price}
    ratios_dict = compute_all_ratios(flat)
    company_name = yf_data.get("company_name", symbol)

    # Fetch latest news headlines
    try:
        news_raw = await _news.get_news_for_stock(symbol, company_name)
        headlines = [n["headline"] for n in news_raw[:5]]
    except Exception:
        headlines = []

    summary = await _ai.investment_summary(symbol, company_name, ratios_dict, headlines)
    risk_overall, risk_flags = analyse_risk(ratios_dict)
    risk_text = await _ai.risk_summary(symbol, [{"severity": f.severity, "label": f.label, "description": f.description} for f in risk_flags])

    from datetime import datetime
    result = {
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "summary": summary or f"AI summary not available for {symbol}. Please check Ollama is running.",
        "risk_summary": risk_text,
        "disclaimer": DISCLAIMER,
        "generated_at": datetime.utcnow().isoformat(),
    }
    await cache_set(cache_key, result, ttl=3600)
    return result
