"""Unit tests for stdlib hiring module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code


@pytest.mark.unit
def test_hiring_funnel():
    """Test hiring funnel calculation."""
    pel_code = """
    param applicants: Count<Applicant> = 200 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param screen_pass: Fraction = 0.30 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    param interview_pass: Fraction = 0.25 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    param offer_accept: Fraction = 0.70 {
        source: "recruiting",
        method: "derived",
        confidence: 0.85
    }

    var conversion_rates: Array<Fraction> = [screen_pass, interview_pass, offer_accept]
    var hires: Count<Person> = hiring_funnel(applicants, conversion_rates)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_offer_acceptance_rate():
    """Test offer acceptance rate calculation."""
    pel_code = """
    param accepted: Count<Offer> = 14 {
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
def test_hiring_velocity():
    """Test hiring velocity calculation."""
    pel_code = """
    param total_person_days: Fraction = 300.0 {
        source: "ats",
        method: "derived",
        confidence: 0.9
    }

    param num_hires: Count<Person> = 10 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    var avg_time: Duration<Day> = hiring_velocity(total_person_days, num_hires)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_cost_per_hire():
    """Test cost per hire calculation."""
    pel_code = """
    param recruiting_cost: Currency<USD> = $250000 {
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
def test_required_headcount():
    """Test required headcount calculation."""
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
def test_hiring_plan():
    """Test hiring plan calculation."""
    pel_code = """
    param current: Count<Person> = 50 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param target: Count<Person> = 100 {
        source: "business_plan",
        method: "assumption",
        confidence: 0.8
    }

    param horizon: Duration<Month> = 12mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param period: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_needed: Count<Person> = hiring_plan(current, target, horizon, period)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_attrition_replacement():
    """Test attrition replacement calculation."""
    pel_code = """
    param headcount: Count<Person> = 100 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param attrition: Rate per Year = 0.15/1yr {
        source: "hr",
        method: "derived",
        confidence: 0.85
    }

    var replacement: Count<Person> = attrition_replacement(headcount, attrition)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_growth_hiring():
    """Test growth hiring calculation."""
    pel_code = """
    param current: Count<Person> = 50 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param target: Count<Person> = 75 {
        source: "business_plan",
        method: "assumption",
        confidence: 0.75
    }

    param horizon: Duration<Month> = 6mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var growth_hires: Count<Person> = growth_hiring(current, target, horizon)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_time():
    """Test ramp time calculation."""
    pel_code = """
    param base_ramp: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param onboarding_quality: Fraction = 0.9 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    var ramp: Duration<Month> = ramp_time(base_ramp, onboarding_quality)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_ramp_curve():
    """Test ramp curve calculation."""
    pel_code = """
    param time_since_hire: Duration<Month> = 2mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param ramp_duration: Duration<Month> = 6mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    var productivity: Fraction = ramp_curve(time_since_hire, ramp_duration, "linear")
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_effective_headcount():
    """Test effective headcount with ramp."""
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

    param avg_progress: Fraction = 0.60 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    var effective: Count<Person> = effective_headcount(ramped, ramping, avg_progress)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_team_productivity():
    """Test team productivity calculation."""
    pel_code = """
    param effective: Count<Person> = 47 {
        source: "hr",
        method: "derived",
        confidence: 0.85
    }

    param productivity_per_person: Rate per Month = 8 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    var total_productivity: Rate per Month = team_productivity(effective, productivity_per_person)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_headcount_capacity():
    """Test headcount capacity calculation."""
    pel_code = """
    param headcount: Count<Person> = 50 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param capacity_per_person: Rate per Month = 20 / 1mo {
        source: "operations",
        method: "derived",
        confidence: 0.85
    }

    param utilization: Fraction = 0.80 {
        source: "policy",
        method: "assumption",
        confidence: 1.0
    }

    var total_capacity: Rate per Month = headcount_capacity(headcount, capacity_per_person, utilization)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_team_capacity():
    """Test team capacity calculation."""
    pel_code = """
    param role_a: Count<Person> = 10 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param role_b: Count<Person> = 15 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param cap_a: Rate per Month = 5 / 1mo {
        source: "ops",
        method: "derived",
        confidence: 0.85
    }

    param cap_b: Rate per Month = 7 / 1mo {
        source: "ops",
        method: "derived",
        confidence: 0.85
    }

    var heads: Array<Count<Person>> = [role_a, role_b]
    var caps: Array<Rate per Month> = [cap_a, cap_b]
    var total_capacity: Rate per Month = team_capacity(heads, caps)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_per_hire():
    """Test incremental capacity per hire calculation."""
    pel_code = """
    param capacity_per_person: Rate per Month = 10 / 1mo {
        source: "ops",
        method: "derived",
        confidence: 0.85
    }

    param ramp_time_months: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param full_productivity: Duration<Month> = 6mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    var incremental_capacity: Rate per Month = capacity_per_hire(
        capacity_per_person,
        ramp_time_months,
        full_productivity
    )
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_hiring_lag_impact():
    """Test hiring lag impact calculation."""
    pel_code = """
    param current_gap: Rate per Month = 100 / 1mo {
        source: "ops",
        method: "derived",
        confidence: 0.85
    }

    param planned_date: Duration<Month> = 2mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param actual_date: Duration<Month> = 4mo {
        source: "hr",
        method: "observed",
        confidence: 0.9
    }

    var impact: Rate per Month = hiring_lag_impact(current_gap, planned_date, actual_date)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_recruiting_cost():
    """Test recruiting cost calculation."""
    pel_code = """
    param applicants: Count<Applicant> = 1000 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param cost_per_applicant: Currency<USD> per Applicant = $50 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    param interviews: Count<Interview> = 150 {
        source: "ats",
        method: "observed",
        confidence: 1.0
    }

    param cost_per_interview: Currency<USD> per Interview = $500 {
        source: "recruiting",
        method: "derived",
        confidence: 0.85
    }

    var total_cost: Currency<USD> = recruiting_cost(applicants, cost_per_applicant, interviews, cost_per_interview)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_onboarding_cost():
    """Test onboarding cost calculation."""
    pel_code = """
    param hires: Count<Person> = 20 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param cost_per_hire: Currency<USD> per Person = $5000 {
        source: "hr",
        method: "derived",
        confidence: 0.85
    }

    var total_onboarding: Currency<USD> = onboarding_cost(hires, cost_per_hire)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_total_talent_cost():
    """Test total talent cost calculation."""
    pel_code = """
    param hires: Count<Person> = 10 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param cost_per_hire: Currency<USD> per Person = $25000 {
        source: "recruiting",
        method: "derived",
        confidence: 0.85
    }

    param annual_comp: Currency<USD> per Person = $150000 {
        source: "compensation",
        method: "assumption",
        confidence: 0.9
    }

    param period: Duration<Year> = 1yr {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var total_cost: Currency<USD> = total_talent_cost(hires, cost_per_hire, annual_comp, period)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_hire_roi():
    """Test hire ROI calculation."""
    pel_code = """
    param value_created: Currency<USD> per Person = $500000 {
        source: "finance",
        method: "derived",
        confidence: 0.7
    }

    param total_cost: Currency<USD> per Person = $175000 {
        source: "finance",
        method: "derived",
        confidence: 0.85
    }

    var roi: Fraction = hire_roi(value_created, total_cost)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
