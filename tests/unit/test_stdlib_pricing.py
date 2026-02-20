"""Unit tests for stdlib pricing module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code


@pytest.mark.unit
def test_elasticity_curve():
    """Test price elasticity curve."""
    pel_code = """
    param baseline_price: Currency<USD> = $100 {
        source: "pricing_strategy",
        method: "assumption",
        confidence: 1.0
    }

    param new_price: Currency<USD> = $120 {
        source: "pricing_test",
        method: "assumption",
        confidence: 1.0
    }

    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "sales_data",
        method: "observed",
        confidence: 0.95
    }

    param price_elasticity: Fraction = -1.5 {
        source: "price_sensitivity_analysis",
        method: "derived",
        confidence: 0.8
    }

    var new_demand: Rate per Month = elasticity_curve(baseline_price, new_price, baseline_demand, price_elasticity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_competitive_pricing():
    """Test competitive pricing response."""
    pel_code = """
    param your_price: Currency<USD> = $100 {
        source: "pricing_team",
        method: "observed",
        confidence: 1.0
    }

    param competitor_price: Currency<USD> = $90 {
        source: "competitive_intelligence",
        method: "observed",
        confidence: 0.9
    }

    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "sales_forecast",
        method: "derived",
        confidence: 0.9
    }

    param sensitivity: Fraction = 0.6 {
        source: "market_research",
        method: "derived",
        confidence: 0.75
    }

    var adjusted_demand: Rate per Month = competitive_pricing(your_price, competitor_price, baseline_demand, sensitivity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_dynamic_pricing():
    """Test dynamic pricing based on utilization."""
    pel_code = """
    param base_price: Currency<USD> = $100 {
        source: "standard_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param current_utilization: Fraction = 0.9 {
        source: "operations",
        method: "observed",
        confidence: 0.95
    }

    param target_utilization: Fraction = 0.75 {
        source: "capacity_planning",
        method: "assumption",
        confidence: 1.0
    }

    param adjustment_rate: Fraction = 0.3 {
        source: "pricing_policy",
        method: "assumption",
        confidence: 1.0
    }

    var adjusted_price: Currency<USD> = dynamic_pricing(base_price, current_utilization, target_utilization, adjustment_rate)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_discount_impact():
    """Test revenue impact of discount."""
    pel_code = """
    param base_price: Currency<USD> = $100 {
        source: "standard_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param discount_pct: Fraction = 0.2 {
        source: "promotion_plan",
        method: "assumption",
        confidence: 1.0
    }

    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "sales_data",
        method: "observed",
        confidence: 0.95
    }

    param demand_lift: Fraction = 0.3 {
        source: "promotion_history",
        method: "derived",
        confidence: 0.8
    }

    var revenue: Currency<USD> per Month = discount_impact(base_price, discount_pct, baseline_demand, demand_lift)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_price_point_optimization():
    """Test price point optimization."""
    pel_code = """
    param price1: Currency<USD> = $80 {
        source: "pricing_options",
        method: "assumption",
        confidence: 1.0
    }

    param price2: Currency<USD> = $100 {
        source: "pricing_options",
        method: "assumption",
        confidence: 1.0
    }

    param price3: Currency<USD> = $120 {
        source: "pricing_options",
        method: "assumption",
        confidence: 1.0
    }

    param baseline_price: Currency<USD> = $100 {
        source: "current_price",
        method: "observed",
        confidence: 1.0
    }

    param baseline_demand: Rate per Month = 1000 / 1mo {
        source: "sales_data",
        method: "observed",
        confidence: 0.95
    }

    param elasticity: Fraction = -1.2 {
        source: "elasticity_model",
        method: "derived",
        confidence: 0.8
    }

    var optimal_idx: Int = price_point_optimization([price1, price2, price3], baseline_price, baseline_demand, elasticity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_tiered_pricing_revenue():
    """Test tiered pricing revenue calculation."""
    pel_code = """
    param usage: Fraction = 150.0 {
        source: "usage_metering",
        method: "observed",
        confidence: 1.0
    }

    param tier1_limit: Fraction = 0.0 {
        source: "pricing_tier_structure",
        method: "assumption",
        confidence: 1.0
    }

    param tier2_limit: Fraction = 100.0 {
        source: "pricing_tier_structure",
        method: "assumption",
        confidence: 1.0
    }

    param tier3_limit: Fraction = 200.0 {
        source: "pricing_tier_structure",
        method: "assumption",
        confidence: 1.0
    }

    param price1: Currency<USD> = $1 {
        source: "tier_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param price2: Currency<USD> = $0.80 {
        source: "tier_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param price3: Currency<USD> = $0.60 {
        source: "tier_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param price4: Currency<USD> = $0.50 {
        source: "tier_pricing",
        method: "assumption",
        confidence: 1.0
    }

    var revenue: Currency<USD> = tiered_pricing_revenue(usage, [tier1_limit, tier2_limit, tier3_limit], [price1, price2, price3, price4])
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_bundle_pricing():
    """Test bundle pricing calculation."""
    pel_code = """
    param price1: Currency<USD> = $50 {
        source: "product_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param price2: Currency<USD> = $30 {
        source: "product_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param price3: Currency<USD> = $20 {
        source: "product_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param bundle_discount: Fraction = 0.15 {
        source: "bundle_strategy",
        method: "assumption",
        confidence: 1.0
    }

    var bundle_price: Currency<USD> = bundle_pricing([price1, price2, price3], bundle_discount)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_freemium_conversion():
    """Test freemium to paid conversion revenue."""
    pel_code = """
    param free_users: Count = 10000 {
        source: "user_database",
        method: "observed",
        confidence: 1.0
    }

    param conversion_rate: Fraction = 0.03 {
        source: "conversion_analytics",
        method: "derived",
        confidence: 0.9
    }

    param paid_price: Currency<USD> = $29 {
        source: "pricing_tier",
        method: "assumption",
        confidence: 1.0
    }

    var revenue: Currency<USD> per Month = freemium_conversion(free_users, conversion_rate, paid_price)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_willingness_to_pay():
    """Test willingness to pay quantile calculation."""
    pel_code = """
    param wtp_median: Currency<USD> = $100 {
        source: "van_westendorp",
        method: "derived",
        confidence: 0.8
    }

    param wtp_spread: Currency<USD> = $30 {
        source: "van_westendorp",
        method: "derived",
        confidence: 0.75
    }

    param quantile: Fraction = 0.9 {
        source: "pricing_analysis",
        method: "assumption",
        confidence: 1.0
    }

    var wtp_90th: Currency<USD> = willingness_to_pay(wtp_median, wtp_spread, quantile)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_reservation_price():
    """Test reservation price calculation."""
    pel_code = """
    param value_delivered: Currency<USD> = $150 {
        source: "value_proposition",
        method: "estimate",
        confidence: 0.75
    }

    param next_best_alternative: Currency<USD> = $100 {
        source: "competitive_analysis",
        method: "observed",
        confidence: 0.9
    }

    param switching_cost: Currency<USD> = $20 {
        source: "customer_research",
        method: "estimate",
        confidence: 0.7
    }

    var max_price: Currency<USD> = reservation_price(value_delivered, next_best_alternative, switching_cost)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_value_based_pricing():
    """Test value-based pricing calculation."""
    pel_code = """
    param cost_to_serve: Currency<USD> = $40 {
        source: "cost_accounting",
        method: "observed",
        confidence: 0.95
    }

    param value_delivered: Currency<USD> = $200 {
        source: "value_analysis",
        method: "estimate",
        confidence: 0.75
    }

    param value_capture_rate: Fraction = 0.4 {
        source: "pricing_strategy",
        method: "assumption",
        confidence: 1.0
    }

    var price: Currency<USD> = value_based_pricing(cost_to_serve, value_delivered, value_capture_rate)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_penetration_pricing():
    """Test penetration pricing market share impact."""
    pel_code = """
    param market_price: Currency<USD> = $100 {
        source: "market_data",
        method: "observed",
        confidence: 0.9
    }

    param penetration_discount: Fraction = 0.2 {
        source: "pricing_strategy",
        method: "assumption",
        confidence: 1.0
    }

    param share_gained: Fraction = 0.5 {
        source: "market_model",
        method: "assumption",
        confidence: 0.7
    }

    var share_increase: Fraction = penetration_pricing(market_price, penetration_discount, share_gained)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_price_skimming():
    """Test price skimming decay."""
    pel_code = """
    param launch_price: Currency<USD> = $200 {
        source: "launch_strategy",
        method: "assumption",
        confidence: 1.0
    }

    param final_price: Currency<USD> = $100 {
        source: "target_pricing",
        method: "assumption",
        confidence: 1.0
    }

    param decay_rate: Fraction = 0.05 {
        source: "pricing_roadmap",
        method: "assumption",
        confidence: 0.8
    }

    param time_period: Duration<Day> = 12d {
        source: "calendar",
        method: "observed",
        confidence: 1.0
    }

    var current_price: Currency<USD> = price_skimming(launch_price, final_price, decay_rate, time_period)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_psychological_anchor():
    """Test psychological pricing anchor effect."""
    pel_code = """
    param reference_price: Currency<USD> = $150 {
        source: "pricing_display",
        method: "assumption",
        confidence: 1.0
    }

    param actual_price: Currency<USD> = $99 {
        source: "actual_offer",
        method: "assumption",
        confidence: 1.0
    }

    param anchor_strength: Fraction = 0.5 {
        source: "behavioral_model",
        method: "assumption",
        confidence: 0.7
    }

    var perceived_value: Fraction = psychological_anchor(reference_price, actual_price, anchor_strength)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_usage_based_pricing():
    """Test usage-based pricing revenue."""
    pel_code = """
    param base_fee: Currency<USD> = $50 {
        source: "pricing_tier",
        method: "assumption",
        confidence: 1.0
    }

    param usage_volume: Fraction = 1000.0 {
        source: "usage_metering",
        method: "observed",
        confidence: 1.0
    }

    param price_per_unit: Currency<USD> = $0.10 {
        source: "unit_pricing",
        method: "assumption",
        confidence: 1.0
    }

    var revenue: Currency<USD> per Month = usage_based_pricing(base_fee, usage_volume, price_per_unit)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_price_discrimination():
    """Test price discrimination revenue."""
    pel_code = """
    param high_value_segment: Count = 1000 {
        source: "customer_segmentation",
        method: "derived",
        confidence: 0.9
    }

    param low_value_segment: Count = 5000 {
        source: "customer_segmentation",
        method: "derived",
        confidence: 0.9
    }

    param premium_price: Currency<USD> = $100 {
        source: "premium_tier",
        method: "assumption",
        confidence: 1.0
    }

    param basic_price: Currency<USD> = $40 {
        source: "basic_tier",
        method: "assumption",
        confidence: 1.0
    }

    var revenue: Currency<USD> per Month = price_discrimination(high_value_segment, low_value_segment, premium_price, basic_price)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_cost_plus_pricing():
    """Test cost-plus pricing calculation."""
    pel_code = """
    param cost: Currency<USD> = $60 {
        source: "cost_accounting",
        method: "observed",
        confidence: 0.95
    }

    param target_margin: Fraction = 0.4 {
        source: "pricing_policy",
        method: "assumption",
        confidence: 1.0
    }

    var price: Currency<USD> = cost_plus_pricing(cost, target_margin)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
