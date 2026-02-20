"""Unit tests for stdlib shocks module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code


@pytest.mark.unit
def test_recession_shock():
    """Test recession impact on demand."""
    pel_code = """
    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "forecast",
        method: "derived",
        confidence: 0.9
    }

    param recession_severity: Fraction = 0.7 {
        source: "macro_model",
        method: "assumption",
        confidence: 0.75
    }

    param demand_sensitivity: Fraction = 0.5 {
        source: "historical_analysis",
        method: "derived",
        confidence: 0.8
    }

    var shocked_demand: Rate per Month = recession_shock(baseline_demand, recession_severity, demand_sensitivity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_platform_change_shock():
    """Test platform change shock with recovery."""
    pel_code = """
    param baseline_metric: Rate per Month = 1000 / 1mo {
        source: "normal_operations",
        method: "observed",
        confidence: 0.95
    }

    param change_severity: Fraction = 0.5 {
        source: "impact_assessment",
        method: "estimate",
        confidence: 0.7
    }

    param adaptation_rate: Fraction = 0.2 {
        source: "recovery_model",
        method: "assumption",
        confidence: 0.75
    }

    param time_since_change: Duration<Day> = 30d {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }

    var current_metric: Rate per Month = platform_change_shock(baseline_metric, change_severity, adaptation_rate, time_since_change)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_supply_chain_disruption():
    """Test supply chain disruption impact."""
    pel_code = """
    param baseline_capacity: Rate per Month = 1000 / 1mo {
        source: "capacity_planning",
        method: "observed",
        confidence: 0.95
    }

    param disruption_severity: Fraction = 0.6 {
        source: "risk_assessment",
        method: "estimate",
        confidence: 0.7
    }

    param duration: Duration<Day> = 14d {
        source: "scenario_planning",
        method: "assumption",
        confidence: 0.75
    }

    param current_time: Duration<Day> = 7d {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }

    var available_capacity: Rate per Month = supply_chain_disruption(baseline_capacity, disruption_severity, duration, current_time)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_regulatory_shock():
    """Test regulatory shock impact."""
    pel_code = """
    param baseline_revenue: Currency<USD> per Month = $100000 / 1mo {
        source: "financial_forecast",
        method: "derived",
        confidence: 0.9
    }

    param compliance_cost: Currency<USD> per Month = $15000 / 1mo {
        source: "compliance_budget",
        method: "estimate",
        confidence: 0.8
    }

    param market_restriction: Fraction = 0.2 {
        source: "legal_analysis",
        method: "estimate",
        confidence: 0.7
    }

    var net_revenue: Currency<USD> per Month = regulatory_shock(baseline_revenue, compliance_cost, market_restriction)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_competitor_disruption():
    """Test competitive disruption impact."""
    pel_code = """
    param your_market_share: Fraction = 0.35 {
        source: "market_research",
        method: "derived",
        confidence: 0.85
    }

    param disruption_strength: Fraction = 0.6 {
        source: "competitive_analysis",
        method: "estimate",
        confidence: 0.75
    }

    param defensive_moat: Fraction = 0.4 {
        source: "strategic_assessment",
        method: "judgment",
        confidence: 0.7
    }

    var new_market_share: Fraction = competitor_disruption(your_market_share, disruption_strength, defensive_moat)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_macro_interest_rate_shock():
    """Test interest rate shock on costs."""
    pel_code = """
    param baseline_cost: Currency<USD> per Month = $100000 / 1mo {
        source: "financial_model",
        method: "observed",
        confidence: 0.95
    }

    param debt_ratio: Fraction = 0.3 {
        source: "balance_sheet",
        method: "observed",
        confidence: 1.0
    }

    param rate_change: Fraction = 0.02 {
        source: "fed_policy",
        method: "assumption",
        confidence: 0.9
    }

    var new_cost: Currency<USD> per Month = macro_interest_rate_shock(baseline_cost, debt_ratio, rate_change)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_talent_market_shock():
    """Test talent market shock on compensation."""
    pel_code = """
    param baseline_headcount_cost: Currency<USD> per Month = $500000 / 1mo {
        source: "payroll",
        method: "observed",
        confidence: 1.0
    }

    param market_tightness: Fraction = 0.7 {
        source: "labor_market_data",
        method: "derived",
        confidence: 0.8
    }

    param wage_elasticity: Fraction = 0.5 {
        source: "compensation_model",
        method: "assumption",
        confidence: 0.75
    }

    var adjusted_cost: Currency<USD> per Month = talent_market_shock(baseline_headcount_cost, market_tightness, wage_elasticity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_demand_shock_correlated():
    """Test correlated demand shock across segments."""
    pel_code = """
    param segment1_demand: Rate per Month = 100 / 1mo {
        source: "segment_forecast",
        method: "derived",
        confidence: 0.9
    }

    param segment2_demand: Rate per Month = 200 / 1mo {
        source: "segment_forecast",
        method: "derived",
        confidence: 0.9
    }

    param shock_severity: Fraction = 0.5 {
        source: "scenario_planning",
        method: "assumption",
        confidence: 0.8
    }

    param correlation: Fraction = 0.8 {
        source: "correlation_analysis",
        method: "derived",
        confidence: 0.75
    }

    param sensitivity1: Fraction = 0.6 {
        source: "segment_model",
        method: "assumption",
        confidence: 0.8
    }

    param sensitivity2: Fraction = 0.4 {
        source: "segment_model",
        method: "assumption",
        confidence: 0.8
    }

    var shocked_demands: Array<Rate per Month> = demand_shock_correlated([segment1_demand, segment2_demand], shock_severity, correlation, [sensitivity1, sensitivity2])
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_combined_shock_impact():
    """Test combined impact of multiple shocks."""
    pel_code = """
    param baseline_value: Rate per Month = 1000 / 1mo {
        source: "baseline_forecast",
        method: "derived",
        confidence: 0.9
    }

    param shock1: Fraction = 0.9 {
        source: "shock_scenario",
        method: "assumption",
        confidence: 0.8
    }

    param shock2: Fraction = 0.8 {
        source: "shock_scenario",
        method: "assumption",
        confidence: 0.8
    }

    param shock3: Fraction = 0.95 {
        source: "shock_scenario",
        method: "assumption",
        confidence: 0.8
    }

    param correlation: Fraction = 0.3 {
        source: "correlation_model",
        method: "assumption",
        confidence: 0.7
    }

    var final_value: Rate per Month = combined_shock_impact(baseline_value, [shock1, shock2, shock3], correlation)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_shock_recovery():
    """Test shock recovery trajectory."""
    pel_code = """
    param shocked_value: Rate per Month = 700 / 1mo {
        source: "post_shock_state",
        method: "observed",
        confidence: 0.95
    }

    param pre_shock_value: Rate per Month = 1000 / 1mo {
        source: "pre_shock_baseline",
        method: "observed",
        confidence: 0.95
    }

    param recovery_rate: Fraction = 0.15 {
        source: "recovery_model",
        method: "assumption",
        confidence: 0.75
    }

    param time_elapsed: Duration<Day> = 20d {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }

    var current_value: Rate per Month = shock_recovery(shocked_value, pre_shock_value, recovery_rate, time_elapsed)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_value_at_risk():
    """Test value at risk calculation."""
    pel_code = """
    param baseline_value: Rate per Month = 1000000 / 1mo {
        source: "revenue_forecast",
        method: "derived",
        confidence: 0.9
    }

    param shock_probability: Fraction = 0.1 {
        source: "risk_assessment",
        method: "estimate",
        confidence: 0.7
    }

    param shock_magnitude: Fraction = 0.4 {
        source: "impact_model",
        method: "assumption",
        confidence: 0.75
    }

    var var_amount: Rate per Month = value_at_risk(baseline_value, shock_probability, shock_magnitude)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_black_swan_event():
    """Test black swan event modeling."""
    pel_code = """
    param baseline_metric: Rate per Month = 1000 / 1mo {
        source: "normal_operations",
        method: "observed",
        confidence: 0.95
    }

    param tail_risk_multiplier: Fraction = 0.1 {
        source: "tail_risk_model",
        method: "assumption",
        confidence: 0.6
    }

    param triggered: Fraction = 1.0 {
        source: "scenario_flag",
        method: "assumption",
        confidence: 1.0
    }

    var shocked_metric: Rate per Month = black_swan_event(baseline_metric, tail_risk_multiplier, triggered)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_conditional_shock():
    """Test conditional shock cascade."""
    pel_code = """
    param baseline_value: Rate per Month = 1000 / 1mo {
        source: "baseline_forecast",
        method: "derived",
        confidence: 0.9
    }

    param primary_shock_impact: Fraction = 0.3 {
        source: "primary_scenario",
        method: "assumption",
        confidence: 0.8
    }

    param conditional_shock_impact: Fraction = 0.5 {
        source: "conditional_scenario",
        method: "assumption",
        confidence: 0.75
    }

    param primary_occurred: Fraction = 1.0 {
        source: "scenario_flag",
        method: "assumption",
        confidence: 1.0
    }

    var final_value: Rate per Month = conditional_shock(baseline_value, primary_shock_impact, conditional_shock_impact, primary_occurred)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_shock_duration_percentile():
    """Test shock duration percentile calculation."""
    pel_code = """
    param median_duration: Duration<Day> = 30d {
        source: "historical_shocks",
        method: "derived",
        confidence: 0.8
    }

    param duration_spread: Duration<Day> = 10d {
        source: "duration_variability",
        method: "derived",
        confidence: 0.75
    }

    param percentile: Fraction = 0.9 {
        source: "risk_analysis",
        method: "assumption",
        confidence: 1.0
    }

    var duration_90th: Duration<Day> = shock_duration_percentile(median_duration, duration_spread, percentile)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
