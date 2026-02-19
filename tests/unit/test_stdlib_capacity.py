"""Unit tests for stdlib capacity module."""
# ruff: noqa: W293
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code


@pytest.mark.unit
def test_calculate_utilization():
    """Test utilization calculation."""
    pel_code = """
    param used: Rate per Month = 80 / 1mo {
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
def test_capacity_gap():
    """Test capacity gap calculation."""
    pel_code = """
    param demand: Rate per Month = 1000 / 1mo {
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
def test_required_capacity():
    """Test required capacity calculation."""
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
def test_effective_capacity():
    """Test effective capacity with efficiency losses."""
    pel_code = """
    param total: Rate per Month = 100 / 1mo {
        source: "capacity_model",
        method: "assumption",
        confidence: 1.0
    }

    param efficiency: Fraction = 0.90 {
        source: "operations",
        method: "derived",
        confidence: 0.85
    }

    var effective: Rate per Month = effective_capacity(total, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_allocate_capacity():
    """Test capacity allocation."""
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
    var priorities: Array<Fraction> = [0.6, 0.4]
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_constraint():
    """Test capacity constraint calculation."""
    pel_code = """
    param capacity: Rate per Month = 500 / 1mo {
        source: "production",
        method: "observed",
        confidence: 1.0
    }

    param efficiency: Fraction = 0.95 {
        source: "operations",
        method: "derived",
        confidence: 0.9
    }

    var max_output: Rate per Month = capacity_constraint(capacity, efficiency)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_bottleneck_capacity():
    """Test bottleneck capacity identification."""
    pel_code = """
    param stage_1: Rate per Month = 1000 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    param stage_2: Rate per Month = 800 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    param stage_3: Rate per Month = 900 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    var capacities: Array<Rate per Month> = [stage_1, stage_2, stage_3]
    var bottleneck: Int = bottleneck_capacity(capacities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_parallel_capacity():
    """Test parallel capacity calculation."""
    pel_code = """
    param line_a: Rate per Month = 500 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    param line_b: Rate per Month = 700 / 1mo {
        source: "ops",
        method: "observed",
        confidence: 0.9
    }

    var capacities: Array<Rate per Month> = [line_a, line_b]
    var total: Rate per Month = parallel_capacity(capacities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_scale_capacity():
    """Test capacity scaling for growth."""
    pel_code = """
    param current: Rate per Month = 1000 / 1mo {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param growth: Fraction = 0.20 {
        source: "business_plan",
        method: "assumption",
        confidence: 0.7
    }

    param periods: Count = 4 {
        source: "model",
        method: "assumption",
        confidence: 1.0
    }

    var future_capacity: Rate per Month = scale_capacity(current, growth, periods)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_increment():
    """Test discrete capacity increment calculation."""
    pel_code = """
    param needed: Fraction = 23 {
        source: "capacity_plan",
        method: "derived",
        confidence: 0.9
    }

    param increment: Fraction = 10 {
        source: "procurement",
        method: "assumption",
        confidence: 1.0
    }

    var rounded_capacity: Fraction = capacity_increment(needed, increment)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_lead_time():
    """Test capacity lead time calculation."""
    pel_code = """
    param quantity: Fraction = 3 {
        source: "procurement",
        method: "assumption",
        confidence: 1.0
    }

    var lead_time: Duration<Day> = capacity_lead_time("servers", quantity)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_cost():
    """Test capacity cost calculation."""
    pel_code = """
    param quantity: Count = 10 {
        source: "capacity_plan",
        method: "derived",
        confidence: 0.9
    }

    param cost_per_unit: Currency<USD> = $5000 {
        source: "vendor",
        method: "observed",
        confidence: 1.0
    }

    var total_cost: Currency<USD> = capacity_cost(quantity, cost_per_unit)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_peak_utilization():
    """Test peak utilization calculation."""
    pel_code = """
    param util_1: Fraction = 0.75 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param util_2: Fraction = 0.92 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param util_3: Fraction = 0.68 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    var util_series: Array<Fraction> = [util_1, util_2, util_3]
    var peak: Fraction = peak_utilization(util_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_average_utilization():
    """Test average utilization calculation."""
    pel_code = """
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

    param util_3: Fraction = 0.68 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    var util_series: Array<Fraction> = [util_1, util_2, util_3]
    var avg_util: Fraction = average_utilization(util_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_utilization_variability():
    """Test utilization variability calculation."""
    pel_code = """
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

    param util_3: Fraction = 0.68 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    var util_series: Array<Fraction> = [util_1, util_2, util_3]
    var variability: Fraction = utilization_variability(util_series)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_overutilization_penalty():
    """Test overutilization penalty calculation."""
    pel_code = """
    param actual: Fraction = 1.15 {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param max_safe: Fraction = 1.0 {
        source: "policy",
        method: "assumption",
        confidence: 1.0
    }

    param penalty_rate: Currency<USD> = $1000.0 {
        source: "sla",
        method: "assumption",
        confidence: 0.8
    }

    var penalty: Currency<USD> = overutilization_penalty(actual, max_safe, penalty_rate)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
