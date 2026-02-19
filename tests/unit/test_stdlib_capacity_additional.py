"""Additional unit tests for stdlib capacity edge cases."""
import pytest

from tests.conftest import assert_compiles_successfully, compile_pel_code


@pytest.mark.unit
def test_allocate_capacity_capping_behavior():
    pel_code = """
    param total_capacity: Rate per Month = 120 / 1mo
    param demand_a: Rate per Month = 100 / 1mo
    param demand_b: Rate per Month = 50 / 1mo

    var demands: Array<Rate per Month> = [demand_a, demand_b]
    var priorities: Array<Fraction> = [0.9, 0.1]
    var allocation: Array<Rate per Month> = allocate_capacity(total_capacity, demands, priorities)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_per_hire_clamped_when_ramp_exceeds_full_time():
    pel_code = """
    param capacity_per_person: Rate per Month = 100 / 1mo
    param ramp_time: Duration<Month> = 6mo
    param full_time: Duration<Month> = 3mo

    var cap_per_hire: Rate per Month = capacity_per_hire(capacity_per_person, ramp_time, full_time)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)


@pytest.mark.unit
def test_capacity_increment_exact_multiple():
    pel_code = """
    param needed: Fraction = 30
    param increment: Fraction = 10

    var rounded_capacity: Fraction = capacity_increment(needed, increment)
    """
    result = compile_pel_code(pel_code)
    assert_compiles_successfully(result)
