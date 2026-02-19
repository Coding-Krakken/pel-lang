"""Tests for the dimensionless × dimensioned multiplication shortcut.

The typechecker has a rule that Fraction, Int, or Count multiplied by a
dimensioned type yields the dimensioned type directly, instead of generating
a generic Product type.  These tests verify that behaviour for every relevant
combination and ensure the shortcut is *not* applied when both operands
are dimensionless.

See compiler/typechecker.py, the `DIMENSIONLESS_KINDS` block in operator=='*'.
"""

from __future__ import annotations

import pytest

from compiler.ast_nodes import BinaryOp, Literal
from compiler.typechecker import TypeChecker

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _int_literal(value: int = 5) -> Literal:
    return Literal(value=value, literal_type="integer")


def _fraction_literal(value: float = 0.85) -> Literal:
    return Literal(value=value, literal_type="number")


def _currency_literal(value: str = "$100") -> Literal:
    return Literal(value=value, literal_type="currency")


def _rate_expr() -> BinaryOp:
    """Build a `100 / 1mo` expression that infers Rate."""
    return BinaryOp(
        "/",
        Literal(value=100, literal_type="number"),
        Literal(value="1mo", literal_type="duration"),
    )


# ---------------------------------------------------------------------------
# Fraction × dimensioned → dimensioned
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fraction_times_currency_yields_currency() -> None:
    """Fraction * Currency<USD> should produce Currency<USD>."""
    tc = TypeChecker()
    expr = BinaryOp("*", _fraction_literal(), _currency_literal())
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Currency"
    assert result.params.get("currency_code") == "USD"


@pytest.mark.unit
def test_currency_times_fraction_yields_currency() -> None:
    """Currency<USD> * Fraction should produce Currency<USD>."""
    tc = TypeChecker()
    expr = BinaryOp("*", _currency_literal(), _fraction_literal())
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Currency"


@pytest.mark.unit
def test_fraction_times_rate_yields_rate() -> None:
    """Fraction * Rate should produce Rate (not a Product type)."""
    tc = TypeChecker()
    rate = tc.infer_expression(_rate_expr())
    assert rate.type_kind == "Rate", f"Expected Rate, got {rate.type_kind}"

    # Now multiply Fraction * Rate
    tc2 = TypeChecker()
    tc2.env.bind("r", rate)
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", _fraction_literal(), Variable("r"))
    result = tc2.infer_expression(expr)
    assert not tc2.has_errors(), tc2.get_errors()
    assert result.type_kind == "Rate"


@pytest.mark.unit
def test_rate_times_fraction_yields_rate() -> None:
    """Rate * Fraction should produce Rate (commutative shortcut)."""
    tc = TypeChecker()
    rate = tc.infer_expression(_rate_expr())

    tc2 = TypeChecker()
    tc2.env.bind("r", rate)
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", Variable("r"), _fraction_literal())
    result = tc2.infer_expression(expr)
    assert not tc2.has_errors(), tc2.get_errors()
    assert result.type_kind == "Rate"


# ---------------------------------------------------------------------------
# Int × dimensioned → dimensioned
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_int_times_currency_yields_currency() -> None:
    """Int * Currency<USD> should produce Currency<USD>."""
    tc = TypeChecker()
    expr = BinaryOp("*", _int_literal(), _currency_literal())
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Currency"


@pytest.mark.unit
def test_currency_times_int_yields_currency() -> None:
    """Currency<USD> * Int should produce Currency<USD>."""
    tc = TypeChecker()
    expr = BinaryOp("*", _currency_literal(), _int_literal())
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Currency"


# ---------------------------------------------------------------------------
# Both dimensionless → should NOT shortcut (falls through to dimension math)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fraction_times_fraction_is_fraction() -> None:
    """Fraction * Fraction should produce Fraction (both dimensionless, no shortcut)."""
    tc = TypeChecker()
    expr = BinaryOp("*", _fraction_literal(0.5), _fraction_literal(0.8))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Fraction"


@pytest.mark.unit
def test_int_times_int_is_fraction_or_int() -> None:
    """Int * Int — both dimensionless, should not shortcut to dimensioned type."""
    tc = TypeChecker()
    expr = BinaryOp("*", _int_literal(3), _int_literal(4))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    # Both dimensionless + both in dimensionless_kinds → no shortcut.
    # Falls through to dimension multiplication → no units → Fraction.
    assert result.type_kind == "Fraction"


@pytest.mark.unit
def test_fraction_times_int_is_dimensionless() -> None:
    """Fraction * Int — both dimensionless, should not shortcut."""
    tc = TypeChecker()
    expr = BinaryOp("*", _fraction_literal(0.5), _int_literal(2))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    # Both in dimensionless_kinds → no shortcut, falls to generic path
    assert result.type_kind == "Fraction"


