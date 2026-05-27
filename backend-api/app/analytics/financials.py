"""Financial analytics engine.

Computes all key financial ratios and growth metrics from raw statement data.
All calculations are purely numerical — no external API calls.
"""
from __future__ import annotations

import math
from typing import Optional


# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------

def pe_ratio(price: float, eps: float) -> Optional[float]:
    """Price-to-Earnings ratio."""
    return round(price / eps, 2) if eps and eps != 0 else None


def pb_ratio(price: float, book_value_per_share: float) -> Optional[float]:
    """Price-to-Book ratio."""
    return round(price / book_value_per_share, 2) if book_value_per_share and book_value_per_share != 0 else None


def peg_ratio(pe: float, eps_growth_pct: float) -> Optional[float]:
    """PEG ratio (PE / EPS growth %)."""
    return round(pe / eps_growth_pct, 2) if pe and eps_growth_pct and eps_growth_pct != 0 else None


def ev_ebitda(enterprise_value: float, ebitda: float) -> Optional[float]:
    return round(enterprise_value / ebitda, 2) if ebitda and ebitda != 0 else None


def ev_sales(enterprise_value: float, revenue: float) -> Optional[float]:
    return round(enterprise_value / revenue, 2) if revenue and revenue != 0 else None


def price_to_sales(market_cap: float, revenue: float) -> Optional[float]:
    return round(market_cap / revenue, 2) if revenue and revenue != 0 else None


def enterprise_value(market_cap: float, total_debt: float, cash: float) -> float:
    return market_cap + total_debt - cash


# ---------------------------------------------------------------------------
# Profitability
# ---------------------------------------------------------------------------

def roe(net_profit: float, avg_equity: float) -> Optional[float]:
    """Return on Equity (%)."""
    return round(net_profit / avg_equity * 100, 2) if avg_equity and avg_equity != 0 else None


def roce(ebit: float, capital_employed: float) -> Optional[float]:
    """Return on Capital Employed (%)."""
    return round(ebit / capital_employed * 100, 2) if capital_employed and capital_employed != 0 else None


def roa(net_profit: float, avg_total_assets: float) -> Optional[float]:
    """Return on Assets (%)."""
    return round(net_profit / avg_total_assets * 100, 2) if avg_total_assets and avg_total_assets != 0 else None


def ebitda_margin(ebitda: float, revenue: float) -> Optional[float]:
    return round(ebitda / revenue * 100, 2) if revenue and revenue != 0 else None


def net_profit_margin(pat: float, revenue: float) -> Optional[float]:
    return round(pat / revenue * 100, 2) if revenue and revenue != 0 else None


def gross_margin(gross_profit: float, revenue: float) -> Optional[float]:
    return round(gross_profit / revenue * 100, 2) if revenue and revenue != 0 else None


def operating_margin(ebit: float, revenue: float) -> Optional[float]:
    return round(ebit / revenue * 100, 2) if revenue and revenue != 0 else None


# ---------------------------------------------------------------------------
# Debt / Solvency
# ---------------------------------------------------------------------------

def debt_to_equity(total_debt: float, equity: float) -> Optional[float]:
    return round(total_debt / equity, 2) if equity and equity != 0 else None


def debt_to_ebitda(total_debt: float, ebitda: float) -> Optional[float]:
    return round(total_debt / ebitda, 2) if ebitda and ebitda != 0 else None


def interest_coverage(ebit: float, interest_expense: float) -> Optional[float]:
    return round(ebit / interest_expense, 2) if interest_expense and interest_expense != 0 else None


def altman_z_score(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_liabilities: float,
    revenue: float,
) -> Optional[float]:
    """Altman Z-Score for public companies.
    Z > 2.99 = safe zone; 1.81–2.99 = grey zone; < 1.81 = distress zone.
    """
    if total_assets == 0 or total_liabilities == 0:
        return None
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = revenue / total_assets
    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
    return round(z, 2)


# ---------------------------------------------------------------------------
# Liquidity
# ---------------------------------------------------------------------------

def current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
    return round(current_assets / current_liabilities, 2) if current_liabilities and current_liabilities != 0 else None


def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> Optional[float]:
    return round((current_assets - inventory) / current_liabilities, 2) if current_liabilities and current_liabilities != 0 else None


# ---------------------------------------------------------------------------
# Efficiency
# ---------------------------------------------------------------------------

def asset_turnover(revenue: float, avg_total_assets: float) -> Optional[float]:
    return round(revenue / avg_total_assets, 2) if avg_total_assets and avg_total_assets != 0 else None


def inventory_turnover(cogs: float, avg_inventory: float) -> Optional[float]:
    return round(cogs / avg_inventory, 2) if avg_inventory and avg_inventory != 0 else None


def receivables_turnover(revenue: float, avg_receivables: float) -> Optional[float]:
    return round(revenue / avg_receivables, 2) if avg_receivables and avg_receivables != 0 else None


# ---------------------------------------------------------------------------
# Growth metrics
# ---------------------------------------------------------------------------

def cagr(start_value: float, end_value: float, years: float) -> Optional[float]:
    """Compound Annual Growth Rate (%)."""
    if start_value is None or end_value is None or years == 0 or start_value <= 0:
        return None
    return round(((end_value / start_value) ** (1 / years) - 1) * 100, 2)


def growth_yoy(current: float, previous: float) -> Optional[float]:
    """Year-over-year growth (%)."""
    if previous is None or previous == 0:
        return None
    return round((current - previous) / abs(previous) * 100, 2)


# ---------------------------------------------------------------------------
# XIRR (Newton-Raphson implementation)
# ---------------------------------------------------------------------------

