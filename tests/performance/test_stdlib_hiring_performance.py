"""Performance tests for stdlib hiring module."""
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code_with_timing


@pytest.mark.performance
def test_hiring_funnel_performance():
    """Test hiring_funnel performance with typical usage."""
    pel_code = """
    param applicants: Count<Applicant> = 500 {
        source: "ats",
        method: "observed",
        confidence: 0.95
    }

    param screen_rate: Fraction = 0.30 {
        source: "recruiting",
        method: "derived",
        confidence: 0.90
    }

    param interview_rate: Fraction = 0.25 {
        source: "recruiting",
        method: "derived",
        confidence: 0.90
    }

    param offer_rate: Fraction = 0.70 {
        source: "recruiting",
        method: "derived",
        confidence: 0.85
    }

    var conversion_rates: Array<Fraction> = [screen_rate, interview_rate, offer_rate]
    var hires: Count<Person> = hiring_funnel(applicants, conversion_rates)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion
    assert elapsed < 0.1, f"Compilation took {elapsed:.3f}s, expected < 0.1s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_ramp_curve_performance():
    """Test ramp_curve performance with various shapes."""
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

    param linear_shape: String = "linear" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param s_curve_shape: String = "s-curve" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param exponential_shape: String = "exponential" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var linear_progress: Fraction = ramp_curve(time_since_hire, ramp_duration, linear_shape)
    var s_curve_progress: Fraction = ramp_curve(time_since_hire, ramp_duration, s_curve_shape)
    var exponential_progress: Fraction = ramp_curve(time_since_hire, ramp_duration, exponential_shape)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: high-precision exponential calculations should still be fast
    assert elapsed < 0.15, f"Compilation took {elapsed:.3f}s, expected < 0.15s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_team_capacity_large_team_performance():
    """Test team_capacity with large teams (100 roles)."""
    # Generate 100 roles
    headcount_params = "\n".join([
        f"""    param headcount_{i}: Count<Person> = {10 + i} {{
        source: "hr",
        method: "observed",
        confidence: 1.0
    }}""" for i in range(100)
    ])

    capacity_params = "\n".join([
        f"""    param capacity_{i}: Rate per Month = {5 + (i % 10)} / 1mo {{
        source: "role_{i}",
        method: "derived",
        confidence: 0.85
    }}""" for i in range(100)
    ])

    headcounts_array = "[" + ", ".join([f"headcount_{i}" for i in range(100)]) + "]"
    capacities_array = "[" + ", ".join([f"capacity_{i}" for i in range(100)]) + "]"

    pel_code = f"""
{headcount_params}

{capacity_params}

    var headcounts: Array<Count<Person>> = {headcounts_array}
    var capacities: Array<Rate per Month> = {capacities_array}
    var total_cap: Rate per Month = team_capacity(headcounts, capacities)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: even with 100 roles, should compile quickly
    assert elapsed < 0.8, f"Compilation took {elapsed:.3f}s, expected < 0.8s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_effective_headcount_performance():
    """Test effective_headcount calculations."""
    pel_code = """
    param fully_ramped: Count<Person> = 100 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param ramping: Count<Person> = 25 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param avg_progress: Fraction = 0.65 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    var effective_hc: Count<Person> = effective_headcount(fully_ramped, ramping, avg_progress)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion
    assert elapsed < 0.1, f"Compilation took {elapsed:.3f}s, expected < 0.1s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_hiring_plan_performance():
    """Test hiring_plan generation."""
    pel_code = """
    param current_hc: Count<Person> = 50 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param target_hc: Count<Person> = 100 {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param planning_horizon: Duration<Month> = 12mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    param reporting_period: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_month: Count<Person> = hiring_plan(
        current_hc,
        target_hc,
        planning_horizon,
        reporting_period
    )
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion
    assert elapsed < 0.1, f"Compilation took {elapsed:.3f}s, expected < 0.1s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_complete_hiring_workflow_performance():
    """Test complete hiring workflow from funnel to capacity."""
    pel_code = """
    // Step 1: Hiring funnel
    param applicants_per_month: Count<Applicant> = 200 {
        source: "ats",
        method: "observed",
        confidence: 0.95
    }

    param screen_pass_rate: Fraction = 0.30 {
        source: "recruiting",
        method: "derived",
        confidence: 0.90
    }

    param interview_pass_rate: Fraction = 0.25 {
        source: "recruiting",
        method: "derived",
        confidence: 0.90
    }

    param offer_acceptance: Fraction = 0.70 {
        source: "recruiting",
        method: "derived",
        confidence: 0.85
    }

    var conversion_rates: Array<Fraction> = [screen_pass_rate, interview_pass_rate, offer_acceptance]
    var hires_per_month: Count<Person> = hiring_funnel(applicants_per_month, conversion_rates)

    // Step 2: Ramp calculation
    param ramp_duration: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param time_since_hire: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    param ramp_shape: String = "s-curve" {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var productivity_level: Fraction = ramp_curve(time_since_hire, ramp_duration, ramp_shape)

    // Step 3: Effective headcount
    param current_team: Count<Person> = 50 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    param ramping_team: Count<Person> = 10 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    var effective_team: Count<Person> = effective_headcount(current_team, ramping_team, productivity_level)

    // Step 4: Team capacity
    param productivity_per_person: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    var team_prod: Rate per Month = team_productivity(current_team, productivity_per_person)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: complete workflow should compile quickly
    assert elapsed < 0.2, f"Compilation took {elapsed:.3f}s, expected < 0.2s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_cost_modeling_performance():
    """Test cost modeling functions performance."""
    pel_code = """
    param num_hires: Count<Person> = 25 {
        source: "recruiting",
        method: "derived",
        confidence: 0.9
    }

    param cost_per_hire_value: Currency<USD> per Person = $25000 {
        source: "recruiting",
        method: "derived",
        confidence: 0.85
    }

    param annual_comp: Currency<USD> per Person = $150000 {
        source: "compensation",
        method: "assumption",
        confidence: 0.9
    }

    param time_period: Duration<Year> = 1yr {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var total_cost: Currency<USD> = total_talent_cost(
        num_hires,
        cost_per_hire_value,
        annual_comp,
        time_period
    )

    param value_per_hire: Currency<USD> per Person = $500000 {
        source: "finance",
        method: "derived",
        confidence: 0.7
    }

    var roi: Fraction = hire_roi(value_per_hire, cost_per_hire_value)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion
    assert elapsed < 0.15, f"Compilation took {elapsed:.3f}s, expected < 0.15s"
    assert_compiles_successfully(ir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance"])