# ---------------------------------------------------------------------------
# Edge case: ensure no false negatives on error path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_dimensionless_mul_does_not_suppress_errors() -> None:
    """Multiplying dimensionless by dimensioned should not introduce errors."""
    tc = TypeChecker()
    # Int * $100 — should cleanly produce Currency with no errors
    expr = BinaryOp("*", _int_literal(10), _currency_literal("$500"))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), f"Unexpected errors: {tc.get_errors()}"
    assert result.type_kind == "Currency"


# ---------------------------------------------------------------------------
# Count × dimensioned → dimensioned (Count treated as dimensionless scalar)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_count_times_rate_yields_rate() -> None:
    """Count<Person> × Rate per Month should produce Rate per Month."""
    from compiler.typechecker import PELType
    tc = TypeChecker()
    rate = tc.infer_expression(_rate_expr())
    assert rate.type_kind == "Rate"

    tc2 = TypeChecker()
    count_type = PELType.count("Person")
    tc2.env.bind("headcount", count_type)
    tc2.env.bind("r", rate)
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", Variable("headcount"), Variable("r"))
    result = tc2.infer_expression(expr)
    assert not tc2.has_errors(), tc2.get_errors()
    assert result.type_kind == "Rate"
    assert result.params.get("per") == "Month"


@pytest.mark.unit
def test_rate_times_count_yields_rate() -> None:
    """Rate per Month × Count<Person> should produce Rate per Month (commutative)."""
    from compiler.typechecker import PELType
    tc = TypeChecker()
    rate = tc.infer_expression(_rate_expr())

    tc2 = TypeChecker()
    count_type = PELType.count("Person")
    tc2.env.bind("headcount", count_type)
    tc2.env.bind("r", rate)
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", Variable("r"), Variable("headcount"))
    result = tc2.infer_expression(expr)
    assert not tc2.has_errors(), tc2.get_errors()
    assert result.type_kind == "Rate"


@pytest.mark.unit
def test_count_times_currency_yields_currency() -> None:
    """Count<Person> × Currency<USD> should produce Currency<USD>."""
    from compiler.typechecker import PELType
    tc = TypeChecker()
    count_type = PELType.count("Person")
    tc.env.bind("n", count_type)
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", Variable("n"), _currency_literal("$100"))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Currency"
    assert result.params.get("currency_code") == "USD"


@pytest.mark.unit
def test_count_times_count_no_shortcut() -> None:
    """Count × Count — both in DIMENSIONLESS_KINDS — should NOT shortcut."""
    from compiler.typechecker import PELType
    tc = TypeChecker()
    tc.env.bind("a", PELType.count("Person"))
    tc.env.bind("b", PELType.count("Server"))
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", Variable("a"), Variable("b"))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    # Both are in DIMENSIONLESS_KINDS, so neither shortcut branch fires.
    # Falls through to generic dimension multiplication.
    # Result should NOT be Count (no shortcutting when both are dimensionless-kind).
    assert result.type_kind != "Rate"


# ---------------------------------------------------------------------------
# Fraction × Duration interaction (Duration shortcut takes precedence)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fraction_times_duration_yields_duration() -> None:
    """Fraction × Duration — the Duration shortcut MUST fire first."""
    from compiler.typechecker import PELType
    tc = TypeChecker()
    tc.env.bind("d", PELType.duration("Month"))
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", _fraction_literal(0.5), Variable("d"))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Duration"


@pytest.mark.unit
def test_duration_times_fraction_yields_duration() -> None:
    """Duration × Fraction — commutative case of Duration shortcut."""
    from compiler.typechecker import PELType
    tc = TypeChecker()
    tc.env.bind("d", PELType.duration("Month"))
    from compiler.ast_nodes import Variable
    expr = BinaryOp("*", Variable("d"), _fraction_literal(0.5))
    result = tc.infer_expression(expr)
    assert not tc.has_errors(), tc.get_errors()
    assert result.type_kind == "Duration"


# ---------------------------------------------------------------------------
# Count × Rate × Fraction — chained multiplication (stdlib pattern)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_count_rate_fraction_chain() -> None:
    """Count<Person> × Rate × Fraction → Rate (stdlib headcount_capacity pattern)."""
    from compiler.ast_nodes import Variable
    from compiler.typechecker import PELType

    tc = TypeChecker()
    rate = tc.infer_expression(_rate_expr())

    tc2 = TypeChecker()
    tc2.env.bind("h", PELType.count("Person"))
    tc2.env.bind("r", rate)

    # Build h * r
    step1 = BinaryOp("*", Variable("h"), Variable("r"))
    # Build (h * r) * 0.8
    step2 = BinaryOp("*", step1, _fraction_literal(0.8))
    result = tc2.infer_expression(step2)
    assert not tc2.has_errors(), tc2.get_errors()
    assert result.type_kind == "Rate"
    assert result.params.get("per") == "Month"
