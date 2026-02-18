"""Unit tests for stdlib funnel module."""
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
def test_multi_stage_funnel():
    """Test multi-stage funnel calculation."""
    pel_code = """
    param visitors: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signup_rate: Fraction = 0.08 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param activation_rate: Fraction = 0.60 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var conversion_rates: Array<Fraction> = [signup_rate, activation_rate]
    var funnel: Array<Count<User>> = multi_stage_funnel(visitors, conversion_rates)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_step_down():
    """Test funnel step-down calculation."""
    pel_code = """
    param stage_count: Count<User> = 1000 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param conversion_rate: Fraction = 0.25 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var next_stage: Count<User> = funnel_step_down(stage_count, conversion_rate)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_overall_conversion_rate():
    """Test overall conversion rate calculation."""
    pel_code = """
    param signup_rate: Fraction = 0.08 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param activation_rate: Fraction = 0.60 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param trial_rate: Fraction = 0.75 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param paid_rate: Fraction = 0.25 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var conversion_rates: Array<Fraction> = [signup_rate, activation_rate, trial_rate, paid_rate]
    var overall: Fraction = overall_conversion_rate(conversion_rates)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_stage_conversion_rate():
    """Test stage-specific conversion rate calculation."""
    pel_code = """
    param stage_i: Count<User> = 1000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param stage_i_plus_1: Count<User> = 600 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    var conversion: Fraction = stage_conversion_rate(stage_i, stage_i_plus_1)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_leakage():
    """Test funnel leakage calculation."""
    pel_code = """
    param visitors: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signups: Count<User> = 800 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param activated: Count<User> = 480 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    var stage_sizes: Array<Count<User>> = [visitors, signups, activated]
    var leakage: Array<Count<User>> = funnel_leakage(stage_sizes)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_leakage_pct():
    """Test funnel leakage percentage calculation."""
    pel_code = """
    param visitors: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signups: Count<User> = 800 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    var stage_sizes: Array<Count<User>> = [visitors, signups]
    var leakage_pct: Array<Fraction> = funnel_leakage_pct(stage_sizes)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_bottleneck_detection():
    """Test bottleneck detection."""
    pel_code = """
    param signup_rate: Fraction = 0.08 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param activation_rate: Fraction = 0.40 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param trial_rate: Fraction = 0.75 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param paid_rate: Fraction = 0.25 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var conversion_rates: Array<Fraction> = [signup_rate, activation_rate, trial_rate, paid_rate]
    var bottleneck: Count = bottleneck_detection(conversion_rates)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_velocity():
    """Test funnel velocity calculation."""
    pel_code = """
    param visit_time: Duration<Day> = 0d {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }
    
    param signup_time: Duration<Day> = 1d {
        source: "analytics",
        method: "derived",
        confidence: 0.8
    }
    
    param activation_time: Duration<Day> = 2d {
        source: "analytics",
        method: "derived",
        confidence: 0.8
    }
    
    param trial_time: Duration<Day> = 14d {
        source: "product",
        method: "assumption",
        confidence: 1.0
    }
    
    var time_in_stages: Array<Duration<Day>> = [visit_time, signup_time, activation_time, trial_time]
    var total_time: Duration<Day> = funnel_velocity(time_in_stages)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_time_in_funnel_stage():
    """Test time in funnel stage calculation."""
    pel_code = """
    param entry_count: Count<User> = 1000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param total_person_days: Fraction = 5000.0 {
        source: "analytics",
        method: "derived",
        confidence: 0.8
    }
    
    var avg_time: Duration<Day> = time_in_funnel_stage(entry_count, total_person_days)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_throughput():
    """Test funnel throughput calculation."""
    pel_code = """
    param users: Count<User> = 1000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param time_period: Duration<Day> = 30d {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }
    
    var throughput: Count<User> per Day = funnel_throughput(users, time_period)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cohort_funnel():
    """Test cohort-specific funnel calculation."""
    pel_code = """
    param cohort_size: Count<User> = 1000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signup_rate: Fraction = 0.10 {
        source: "cohort_data",
        method: "derived",
        confidence: 0.85
    }
    
    param activation_rate: Fraction = 0.65 {
        source: "cohort_data",
        method: "derived",
        confidence: 0.85
    }
    
    var conversion_rates: Array<Fraction> = [signup_rate, activation_rate]
    var funnel: Array<Count<User>> = cohort_funnel(cohort_size, conversion_rates)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_cohort_funnel_comparison():
    """Test cohort funnel comparison."""
    pel_code = """
    param a_signup: Fraction = 0.08 {
        source: "cohort_a",
        method: "derived",
        confidence: 0.85
    }
    
    param a_activation: Fraction = 0.60 {
        source: "cohort_a",
        method: "derived",
        confidence: 0.85
    }
    
    param b_signup: Fraction = 0.10 {
        source: "cohort_b",
        method: "derived",
        confidence: 0.85
    }
    
    param b_activation: Fraction = 0.65 {
        source: "cohort_b",
        method: "derived",
        confidence: 0.85
    }
    
    var cohort_a_rates: Array<Fraction> = [a_signup, a_activation]
    var cohort_b_rates: Array<Fraction> = [b_signup, b_activation]
    var delta: Array<Fraction> = cohort_funnel_comparison(cohort_a_rates, cohort_b_rates)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_saas_signup_funnel():
    """Test SaaS signup funnel archetype."""
    pel_code = """
    param visitors: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signup_rate: Fraction = 0.08 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param activation_rate: Fraction = 0.60 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param trial_rate: Fraction = 0.75 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param paid_rate: Fraction = 0.30 {
        source: "analytics",
        method: "derived",
        confidence: 0.85
    }
    
    var funnel: Array<Count<User>> = saas_signup_funnel(
        visitors,
        signup_rate,
        activation_rate,
        trial_rate,
        paid_rate
    )
    
    var paid_customers: Count<User> = funnel[4]
    
    constraint minimum_customers: paid_customers >= 100 {
        severity: warning,
        message: "Below minimum customer target"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_ecommerce_checkout_funnel():
    """Test e-commerce checkout funnel archetype."""
    pel_code = """
    param product_views: Count<User> = 50000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param cart_rate: Fraction = 0.12 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param checkout_rate: Fraction = 0.65 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param purchase_rate: Fraction = 0.75 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var funnel: Array<Count<User>> = ecommerce_checkout_funnel(
        product_views,
        cart_rate,
        checkout_rate,
        purchase_rate
    )
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_b2b_sales_funnel():
    """Test B2B sales funnel archetype."""
    pel_code = """
    param leads: Count<Contact> = 1000 {
        source: "crm",
        method: "observed",
        confidence: 1.0
    }
    
    param mql_rate: Fraction = 0.30 {
        source: "marketing",
        method: "derived",
        confidence: 0.85
    }
    
    param sql_rate: Fraction = 0.40 {
        source: "sales",
        method: "derived",
        confidence: 0.85
    }
    
    param opp_rate: Fraction = 0.50 {
        source: "sales",
        method: "derived",
        confidence: 0.85
    }
    
    param close_rate: Fraction = 0.25 {
        source: "sales",
        method: "derived",
        confidence: 0.85
    }
    
    var funnel: Array<Count<Contact>> = b2b_sales_funnel(
        leads,
        mql_rate,
        sql_rate,
        opp_rate,
        close_rate
    )
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_stage_improvement_impact():
    """Test stage improvement impact calculation."""
    pel_code = """
    param visitors: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signups: Count<User> = 800 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    var current_funnel: Array<Count<User>> = [visitors, signups]
    var stage_idx: Count = 0
    var new_rate: Fraction = 0.10
    var old_rate: Fraction = 0.08
    
    var impact: Count<User> = stage_improvement_impact(current_funnel, stage_idx, new_rate, old_rate)
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_required_conversion_rate_for_target():
    """Test required conversion rate calculation."""
    pel_code = """
    param stage_count: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param target: Count<User> = 200 {
        source: "goals",
        method: "assumption",
        confidence: 1.0
    }
    
    param downstream: Fraction = 0.36 {
        source: "analytics",
        method: "derived",
        confidence: 0.85
    }
    
    var required_rate: Fraction = required_conversion_rate_for_target(
        stage_count,
        target,
        downstream
    )
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)
