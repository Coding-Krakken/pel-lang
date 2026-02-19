"""Edge case tests for stdlib capacity module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code

# =============================================================================
# Division by Zero Edge Cases
# =============================================================================

@pytest.mark.unit
def test_calculate_utilization_zero_total():
    """Test utilization with zero total capacity."""
    pel_code = """
    param used: Rate per Month = 80 / 1mo {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param total: Rate per Month = 0 / 1mo {
        source: "infrastructure",
        method: "observed",
        confidence: 1.0
    }

    var utilization: Fraction = calculate_utilization(used, total)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_calculate_utilization_negative_used():
    """Test utilization with negative used capacity."""
    pel_code = """
    param used: Rate per Month = -10 / 1mo {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param total: Rate per Month = 100 / 1mo {
        source: "infrastructure",
        method: "observed",
        confidence: 1.0
    }

    var utilization: Fraction = calculate_utilization(used, total)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_required_capacity_zero_efficiency():
    """Test required capacity with zero efficiency."""
    pel_code = """
    param target: Rate per Month = 1000 / 1mo {
        source: "production_plan",
        method: "assumption",
        confidence: 1.0
    }

    param capacity_per_unit: Rate per Month = 50 / 1mo {
        source: "equipment_specs",
        method: "observed",
        confidence: 0.95
    }

    param efficiency: Fraction = 0.0 {
        source: "operations",
        method: "derived",
        confidence: 0.8
    }

    var required: Fraction = required_capacity(target, capacity_per_unit, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_required_capacity_zero_capacity_per_unit():
    """Test required capacity with zero capacity per unit."""
    pel_code = """
    param target: Rate per Month = 1000 / 1mo {
        source: "production_plan",
        method: "assumption",
        confidence: 1.0
    }

    param capacity_per_unit: Rate per Month = 0 / 1mo {
        source: "equipment_specs",
        method: "observed",
        confidence: 0.95
    }

    param efficiency: Fraction = 0.85 {
        source: "operations",
        method: "derived",
        confidence: 0.8
    }

    var required: Fraction = required_capacity(target, capacity_per_unit, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_average_utilization_single_zero_element():
    """Test average utilization with single zero-value element array."""
    pel_code = """
    var empty_series: Array<Fraction> = [0.0]
    var avg: Fraction = average_utilization(empty_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_increment_zero_increment_size():
    """Test capacity increment with zero increment size."""
    pel_code = """
    param needed: Fraction = 100.0 {
        source: "capacity_planning",
        method: "derived",
        confidence: 0.9
    }

    param increment: Fraction = 0.0 {
        source: "provisioning",
        method: "assumption",
        confidence: 1.0
    }

    var incremented: Fraction = capacity_increment(needed, increment)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Empty Array Edge Cases
# =============================================================================

@pytest.mark.unit
def test_bottleneck_capacity_single_zero_element():
    """Test bottleneck with single zero-value capacity array."""
    pel_code = """
    var empty_capacities: Array<Rate per Month> = [0 / 1mo]
    var bottleneck_idx: Int = bottleneck_capacity(empty_capacities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_peak_utilization_single_zero_element():
    """Test peak utilization with single zero-value element array."""
    pel_code = """
    var empty_series: Array<Fraction> = [0.0]
    var peak: Fraction = peak_utilization(empty_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_utilization_variability_single_zero_element():
    """Test utilization variability with single zero-value element array."""
    pel_code = """
    var empty_series: Array<Fraction> = [0.0]
    var variability: Fraction = utilization_variability(empty_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_utilization_variability_single_element():
    """Test utilization variability with single element."""
    pel_code = """
    param single_value: Fraction = 0.8 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }
    
    var single_series: Array<Fraction> = [single_value]
    var variability: Fraction = utilization_variability(single_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_allocate_capacity_single_zero_demand():
    """Test capacity allocation with single zero-value demand array."""
    pel_code = """
    param total_capacity: Rate per Month = 1000 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 1.0
    }

    var empty_demands: Array<Rate per Month> = [0 / 1mo]
    var empty_priorities: Array<Fraction> = [0.0]
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, empty_demands, empty_priorities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Negative Value Edge Cases
# =============================================================================

@pytest.mark.unit
def test_capacity_gap_negative_demand():
    """Test capacity gap with negative demand."""
    pel_code = """
    param demand: Rate per Month = -100 / 1mo {
        source: "load_balancer",
        method: "observed",
        confidence: 0.95
    }

    param available: Rate per Month = 800 / 1mo {
        source: "capacity_planning",
        method: "derived",
        confidence: 0.9
    }

    var gap: Rate per Month = capacity_gap(demand, available)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_scale_capacity_negative_periods():
    """Test scale capacity with negative time periods."""
    pel_code = """
    param current: Rate per Month = 100 / 1mo {
        source: "current_state",
        method: "observed",
        confidence: 1.0
    }

    param growth: Fraction = 0.10 {
        source: "projections",
        method: "assumption",
        confidence: 0.8
    }

    param periods: Count = -5 {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var scaled: Rate per Month = scale_capacity(current, growth, periods)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Boundary Value Tests
# =============================================================================

@pytest.mark.unit
def test_effective_capacity_efficiency_over_one():
    """Test effective capacity with efficiency > 1.0."""
    pel_code = """
    param total: Rate per Month = 100 / 1mo {
        source: "capacity_model",
        method: "assumption",
        confidence: 1.0
    }

    param efficiency: Fraction = 1.5 {
        source: "operations",
        method: "derived",
        confidence: 0.85
    }

    var effective: Rate per Month = effective_capacity(total, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_effective_capacity_negative_efficiency():
    """Test effective capacity with negative efficiency."""
    pel_code = """
    param total: Rate per Month = 100 / 1mo {
        source: "capacity_model",
        method: "assumption",
        confidence: 1.0
    }

    param efficiency: Fraction = -0.5 {
        source: "operations",
        method: "derived",
        confidence: 0.85
    }

    var effective: Rate per Month = effective_capacity(total, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_scale_capacity_large_periods():
    """Test scale capacity with very large time periods (potential overflow)."""
    pel_code = """
    param current: Rate per Month = 100 / 1mo {
        source: "current_state",
        method: "observed",
        confidence: 1.0
    }

    param growth: Fraction = 0.50 {
        source: "projections",
        method: "assumption",
        confidence: 0.8
    }

    param periods: Count = 20 {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var scaled: Rate per Month = scale_capacity(current, growth, periods)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


# =============================================================================
# Complex Scenario Tests
# =============================================================================

@pytest.mark.unit
def test_allocate_capacity_zero_total_demand():
    """Test capacity allocation when all demands are zero."""
    pel_code = """
    param total_capacity: Rate per Month = 1000 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 1.0
    }

    param demand_a: Rate per Month = 0 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    param demand_b: Rate per Month = 0 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    var demands: Array<Rate per Month> = [demand_a, demand_b]
    var priorities: Array<Fraction> = [0.0]
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_allocate_capacity_zero_priorities():
    """Test capacity allocation with all zero priorities."""
    pel_code = """
    param total_capacity: Rate per Month = 1000 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 1.0
    }

    param demand_a: Rate per Month = 700 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    param demand_b: Rate per Month = 600 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    var demands: Array<Rate per Month> = [demand_a, demand_b]
    var priorities: Array<Fraction> = [0.0, 0.0]
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_lead_time_zero_quantity():
    """Test capacity lead time with zero quantity."""
    pel_code = """
    param cap_type: String = "server" {
        source: "infrastructure",
        method: "assumption",
        confidence: 1.0
    }

    param qty: Fraction = 0.0 {
        source: "provisioning",
        method: "derived",
        confidence: 1.0
    }

    var lead_time: Duration<Day> = capacity_lead_time(cap_type, qty)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_lead_time_unknown_type():
    """Test capacity lead time with unknown capacity type."""
    pel_code = """
    param cap_type: String = "unknown_type_xyz" {
        source: "infrastructure",
        method: "assumption",
        confidence: 1.0
    }

    param qty: Fraction = 10.0 {
        source: "provisioning",
        method: "derived",
        confidence: 1.0
    }

    var lead_time: Duration<Day> = capacity_lead_time(cap_type, qty)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
