"""Initial schema — all tables.

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exchanges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(8), nullable=False, unique=True),
        sa.Column("name", sa.String(64), nullable=False),
    )
    op.execute("INSERT INTO exchanges (code, name) VALUES ('NSE', 'National Stock Exchange of India')")
    op.execute("INSERT INTO exchanges (code, name) VALUES ('BSE', 'Bombay Stock Exchange')")

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False, index=True),
        sa.Column("isin", sa.String(12), index=True),
        sa.Column("company_name", sa.String(256), nullable=False),
        sa.Column("exchange_id", sa.Integer(), sa.ForeignKey("exchanges.id"), nullable=False),
        sa.Column("sector", sa.String(128)),
        sa.Column("industry", sa.String(128)),
        sa.Column("sub_industry", sa.String(128)),
        sa.Column("logo_url", sa.String(512)),
        sa.Column("website", sa.String(256)),
        sa.Column("description", sa.Text()),
        sa.Column("founded_year", sa.Integer()),
        sa.Column("headquarters", sa.String(256)),
        sa.Column("ceo", sa.String(128)),
        sa.Column("employee_count", sa.Integer()),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.UniqueConstraint("symbol", "exchange_id", name="uq_symbol_exchange"),
    )

    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("price", sa.Float()),
        sa.Column("open", sa.Float()),
        sa.Column("high", sa.Float()),
        sa.Column("low", sa.Float()),
        sa.Column("prev_close", sa.Float()),
        sa.Column("change", sa.Float()),
        sa.Column("change_pct", sa.Float()),
        sa.Column("volume", sa.BigInteger()),
        sa.Column("traded_value", sa.Float()),
        sa.Column("vwap", sa.Float()),
        sa.Column("week52_high", sa.Float()),
        sa.Column("week52_low", sa.Float()),
        sa.Column("market_cap", sa.Float()),
        sa.Column("delivery_pct", sa.Float()),
        sa.Column("timestamp", sa.DateTime()),
    )

    op.create_table(
        "historical_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Float()),
        sa.Column("high", sa.Float()),
        sa.Column("low", sa.Float()),
        sa.Column("close", sa.Float()),
        sa.Column("volume", sa.BigInteger()),
        sa.Column("adjusted_close", sa.Float()),
        sa.UniqueConstraint("company_id", "date", name="uq_company_date"),
    )

    op.create_table(
        "financials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("period", sa.String(16), nullable=False),
        sa.Column("period_type", sa.String(8), nullable=False),
        sa.Column("revenue", sa.Float()),
        sa.Column("gross_profit", sa.Float()),
        sa.Column("ebitda", sa.Float()),
        sa.Column("ebit", sa.Float()),
        sa.Column("pat", sa.Float()),
        sa.Column("eps", sa.Float()),
        sa.Column("operating_expenses", sa.Float()),
        sa.Column("finance_cost", sa.Float()),
        sa.Column("tax_expense", sa.Float()),
        sa.Column("total_assets", sa.Float()),
        sa.Column("current_assets", sa.Float()),
        sa.Column("non_current_assets", sa.Float()),
        sa.Column("total_liabilities", sa.Float()),
        sa.Column("current_liabilities", sa.Float()),
        sa.Column("debt", sa.Float()),
        sa.Column("equity", sa.Float()),
        sa.Column("retained_earnings", sa.Float()),
        sa.Column("cash", sa.Float()),
        sa.Column("operating_cashflow", sa.Float()),
        sa.Column("investing_cashflow", sa.Float()),
        sa.Column("financing_cashflow", sa.Float()),
        sa.Column("capex", sa.Float()),
        sa.Column("free_cashflow", sa.Float()),
        sa.UniqueConstraint("company_id", "period", "period_type", name="uq_company_period"),
    )

    op.create_table(
        "filings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("filing_type", sa.String(64)),
        sa.Column("title", sa.String(512)),
        sa.Column("source_url", sa.String(1024)),
        sa.Column("filing_date", sa.DateTime()),
        sa.Column("financial_year", sa.String(16)),
        sa.Column("source", sa.String(16)),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "shareholding",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("period", sa.String(16)),
        sa.Column("promoter_pct", sa.Float()),
        sa.Column("fii_pct", sa.Float()),
        sa.Column("dii_pct", sa.Float()),
        sa.Column("mutual_fund_pct", sa.Float()),
        sa.Column("public_pct", sa.Float()),
        sa.Column("promoter_pledge_pct", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
        sa.UniqueConstraint("company_id", "period", name="uq_shareholding_period"),
    )

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("headline", sa.String(512), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("url", sa.String(1024)),
        sa.Column("source", sa.String(128)),
        sa.Column("sentiment", sa.String(16)),
        sa.Column("published_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "portfolios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128)),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "holdings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("portfolio_id", sa.Integer(), sa.ForeignKey("portfolios.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("avg_price", sa.Float(), nullable=False),
        sa.Column("buy_date", sa.DateTime()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("watchlist_id", sa.Integer(), sa.ForeignKey("watchlists.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("alert_price_above", sa.Float()),
        sa.Column("alert_price_below", sa.Float()),
        sa.Column("alert_rsi_below", sa.Float()),
        sa.Column("added_at", sa.DateTime()),
    )

    op.create_table(
        "ai_summaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("summary_type", sa.String(32)),
        sa.Column("content", sa.Text()),
        sa.Column("model", sa.String(64)),
        sa.Column("generated_at", sa.DateTime()),
    )


def downgrade() -> None:
    for table in [
        "ai_summaries", "watchlist_items", "watchlists",
        "holdings", "portfolios", "news", "shareholding",
        "filings", "financials", "historical_prices",
        "quotes", "companies", "exchanges",
    ]:
        op.drop_table(table)
