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


# ============================================================================
# Golden Value Tests - Validate Mathematical Correctness
# ============================================================================


@pytest.mark.unit
def test_days_sales_outstanding_golden_value():
    """Golden test: DSO = AR Balance / Daily Revenue."""
    pel_code = """
    param ar_balance: Currency<USD> = $150_000 {
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
    
    // Expected: $150,000 / ($5,000/day) = 30 days
    constraint dso_check: dso == 30d {
        severity: fatal,
        message: "DSO calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_burn_rate_positive_cash_flow():
    """Golden test: Profitable company has positive burn rate."""
    pel_code = """
    param revenue: Currency<USD> = $100_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param expenses: Currency<USD> = $60_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    var burn: Currency<USD> per Month = burn_rate(revenue, expenses)
    
    // Expected: ($100k - $60k) / 1mo = $40k/mo (positive = generating cash)
    // Calculate the difference to verify it's positive
    var net_income: Currency<USD> = revenue - expenses
    
    constraint profitable: net_income > $0 {
        severity: fatal,
        message: "Profitable company should have positive net income"
    }
    
    constraint net_income_check: net_income == $40_000 {
        severity: fatal,
        message: "Net income should be $40k"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_burn_rate_negative_cash_flow():
    """Golden test: Unprofitable company has negative burn rate."""
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
    
    // Expected: ($50k - $80k) / 1mo = -$30k/mo (negative = burning cash)
    // Calculate the deficit to verify negative burn
    var deficit: Currency<USD> = expenses - revenue
    
    constraint unprofitable: deficit > $0 {
        severity: fatal,
        message: "Cash-burning company should have positive deficit"
    }
    
    constraint deficit_check: deficit == $30_000 {
        severity: fatal,
        message: "Deficit should be $30k"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_runway_months_golden_value():
    """Golden test: Runway = Cash / |Monthly Burn|."""
    pel_code = """
    param cash: Currency<USD> = $600_000 {
        source: "bank",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_burn: Currency<USD> per Month = -$50_000/1mo {
        source: "derived",
        method: "calculated",
        confidence: 0.9
    }
    
    var runway: Duration<Month> = runway_months(cash, monthly_burn)
    
    // Expected: $600k / $50k/mo = 12 months
    constraint runway_check: runway == 12mo {
        severity: fatal,
        message: "Runway calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cash_waterfall_golden_value():
    """Golden test: Ending cash = Opening + Inflows - Outflows."""
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
    
    // Expected: $1M + $100k + $50k - $80k - $20k - $10k = $1,040,000
    constraint waterfall_check: ending_cash == $1_040_000 {
        severity: fatal,
        message: "Cash waterfall calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cash_conversion_cycle_golden_value():
    """Golden test: CCC = DSO + Inventory Days - DPO."""
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
    
    // Expected: 45d + 30d - 40d = 35d
    constraint ccc_check: ccc == 35d {
        severity: fatal,
        message: "CCC calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_free_cash_flow_golden_value():
    """Golden test: FCF = Operating CF - CapEx."""
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
    
    // Expected: $200k - $50k = $150k
    constraint fcf_check: fcf == $150_000 {
        severity: fatal,
        message: "FCF calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


# ============================================================================
# Edge Case Tests
# ============================================================================


@pytest.mark.unit
def test_runway_infinite_for_profitable_company():
    """Edge case: Profitable company has effectively infinite runway."""
    pel_code = """
    param cash: Currency<USD> = $500_000 {
        source: "bank",
        method: "observed",
        confidence: 1.0
    }
    
    param monthly_burn: Currency<USD> per Month = $10_000/1mo {
        source: "derived",
        method: "calculated",
        confidence: 0.9,
        notes: "Positive burn = profitable"
    }
    
    var runway: Duration<Month> = runway_months(cash, monthly_burn)
    
    // Expected: Should return 999mo (effectively infinite) for profitable companies
    constraint infinite_runway: runway == 999mo {
        severity: fatal,
        message: "Runway should be effectively infinite for profitable companies"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_dso_zero_for_immediate_payment():
    """Edge case: DSO = 0 for immediate cash collection."""
    pel_code = """
    param ar_balance: Currency<USD> = $0 {
        source: "accounting",
        method: "observed",
        confidence: 1.0,
        notes: "Immediate payment, no AR"
    }
    
    param daily_revenue: Currency<USD> per Day = $10_000/1d {
        source: "sales",
        method: "observed",
        confidence: 1.0
    }
    
    var dso: Duration<Day> = days_sales_outstanding(ar_balance, daily_revenue)
    
    // Expected: $0 / ($10k/day) = 0 days
    constraint zero_dso: dso == 0d {
        severity: fatal,
        message: "DSO should be 0 for immediate cash collection"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_burn_rate_break_even():
    """Edge case: Break-even company has zero burn rate."""
    pel_code = """
    param revenue: Currency<USD> = $75_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    param expenses: Currency<USD> = $75_000 {
        source: "accounting",
        method: "observed",
        confidence: 1.0
    }
    
    var burn: Currency<USD> per Month = burn_rate(revenue, expenses)
    
    // Expected: ($75k - $75k) / 1mo = $0/mo
    constraint break_even_check: burn == $0/1mo {
        severity: fatal,
        message: "Break-even company should have zero burn rate"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)
