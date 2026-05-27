"""SQLAlchemy ORM models for BharatStocks."""
from __future__ import annotations

import datetime
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Reference tables
# ---------------------------------------------------------------------------

class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)   # NSE / BSE
    name = Column(String(64), nullable=False)

    companies: list["Company"] = relationship("Company", back_populates="exchange")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(32), nullable=False, index=True)
    isin = Column(String(12), index=True)
    company_name = Column(String(256), nullable=False)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    sector = Column(String(128))
    industry = Column(String(128))
    sub_industry = Column(String(128))
    logo_url = Column(String(512))
    website = Column(String(256))
    description = Column(Text)
    founded_year = Column(Integer)
    headquarters = Column(String(256))
    ceo = Column(String(128))
    employee_count = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint("symbol", "exchange_id", name="uq_symbol_exchange"),)

    exchange: Exchange = relationship("Exchange", back_populates="companies")
    quotes: list["Quote"] = relationship("Quote", back_populates="company")
    financials: list["Financial"] = relationship("Financial", back_populates="company")
    filings: list["Filing"] = relationship("Filing", back_populates="company")
    shareholdings: list["Shareholding"] = relationship("Shareholding", back_populates="company")
    news: list["News"] = relationship("News", back_populates="company")


# ---------------------------------------------------------------------------
# Market data
# ---------------------------------------------------------------------------

class Quote(Base):
    """Latest intraday quote snapshot."""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    price = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    prev_close = Column(Float)
    change = Column(Float)
    change_pct = Column(Float)
    volume = Column(BigInteger)
    traded_value = Column(Float)
    vwap = Column(Float)
    week52_high = Column(Float)
    week52_low = Column(Float)
    market_cap = Column(Float)
    delivery_pct = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    company: Company = relationship("Company", back_populates="quotes")


class HistoricalPrice(Base):
    """EOD OHLCV data for charts."""
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    adjusted_close = Column(Float)

    __table_args__ = (UniqueConstraint("company_id", "date", name="uq_company_date"),)


# ---------------------------------------------------------------------------
# Financials
# ---------------------------------------------------------------------------

class Financial(Base):
    """Aggregated financials per period."""
    __tablename__ = "financials"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(16), nullable=False)      # e.g. "FY2024", "Q3FY24"
    period_type = Column(String(8), nullable=False)  # "annual" / "quarterly"

    # Income statement
    revenue = Column(Float)
    gross_profit = Column(Float)
    ebitda = Column(Float)
    ebit = Column(Float)
    pat = Column(Float)
    eps = Column(Float)
    operating_expenses = Column(Float)
    finance_cost = Column(Float)
    tax_expense = Column(Float)

    # Balance sheet
    total_assets = Column(Float)
    current_assets = Column(Float)
    non_current_assets = Column(Float)
    total_liabilities = Column(Float)
    current_liabilities = Column(Float)
    debt = Column(Float)
    equity = Column(Float)
    retained_earnings = Column(Float)
    cash = Column(Float)

    # Cash flow
    operating_cashflow = Column(Float)
    investing_cashflow = Column(Float)
    financing_cashflow = Column(Float)
    capex = Column(Float)
    free_cashflow = Column(Float)

    company: Company = relationship("Company", back_populates="financials")

    __table_args__ = (UniqueConstraint("company_id", "period", "period_type", name="uq_company_period"),)


# ---------------------------------------------------------------------------
# Filings & Reports
# ---------------------------------------------------------------------------

class Filing(Base):
    __tablename__ = "filings"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    filing_type = Column(String(64))        # "annual_report", "investor_pres", etc.
    title = Column(String(512))
    source_url = Column(String(1024))       # link only — never store document content
    filing_date = Column(DateTime)
    financial_year = Column(String(16))
    source = Column(String(16))             # "NSE" / "BSE"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company: Company = relationship("Company", back_populates="filings")


# ---------------------------------------------------------------------------
# Shareholding
# ---------------------------------------------------------------------------

class Shareholding(Base):
    __tablename__ = "shareholding"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period = Column(String(16))             # "Mar2025"
    promoter_pct = Column(Float)
    fii_pct = Column(Float)
    dii_pct = Column(Float)
    mutual_fund_pct = Column(Float)
    public_pct = Column(Float)
    promoter_pledge_pct = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint("company_id", "period", name="uq_shareholding_period"),)

    company: Company = relationship("Company", back_populates="shareholding")


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    headline = Column(String(512), nullable=False)
    summary = Column(Text)
    url = Column(String(1024))
    source = Column(String(128))
    sentiment = Column(String(16))          # "bullish" / "bearish" / "neutral"
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company: Company = relationship("Company", back_populates="news")


# ---------------------------------------------------------------------------
# Portfolio & Watchlist
# ---------------------------------------------------------------------------

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), default="My Portfolio")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    holdings: list["Holding"] = relationship("Holding", back_populates="portfolio")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    buy_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    portfolio: Portfolio = relationship("Portfolio", back_populates="holdings")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items: list["WatchlistItem"] = relationship("WatchlistItem", back_populates="watchlist")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    alert_price_above = Column(Float)
    alert_price_below = Column(Float)
    alert_rsi_below = Column(Float)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

    watchlist: Watchlist = relationship("Watchlist", back_populates="items")


# ---------------------------------------------------------------------------
# AI Summaries
# ---------------------------------------------------------------------------

class AiSummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    summary_type = Column(String(32))   # "investment", "risk", "quarter"
    content = Column(Text)
    model = Column(String(64))
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
