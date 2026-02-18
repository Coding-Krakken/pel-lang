"""Regression tests for stdlib loop/index bounds and retention indexing semantics."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_funnel_loops_use_safe_length_bounds() -> None:
    src = (ROOT / "stdlib" / "funnel" / "funnel.pel").read_text(encoding="utf-8")

    unsafe_patterns = [
        "for i in 0..conversion_rates.length {",
        "for i in 1..stage_sizes.length {",
        "for i in 0..time_in_stages.length {",
        "for i in 0..cohort_a_conversion_rates.length {",
    ]
    for pattern in unsafe_patterns:
        assert pattern not in src

    expected_safe_patterns = [
        "for i in 0..conversion_rates.length - 1 {",
        "for i in 1..stage_sizes.length - 1 {",
        "for i in 0..time_in_stages.length - 1 {",
        "for i in 0..cohort_a_conversion_rates.length - 1 {",
    ]
    for pattern in expected_safe_patterns:
        assert pattern in src


@pytest.mark.unit
def test_retention_loops_use_safe_length_bounds() -> None:
    src = (ROOT / "stdlib" / "retention" / "retention.pel").read_text(encoding="utf-8")

    unsafe_patterns = [
        "for i in 1..cohort_sizes_over_time.length {",
        "for i in 0..retention_curve.length {",
        "for i in 1..retention_rates.length {",
    ]
    for pattern in unsafe_patterns:
        assert pattern not in src

    expected_safe_patterns = [
        "for i in 1..cohort_sizes_over_time.length - 1 {",
        "for i in 0..retention_curve.length - 1 {",
        "for i in 1..retention_rates.length - 1 {",
    ]
    for pattern in expected_safe_patterns:
        assert pattern in src


@pytest.mark.unit
def test_retention_cohort_table_uses_curve_index_directly() -> None:
    src = (ROOT / "stdlib" / "retention" / "retention.pel").read_text(encoding="utf-8")

    assert "cohort_sizes[i] = initial_cohort_size * retention_rates[i]" in src
    assert "cohort_sizes[i] = cohort_sizes[i-1] * retention_rates[i-1]" not in src
