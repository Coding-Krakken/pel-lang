from __future__ import annotations

import pytest

from compiler.typechecker import Dimension


@pytest.mark.unit
def test_dimension_multiply_currency_by_dimensionless_preserves_currency() -> None:
    usd = Dimension.currency("USD")
    scalar = Dimension.dimensionless()

    assert usd.multiply(scalar) == usd
    assert scalar.multiply(usd) == usd


@pytest.mark.unit
def test_dimension_multiply_rate_by_duration_is_dimensionless() -> None:
    rate = Dimension.rate("Month")
    dur = Dimension.duration("Month")

    assert rate.multiply(dur) == Dimension.dimensionless()

    generic_dur = Dimension.duration("generic")
    assert rate.multiply(generic_dur) == Dimension.dimensionless()


@pytest.mark.unit
def test_dimension_multiply_count_by_scoped_removes_scope() -> None:
    count_customer = Dimension.count("Customer")
    scoped_usd_per_customer = Dimension({"currency": "USD", "scoped": "Customer"})

    assert count_customer.multiply(scoped_usd_per_customer) == Dimension({"currency": "USD"})


@pytest.mark.unit
def test_dimension_multiply_currency_currency_same_is_dimensionless_and_diff_raises() -> None:
    assert (
        Dimension.currency("USD").multiply(Dimension.currency("USD")) == Dimension.dimensionless()
    )

    with pytest.raises(ValueError):
        Dimension.currency("USD").multiply(Dimension.currency("EUR"))


@pytest.mark.unit
def test_dimension_hash_is_defined_and_stable_for_equal_units() -> None:
    d1 = Dimension({"a": 1, "b": 2})
    d2 = Dimension({"b": 2, "a": 1})
    assert hash(d1) == hash(d2)


@pytest.mark.unit
def test_dimension_multiply_generic_combine_and_overlap_key_paths() -> None:
    # Combine non-overlapping keys
    combined = Dimension({"x": 1}).multiply(Dimension({"y": 2}))
    assert combined == Dimension({"x": 1, "y": 2})

    # Overlap with same value should keep as-is
    overlapped = Dimension({"x": 1}).multiply(Dimension({"x": 1}))
    assert overlapped == Dimension({"x": 1})


@pytest.mark.unit
def test_dimension_divide_currency_count_duration_and_generic_inversion() -> None:
    # Currency / Count => scoped currency
    scoped = Dimension.currency("USD").divide(Dimension.count("Customer"))
    assert scoped == Dimension({"currency": "USD", "scoped": "Customer"})

    # Duration / Duration => dimensionless
    assert (
        Dimension.duration("Month").divide(Dimension.duration("Month")) == Dimension.dimensionless()
    )

    # Divide by dimensionless => same dimension
    assert Dimension({"k": 1}).divide(Dimension.dimensionless()) == Dimension({"k": 1})

    # Generic inversion path
    inverted = Dimension({"a": 1}).divide(Dimension({"b": 2}))
    assert inverted == Dimension({"a": 1, "inv_b": 2})
