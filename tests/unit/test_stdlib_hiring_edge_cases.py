"""Edge case tests for stdlib hiring module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code

# =============================================================================
# Division by Zero Edge Cases
# =============================================================================

@pytest.mark.unit
def test_offer_acceptance_rate_zero_offers():
    """Test offer acceptance rate with zero offers extended."""
    pel_code = """
    param accepted: Count<Offer> = 5 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param extended: Count<Offer> = 0 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    var acceptance_rate: Fraction = offer_acceptance_rate(accepted, extended)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_cost_per_hire_zero_hires():
    """Test cost per hire with zero hires."""
    pel_code = """
    param recruiting_cost: Currency<USD> = $250000 {
        source: "finance",
        method: "observed",
        confidence: 1.0
    }

    param num_hires: Count<Person> = 0 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    var cost: Currency<USD> per Person = cost_per_hire(recruiting_cost, num_hires)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_required_headcount_zero_productivity():
    """Test required headcount with zero productivity per person."""
    pel_code = """
    param target: Rate per Month = 40 / 1mo {
        source: "product_roadmap",
        method: "assumption",
        confidence: 0.7
    }

    param productivity: Rate per Month = 0 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    param ramp_factor: Fraction = 0.85 {
        source: "hr",
        method: "derived",
        confidence: 0.75
    }

    var headcount: Count<Person> = required_headcount(target, productivity, ramp_factor)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_required_headcount_zero_ramp_factor():
    """Test required headcount with zero ramp factor."""
    pel_code = """
    param target: Rate per Month = 40 / 1mo {
        source: "product_roadmap",
        method: "assumption",
        confidence: 0.7
    }

    param productivity: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    param ramp_factor: Fraction = 0.0 {
        source: "hr",
        method: "derived",
        confidence: 0.75
    }

    var headcount: Count<Person> = required_headcount(target, productivity, ramp_factor)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_hiring_plan_zero_period():
    """Test hiring plan with zero period."""
    pel_code = """
    param current: Count<Person> = 50 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    param target: Count<Person> = 100 {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param horizon: Duration<Month> = 12mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    param period: Duration<Month> = 0mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_period: Count<Person> = hiring_plan(current, target, horizon, period)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_growth_hiring_zero_time_horizon():
    """Test growth hiring with zero time horizon."""
    pel_code = """
    param current: Count<Person> = 50 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    param target: Count<Person> = 100 {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param horizon: Duration<Month> = 0mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_month: Count<Person> = growth_hiring(current, target, horizon)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_time_zero_onboarding_quality():
    """Test ramp time with zero onboarding quality."""
    pel_code = """
    param base_time: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param quality: Fraction = 0.0 {
        source: "hr",
        method: "derived",
        confidence: 0.7
    }

    var ramp: Duration<Month> = ramp_time(base_time, quality)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_per_hire_zero_full_productivity_time():
    """Test capacity per hire with zero full productivity time."""
    pel_code = """
    param capacity: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    param ramp: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param full_time: Duration<Month> = 0mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var cap_per_hire: Rate per Month = capacity_per_hire(capacity, ramp, full_time)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_hire_roi_zero_cost():
    """Test hire ROI with zero cost per hire."""
    pel_code = """
    param value: Currency<USD> per Person = $500000 {
        source: "finance",
        method: "derived",
        confidence: 0.8
    }

    param cost: Currency<USD> per Person = $0 {
        source: "recruiting",
        method: "observed",
        confidence: 0.9
    }

    var roi: Fraction = hire_roi(value, cost)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Negative Value Edge Cases
# =============================================================================

@pytest.mark.unit
def test_hiring_funnel_negative_applicants():
    """Test hiring funnel with negative applicants."""
    pel_code = """
    param applicants: Count<Applicant> = -100 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param screen_pass: Fraction = 0.30 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    var conversion_rates: Array<Fraction> = [screen_pass]
    var hires: Count<Person> = hiring_funnel(applicants, conversion_rates)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_offer_acceptance_rate_negative_accepted():
    """Test offer acceptance rate with negative accepted offers."""
    pel_code = """
    param accepted: Count<Offer> = -5 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param extended: Count<Offer> = 20 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    var acceptance_rate: Fraction = offer_acceptance_rate(accepted, extended)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_cost_per_hire_negative_cost():
    """Test cost per hire with negative recruiting cost."""
    pel_code = """
    param recruiting_cost: Currency<USD> = -$50000 {
        source: "finance",
        method: "observed",
        confidence: 1.0
    }

    param num_hires: Count<Person> = 10 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    var cost: Currency<USD> per Person = cost_per_hire(recruiting_cost, num_hires)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_time_negative_base():
    """Test ramp time with negative base time."""
    pel_code = """
    param base_time: Duration<Month> = -3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param quality: Fraction = 1.0 {
        source: "hr",
        method: "derived",
        confidence: 0.7
    }

    var ramp: Duration<Month> = ramp_time(base_time, quality)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Boundary Value Tests - Ramp Curve
# =============================================================================

@pytest.mark.unit
def test_ramp_curve_zero_duration():
    """Test ramp curve with zero ramp duration."""
    pel_code = """
    param time: Duration<Month> = 1mo {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param duration: Duration<Month> = 0mo {
        source: "hr",
        method: "assumption",
        confidence: 1.0
    }

    param shape: String = "linear" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var productivity: Fraction = ramp_curve(time, duration, shape)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_curve_negative_time():
    """Test ramp curve with negative time since hire."""
    pel_code = """
    param time: Duration<Month> = -1mo {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param duration: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 1.0
    }

    param shape: String = "linear" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var productivity: Fraction = ramp_curve(time, duration, shape)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_curve_invalid_shape():
    """Test ramp curve with invalid shape string."""
    pel_code = """
    param time: Duration<Month> = 1mo {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param duration: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 1.0
    }

    param shape: String = "invalid_curve_xyz" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var productivity: Fraction = ramp_curve(time, duration, shape)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_curve_all_shapes():
    """Test ramp curve with all valid shape options."""
    pel_code = """
    param time: Duration<Month> = 1mo {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param duration: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 1.0
    }

    param linear: String = "linear" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param exponential: String = "exponential" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param s_curve: String = "s-curve" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var prod_linear: Fraction = ramp_curve(time, duration, linear)
    var prod_exp: Fraction = ramp_curve(time, duration, exponential)
    var prod_s: Fraction = ramp_curve(time, duration, s_curve)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Effective Headcount Edge Cases
# =============================================================================

@pytest.mark.unit
def test_effective_headcount_negative_values():
    """Test effective headcount with negative inputs."""
    pel_code = """
    param ramped: Count<Person> = -10 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param ramping: Count<Person> = -5 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param progress: Fraction = 0.5 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    var effective: Count<Person> = effective_headcount(ramped, ramping, progress)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_effective_headcount_progress_over_one():
    """Test effective headcount with progress > 1.0."""
    pel_code = """
    param ramped: Count<Person> = 45 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param ramping: Count<Person> = 5 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param progress: Fraction = 1.5 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    var effective: Count<Person> = effective_headcount(ramped, ramping, progress)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_effective_headcount_negative_progress():
    """Test effective headcount with negative progress."""
    pel_code = """
    param ramped: Count<Person> = 45 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param ramping: Count<Person> = 5 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param progress: Fraction = -0.5 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    var effective: Count<Person> = effective_headcount(ramped, ramping, progress)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Team Capacity Edge Cases
# =============================================================================

@pytest.mark.unit
def test_team_capacity_single_zero_element():
    """Test team capacity with single zero-value element arrays."""
    pel_code = """
    var empty_headcounts: Array<Count<Person>> = [0]
    var empty_capacities: Array<Rate per Month> = [0 / 1mo]
    var total_cap: Rate per Month = team_capacity(empty_headcounts, empty_capacities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_team_capacity_mismatched_lengths():
    """Test team capacity with mismatched array lengths."""
    pel_code = """
    param eng_count: Count<Person> = 10 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param sales_count: Count<Person> = 5 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param eng_cap: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    var headcounts: Array<Count<Person>> = [eng_count, sales_count]
    var capacities: Array<Rate per Month> = [eng_cap]
    var total_cap: Rate per Month = team_capacity(headcounts, capacities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Conversion Rate Edge Cases
# =============================================================================

@pytest.mark.unit
def test_hiring_funnel_conversion_rates_over_one():
    """Test hiring funnel with conversion rates > 1.0."""
    pel_code = """
    param applicants: Count<Applicant> = 100 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param invalid_rate: Fraction = 1.5 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    var conversion_rates: Array<Fraction> = [invalid_rate]
    var hires: Count<Person> = hiring_funnel(applicants, conversion_rates)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_hiring_funnel_negative_conversion_rates():
    """Test hiring funnel with negative conversion rates."""
    pel_code = """
    param applicants: Count<Applicant> = 100 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param invalid_rate: Fraction = -0.3 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    var conversion_rates: Array<Fraction> = [invalid_rate]
    var hires: Count<Person> = hiring_funnel(applicants, conversion_rates)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Already at Target Edge Cases
# =============================================================================

@pytest.mark.unit
def test_hiring_plan_already_at_target():
    """Test hiring plan when already at target headcount."""
    pel_code = """
    param current: Count<Person> = 100 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    param target: Count<Person> = 100 {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param horizon: Duration<Month> = 12mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    param period: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_period: Count<Person> = hiring_plan(current, target, horizon, period)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_hiring_plan_above_target():
    """Test hiring plan when above target headcount."""
    pel_code = """
    param current: Count<Person> = 120 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    param target: Count<Person> = 100 {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param horizon: Duration<Month> = 12mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    param period: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_period: Count<Person> = hiring_plan(current, target, horizon, period)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
