"""Unit tests for risk analysis engine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend-api"))

from app.analytics.risk import analyse_risk


class TestRiskAnalysis:
    def test_no_flags_for_healthy_company(self):
        ratios = {
            "debt_to_equity": 0.3,
            "interest_coverage": 10.0,
            "net_margin": 18.0,
            "ebitda_margin": 28.0,
            "roe": 22.0,
            "roce": 20.0,
            "current_ratio": 2.5,
            "pe": 25.0,
            "altman_z": 4.5,
        }
        overall, flags = analyse_risk(ratios)
        assert overall == "low"
        assert len(flags) == 0

    def test_high_debt_flag(self):
        ratios = {"debt_to_equity": 3.5}
        overall, flags = analyse_risk(ratios)
        keys = [f.key for f in flags]
        assert "high_debt" in keys
        assert overall == "high"

    def test_negative_margins_flag(self):
        ratios = {"net_margin": -5.0}
        overall, flags = analyse_risk(ratios)
        keys = [f.key for f in flags]
        assert "negative_margins" in keys
        assert overall == "high"

    def test_weak_interest_coverage_flag(self):
        ratios = {"interest_coverage": 1.2}
        overall, flags = analyse_risk(ratios)
        keys = [f.key for f in flags]
        assert "weak_interest_coverage" in keys

    def test_poor_liquidity_flag(self):
        ratios = {"current_ratio": 0.7}
        overall, flags = analyse_risk(ratios)
        keys = [f.key for f in flags]
        assert "poor_liquidity" in keys
        assert overall == "high"

    def test_altman_z_distress_flag(self):
        ratios = {"altman_z": 1.2}
        overall, flags = analyse_risk(ratios)
        keys = [f.key for f in flags]
        assert "financial_distress" in keys
        assert overall == "high"

    def test_altman_z_grey_zone(self):
        ratios = {"altman_z": 2.3}
        overall, flags = analyse_risk(ratios)
        keys = [f.key for f in flags]
        assert "grey_zone" in keys

    def test_falling_promoter_holding_flag(self):
        ratios = {}
        shareholding = [
            {"promoter_pct": 55.0, "promoter_pledge_pct": 0.0},
            {"promoter_pct": 49.0, "promoter_pledge_pct": 0.0},
        ]
        overall, flags = analyse_risk(ratios, shareholding_history=shareholding)
        keys = [f.key for f in flags]
        assert "falling_promoter_holding" in keys

    def test_high_pledge_flag(self):
        ratios = {}
        shareholding = [
            {"promoter_pct": 51.0, "promoter_pledge_pct": 2.0},
            {"promoter_pct": 51.0, "promoter_pledge_pct": 25.0},
        ]
        overall, flags = analyse_risk(ratios, shareholding_history=shareholding)
        keys = [f.key for f in flags]
        assert "high_pledge" in keys

    def test_multiple_high_flags_give_high_overall(self):
        ratios = {
            "debt_to_equity": 3.0,
            "net_margin": -10.0,
            "current_ratio": 0.5,
        }
        overall, flags = analyse_risk(ratios)
        assert overall == "high"
        assert len(flags) >= 3

    def test_medium_overall_when_only_medium_flags(self):
        ratios = {
            "roe": 8.0,
            "roce": 10.0,
            "ebitda_margin": 3.0,
        }
        overall, flags = analyse_risk(ratios)
        assert overall == "medium"
        assert all(f.severity == "medium" for f in flags)

    def test_negative_operating_cashflow(self):
        ratios = {}
        financials_history = [
            {"revenue": 1000, "pat": 50, "operating_cashflow": 100},
            {"revenue": 1100, "pat": 55, "operating_cashflow": -200},
        ]
        _, flags = analyse_risk(ratios, financials_history=financials_history)
        keys = [f.key for f in flags]
        assert "negative_ocf" in keys
