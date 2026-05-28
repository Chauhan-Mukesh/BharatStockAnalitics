"""Pydantic schemas used in API request/response."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class StockSearchResult(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    isin: Optional[str] = None
    sector: Optional[str] = None


# ---------------------------------------------------------------------------
# Quote
# ---------------------------------------------------------------------------

class QuoteResponse(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    price: float
    open: float
    high: float
    low: float
    prev_close: float
    change: float
    change_pct: float
    volume: int
    traded_value: Optional[float] = None
    vwap: Optional[float] = None
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None
    market_cap: Optional[float] = None
    delivery_pct: Optional[float] = None
    timestamp: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

class ManagementPerson(BaseModel):
    name: str
    designation: str


class OverviewResponse(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    isin: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    employee_count: Optional[int] = None
    management: list[ManagementPerson] = []
    logo_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Financials
# ---------------------------------------------------------------------------

class IncomeStatementRow(BaseModel):
    period: str
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    ebitda: Optional[float] = None
    ebit: Optional[float] = None
    pat: Optional[float] = None
    eps: Optional[float] = None


class BalanceSheetRow(BaseModel):
    period: str
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    debt: Optional[float] = None
    equity: Optional[float] = None
    cash: Optional[float] = None


class CashFlowRow(BaseModel):
    period: str
    operating_cashflow: Optional[float] = None
    investing_cashflow: Optional[float] = None
    financing_cashflow: Optional[float] = None
    capex: Optional[float] = None
    free_cashflow: Optional[float] = None


class RatiosSnapshot(BaseModel):
    pe: Optional[float] = None
    forward_pe: Optional[float] = None
    pb: Optional[float] = None
    peg: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_sales: Optional[float] = None
    price_sales: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    roa: Optional[float] = None
    roi: Optional[float] = None
    ebitda_margin: Optional[float] = None
    net_margin: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    interest_coverage: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    altman_z: Optional[float] = None
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    eps_cagr_3y: Optional[float] = None
    eps_cagr_5y: Optional[float] = None
    pat_cagr_3y: Optional[float] = None


class FinancialsResponse(BaseModel):
    symbol: str
    exchange: str
    ratios: RatiosSnapshot
    income_statement: list[IncomeStatementRow] = []
    balance_sheet: list[BalanceSheetRow] = []
    cash_flow: list[CashFlowRow] = []


# ---------------------------------------------------------------------------
# Technicals
# ---------------------------------------------------------------------------

class TechnicalIndicators(BaseModel):
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr_14: Optional[float] = None
    adx_14: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    supertrend: Optional[float] = None
    supertrend_direction: Optional[str] = None   # "up" / "down"
    support: Optional[float] = None
    resistance: Optional[float] = None


class OhlcvPoint(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalsResponse(BaseModel):
    symbol: str
    exchange: str
    indicators: TechnicalIndicators
    ohlcv: list[OhlcvPoint] = []


# ---------------------------------------------------------------------------
# Shareholding
# ---------------------------------------------------------------------------

class ShareholdingPeriod(BaseModel):
    period: str
    promoter_pct: Optional[float] = None
    fii_pct: Optional[float] = None
    dii_pct: Optional[float] = None
    mutual_fund_pct: Optional[float] = None
    public_pct: Optional[float] = None
    promoter_pledge_pct: Optional[float] = None


class ShareholdingResponse(BaseModel):
    symbol: str
    exchange: str
    history: list[ShareholdingPeriod] = []


# ---------------------------------------------------------------------------
# Filings
# ---------------------------------------------------------------------------

class FilingItem(BaseModel):
    id: int
    filing_type: Optional[str] = None
    title: str
    source_url: str
    filing_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    source: Optional[str] = None


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------

class NewsItem(BaseModel):
    id: int
    headline: str
    summary: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    sentiment: Optional[str] = None   # bullish / bearish / neutral
    published_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Risk
# ---------------------------------------------------------------------------

class RiskFlag(BaseModel):
    key: str
    label: str
    severity: str           # "high" / "medium" / "low"
    description: str


class RiskResponse(BaseModel):
    symbol: str
    exchange: str
    overall_risk: str       # "high" / "medium" / "low"
    flags: list[RiskFlag] = []


# ---------------------------------------------------------------------------
# Peers
# ---------------------------------------------------------------------------

class PeerItem(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    market_cap: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    revenue_growth: Optional[float] = None
    debt_to_equity: Optional[float] = None


# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------

class AiSummaryResponse(BaseModel):
    symbol: str
    exchange: str
    summary: str
    risk_summary: Optional[str] = None
    disclaimer: str = (
        "This summary is generated by an AI model for informational purposes only. "
        "It does not constitute financial advice. Please do your own research before "
        "making any investment decisions."
    )
    generated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

class HoldingIn(BaseModel):
    symbol: str
    exchange: str
    quantity: float
    avg_price: float
    buy_date: Optional[datetime] = None


class HoldingOut(BaseModel):
    id: int
    symbol: str
    company_name: str
    exchange: str
    quantity: float
    avg_price: float
    current_price: Optional[float] = None
    invested_value: float
    current_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_pct: Optional[float] = None


class PortfolioResponse(BaseModel):
    portfolio_id: int
    total_invested: float
    total_current_value: Optional[float] = None
    total_unrealized_pnl: Optional[float] = None
    total_unrealized_pnl_pct: Optional[float] = None
    holdings: list[HoldingOut] = []


# ---------------------------------------------------------------------------
# Watchlist
# ---------------------------------------------------------------------------

class WatchlistCreate(BaseModel):
    name: str


class WatchlistItemIn(BaseModel):
    symbol: str
    exchange: str
    alert_price_above: Optional[float] = None
    alert_price_below: Optional[float] = None
    alert_rsi_below: Optional[float] = None


class WatchlistOut(BaseModel):
    id: int
    name: str
    items: list[WatchlistItemIn] = []
