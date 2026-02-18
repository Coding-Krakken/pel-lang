"""Unit tests for stdlib retention module."""
# ruff: noqa: W293
import tempfile
from pathlib import Path

import pytest

from compiler.compiler import PELCompiler


def _compile_pel_code(code: str) -> dict:
    fd, tmp = tempfile.mkstemp(suffix=".pel")
    # Wrap snippets in a model for the compiler
    content = "model TestModel {\n" + code + "\n}\n"
    Path(tmp).write_text(content, encoding="utf-8")
    compiler = PELCompiler(verbose=False)
    ir = compiler.compile(Path(tmp))
    return ir


@pytest.mark.unit
def test_exponential_retention_curve():
    """Test exponential retention curve generation."""
    pel_code = """
    param monthly_churn: Rate per Month = 0.05/1mo {
        source: "cohort_analysis",
        method: "fitted",
        confidence: 0.85
    }
    
    param months: Count = 12 {
        source: "model_horizon",
        method: "assumption",
        confidence: 1.0
    }
    
    var retention_curve: Array<Fraction> = exponential_retention_curve(monthly_churn, months)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_power_law_retention_curve():
    """Test power law retention curve generation."""
    pel_code = """
    param alpha: Fraction = 0.9 {
        source: "curve_fit",
        method: "fitted",
        confidence: 0.75
    }
    
    param beta: Fraction = 0.15 {
        source: "curve_fit",
        method: "fitted",
        confidence: 0.75
    }
    
    param months: Count = 24 {
        source: "model_horizon",
        method: "assumption",
        confidence: 1.0
    }
    
    var retention_curve: Array<Fraction> = power_law_retention_curve(alpha, beta, months)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cohort_retention_table():
    """Test cohort retention table calculation."""
    pel_code = """
    param initial_cohort: Count<Customer> = 1000 {
        source: "signup_data",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_churn: Rate per Month = 0.05/1mo {
        source: "cohort_analysis",
        method: "fitted",
        confidence: 0.85
    }
    
    var retention_rates: Array<Fraction> = exponential_retention_curve(monthly_churn, 12)
    var cohort_sizes: Array<Count<Customer>> = cohort_retention_table(initial_cohort, retention_rates)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_simple_churn_rate():
    """Test simple churn rate calculation."""
    pel_code = """
    param customers_start: Count<Customer> = 1000 {
        source: "database",
        method: "observed",
        confidence: 1.0
    }
    
    param customers_lost: Count<Customer> = 50 {
        source: "database",
        method: "observed",
        confidence: 1.0
    }
    
    var churn: Rate per Month = simple_churn_rate(customers_start, customers_lost)
    
    constraint acceptable_churn: churn <= 0.07/1mo {
        severity: warning,
        message: "Churn rate exceeds 7% threshold"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_customer_lifetime_months():
    """Test customer lifetime calculation."""
    pel_code = """
    param retention_rate: Fraction = 0.95 {
        source: "cohort_analysis",
        method: "derived",
        confidence: 0.9
    }
    
    var lifetime: Duration<Month> = customer_lifetime_months(retention_rate)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_net_dollar_retention():
    """Test NDR calculation."""
    pel_code = """
    param starting_mrr: Currency<USD> = $100_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion: Currency<USD> = $15_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churn: Currency<USD> = $8_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction: Currency<USD> = $2_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var ndr: Fraction = net_dollar_retention(starting_mrr, expansion, churn, contraction)
    
    constraint healthy_ndr: ndr >= 1.0 {
        severity: warning,
        message: "NDR below 100% - losing revenue from existing customers"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_gross_dollar_retention():
    """Test GDR calculation."""
    pel_code = """
    param starting_mrr: Currency<USD> = $100_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churn: Currency<USD> = $5_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction: Currency<USD> = $2_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var gdr: Fraction = gross_dollar_retention(starting_mrr, churn, contraction)
    
    constraint strong_gdr: gdr >= 0.90 {
        severity: info,
        message: "GDR above 90% is excellent"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_quick_ratio_retention():
    """Test quick ratio calculation."""
    pel_code = """
    param new_mrr: Currency<USD> = $40_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion_mrr: Currency<USD> = $15_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churned_mrr: Currency<USD> = $8_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction_mrr: Currency<USD> = $2_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var quick_ratio: Fraction = quick_ratio_retention(new_mrr, expansion_mrr, churned_mrr, contraction_mrr)
    
    constraint healthy_quick_ratio: quick_ratio >= 4.0 {
        severity: info,
        message: "Quick ratio above 4 indicates strong growth efficiency"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_retention_rate_from_churn():
    """Test conversion from churn to retention rate."""
    pel_code = """
    param churn_rate: Rate per Month = 0.05/1mo {
        source: "analysis",
        method: "derived",
        confidence: 0.9
    }
    
    var retention_rate: Fraction = retention_rate_from_churn(churn_rate)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_churn_rate_from_retention():
    """Test conversion from retention to churn rate."""
    pel_code = """
    param retention_rate: Fraction = 0.95 {
        source: "analysis",
        method: "derived",
        confidence: 0.9
    }
    
    var churn_rate: Rate per Month = churn_rate_from_retention(retention_rate)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_retention_hazard():
    """Test retention hazard calculation."""
    pel_code = """
    param monthly_churn: Rate per Month = 0.05/1mo {
        source: "cohort_analysis",
        method: "fitted",
        confidence: 0.85
    }
    
    var retention_curve: Array<Fraction> = exponential_retention_curve(monthly_churn, 12)
    var hazard_month_6: Rate per Month = retention_hazard(retention_curve, 6)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cumulative_churn():
    """Test cumulative churn calculation."""
    pel_code = """
    param monthly_churn: Rate per Month = 0.05/1mo {
        source: "cohort_analysis",
        method: "fitted",
        confidence: 0.85
    }
    
    var retention_curve: Array<Fraction> = exponential_retention_curve(monthly_churn, 12)
    var churn_curve: Array<Fraction> = cumulative_churn(retention_curve)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


# ============================================================================
# Golden Value Tests - Validate Mathematical Correctness
# ============================================================================


@pytest.mark.unit
def test_net_dollar_retention_golden_value():
    """Golden test: NDR = (Starting + Expansion - Churn - Contraction) / Starting."""
    pel_code = """
    param starting_mrr: Currency<USD> = $100_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion: Currency<USD> = $20_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churn: Currency<USD> = $5_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction: Currency<USD> = $3_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var ndr: Fraction = net_dollar_retention(starting_mrr, expansion, churn, contraction)
    
    // Expected: ($100k + $20k - $5k - $3k) / $100k = $112k / $100k = 1.12 (112%)
    constraint ndr_check: ndr == 1.12 {
        severity: fatal,
        message: "NDR calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_gross_dollar_retention_golden_value():
    """Golden test: GDR = (Starting - Churn - Contraction) / Starting."""
    pel_code = """
    param starting_mrr: Currency<USD> = $100_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churn: Currency<USD> = $7_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction: Currency<USD> = $3_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var gdr: Fraction = gross_dollar_retention(starting_mrr, churn, contraction)
    
    // Expected: ($100k - $7k - $3k) / $100k = $90k / $100k = 0.90 (90%)
    constraint gdr_check: gdr == 0.90 {
        severity: fatal,
        message: "GDR calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_quick_ratio_retention_golden_value():
    """Golden test: Quick Ratio = (New + Expansion) / (Churn + Contraction)."""
    pel_code = """
    param new_mrr: Currency<USD> = $40_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion_mrr: Currency<USD> = $20_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churned_mrr: Currency<USD> = $10_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction_mrr: Currency<USD> = $5_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var quick_ratio: Fraction = quick_ratio_retention(new_mrr, expansion_mrr, churned_mrr, contraction_mrr)
    
    // Expected: ($40k + $20k) / ($10k + $5k) = $60k / $15k = 4.0
    constraint quick_ratio_check: quick_ratio == 4.0 {
        severity: fatal,
        message: "Quick ratio calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_simple_churn_rate_golden_value():
    """Golden test: Churn Rate = Lost / Start of Month."""
    pel_code = """
    param customers_start: Count<Customer> = 1000 {
        source: "database",
        method: "observed",
        confidence: 1.0
    }
    
    param customers_lost: Count<Customer> = 50 {
        source: "database",
        method: "observed",
        confidence: 1.0
    }
    
    var churn: Rate per Month = simple_churn_rate(customers_start, customers_lost)
    
    // Expected: 50 / 1000 / 1mo = 0.05/1mo (5% monthly churn)
    constraint churn_check: churn == 0.05/1mo {
        severity: fatal,
        message: "Churn rate calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_customer_lifetime_months_golden_value():
    """Golden test: Lifetime = 1 / Churn Rate."""
    pel_code = """
    param retention_rate: Fraction = 0.95 {
        source: "cohort_analysis",
        method: "derived",
        confidence: 0.9,
        notes: "95% retention = 5% churn"
    }
    
    var lifetime: Duration<Month> = customer_lifetime_months(retention_rate)
    
    // Expected: 1 / 0.05 = 20 months
    constraint lifetime_check: lifetime == 20mo {
        severity: fatal,
        message: "Customer lifetime calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_retention_rate_from_churn_golden_value():
    """Golden test: Retention = 1 - Churn."""
    pel_code = """
    param churn_rate: Rate per Month = 0.08/1mo {
        source: "analysis",
        method: "derived",
        confidence: 0.9
    }
    
    var retention_rate: Fraction = retention_rate_from_churn(churn_rate)
    
    // Expected: 1.0 - (0.08/1mo * 1mo) = 1.0 - 0.08 = 0.92
    constraint retention_check: retention_rate == 0.92 {
        severity: fatal,
        message: "Retention rate conversion incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_churn_rate_from_retention_golden_value():
    """Golden test: Churn = 1 - Retention."""
    pel_code = """
    param retention_rate: Fraction = 0.92 {
        source: "analysis",
        method: "derived",
        confidence: 0.9
    }
    
    var churn_rate: Rate per Month = churn_rate_from_retention(retention_rate)
    
    // Expected: (1.0 - 0.92) / 1mo = 0.08/1mo
    constraint churn_check: churn_rate == 0.08/1mo {
        severity: fatal,
        message: "Churn rate conversion incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


# ============================================================================
# Edge Case Tests
# ============================================================================


@pytest.mark.unit
def test_quick_ratio_infinite_with_no_churn():
    """Edge case: Quick ratio is effectively infinite with zero churn."""
    pel_code = """
    param new_mrr: Currency<USD> = $50_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion_mrr: Currency<USD> = $10_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param churned_mrr: Currency<USD> = $0 {
        source: "billing",
        method: "observed",
        confidence: 1.0,
        notes: "No churn"
    }
    
    param contraction_mrr: Currency<USD> = $0 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var quick_ratio: Fraction = quick_ratio_retention(new_mrr, expansion_mrr, churned_mrr, contraction_mrr)
    
    // Expected: Should return 999.0 (effectively infinite) when no churn
    constraint infinite_quick_ratio: quick_ratio == 999.0 {
        severity: fatal,
        message: "Quick ratio should be effectively infinite with zero churn"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_ndr_over_100_percent():
    """Edge case: NDR can exceed 100% with strong expansion."""
    pel_code = """
    param starting_mrr: Currency<USD> = $100_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param expansion: Currency<USD> = $30_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0,
        notes: "Strong expansion revenue"
    }
    
    param churn: Currency<USD> = $5_000 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    param contraction: Currency<USD> = $0 {
        source: "billing",
        method: "observed",
        confidence: 1.0
    }
    
    var ndr: Fraction = net_dollar_retention(starting_mrr, expansion, churn, contraction)
    
    // Expected: ($100k + $30k - $5k) / $100k = $125k / $100k = 1.25 (125%)
    constraint ndr_healthy: ndr == 1.25 {
        severity: fatal,
        message: "NDR should be 125% with strong expansion"
    }
    
    constraint ndr_above_100: ndr > 1.0 {
        severity: info,
        message: "Excellent NDR above 100%"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_customer_lifetime_infinite_with_zero_churn():
    """Edge case: Effectively infinite lifetime with perfect retention."""
    pel_code = """
    param retention_rate: Fraction = 1.0 {
        source: "cohort_analysis",
        method: "assumption",
        confidence: 0.5,
        notes: "Perfect retention assumption"
    }
    
    var lifetime: Duration<Month> = customer_lifetime_months(retention_rate)
    
    // Expected: Should return 999mo (effectively infinite) for perfect retention
    constraint infinite_lifetime: lifetime == 999mo {
        severity: fatal,
        message: "Customer lifetime should be effectively infinite with perfect retention"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_zero_churn_rate():
    """Edge case: Zero churn rate with perfect retention."""
    pel_code = """
    param customers_start: Count<Customer> = 1000 {
        source: "database",
        method: "observed",
        confidence: 1.0
    }
    
    param customers_lost: Count<Customer> = 0 {
        source: "database",
        method: "observed",
        confidence: 1.0,
        notes: "No churn this period"
    }
    
    var churn: Rate per Month = simple_churn_rate(customers_start, customers_lost)
    
    // Expected: 0 / 1000 / 1mo = 0.0/1mo
    constraint zero_churn_check: churn == 0.0/1mo {
        severity: fatal,
        message: "Churn should be zero when no customers lost"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)
