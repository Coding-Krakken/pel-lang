"""Unit tests for stdlib demand module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code


@pytest.mark.unit
def test_seasonal_multiplier():
    """Test seasonal demand multiplier."""
    pel_code = """
    param month: Int = 12 {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }

    param seasonality: Fraction = 0.3 {
        source: "historical_data",
        method: "derived",  
        confidence: 0.9
    }

    param peak_month: Int = 12 {
        source: "business_planning",
        method: "assumption",
        confidence: 1.0
    }

    var multiplier: Fraction = seasonal_multiplier(month, seasonality, peak_month)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_lead_generation():
    """Test lead generation from marketing spend."""
    pel_code = """
    param marketing_spend: Currency<USD> = $10000 {
        source: "marketing_budget",
        method: "observed",
        confidence: 1.0
    }

    param cpl: Currency<USD> = $50 {
        source: "ad_platform",
        method: "observed",
        confidence: 0.95
    }

    param efficiency: Fraction = 0.9 {
        source: "campaign_performance",
        method: "derived",
        confidence: 0.85
    }

    var leads: Count = lead_generation(marketing_spend, cpl, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_funnel_demand():
    """Test demand through funnel stage."""
    pel_code = """
    param top_of_funnel: Count = 1000 {
        source: "crm",
        method: "observed",
        confidence: 1.0
    }

    param conversion_rate: Fraction = 0.25 {
        source: "funnel_analytics",
        method: "derived",
        confidence: 0.9
    }

    param stage_duration: Duration<Day> = 7d {
        source: "sales_ops",
        method: "observed",
        confidence: 0.95
    }

    var demand: Rate per Month = funnel_demand(top_of_funnel, conversion_rate, stage_duration)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_elasticity_demand():
    """Test price elasticity of demand."""
    pel_code = """
    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "sales_data",
        method: "observed",
        confidence: 0.95
    }

    param price_change_pct: Fraction = 0.1 {
        source: "pricing_team",
        method: "assumption",
        confidence: 1.0
    }

    param price_elasticity: Fraction = -1.5 {
        source: "econometric_analysis",
        method: "derived",
        confidence: 0.8
    }

    var new_demand: Rate per Month = elasticity_demand(baseline_demand, price_change_pct, price_elasticity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_market_saturation():
    """Test market saturation model."""
    pel_code = """
    param potential_market: Count = 1000000 {
        source: "market_research",
        method: "estimate",
        confidence: 0.7
    }

    param current_penetration: Fraction = 0.6 {
        source: "customer_database",
        method: "derived",
        confidence: 0.9
    }

    param saturation_rate: Fraction = 0.8 {
        source: "growth_model",
        method: "assumption",
        confidence: 0.8
    }

    var remaining_opportunity: Fraction = market_saturation(potential_market, current_penetration, saturation_rate)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_competitor_impact():
    """Test competitive impact on demand."""
    pel_code = """
    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "sales_forecast",
        method: "derived",
        confidence: 0.9
    }

    param competitor_share: Fraction = 0.4 {
        source: "market_intelligence",
        method: "estimate",
        confidence: 0.75
    }

    param competitive_intensity: Fraction = 0.6 {
        source: "analyst_assessment",
        method: "judgment",
        confidence: 0.7
    }

    var adjusted_demand: Rate per Month = competitor_impact(baseline_demand, competitor_share, competitive_intensity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_event_driven_spike():
    """Test event-driven demand spike."""
    pel_code = """
    param baseline_demand: Rate per Month = 100 / 1mo {
        source: "normal_operations",
        method: "observed",
        confidence: 0.95
    }

    param event_multiplier: Fraction = 2.5 {
        source: "historical_events",
        method: "derived",
        confidence: 0.8
    }

    param event_duration: Duration<Day> = 7d {
        source: "event_planning",
        method: "assumption",
        confidence: 1.0
    }

    param current_period: Duration<Day> = 5d {
        source: "clock",
        method: "observed",
        confidence: 1.0
    }

    param event_start: Duration<Day> = 0d {
        source: "event_schedule",
        method: "observed",
        confidence: 1.0
    }

    var spike_demand: Rate per Month = event_driven_spike(baseline_demand, event_multiplier, event_duration, current_period, event_start)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_churn_demand_feedback():
    """Test churn feedback on demand."""
    pel_code = """
    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "demand_forecast",
        method: "derived",
        confidence: 0.9
    }

    param churn_rate: Fraction = 0.15 {
        source: "customer_analytics",
        method: "observed",
        confidence: 0.95
    }

    param feedback_strength: Fraction = 0.5 {
        source: "customer_surveys",
        method: "derived",
        confidence: 0.75
    }

    var adjusted_demand: Rate per Month = churn_demand_feedback(baseline_demand, churn_rate, feedback_strength)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_bass_diffusion():
    """Test Bass diffusion model for product adoption."""
    pel_code = """
    param innovation_rate: Fraction = 0.03 {
        source: "adoption_model",
        method: "assumption",
        confidence: 0.8
    }

    param imitation_rate: Fraction = 0.38 {
        source: "adoption_model",
        method: "assumption",
        confidence: 0.8
    }

    param market_potential: Count = 10000 {
        source: "tam_analysis",
        method: "estimate",
        confidence: 0.7
    }

    param current_adopters: Count = 2000 {
        source: "user_database",
        method: "observed",
        confidence: 1.0
    }

    var new_adopters: Count = bass_diffusion(innovation_rate, imitation_rate, market_potential, current_adopters)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_aggregate_demand():
    """Test aggregating demand across channels."""
    pel_code = """
    param channel1: Rate per Month = 100 / 1mo {
        source: "direct_sales",
        method: "observed",
        confidence: 0.95
    }

    param channel2: Rate per Month = 200 / 1mo {
        source: "partner_channel",
        method: "observed",
        confidence: 0.9
    }

    param channel3: Rate per Month = 150 / 1mo {
        source: "online_channel",
        method: "observed",
        confidence: 0.95
    }

    var total_demand: Rate per Month = aggregate_demand([channel1, channel2, channel3])
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_demand_decay():
    """Test demand decay over time."""
    pel_code = """
    param peak_demand: Rate per Month = 1000 / 1mo {
        source: "promotion_peak",
        method: "observed",
        confidence: 1.0
    }

    param decay_rate: Fraction = 0.1 {
        source: "decay_model",
        method: "derived",
        confidence: 0.85
    }

    param time_since_peak: Duration<Day> = 10d {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }

    var current_demand: Rate per Month = demand_decay(peak_demand, decay_rate, time_since_peak)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_viral_coefficient():
    """Test viral coefficient calculation."""
    pel_code = """
    param invites_per_user: Fraction = 5.0 {
        source: "user_behavior",
        method: "observed",
        confidence: 0.9
    }

    param invite_conversion: Fraction = 0.25 {
        source: "invite_analytics",
        method: "derived",
        confidence: 0.85
    }

    var k_factor: Fraction = viral_coefficient(invites_per_user, invite_conversion)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_constrained_demand():
    """Test capacity-constrained demand."""
    pel_code = """
    param unconstrained_demand: Rate per Month = 1000 / 1mo {
        source: "market_demand",
        method: "derived",
        confidence: 0.9
    }

    param capacity_limit: Rate per Month = 800 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 0.95
    }

    param backlog_conversion: Fraction = 0.5 {
        source: "backlog_analysis",
        method: "derived",
        confidence: 0.8
    }

    var actual_demand: Rate per Month = constrained_demand(unconstrained_demand, capacity_limit, backlog_conversion)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_addressable_segment():
    """Test addressable market segment calculation."""
    pel_code = """
    param total_market: Count = 1000000 {
        source: "market_research",
        method: "estimate",
        confidence: 0.7
    }

    param segment_fraction: Fraction = 0.3 {
        source: "segmentation_analysis",
        method: "derived",
        confidence: 0.8
    }

    param penetration_rate: Fraction = 0.15 {
        source: "go_to_market",
        method: "assumption",
        confidence: 0.75
    }

    var addressable: Count = addressable_segment(total_market, segment_fraction, penetration_rate)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_network_demand():
    """Test network effects on demand."""
    pel_code = """
    param baseline_demand: Rate per Month = 100 / 1mo {
        source: "baseline_model",
        method: "derived",
        confidence: 0.9
    }

    param network_size: Count = 10000 {
        source: "user_database",
        method: "observed",
        confidence: 1.0
    }

    param network_coefficient: Fraction = 0.0001 {
        source: "network_model",
        method: "assumption",
        confidence: 0.8
    }

    var boosted_demand: Rate per Month = network_demand(baseline_demand, network_size, network_coefficient)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_demand_forecast():
    """Test demand forecasting with trend."""
    pel_code = """
    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "current_sales",
        method: "observed",
        confidence: 0.95
    }

    param trend_rate: Fraction = 0.05 {
        source: "trend_analysis",
        method: "derived",
        confidence: 0.8
    }

    param periods_ahead: Int = 12 {
        source: "planning_horizon",
        method: "assumption",
        confidence: 1.0
    }

    var forecast: Rate per Month = demand_forecast(baseline_demand, trend_rate, periods_ahead)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_weighted_demand():
    """Test weighted average demand across scenarios."""
    pel_code = """
    param demand1: Rate per Month = 100 / 1mo {
        source: "pessimistic_scenario",
        method: "derived",
        confidence: 0.8
    }

    param demand2: Rate per Month = 200 / 1mo {
        source: "base_scenario",
        method: "derived",
        confidence: 0.9
    }

    param demand3: Rate per Month = 300 / 1mo {
        source: "optimistic_scenario",
        method: "derived",
        confidence: 0.8
    }

    param prob1: Fraction = 0.2 {
        source: "scenario_planning",
        method: "judgment",
        confidence: 0.7
    }

    param prob2: Fraction = 0.5 {
        source: "scenario_planning",
        method: "judgment",
        confidence: 0.7
    }

    param prob3: Fraction = 0.3 {
        source: "scenario_planning",
        method: "judgment",
        confidence: 0.7
    }

    var avg_demand: Rate per Month = weighted_demand([demand1, demand2, demand3], [prob1, prob2, prob3])
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
