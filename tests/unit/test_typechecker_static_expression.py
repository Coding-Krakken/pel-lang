"""Unit tests for TypeChecker._evaluate_static_expression method.

Tests the compile-time static expression evaluator used for constraint checking.
"""
from __future__ import annotations

import pytest

from compiler.ast_nodes import BinaryOp, Literal, UnaryOp, Variable
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_evaluate_static_literal_integer() -> None:
    """Test evaluating integer literals."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Literal("42", "integer"))
    assert result == 42


@pytest.mark.unit
def test_evaluate_static_literal_number() -> None:
    """Test evaluating number literals with decimals."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Literal("3.14", "number"))
    assert result == 3.14


@pytest.mark.unit
def test_evaluate_static_literal_boolean_true() -> None:
    """Test evaluating boolean true literal."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Literal(True, "boolean"))
    assert result is True


@pytest.mark.unit
def test_evaluate_static_literal_boolean_false() -> None:
    """Test evaluating boolean false literal."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Literal(False, "boolean"))
    assert result is False


@pytest.mark.unit
def test_evaluate_static_literal_currency() -> None:
    """Test evaluating currency literals."""
    tc = TypeChecker()

    # Simple currency
    result = tc._evaluate_static_expression(Literal("$100", "currency"))
    assert result == 100.0

    # Currency with decimals
    result = tc._evaluate_static_expression(Literal("$100.50", "currency"))
    assert result == 100.50


@pytest.mark.unit
def test_evaluate_static_literal_currency_negative() -> None:
    """Test evaluating negative currency literals."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Literal("$-100", "currency"))
    assert result == -100.0


@pytest.mark.unit
def test_evaluate_static_literal_rate() -> None:
    """Test evaluating rate literals."""
    tc = TypeChecker()
    # Rate like "$100/1mo"
    result = tc._evaluate_static_expression(Literal("$100.50/1mo", "rate"))
    assert result == 100.50


@pytest.mark.unit
def test_evaluate_static_variable_lookup() -> None:
    """Test looking up variable values from static_values."""
    tc = TypeChecker()

    # Store a static value
    tc.static_values["x"] = Literal("42", "integer")

    # Look it up
    result = tc._evaluate_static_expression(Variable("x"))
    assert result == 42


@pytest.mark.unit
def test_evaluate_static_variable_not_found() -> None:
    """Test that unknown variables return None."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Variable("unknown"))
    assert result is None


