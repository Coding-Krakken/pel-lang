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
