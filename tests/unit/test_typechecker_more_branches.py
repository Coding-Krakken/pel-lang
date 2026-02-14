from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    ArrayLiteral,
    BinaryOp,
    FunctionCall,
    Indexing,
    Literal,
    TypeAnnotation,
    Variable,
)
from compiler.typechecker import Dimension, TypeChecker


@pytest.mark.unit
def test_typechecker_duration_generic_addition_is_compatible() -> None:
    tc = TypeChecker()

    generic_duration = Literal(
        value="1m", literal_type="duration"
    )  # invalid suffix => generic Duration
    month_duration = Literal(value="1mo", literal_type="duration")

    expr = BinaryOp(operator="+", left=generic_duration, right=month_duration)
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Duration"
    assert tc.errors == []


@pytest.mark.unit
def test_typechecker_exponent_requires_dimensionless() -> None:
    tc = TypeChecker()

    base = Literal(value=2.0, literal_type="number")
    exponent = Literal(value="$1", literal_type="currency")

    expr = BinaryOp(operator="^", left=base, right=exponent)
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Fraction"
    assert any(getattr(err, "code", None) == "E0100" for err in tc.errors)


@pytest.mark.unit
def test_typechecker_logical_ops_require_boolean_operands() -> None:
    tc = TypeChecker()

    expr = BinaryOp(
        operator="&&",
        left=Literal(value=1.0, literal_type="number"),
        right=Literal(value=0.0, literal_type="number"),
    )
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Boolean"
    assert sum(1 for e in tc.errors if getattr(e, "code", None) == "E0100") == 2


@pytest.mark.unit
def test_typechecker_comparison_dimension_mismatch_reports_error() -> None:
    tc = TypeChecker()

    # Produce a Rate via (dimensionless / Duration)
    rate = BinaryOp(
        operator="/",
        left=Literal(value=1.0, literal_type="number"),
        right=Literal(value="1mo", literal_type="duration"),
    )
    currency = Literal(value="$10", literal_type="currency")

    expr = BinaryOp(operator="<", left=currency, right=rate)
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Boolean"
    assert any(getattr(err, "code", None) == "E0200" for err in tc.errors)


@pytest.mark.unit
def test_typechecker_function_call_sqrt_wrong_arity_reports_error() -> None:
    tc = TypeChecker()

    expr = FunctionCall(
        function_name="sqrt",
        arguments=[
            Literal(value=4.0, literal_type="number"),
            Literal(value=9.0, literal_type="number"),
        ],
    )
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Fraction"
    assert any(getattr(err, "code", None) == "E0100" for err in tc.errors)


@pytest.mark.unit
def test_typechecker_function_call_sum_over_array_returns_element_type() -> None:
    tc = TypeChecker()

    arr = ArrayLiteral(
        elements=[
            Literal(value=1.0, literal_type="number"),
            Literal(value=2.0, literal_type="number"),
        ]
    )

    expr = FunctionCall(function_name="sum", arguments=[arr])
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Fraction"
    assert tc.errors == []


@pytest.mark.unit
def test_typechecker_indexing_scalar_returns_same_type() -> None:
    tc = TypeChecker()

    tc.env.bind(
        "x",
        tc.ast_type_to_pel_type(
            TypeAnnotation(type_kind="Currency", params={"currency_code": "USD"})
        ),
    )

    expr = Indexing(expression=Variable(name="x"), index=Variable(name="t"))
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Currency"
    assert inferred.params.get("currency_code") == "USD"


@pytest.mark.unit
def test_dimension_divide_different_currencies_raises() -> None:
    with pytest.raises(ValueError):
        Dimension.currency("USD").divide(Dimension.currency("EUR"))