@pytest.mark.unit
def test_evaluate_static_unary_negation() -> None:
    """Test unary negation operator."""
    tc = TypeChecker()
    expr = UnaryOp("-", Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result == -42


@pytest.mark.unit
def test_evaluate_static_unary_plus() -> None:
    """Test unary plus operator."""
    tc = TypeChecker()
    expr = UnaryOp("+", Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result == 42


@pytest.mark.unit
def test_evaluate_static_unary_not() -> None:
    """Test unary not operator."""
    tc = TypeChecker()
    expr = UnaryOp("not", Literal(True, "boolean"))
    result = tc._evaluate_static_expression(expr)
    assert result is False


@pytest.mark.unit
def test_evaluate_static_binary_add() -> None:
    """Test binary addition."""
    tc = TypeChecker()
    expr = BinaryOp("+", Literal("10", "integer"), Literal("32", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result == 42


@pytest.mark.unit
def test_evaluate_static_binary_subtract() -> None:
    """Test binary subtraction."""
    tc = TypeChecker()
    expr = BinaryOp("-", Literal("50", "integer"), Literal("8", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result == 42


@pytest.mark.unit
def test_evaluate_static_binary_multiply() -> None:
    """Test binary multiplication."""
    tc = TypeChecker()
    expr = BinaryOp("*", Literal("6", "integer"), Literal("7", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result == 42


@pytest.mark.unit
def test_evaluate_static_binary_divide() -> None:
    """Test binary division."""
    tc = TypeChecker()
    expr = BinaryOp("/", Literal("84", "integer"), Literal("2", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result == 42.0


@pytest.mark.unit
def test_evaluate_static_binary_divide_by_zero() -> None:
    """Test division by zero returns None."""
    tc = TypeChecker()
    expr = BinaryOp("/", Literal("42", "integer"), Literal("0", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is None


@pytest.mark.unit
def test_evaluate_static_binary_comparison_eq() -> None:
    """Test equality comparison."""
    tc = TypeChecker()
    expr = BinaryOp("==", Literal("42", "integer"), Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_binary_comparison_ne() -> None:
    """Test not-equal comparison."""
    tc = TypeChecker()
    expr = BinaryOp("!=", Literal("42", "integer"), Literal("100", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_binary_comparison_lt() -> None:
    """Test less-than comparison."""
    tc = TypeChecker()
    expr = BinaryOp("<", Literal("10", "integer"), Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_binary_comparison_lte() -> None:
    """Test less-than-or-equal comparison."""
    tc = TypeChecker()

    # Equal case
    expr = BinaryOp("<=", Literal("42", "integer"), Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True

    # Less than case
    expr = BinaryOp("<=", Literal("10", "integer"), Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_binary_comparison_gt() -> None:
    """Test greater-than comparison."""
    tc = TypeChecker()
    expr = BinaryOp(">", Literal("42", "integer"), Literal("10", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_binary_comparison_gte() -> None:
    """Test greater-than-or-equal comparison."""
    tc = TypeChecker()
    expr = BinaryOp(">=", Literal("42", "integer"), Literal("42", "integer"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_binary_logical_and() -> None:
    """Test logical AND operator."""
    tc = TypeChecker()
    expr = BinaryOp("and", Literal(True, "boolean"), Literal(True, "boolean"))
    result = tc._evaluate_static_expression(expr)
    assert result is True

    expr = BinaryOp("and", Literal(True, "boolean"), Literal(False, "boolean"))
    result = tc._evaluate_static_expression(expr)
    assert result is False


@pytest.mark.unit
def test_evaluate_static_binary_logical_or() -> None:
    """Test logical OR operator."""
    tc = TypeChecker()
    expr = BinaryOp("or", Literal(False, "boolean"), Literal(True, "boolean"))
    result = tc._evaluate_static_expression(expr)
    assert result is True

    expr = BinaryOp("or", Literal(False, "boolean"), Literal(False, "boolean"))
    result = tc._evaluate_static_expression(expr)
    assert result is False


@pytest.mark.unit
def test_evaluate_static_complex_expression() -> None:
    """Test evaluating a complex nested expression."""
    tc = TypeChecker()

    # Store parameter: revenue = $100
    tc.static_values["revenue"] = Literal("$100", "currency")

    # Expression: revenue >= $0
    expr = BinaryOp(">=", Variable("revenue"), Literal("$0", "currency"))
    result = tc._evaluate_static_expression(expr)
    assert result is True


@pytest.mark.unit
def test_evaluate_static_complex_expression_negative() -> None:
    """Test evaluating a complex expression that evaluates to False."""
    tc = TypeChecker()

    # Store parameter: revenue = -$100
    tc.static_values["revenue"] = UnaryOp("-", Literal("$100", "currency"))

    # Expression: revenue >= $0
    expr = BinaryOp(">=", Variable("revenue"), Literal("$0", "currency"))
    result = tc._evaluate_static_expression(expr)
    assert result is False


@pytest.mark.unit
def test_evaluate_static_non_evaluable_expression() -> None:
    """Test that non-evaluable expressions return None."""
    tc = TypeChecker()

    # Create a mock expression type that's not handled
    from compiler.ast_nodes import FunctionCall

    # FunctionCall is not evaluated statically
    expr = FunctionCall("sum", [Literal("1", "integer"), Literal("2", "integer")])
    result = tc._evaluate_static_expression(expr)
    assert result is None


@pytest.mark.unit
def test_evaluate_static_partial_evaluation() -> None:
    """Test that expressions with non-static parts return None."""
    tc = TypeChecker()

    # Only 'x' is in static_values
    tc.static_values["x"] = Literal("10", "integer")

    # Expression: x + y (where y is not static)
    expr = BinaryOp("+", Variable("x"), Variable("y"))
    result = tc._evaluate_static_expression(expr)
    assert result is None


@pytest.mark.unit
def test_evaluate_static_currency_with_no_numeric_match() -> None:
    """Test currency literals that don't contain valid numbers return None."""
    tc = TypeChecker()
    result = tc._evaluate_static_expression(Literal("invalid", "currency"))
    assert result is None


@pytest.mark.unit
def test_evaluate_static_literal_unsupported_type() -> None:
    """Test that unsupported literal types return None."""
    tc = TypeChecker()
    # String literals are not used for static constraint evaluation
    result = tc._evaluate_static_expression(Literal("hello", "string"))
    assert result is None
