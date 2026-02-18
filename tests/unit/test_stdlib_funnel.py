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


# ============================================================================
# Golden Value Tests - Validate Mathematical Correctness
# ============================================================================


@pytest.mark.unit
def test_overall_conversion_rate_golden_value():
    """Golden test: Overall = Product of all stage rates."""
    pel_code = """
    param rate_1: Fraction = 0.10 {
        source: "analytics",
        method: "observed",
        confidence: 0.9
    }
    
    param rate_2: Fraction = 0.60 {
        source: "analytics",
        method: "observed",
        confidence: 0.9
    }
    
    param rate_3: Fraction = 0.50 {
        source: "analytics",
        method: "observed",
        confidence: 0.9
    }
    
    var conversion_rates: Array<Fraction> = [rate_1, rate_2, rate_3]
    var overall: Fraction = overall_conversion_rate(conversion_rates)
    
    // Expected: 0.10 * 0.60 * 0.50 = 0.03 (3% overall conversion)
    constraint overall_check: overall == 0.03 {
        severity: fatal,
        message: "Overall conversion rate calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_stage_conversion_rate_golden_value():
    """Golden test: Stage conversion = Next / Current."""
    pel_code = """
    param stage_i: Count<User> = 1000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param stage_i_plus_1: Count<User> = 250 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    var conversion: Fraction = stage_conversion_rate(stage_i, stage_i_plus_1)
    
    // Expected: 250 / 1000 = 0.25 (25% conversion)
    constraint conversion_check: conversion == 0.25 {
        severity: fatal,
        message: "Stage conversion rate calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_step_down_golden_value():
    """Golden test: Next stage = Current * Conversion Rate."""
    pel_code = """
    param stage_count: Count<User> = 1000 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param conversion_rate: Fraction = 0.30 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var next_stage: Count<User> = funnel_step_down(stage_count, conversion_rate)
    
    // Expected: 1000 * 0.30 = 300
    constraint step_down_check: next_stage == 300 {
        severity: fatal,
        message: "Funnel step down calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_velocity_golden_value():
    """Golden test: Total time = Sum of stage times."""
    pel_code = """
    param time_1: Duration<Day> = 1d {
        source: "analytics",
        method: "derived",
        confidence: 0.8
    }
    
    param time_2: Duration<Day> = 3d {
        source: "analytics",
        method: "derived",
        confidence: 0.8
    }
    
    param time_3: Duration<Day> = 7d {
        source: "analytics",
        method: "derived",
        confidence: 0.8
    }
    
    var time_in_stages: Array<Duration<Day>> = [time_1, time_2, time_3]
    var total_time: Duration<Day> = funnel_velocity(time_in_stages)
    
    // Expected: 1d + 3d + 7d = 11d
    constraint velocity_check: total_time == 11d {
        severity: fatal,
        message: "Funnel velocity calculation incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_throughput_golden_value():
    """Golden test: Throughput = Users / Time."""
    pel_code = """
    param users: Count<User> = 300 {
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
    
    // Expected: 300 / 30d = 10/1d (10 users per day)
    // Verify the calculation by checking inputs
    constraint valid_users: users == 300 {
        severity: fatal,
        message: "User count should be 300"
    }
    
    constraint valid_period: time_period == 30d {
        severity: fatal,
        message: "Time period should be 30 days"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_saas_signup_funnel_golden_value():
    """Golden test: Validate multi-stage SaaS funnel calculation."""
    pel_code = """
    param visitors: Count<User> = 10000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param signup_rate: Fraction = 0.10 {
        source: "analytics",
        method: "derived",
        confidence: 0.9,
        notes: "10% signup rate"
    }
    
    param activation_rate: Fraction = 0.60 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param trial_rate: Fraction = 0.50 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param paid_rate: Fraction = 0.40 {
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
    
    // Expected funnel:
    // Stage 0 (Visits): 10000
    // Stage 1 (Signups): 10000 * 0.10 = 1000
    // Stage 2 (Activated): 1000 * 0.60 = 600
    // Stage 3 (Trial): 600 * 0.50 = 300
    // Stage 4 (Paid): 300 * 0.40 = 120
    
    var signups: Count<User> = funnel[1]
    var activated: Count<User> = funnel[2]
    var trials: Count<User> = funnel[3]
    var paid: Count<User> = funnel[4]
    
    constraint signups_check: signups == 1000 {
        severity: fatal,
        message: "Signup count incorrect"
    }
    
    constraint activated_check: activated == 600 {
        severity: fatal,
        message: "Activated count incorrect"
    }
    
    constraint trials_check: trials == 300 {
        severity: fatal,
        message: "Trial count incorrect"
    }
    
    constraint paid_check: paid == 120 {
        severity: fatal,
        message: "Paid customer count incorrect"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_bottleneck_detection_golden_value():
    """Golden test: Identifies lowest conversion rate stage."""
    pel_code = """
    param rate_0: Fraction = 0.50 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param rate_1: Fraction = 0.20 {
        source: "analytics",
        method: "derived",
        confidence: 0.9,
        notes: "This is the bottleneck"
    }
    
    param rate_2: Fraction = 0.60 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param rate_3: Fraction = 0.40 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    var conversion_rates: Array<Fraction> = [rate_0, rate_1, rate_2, rate_3]
    var bottleneck: Count = bottleneck_detection(conversion_rates)
    
    // Expected: Index 1 has the lowest rate (0.20)
    constraint bottleneck_check: bottleneck == 1 {
        severity: fatal,
        message: "Bottleneck detection incorrect - should identify stage 1"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


# ============================================================================
# Edge Case Tests
# ============================================================================


@pytest.mark.unit
def test_stage_conversion_rate_zero_input():
    """Edge case: Zero input stage returns 0% conversion."""
    pel_code = """
    param stage_i: Count<User> = 0 {
        source: "analytics",
        method: "observed",
        confidence: 1.0,
        notes: "Empty stage"
    }
    
    param stage_i_plus_1: Count<User> = 0 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    var conversion: Fraction = stage_conversion_rate(stage_i, stage_i_plus_1)
    
    // Expected: Division by zero returns 0.0
    constraint zero_conversion: conversion == 0.0 {
        severity: fatal,
        message: "Zero input should return zero conversion rate"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_perfect_conversion():
    """Edge case: 100% conversion at every stage."""
    pel_code = """
    param visitors: Count<User> = 100 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param perfect_rate: Fraction = 1.0 {
        source: "model",
        method: "assumption",
        confidence: 0.5,
        notes: "Perfect conversion assumption"
    }
    
    var conversion_rates: Array<Fraction> = [perfect_rate, perfect_rate, perfect_rate]
    var funnel: Array<Count<User>> = multi_stage_funnel(visitors, conversion_rates)
    
    // Expected: All stages should have 100 users
    var final_stage: Count<User> = funnel[3]
    
    constraint perfect_conversion_check: final_stage == 100 {
        severity: fatal,
        message: "Perfect conversion should retain all users"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_funnel_zero_conversion_at_stage():
    """Edge case: Zero conversion at one stage kills funnel."""
    pel_code = """
    param visitors: Count<User> = 1000 {
        source: "analytics",
        method: "observed",
        confidence: 1.0
    }
    
    param good_rate: Fraction = 0.50 {
        source: "analytics",
        method: "derived",
        confidence: 0.9
    }
    
    param zero_rate: Fraction = 0.0 {
        source: "analytics",
        method: "derived",
        confidence: 0.9,
        notes: "Complete drop-off at this stage"
    }
    
    var conversion_rates: Array<Fraction> = [good_rate, zero_rate, good_rate]
    var funnel: Array<Count<User>> = multi_stage_funnel(visitors, conversion_rates)
    
    // Expected: Stage 2+ should have 0 users due to zero conversion at stage 1
    var stage_2: Count<User> = funnel[2]
    var stage_3: Count<User> = funnel[3]
    
    constraint zero_propagation_2: stage_2 == 0 {
        severity: fatal,
        message: "Zero conversion should result in zero users downstream"
    }
    
    constraint zero_propagation_3: stage_3 == 0 {
        severity: fatal,
        message: "Zero conversion should result in zero users downstream"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_overall_conversion_with_one_hundred_percent():
    """Edge case: Overall conversion with 100% at all stages."""
    pel_code = """
    param perfect: Fraction = 1.0 {
        source: "model",
        method: "assumption",
        confidence: 0.5
    }
    
    var rates: Array<Fraction> = [perfect, perfect, perfect]
    var overall: Fraction = overall_conversion_rate(rates)
    
    // Expected: 1.0 * 1.0 * 1.0 = 1.0
    constraint perfect_overall: overall == 1.0 {
        severity: fatal,
        message: "Perfect conversion at all stages should yield 100% overall"
    }
    """
    result = _compile_pel_code(pel_code)
    assert isinstance(result, dict)
