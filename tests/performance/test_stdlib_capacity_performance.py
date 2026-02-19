"""Performance tests for stdlib capacity module."""
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code_with_timing


@pytest.mark.performance
def test_calculate_utilization_performance():
    """Test calculate_utilization performance with typical usage."""
    pel_code = """
    param used: Rate per Month = 850 / 1mo {
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }

    param total: Rate per Month = 1000 / 1mo {
        source: "infrastructure",
        method: "observed",
        confidence: 1.0
    }

    var util: Fraction = calculate_utilization(used, total)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: should compile in under 500ms (CI environments are slower)
    assert elapsed < 0.5, f"Compilation took {elapsed:.3f}s, expected < 0.5s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_allocate_capacity_large_array_performance():
    """Test allocate_capacity with large demand arrays."""
    # Generate 100 demand parameters
    demands_code = "\n".join([
        f"""    param demand_{i}: Rate per Month = {100 + i} / 1mo {{
        source: "product_{i}",
        method: "derived",
        confidence: 0.9
    }}""" for i in range(100)
    ])

    priorities_code = "\n".join([
        f"""    param priority_{i}: Fraction = 0.01 {{
        source: "strategy",
        method: "assumption",
        confidence: 1.0
    }}""" for i in range(100)
    ])

    demands_array = "[" + ", ".join([f"demand_{i}" for i in range(100)]) + "]"
    priorities_array = "[" + ", ".join([f"priority_{i}" for i in range(100)]) + "]"

    pel_code = f"""
    param total_capacity: Rate per Month = 10000 / 1mo {{
        source: "operations",
        method: "observed",
        confidence: 1.0
    }}

{demands_code}

{priorities_code}

    var demands: Array<Rate per Month> = {demands_array}
    var priorities: Array<Fraction> = {priorities_array}
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: even with 100 elements, should compile in under 1s (CI overhead)
    assert elapsed < 1.0, f"Compilation took {elapsed:.3f}s, expected < 1.0s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_utilization_variability_performance():
    """Test utilization_variability (Welford's algorithm) performance."""
    # Generate 1000 utilization values
    util_params = "\n".join([
        f"""    param util_{i}: Fraction = {0.5 + (i % 50) / 100.0} {{
        source: "monitoring",
        method: "observed",
        confidence: 1.0
    }}""" for i in range(1000)
    ])

    util_array = "[" + ", ".join([f"util_{i}" for i in range(1000)]) + "]"

    pel_code = f"""
{util_params}

    var utilization_series: Array<Fraction> = {util_array}
    var variability: Fraction = utilization_variability(utilization_series)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: Welford's algorithm should be efficient even with 1000 elements
    assert elapsed < 1.0, f"Compilation took {elapsed:.3f}s, expected < 1.0s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_capacity_planning_workflow_performance():
    """Test complete capacity planning workflow performance."""
    pel_code = """
    // Current state
    param current_capacity: Rate per Month = 5000 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    param target_demand: Rate per Month = 8000 / 1mo {
        source: "forecasting",
        method: "derived",
        confidence: 0.85
    }

    param efficiency: Fraction = 0.90 {
        source: "operations",
        method: "derived",
        confidence: 0.9
    }

    param capacity_per_unit: Rate per Month = 100 / 1mo {
        source: "equipment_specs",
        method: "observed",
        confidence: 0.95
    }

    // Calculate gap
    var gap: Rate per Month = capacity_gap(target_demand, current_capacity)

    // Calculate required units
    var required_units: Fraction = required_capacity(gap, capacity_per_unit, efficiency)

    // Calculate effective capacity after efficiency
    var effective_cap: Rate per Month = effective_capacity(current_capacity, efficiency)

    // Historical utilization for variability
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

    var util_series: Array<Fraction> = [util_1, util_2, util_3]
    var peak: Fraction = peak_utilization(util_series)
    var average: Fraction = average_utilization(util_series)
    var variability: Fraction = utilization_variability(util_series)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: complete workflow should compile quickly (CI overhead)
    assert elapsed < 0.5, f"Compilation took {elapsed:.3f}s, expected < 0.5s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_multi_product_allocation_performance():
    """Test multi-product capacity allocation performance."""
    # 50 products
    pel_code = """
    param total_capacity: Rate per Month = 10000 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }
    """ + "\n".join([
        f"""
    param demand_{i}: Rate per Month = {200 + i * 10} / 1mo {{
        source: "product_{i}",
        method: "derived",
        confidence: 0.9
    }}

    param priority_{i}: Fraction = {0.01 + i * 0.001} {{
        source: "strategy",
        method: "assumption",
        confidence: 1.0
    }}""" for i in range(50)
    ]) + f"""

    var demands: Array<Rate per Month> = [{", ".join([f"demand_{i}" for i in range(50)])}]
    var priorities: Array<Fraction> = [{", ".join([f"priority_{i}" for i in range(50)])}]
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)

    var total_allocated: Rate per Month = allocation[0] + allocation[1]
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion
    assert elapsed < 0.5, f"Compilation took {elapsed:.3f}s, expected < 0.5s"
    assert_compiles_successfully(ir)


@pytest.mark.performance
def test_bottleneck_detection_performance():
    """Test bottleneck detection across multiple stages."""
    pel_code = """
    param stage_1_cap: Rate per Month = 1000 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    param stage_2_cap: Rate per Month = 800 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    param stage_3_cap: Rate per Month = 1200 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    param stage_4_cap: Rate per Month = 750 / 1mo {
        source: "operations",
        method: "observed",
        confidence: 1.0
    }

    var capacities: Array<Rate per Month> = [stage_1_cap, stage_2_cap, stage_3_cap, stage_4_cap]
    var bottleneck_idx: Int = bottleneck_capacity(capacities)
    """

    ir, elapsed = compile_pel_code_with_timing(pel_code)

    # Performance assertion: should compile in under 500ms (CI environments are slower)
    assert elapsed < 0.5, f"Compilation took {elapsed:.3f}s, expected < 0.5s"
    assert_compiles_successfully(ir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance"])
