"""Unit tests for financial analytics engine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend-api"))

from app.analytics.financials import (
    pe_ratio, pb_ratio, roe, roce, roa,
    debt_to_equity, current_ratio, quick_ratio,
    ebitda_margin, net_profit_margin, gross_margin,
    interest_coverage, altman_z_score, cagr, xirr,
    compute_all_ratios,
)


class TestValuationRatios:
    def test_pe_ratio_basic(self):
        assert pe_ratio(100.0, 5.0) == 20.0

    def test_pe_ratio_zero_eps(self):
        assert pe_ratio(100.0, 0.0) is None

    def test_pe_ratio_negative_eps(self):
        # Negative EPS is valid — negative PE
        result = pe_ratio(100.0, -5.0)
        assert result == -20.0

    def test_pb_ratio(self):
        assert pb_ratio(150.0, 50.0) == 3.0

    def test_pb_ratio_zero_book(self):
        assert pb_ratio(150.0, 0.0) is None


class TestProfitabilityRatios:
    def test_roe(self):
        assert roe(1000.0, 5000.0) == 20.0

    def test_roe_zero_equity(self):
        assert roe(1000.0, 0.0) is None

    def test_roce(self):
        result = roce(1500.0, 10000.0)
        assert result == 15.0

    def test_roa(self):
        assert roa(800.0, 8000.0) == 10.0

    def test_ebitda_margin(self):
        assert ebitda_margin(3000.0, 10000.0) == 30.0

    def test_net_profit_margin(self):
        assert net_profit_margin(1200.0, 10000.0) == 12.0

    def test_gross_margin(self):
        assert gross_margin(4000.0, 10000.0) == 40.0

    def test_margin_zero_revenue(self):
        assert ebitda_margin(3000.0, 0.0) is None


class TestDebtMetrics:
    def test_debt_to_equity(self):
        assert debt_to_equity(2000.0, 4000.0) == 0.5

    def test_interest_coverage(self):
        assert interest_coverage(1500.0, 500.0) == 3.0

    def test_interest_coverage_zero(self):
        assert interest_coverage(1500.0, 0.0) is None

    def test_altman_z_safe_zone(self):
        # High-quality company should have Z > 2.99
        z = altman_z_score(
            working_capital=5000,
            total_assets=20000,
            retained_earnings=8000,
            ebit=4000,
            market_cap=50000,
            total_liabilities=8000,
            revenue=30000,
        )
        assert z is not None
        assert z > 2.99

    def test_altman_z_distress(self):
        # Distressed company
        z = altman_z_score(
            working_capital=-2000,
            total_assets=10000,
            retained_earnings=-5000,
            ebit=-500,
            market_cap=2000,
            total_liabilities=9000,
            revenue=5000,
        )
        assert z is not None
        assert z < 1.81


class TestLiquidityRatios:
    def test_current_ratio(self):
        assert current_ratio(6000.0, 3000.0) == 2.0

    def test_quick_ratio(self):
        assert quick_ratio(6000.0, 1000.0, 3000.0) == pytest.approx(1.67, rel=0.01)

    def test_current_ratio_zero_liabilities(self):
        assert current_ratio(6000.0, 0.0) is None


class TestGrowthMetrics:
    def test_cagr_positive(self):
        result = cagr(100.0, 259.37, 10.0)
        assert result == pytest.approx(10.0, rel=0.01)

    def test_cagr_zero_start(self):
        assert cagr(0.0, 100.0, 5.0) is None

    def test_cagr_negative_start(self):
        assert cagr(-100.0, 100.0, 5.0) is None


class TestXirr:
    def test_xirr_simple(self):
        # Invest 10000 today (day 0), receive 11000 in 1 year (365 days) → ~10% return
        cashflows = [(-10000, 0), (11000, 365)]
        result = xirr(cashflows)
        assert result is not None
        assert abs(result - 10.0) < 1.0

    def test_xirr_insufficient_data(self):
        assert xirr([(-10000, 0)]) is None


class TestComputeAllRatios:
    def test_compute_returns_dict(self):
        data = {
            "price": 389.0,
            "eps": 15.0,
            "book_value_per_share": 100.0,
            "market_cap": 28000e7,
            "revenue": 20000e7,
            "gross_profit": 8000e7,
            "ebitda": 5000e7,
            "ebit": 4000e7,
            "pat": 3000e7,
            "total_debt": 2000e7,
            "equity": 12000e7,
            "total_assets": 25000e7,
            "current_assets": 10000e7,
            "current_liabilities": 5000e7,
            "cash": 1000e7,
            "retained_earnings": 8000e7,
            "total_liabilities": 13000e7,
        }
        ratios = compute_all_ratios(data)
        assert "pe" in ratios
        assert "pb" in ratios
        assert "roe" in ratios
        assert "debt_to_equity" in ratios
        assert "current_ratio" in ratios
        assert ratios["pe"] == pytest.approx(25.93, rel=0.01)
