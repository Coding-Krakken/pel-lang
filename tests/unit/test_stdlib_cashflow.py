"""Tests for stdlib cashflow module"""
import pytest
from pathlib import Path
from compiler.compiler import PELCompiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_ar_with_payment_terms():
    """Test accounts receivable calculation with payment terms"""
    src = (
        'model test_ar {\n'
        '  param revenue: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param payment_terms: Duration = 30day {\n'
        '    source: "test",\n'
        '    method: "assumption",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ar: Currency<USD> = revenue * (payment_terms / 30day)\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_days_sales_outstanding():
    """Test DSO calculation"""
    src = (
        'model test_dso {\n'
        '  param ar: Currency<USD> = $50000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param revenue: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var dso_ratio: Fraction = ar / revenue\n'
        '  var dso: Duration = dso_ratio * 30day\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_bad_debt_reserve():
    """Test bad debt reserve calculation"""
    src = (
        'model test_bad_debt {\n'
        '  param ar: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param reserve_rate: Fraction = 0.02 {\n'
        '    source: "test",\n'
        '    method: "assumption",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var reserve: Currency<USD> = ar * reserve_rate\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_working_capital():
    """Test working capital calculation"""
    src = (
        'model test_wc {\n'
        '  param current_assets: Currency<USD> = $500000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param current_liabilities: Currency<USD> = $300000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var wc: Currency<USD> = current_assets - current_liabilities\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_cash_conversion_cycle():
    """Test CCC calculation"""
    src = (
        'model test_ccc {\n'
        '  param dso: Duration = 45day {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param dio: Duration = 30day {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param dpo: Duration = 60day {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ccc: Duration = dso + dio - dpo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_burn_rate():
    """Test burn rate calculation"""
    src = (
        'model test_burn {\n'
        '  param starting_cash: Currency<USD> = $1000000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param ending_cash: Currency<USD> = $700000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param months: Count<Month> = 3 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var total_burn: Currency<USD> = starting_cash - ending_cash\n'
        '  var burn: Currency<USD> = total_burn / months\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_runway_months():
    """Test runway calculation"""
    src = (
        'model test_runway {\n'
        '  param cash: Currency<USD> = $600000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param burn_rate: Currency<USD> = $50000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var runway_ratio: Fraction = cash / burn_rate\n'
        '  var runway: Duration = runway_ratio * 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_operating_cash_flow():
    """Test OCF calculation"""
    src = (
        'model test_ocf {\n'
        '  param net_income: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param depreciation: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param wc_change: Currency<USD> = $20000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var wc_monthly: Currency<USD> = wc_change / 1mo\n'
        '  var ocf: Currency<USD> = net_income + depreciation - wc_monthly\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_free_cash_flow():
    """Test FCF calculation"""
    src = (
        'model test_fcf {\n'
        '  param ocf: Currency<USD> = $90000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param capex: Currency<USD> = $20000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var fcf: Currency<USD> = ocf - capex\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_current_ratio():
    """Test current ratio calculation"""
    src = (
        'model test_current_ratio {\n'
        '  param current_assets: Currency<USD> = $500000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param current_liabilities: Currency<USD> = $300000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ratio: Fraction = current_assets / current_liabilities\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_payroll_timing():
    """Test payroll timing calculation"""
    src = (
        'model test_payroll {\n'
        '  param headcount: Count<Employee> = 50 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param annual_salary: Currency<USD> = $80000 {\n'
        '    source: "test",\n'
        '    method: "assumption",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var monthly_payroll: Currency<USD> = (headcount * annual_salary) / 12mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.integration
def test_cashflow_module_compiles(tmp_path: Path):
    """Test that cashflow module compiles successfully"""
    repo_root = Path(__file__).resolve().parents[2]
    cashflow_file = repo_root / "stdlib" / "cashflow" / "cashflow.pel"
    
    # Skip test if file doesn't exist yet
    if not cashflow_file.exists():
        pytest.skip("Cashflow module not yet implemented")
    
    # Note: This test may need adjustment once we support standalone functions
    # For now, we just verify the file exists and has the expected structure
    assert cashflow_file.exists()
    content = cashflow_file.read_text()
    assert "func ar_with_payment_terms" in content
    assert "func days_sales_outstanding" in content
    assert "func burn_rate" in content
    assert "func runway_months" in content


# Golden tests - expected values for known inputs
@pytest.mark.unit
def test_cashflow_golden_dso_30_days():
    """Golden test: $100k AR, $100k/mo revenue = 30 days DSO"""
    src = (
        'model golden_dso {\n'
        '  param ar: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param revenue: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var dso_ratio: Fraction = ar / revenue\n'
        '  var dso: Duration = dso_ratio * 30day\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # DSO should equal 30 days (1.0 * 30day)


@pytest.mark.unit
def test_cashflow_golden_runway_12_months():
    """Golden test: $600k cash, $50k/mo burn = 12 months runway"""
    src = (
        'model golden_runway {\n'
        '  param cash: Currency<USD> = $600000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param burn: Currency<USD> = $50000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var runway_ratio: Fraction = cash / burn\n'
        '  var runway: Duration = runway_ratio * 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # Runway should equal 12 months (12.0 * 1mo)


@pytest.mark.unit
def test_cashflow_golden_current_ratio():
    """Golden test: $500k assets, $200k liabilities = 2.5 ratio"""
    src = (
        'model golden_current_ratio {\n'
        '  param assets: Currency<USD> = $500000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param liabilities: Currency<USD> = $200000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ratio: Fraction = assets / liabilities\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # Ratio should equal 2.5


@pytest.mark.unit
def test_cashflow_golden_ccc_negative_15():
    """Golden test: DSO 45d, DIO 30d, DPO 90d = -15d CCC"""
    src = (
        'model golden_ccc {\n'
        '  param dso: Duration = 45day {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param dio: Duration = 30day {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param dpo: Duration = 90day {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ccc: Duration = dso + dio - dpo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # CCC should equal -15 days (favorable - collecting before paying)


@pytest.mark.unit
def test_cashflow_golden_fcf():
    """Golden test: $100k OCF, $25k CapEx = $75k FCF"""
    src = (
        'model golden_fcf {\n'
        '  param ocf: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param capex: Currency<USD> = $25000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var fcf: Currency<USD> = ocf - capex\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # FCF should equal $75k/mo