def xirr(cashflows: list[tuple[float, float]], guess: float = 0.1) -> Optional[float]:
    """Calculate XIRR given list of (amount, days_from_start) tuples.

    Returns annualised IRR as a decimal (e.g., 0.15 for 15%).
    Amount is negative for investments, positive for returns.
    """
    if len(cashflows) < 2:
        return None
    rate = guess
    for _ in range(100):
        numerator = sum(cf / (1 + rate) ** (days / 365) for cf, days in cashflows)
        denominator = sum(
            -days / 365 * cf / (1 + rate) ** (days / 365 + 1)
            for cf, days in cashflows
        )
        if denominator == 0:
            return None
        new_rate = rate - numerator / denominator
        if abs(new_rate - rate) < 1e-7:
            return round(new_rate * 100, 2)
        rate = new_rate
    return round(rate * 100, 2)


# ---------------------------------------------------------------------------
# Convenience: compute all ratios from a flat dict of financials
# ---------------------------------------------------------------------------

def compute_all_ratios(data: dict) -> dict:
    """Compute all available ratios from a flat financials dict.

    Keys expected (all optional / None-safe):
      price, eps, book_value_per_share, market_cap, enterprise_value,
      revenue, gross_profit, ebitda, ebit, pat, total_debt, equity,
      total_assets, current_assets, current_liabilities, cash,
      retained_earnings, working_capital, interest_expense,
      total_liabilities, inventory, avg_receivables, cogs,
      eps_growth_pct, revenue_start_3y, revenue_end_3y, ...
    """
    p = data  # shorthand

    ratios: dict = {}

    price = p.get("price")
    eps = p.get("eps")
    book_val = p.get("book_value_per_share")
    mkt_cap = p.get("market_cap")
    ev = p.get("enterprise_value")
    revenue = p.get("revenue")
    gross_profit = p.get("gross_profit")
    ebitda = p.get("ebitda")
    ebit = p.get("ebit")
    pat = p.get("pat")
    total_debt = p.get("total_debt", 0) or 0
    equity = p.get("equity")
    total_assets = p.get("total_assets")
    current_assets = p.get("current_assets")
    current_liabilities = p.get("current_liabilities")
    cash = p.get("cash", 0) or 0
    retained_earnings = p.get("retained_earnings", 0) or 0
    working_capital = (current_assets or 0) - (current_liabilities or 0)
    interest_expense = p.get("interest_expense")
    total_liabilities = p.get("total_liabilities")
    inventory = p.get("inventory", 0) or 0
    avg_receivables = p.get("avg_receivables")
    cogs = p.get("cogs")
    eps_growth_pct = p.get("eps_growth_pct")

    if price and eps:
        ratios["pe"] = pe_ratio(price, eps)
    if price and book_val:
        ratios["pb"] = pb_ratio(price, book_val)
    if ratios.get("pe") and eps_growth_pct:
        ratios["peg"] = peg_ratio(ratios["pe"], eps_growth_pct)
    if ev and ebitda:
        ratios["ev_ebitda"] = ev_ebitda(ev, ebitda)
    if ev and revenue:
        ratios["ev_sales"] = ev_sales(ev, revenue)
    if mkt_cap and revenue:
        ratios["price_sales"] = price_to_sales(mkt_cap, revenue)

    if pat and equity:
        ratios["roe"] = roe(pat, equity)
    if ebit and total_assets and total_debt is not None:
        capital_employed = (total_assets or 0) - (current_liabilities or 0)
        if capital_employed:
            ratios["roce"] = roce(ebit, capital_employed)
    if pat and total_assets:
        ratios["roa"] = roa(pat, total_assets)

    if ebitda and revenue:
        ratios["ebitda_margin"] = ebitda_margin(ebitda, revenue)
    if pat and revenue:
        ratios["net_margin"] = net_profit_margin(pat, revenue)
    if gross_profit and revenue:
        ratios["gross_margin"] = gross_margin(gross_profit, revenue)
    if ebit and revenue:
        ratios["operating_margin"] = operating_margin(ebit, revenue)

    if total_debt is not None and equity:
        ratios["debt_to_equity"] = debt_to_equity(total_debt, equity)
    if total_debt is not None and ebitda:
        ratios["debt_to_ebitda"] = debt_to_ebitda(total_debt, ebitda)
    if ebit and interest_expense:
        ratios["interest_coverage"] = interest_coverage(ebit, interest_expense)

    if current_assets and current_liabilities:
        ratios["current_ratio"] = current_ratio(current_assets, current_liabilities)
        ratios["quick_ratio"] = quick_ratio(current_assets, inventory, current_liabilities)

    if total_assets and total_liabilities and revenue:
        ratios["altman_z"] = altman_z_score(
            working_capital, total_assets, retained_earnings,
            ebit or 0, mkt_cap or 0, total_liabilities, revenue
        )

    if revenue and total_assets:
        ratios["asset_turnover"] = asset_turnover(revenue, total_assets)
    if cogs and inventory:
        ratios["inventory_turnover"] = inventory_turnover(cogs, inventory)
    if revenue and avg_receivables:
        ratios["receivables_turnover"] = receivables_turnover(revenue, avg_receivables)

    # CAGR (pre-computed if data provides start/end/years keys)
    for metric in ("revenue", "eps", "pat"):
        for years in (3, 5):
            start_key = f"{metric}_start_{years}y"
            end_key = f"{metric}_end_{years}y"
            if p.get(start_key) and p.get(end_key):
                ratios[f"{metric}_cagr_{years}y"] = cagr(p[start_key], p[end_key], years)

    return ratios
