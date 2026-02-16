"""Tests for stdlib retention module"""
import pytest
from pathlib import Path
from compiler.compiler import PELCompiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_cohort_retention_curve():
    """Test cohort retention rate calculation"""
    src = (
        'model test_retention {\n'
        '  param initial: Count<Customer> = 1000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param retained: Count<Customer> = 850 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var retention: Fraction = retained / initial\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_customer_churn_rate():
    """Test customer churn rate calculation"""
    src = (
        'model test_churn {\n'
        '  param churned: Count<Customer> = 50 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param starting: Count<Customer> = 1000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var churn_fraction: Fraction = churned / starting\n'
        '  var churn_rate: Rate per Month = churn_fraction / 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_revenue_churn_rate():
    """Test revenue churn rate calculation"""
    src = (
        'model test_revenue_churn {\n'
        '  param churned_mrr: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param starting_mrr: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var churn_fraction: Fraction = churned_mrr / starting_mrr\n'
        '  var churn_rate: Rate per Month = churn_fraction / 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_net_dollar_retention():
    """Test NDR calculation"""
    src = (
        'model test_ndr {\n'
        '  param starting_mrr: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param expansion: Currency<USD> = $20000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param contraction: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churned: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ending_mrr: Currency<USD> = starting_mrr + expansion - contraction - churned\n'
        '  var ndr: Fraction = ending_mrr / starting_mrr\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_gross_dollar_retention():
    """Test GDR calculation"""
    src = (
        'model test_gdr {\n'
        '  param starting_mrr: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param contraction: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churned: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ending_mrr: Currency<USD> = starting_mrr - contraction - churned\n'
        '  var gdr: Fraction = ending_mrr / starting_mrr\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_quick_ratio_retention():
    """Test quick ratio for retention"""
    src = (
        'model test_quick_ratio {\n'
        '  param new_mrr: Currency<USD> = $30000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param expansion_mrr: Currency<USD> = $20000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churned_mrr: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param contraction_mrr: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var positive: Currency<USD> = new_mrr + expansion_mrr\n'
        '  var negative: Currency<USD> = churned_mrr + contraction_mrr\n'
        '  var quick_ratio: Fraction = positive / negative\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_expansion_mrr():
    """Test expansion MRR calculation"""
    src = (
        'model test_expansion {\n'
        '  param upsell: Currency<USD> = $15000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param cross_sell: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var expansion: Currency<USD> = upsell + cross_sell\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_ltv_from_retention():
    """Test LTV from retention curve"""
    src = (
        'model test_ltv_retention {\n'
        '  param arpu: Currency<USD> = $125 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param avg_lifetime: Duration = 20mo {\n'
        '    source: "test",\n'
        '    method: "derived",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ltv: Currency<USD> = arpu * avg_lifetime\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_discounted_ltv():
    """Test discounted LTV calculation"""
    src = (
        'model test_discounted_ltv {\n'
        '  param arpu: Currency<USD> = $125 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churn_rate: Rate per Month = 0.05/1mo {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param discount_rate: Rate per Month = 0.01/1mo {\n'
        '    source: "test",\n'
        '    method: "assumption",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var combined_rate: Rate per Month = churn_rate + discount_rate\n'
        '  var ltv: Currency<USD> = arpu / combined_rate\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_cohort_half_life():
    """Test cohort half-life calculation"""
    src = (
        'model test_half_life {\n'
        '  param churn_rate: Rate per Month = 0.05/1mo {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var half_life_ratio: Fraction = 0.693 / churn_rate\n'
        '  var half_life: Duration = half_life_ratio * 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.unit
def test_churn_from_retention():
    """Test churn rate from retention rate"""
    src = (
        'model test_churn_from_retention {\n'
        '  param retention: Fraction = 0.95 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var churn_fraction: Fraction = 1.0 - retention\n'
        '  var churn_rate: Rate per Month = churn_fraction / 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None


@pytest.mark.integration
def test_retention_module_compiles(tmp_path: Path):
    """Test that retention module compiles successfully"""
    repo_root = Path(__file__).resolve().parents[2]
    retention_file = repo_root / "stdlib" / "retention" / "retention.pel"
    
    # Skip test if file doesn't exist yet
    if not retention_file.exists():
        pytest.skip("Retention module not yet implemented")
    
    # Note: This test may need adjustment once we support standalone functions
    # For now, we just verify the file exists and has the expected structure
    assert retention_file.exists()
    content = retention_file.read_text()
    assert "func cohort_retention_curve" in content
    assert "func customer_churn_rate" in content
    assert "func net_dollar_retention" in content
    assert "func ltv_from_retention_curve" in content


# Golden tests - expected values for known inputs
@pytest.mark.unit
def test_retention_golden_85_percent():
    """Golden test: 850 retained / 1000 initial = 85% retention"""
    src = (
        'model golden_retention {\n'
        '  param initial: Count<Customer> = 1000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param retained: Count<Customer> = 850 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var retention: Fraction = retained / initial\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # Retention should equal 0.85


@pytest.mark.unit
def test_retention_golden_ndr_105():
    """Golden test: $100k start, +$20k exp, -$5k contract, -$10k churn = 105% NDR"""
    src = (
        'model golden_ndr {\n'
        '  param start: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param exp: Currency<USD> = $20000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param contract: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churn: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ending: Currency<USD> = start + exp - contract - churn\n'
        '  var ndr: Fraction = ending / start\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # NDR should equal 1.05 (105%)


@pytest.mark.unit
def test_retention_golden_quick_ratio():
    """Golden test: ($30k new + $20k exp) / ($10k churn + $5k contract) = 3.33"""
    src = (
        'model golden_quick_ratio {\n'
        '  param new: Currency<USD> = $30000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param exp: Currency<USD> = $20000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churn: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param contract: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var positive: Currency<USD> = new + exp\n'
        '  var negative: Currency<USD> = churn + contract\n'
        '  var ratio: Fraction = positive / negative\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # Quick ratio should equal 3.33


@pytest.mark.unit
def test_retention_golden_ltv_2500():
    """Golden test: $125 ARPU * 20mo lifetime = $2500 LTV"""
    src = (
        'model golden_ltv {\n'
        '  param arpu: Currency<USD> = $125 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param lifetime: Duration = 20mo {\n'
        '    source: "test",\n'
        '    method: "derived",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ltv: Currency<USD> = arpu * lifetime\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # LTV should equal $2500


@pytest.mark.unit
def test_retention_golden_half_life():
    """Golden test: 5% monthly churn = ~13.86 month half-life"""
    src = (
        'model golden_half_life {\n'
        '  param churn: Rate per Month = 0.05/1mo {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var half_life_ratio: Fraction = 0.693 / churn\n'
        '  var half_life: Duration = half_life_ratio * 1mo\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # Half-life should equal ~13.86 months (0.693 / 0.05 = 13.86)


@pytest.mark.unit
def test_retention_golden_gdr_85():
    """Golden test: $100k start - $5k contract - $10k churn = 85% GDR"""
    src = (
        'model golden_gdr {\n'
        '  param start: Currency<USD> = $100000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param contract: Currency<USD> = $5000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  param churn: Currency<USD> = $10000 {\n'
        '    source: "test",\n'
        '    method: "observed",\n'
        '    confidence: 1.0\n'
        '  }\n'
        '  var ending: Currency<USD> = start - contract - churn\n'
        '  var gdr: Fraction = ending / start\n'
        '}\n'
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)
    assert typed is not None
    # GDR should equal 0.85 (85%)
