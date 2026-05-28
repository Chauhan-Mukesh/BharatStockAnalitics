"""Risk Analysis Engine.

Detects red flags and governance risks from financials, shareholding,
and other available data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RiskFlag:
    key: str
    label: str
    severity: str           # "high" / "medium" / "low"
    description: str


def analyse_risk(
    ratios: dict,
    shareholding_history: list[dict] | None = None,
    financials_history: list[dict] | None = None,
) -> tuple[str, list[RiskFlag]]:
    """Analyse risk and return (overall_risk_level, list_of_flags).

    Parameters
    ----------
    ratios : dict
        Current ratio values (output of compute_all_ratios).
    shareholding_history : list of dicts sorted by period (oldest first)
        Each with keys: promoter_pct, promoter_pledge_pct, fii_pct.
    financials_history : list of dicts sorted by period (oldest first)
        Each with keys: pat, revenue, ebitda, operating_cashflow, debt,
        equity, receivables, inventory.
    """
    flags: list[RiskFlag] = []

    # --- Debt risk
    dte = ratios.get("debt_to_equity")
    if dte is not None:
        if dte > 2.0:
            flags.append(RiskFlag("high_debt", "High Debt", "high",
                                  f"Debt/Equity ratio is {dte:.1f}x — significantly above safe levels."))
        elif dte > 1.0:
            flags.append(RiskFlag("elevated_debt", "Elevated Debt", "medium",
                                  f"Debt/Equity ratio is {dte:.1f}x — moderately leveraged."))

    # --- Interest coverage
    ic = ratios.get("interest_coverage")
    if ic is not None and ic < 2.0:
        flags.append(RiskFlag("weak_interest_coverage", "Weak Interest Coverage", "high",
                              f"Interest coverage is {ic:.1f}x — earnings may not cover interest obligations."))

    # --- Profitability
    net_margin = ratios.get("net_margin")
    if net_margin is not None and net_margin < 0:
        flags.append(RiskFlag("negative_margins", "Negative Net Margin", "high",
                              "Company is reporting net losses."))

    ebitda_mgn = ratios.get("ebitda_margin")
    if ebitda_mgn is not None and ebitda_mgn < 5:
        flags.append(RiskFlag("thin_ebitda_margin", "Thin EBITDA Margin", "medium",
                              f"EBITDA margin is only {ebitda_mgn:.1f}% — limited buffer for shocks."))

    # --- ROE / ROCE
    roe_val = ratios.get("roe")
    if roe_val is not None and roe_val < 10:
        flags.append(RiskFlag("low_roe", "Low ROE", "medium",
                              f"ROE of {roe_val:.1f}% is below typical acceptable threshold of 15%."))

    roce_val = ratios.get("roce")
    if roce_val is not None and roce_val < 12:
        flags.append(RiskFlag("low_roce", "Low ROCE", "medium",
                              f"ROCE of {roce_val:.1f}% suggests suboptimal capital usage."))

    # --- Liquidity
    cr = ratios.get("current_ratio")
    if cr is not None and cr < 1.0:
        flags.append(RiskFlag("poor_liquidity", "Poor Liquidity", "high",
                              f"Current ratio is {cr:.2f} — company may struggle to meet short-term obligations."))

    # --- Valuation
    pe = ratios.get("pe")
    if pe is not None and pe > 60:
        flags.append(RiskFlag("high_valuation", "High Valuation", "medium",
                              f"PE of {pe:.1f}x is elevated and may reflect overly optimistic expectations."))

    # --- Altman Z
    z = ratios.get("altman_z")
    if z is not None:
        if z < 1.81:
            flags.append(RiskFlag("financial_distress", "Financial Distress Risk", "high",
                                  f"Altman Z-Score of {z:.2f} is in the distress zone (<1.81)."))
        elif z < 2.99:
            flags.append(RiskFlag("grey_zone", "Grey Zone (Altman Z)", "medium",
                                  f"Altman Z-Score of {z:.2f} is in the grey zone (1.81–2.99)."))

    # --- Shareholding trends
    if shareholding_history and len(shareholding_history) >= 2:
        latest = shareholding_history[-1]
        oldest = shareholding_history[0]

        promo_latest = latest.get("promoter_pct")
        promo_oldest = oldest.get("promoter_pct")
        if promo_latest is not None and promo_oldest is not None:
            if promo_oldest - promo_latest > 5:
                flags.append(RiskFlag("falling_promoter_holding", "Falling Promoter Holding", "high",
                                      f"Promoter stake fell from {promo_oldest:.1f}% to {promo_latest:.1f}% — negative signal."))
            elif promo_oldest - promo_latest > 2:
                flags.append(RiskFlag("declining_promoter_holding", "Declining Promoter Holding", "medium",
                                      f"Promoter stake declined from {promo_oldest:.1f}% to {promo_latest:.1f}%."))

        pledge = latest.get("promoter_pledge_pct")
        if pledge is not None and pledge > 20:
            flags.append(RiskFlag("high_pledge", "High Promoter Pledge", "high",
                                  f"{pledge:.1f}% of promoter shares are pledged."))
        elif pledge is not None and pledge > 5:
            flags.append(RiskFlag("promoter_pledge", "Promoter Shares Pledged", "medium",
                                  f"{pledge:.1f}% of promoter shares are pledged."))

    # --- Financial trend analysis
    if financials_history and len(financials_history) >= 2:
        latest_f = financials_history[-1]
        prev_f = financials_history[-2]

        # Falling revenue
        if prev_f.get("revenue") and latest_f.get("revenue"):
            rev_change = (latest_f["revenue"] - prev_f["revenue"]) / abs(prev_f["revenue"]) * 100
            if rev_change < -10:
                flags.append(RiskFlag("revenue_decline", "Revenue Decline", "high",
                                      f"Revenue fell {abs(rev_change):.1f}% YoY."))

        # Receivables spike
        if prev_f.get("receivables") and latest_f.get("receivables") and prev_f.get("revenue"):
            rec_to_rev = latest_f["receivables"] / latest_f.get("revenue", 1)
            if rec_to_rev > 0.4:
                flags.append(RiskFlag("receivables_spike", "High Receivables", "medium",
                                      "Receivables are very high relative to revenue — collection risk."))

        # Negative operating cash flow
        if latest_f.get("operating_cashflow") is not None and latest_f["operating_cashflow"] < 0:
            flags.append(RiskFlag("negative_ocf", "Negative Operating Cash Flow", "high",
                                  "Company is burning cash from operations."))

    # --- Determine overall risk level
    if any(f.severity == "high" for f in flags):
        overall = "high"
    elif any(f.severity == "medium" for f in flags):
        overall = "medium"
    else:
        overall = "low"

    return overall, flags
