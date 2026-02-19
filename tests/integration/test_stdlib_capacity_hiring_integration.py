"""Integration tests for stdlib capacity and hiring modules."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code

# =============================================================================
# Capacity Module Integration Tests
# =============================================================================

@pytest.mark.integration
def test_complete_capacity_planning_workflow():
    """Test complete capacity planning workflow from utilization to scaling."""
    pel_code = """
    // Current state
    param current_capacity: Rate per Month = 1000 / 1mo {
        source: "infrastructure",
        method: "observed",
        confidence: 1.0
    }

    param current_demand: Rate per Month = 900 / 1mo {
        source: "monitoring",
        method: "observed",
        confidence: 0.95
    }

    param efficiency: Fraction = 0.85 {
        source: "operations",
        method: "derived",
        confidence: 0.85
    }

    // Step 1: Calculate current utilization
    var utilization: Fraction = calculate_utilization(current_demand, current_capacity)

    // Step 2: Calculate effective capacity
    var effective: Rate per Month = effective_capacity(current_capacity, efficiency)

    // Step 3: Identify capacity gap
    var gap: Rate per Month = capacity_gap(current_demand, effective)

    // Step 4: Scale capacity for 20% growth over 12 periods
    param growth_rate: Fraction = 0.20 {
        source: "projections",
        method: "assumption",
        confidence: 0.7
    }

    param periods: Count = 12 {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    var future_capacity: Rate per Month = scale_capacity(current_capacity, growth_rate, periods)

    // Step 5: Calculate cost
    param cost_per_unit: Currency<USD> = $1000 {
        source: "finance",
        method: "observed",
        confidence: 0.95
    }

    param units_needed: Count = 100 {
        source: "capacity_planning",
        method: "derived",
        confidence: 0.8
    }

    var total_cost: Currency<USD> = capacity_cost(units_needed, cost_per_unit)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.integration
def test_multi_product_capacity_allocation():
    """Test capacity allocation across multiple product lines with priorities."""
    pel_code = """
    param total_capacity: Rate per Month = 5000 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    // Product demands
    param product_a_demand: Rate per Month = 2000 / 1mo {
        source: "product_a",
        method: "derived",
        confidence: 0.9
    }

    param product_b_demand: Rate per Month = 2500 / 1mo {
        source: "product_b",
        method: "derived",
        confidence: 0.9
    }

    param product_c_demand: Rate per Month = 1500 / 1mo {
        source: "product_c",
        method: "derived",
        confidence: 0.9
    }

    // Priorities
    param priority_a: Fraction = 0.5 {
        source: "strategy",
        method: "assumption",
        confidence: 1.0
    }

    param priority_b: Fraction = 0.3 {
        source: "strategy",
        method: "assumption",
        confidence: 1.0
    }

    param priority_c: Fraction = 0.2 {
        source: "strategy",
        method: "assumption",
        confidence: 1.0
    }

    var demands: Array<Rate per Month> = [product_a_demand, product_b_demand, product_c_demand]
    var priorities: Array<Fraction> = [priority_a, priority_b, priority_c]

    // Allocate capacity
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)

    // Calculate gaps for each product
    var gap_a: Rate per Month = capacity_gap(product_a_demand, allocation[0])
    var gap_b: Rate per Month = capacity_gap(product_b_demand, allocation[1])
    var gap_c: Rate per Month = capacity_gap(product_c_demand, allocation[2])
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.integration
def test_utilization_monitoring_and_analysis():
    """Test utilization monitoring workflow with peak, average, and variability."""
    pel_code = """
    // Historical utilization data
    param util_1: Fraction = 0.75 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param util_2: Fraction = 0.82 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param util_3: Fraction = 0.95 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param util_4: Fraction = 0.88 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param util_5: Fraction = 1.05 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    var utilization_series: Array<Fraction> = [util_1, util_2, util_3, util_4, util_5]

    // Analyze utilization patterns
    var peak: Fraction = peak_utilization(utilization_series)
    var average: Fraction = average_utilization(utilization_series)
    var variability: Fraction = utilization_variability(utilization_series)

    // Calculate penalty for overutilization
    param max_safe: Fraction = 0.90 {
        source: "operations",
        method: "assumption",
        confidence: 1.0
    }

    param penalty_rate: Currency<USD> = $10000 {
        source: "finance",
        method: "assumption",
        confidence: 0.9
    }

    var penalty: Currency<USD> = overutilization_penalty(peak, max_safe, penalty_rate)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Hiring Module Integration Tests
# =============================================================================

@pytest.mark.integration
def test_complete_hiring_funnel_to_capacity():
    """Test complete hiring workflow from applicants to team capacity."""
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

    // Step 2: Calculate costs
    param total_recruiting_cost: Currency<USD> = $250000 {
        source: "finance",
        method: "observed",
        confidence: 1.0
    }

    var cost_per_hire_value: Currency<USD> per Person = cost_per_hire(total_recruiting_cost, hires_per_month)

    // Step 3: Apply ramp curve
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

    // Step 4: Calculate team capacity
    param productivity_per_person: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    param current_team: Count<Person> = 50 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    var team_prod: Rate per Month = team_productivity(current_team, productivity_per_person)

    // Step 5: Calculate ROI
    param value_per_hire: Currency<USD> per Person = $500000 {
        source: "finance",
        method: "derived",
        confidence: 0.7
    }

    var roi: Fraction = hire_roi(value_per_hire, cost_per_hire_value)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.integration
def test_workforce_planning_with_attrition():
    """Test workforce planning accounting for growth and attrition."""
    pel_code = """
    // Current state
    param current_headcount: Count<Person> = 100 {
        source: "hr_system",
        method: "observed",
        confidence: 1.0
    }

    param target_headcount: Count<Person> = 150 {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param planning_horizon: Duration<Month> = 12mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    param attrition_rate: Rate per Year = 0.15 / 1yr {
        source: "hr_analytics",
        method: "derived",
        confidence: 0.85
    }

    // Calculate replacement hires for attrition
    var replacement_hires: Count<Person> = attrition_replacement(current_headcount, attrition_rate)

    // Calculate growth hiring
    var growth_hires: Count<Person> = growth_hiring(current_headcount, target_headcount, planning_horizon)

    // Total hiring need
    var total_hiring_need: Count<Person> = replacement_hires + growth_hires

    // Create hiring plan
    param reporting_period: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_month: Count<Person> = hiring_plan(
        current_headcount,
        target_headcount + replacement_hires,
        planning_horizon,
        reporting_period
    )
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.integration
def test_team_capacity_with_ramp():
    """Test team capacity calculation with ramping employees."""
    pel_code = """
    // Team composition
    param fully_ramped: Count<Person> = 45 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param ramping: Count<Person> = 5 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param avg_ramp_progress: Fraction = 0.60 {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    // Calculate effective headcount
    var effective_team_size: Count<Person> = effective_headcount(
        fully_ramped,
        ramping,
        avg_ramp_progress
    )

    // Calculate team capacity
    param capacity_per_person: Rate per Month = 4 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.85
    }

    param utilization: Fraction = 0.80 {
        source: "operations",
        method: "assumption",
        confidence: 0.9
    }

    var total_capacity: Rate per Month = headcount_capacity(
        effective_team_size,
        capacity_per_person,
        utilization
    )
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.integration
def test_multi_role_team_capacity():
    """Test team capacity across multiple roles."""
    pel_code = """
    // Engineering team
    param engineers: Count<Person> = 20 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param eng_capacity: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    // Sales team
    param sales_reps: Count<Person> = 10 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param sales_capacity: Rate per Month = 10 / 1mo {
        source: "sales",
        method: "derived",
        confidence: 0.85
    }

    // Support team
    param support_staff: Count<Person> = 5 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param support_capacity: Rate per Month = 100 / 1mo {
        source: "support",
        method: "derived",
        confidence: 0.9
    }

    var headcounts: Array<Count<Person>> = [engineers, sales_reps, support_staff]
    var capacities: Array<Rate per Month> = [eng_capacity, sales_capacity, support_capacity]

    var total_team_capacity: Rate per Month = team_capacity(headcounts, capacities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Cross-Module Integration Tests
# =============================================================================

@pytest.mark.integration
def test_capacity_constrained_hiring():
    """Test hiring decisions constrained by capacity needs."""
    pel_code = """
    // Current capacity situation
    param current_capacity: Rate per Month = 200 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    param target_capacity: Rate per Month = 300 / 1mo {
        source: "growth_plan",
        method: "assumption",
        confidence: 0.8
    }

    param efficiency: Fraction = 0.85 {
        source: "operations",
        method: "derived",
        confidence: 0.85
    }

    // Calculate capacity gap
    var capacity_gap_value: Rate per Month = capacity_gap(target_capacity, current_capacity)

    // Calculate required headcount to fill gap
    param productivity_per_person: Rate per Month = 5 / 1mo {
        source: "hr",
        method: "derived",
        confidence: 0.8
    }

    param ramp_factor: Fraction = 0.85 {
        source: "hr",
        method: "derived",
        confidence: 0.75
    }

    var required_hires: Count<Person> = required_headcount(
        capacity_gap_value,
        productivity_per_person,
        ramp_factor
    )

    // Create hiring plan
    param planning_horizon: Duration<Month> = 6mo {
        source: "planning",
        method: "assumption",
        confidence: 1.0
    }

    param current_team: Count<Person> = 40 {
        source: "hr",
        method: "observed",
        confidence: 1.0
    }

    param period: Duration<Month> = 1mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var hires_per_month: Count<Person> = hiring_plan(
        current_team,
        current_team + required_hires,
        planning_horizon,
        period
    )

    // Calculate cost impact (using onboarding cost)
    param num_hires_in_period: Count<Person> = 10 {
        source: "recruiting",
        method: "assumption",
        confidence: 0.8
    }

    param onboarding_cost_per_hire_value: Currency<USD> per Person = $15000 {
        source: "hr",
        method: "derived",
        confidence: 0.85
    }

    var total_onboarding_cost: Currency<USD> = onboarding_cost(
        num_hires_in_period,
        onboarding_cost_per_hire_value
    )
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.integration
def test_hiring_lag_impact_on_capacity():
    """Test impact of hiring delays on capacity delivery."""
    pel_code = """
    // Capacity shortfall
    param capacity_shortfall: Rate per Month = 50 / 1mo {
        source: "capacity_planning",
        method: "derived",
        confidence: 0.9
    }

    // Hiring timeline
    param planned_hire_date: Duration<Month> = 2mo {
        source: "recruiting",
        method: "assumption",
        confidence: 0.8
    }

    param actual_hire_date: Duration<Month> = 4mo {
        source: "recruiting",
        method: "observed",
        confidence: 1.0
    }

    // Calculate impact of delay
    var lag_impact: Rate per Month = hiring_lag_impact(
        capacity_shortfall,
        planned_hire_date,
        actual_hire_date
    )

    // Calculate capacity contribution after ramp
    param capacity_per_person: Rate per Month = 5 / 1mo {
        source: "engineering",
        method: "derived",
        confidence: 0.8
    }

    param ramp_time_value: Duration<Month> = 3mo {
        source: "hr",
        method: "assumption",
        confidence: 0.8
    }

    param full_productivity_time: Duration<Month> = 12mo {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var capacity_per_new_hire: Rate per Month = capacity_per_hire(
        capacity_per_person,
        ramp_time_value,
        full_productivity_time
    )
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
