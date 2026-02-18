"""Unit tests for stdlib cashflow module."""
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
def test_days_sales_outstanding():
    """Test DSO calculation."""
    pel_code = """
    param ar_balance: Currency<USD> = $100_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param daily_revenue: Currency<USD> per Day = $5_000/1d {
        source: "sales",
        method: "observed",
        confidence: 1.0
    }
    
    var dso: Duration<Day> = days_sales_outstanding(ar_balance, daily_revenue)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_accounts_receivable():
    """Test AR balance calculation."""
    pel_code = """
    param revenue: Currency<USD> = $100_000 {
        source: "sales",
        method: "observed",
        confidence: 1.0
    }
    
    param dso: Duration<Day> = 45d {
        source: "aging_report",
        method: "derived",
        confidence: 0.9
    }
    
    param payment_terms: Duration<Day> = 30d {
        source: "policy",
        method: "assumption",
        confidence: 1.0
    }
    
    var ar: Currency<USD> = accounts_receivable(revenue, dso, payment_terms)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_burn_rate():
    """Test burn rate calculation."""
    pel_code = """
    param revenue: Currency<USD> = $50_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param expenses: Currency<USD> = $80_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    var burn: Currency<USD> per Month = burn_rate(revenue, expenses)
    
    constraint check_burn: burn < $0/1mo {
        severity: info,
        message: "Company is burning cash"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_runway_months():
    """Test runway calculation."""
    pel_code = """
    param cash: Currency<USD> = $500_000 {
        source: "bank",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_burn: Currency<USD> per Month = -$30_000/1mo {
        source: "derived",
        method: "calculated",
        confidence: 0.9
    }
    
    var runway: Duration<Month> = runway_months(cash, monthly_burn)
    
    constraint sufficient_runway: runway >= 6mo {
        severity: warning,
        message: "Runway below 6 months"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cash_waterfall():
    """Test cash waterfall calculation."""
    pel_code = """
    param opening: Currency<USD> = $1_000_000 {
        source: "bank",
        method: "observed",
        confidence: 1.0
    }
    
    param revenue_cash: Currency<USD> = $100_000 {
        source: "sales",
        method: "observed",
        confidence: 1.0
    }
    
    param collections: Currency<USD> = $50_000 {
        source: "ar",
        method: "observed",
        confidence: 1.0
    }
    
    param opex: Currency<USD> = $80_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param capex: Currency<USD> = $20_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param debt: Currency<USD> = $10_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    var ending_cash: Currency<USD> = cash_waterfall(
        opening,
        revenue_cash,
        collections,
        opex,
        capex,
        debt
    )
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cash_conversion_cycle():
    """Test CCC calculation."""
    pel_code = """
    param dso: Duration<Day> = 45d {
        source: "ar_report",
        method: "derived",
        confidence: 0.9
    }
    
    param inventory_days: Duration<Day> = 30d {
        source: "inventory_report",
        method: "derived",
        confidence: 0.9
    }
    
    param dpo: Duration<Day> = 40d {
        source: "ap_report",
        method: "derived",
        confidence: 0.9
    }
    
    var ccc: Duration<Day> = cash_conversion_cycle(dso, inventory_days, dpo)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_free_cash_flow():
    """Test FCF calculation."""
    pel_code = """
    param operating_cf: Currency<USD> = $200_000 {
        source: "cash_flow_statement",
        method: "observed",
        confidence: 1.0
    }
    
    param capex: Currency<USD> = $50_000 {
        source: "investment_schedule",
        method: "observed",
        confidence: 1.0
    }
    
    var fcf: Currency<USD> = free_cash_flow(operating_cf, capex)
    
    constraint positive_fcf: fcf >= $0 {
        severity: info,
        message: "Positive free cash flow"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_payroll_timing_semi_monthly():
    """Test semi-monthly payroll timing."""
    pel_code = """
    param monthly_payroll: Currency<USD> = $100_000 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }
    
    param month: Count = 1 {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }
    
    var payments: Array<Currency<USD>> = payroll_timing_semi_monthly(monthly_payroll, month)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)
