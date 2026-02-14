from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    ArrayLiteral,
    BinaryOp,
    BlockExpr,
    ForStmt,
    FunctionCall,
    IfStmt,
    Indexing,
    Literal,
    Return,
    UnaryOp,
    Variable,
)
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_typechecker_undefined_variable_records_error_and_falls_back() -> None:
    tc = TypeChecker()
    inferred = tc.infer_expression(Variable("missing"))

    assert tc.has_errors()
    assert tc.get_errors()[0].code == "E0101"
    assert inferred.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_dimension_mismatch_addition_records_error() -> None:
    tc = TypeChecker()
    expr = BinaryOp(
        "+",
        Literal(value="$1", literal_type="currency"),
        Literal(value=1, literal_type="number"),
    )
    inferred = tc.infer_expression(expr)

    assert tc.has_errors()
    assert any(e.code == "E0200" for e in tc.get_errors())
    assert inferred.type_kind == "Currency"


@pytest.mark.unit
def test_typechecker_unary_not_requires_boolean() -> None:
    tc = TypeChecker()
    inferred = tc.infer_expression(UnaryOp("!", Literal(value=1, literal_type="number")))

    assert tc.has_errors()
    assert any(e.code == "E0100" for e in tc.get_errors())
    assert inferred.type_kind == "Boolean"


@pytest.mark.unit
def test_typechecker_indexing_scalar_returns_same_type() -> None:
    tc = TypeChecker()
    tc.env.bind("x", tc.infer_expression(Literal(value=1, literal_type="number")))

    inferred = tc.infer_expression(Indexing(expression=Variable("x"), index=Variable("t")))
    assert inferred.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_block_expr_infers_type_from_return_in_nested_structures() -> None:
    tc = TypeChecker()
    block = BlockExpr(
        statements=[
            IfStmt(
                condition=Literal(value=True, literal_type="number"),
                then_body=[Return(Literal(value=1, literal_type="number"))],
                else_body=[Return(Literal(value=2, literal_type="number"))],
            ),
            ForStmt(
                var_name="i",
                start=Literal(value=0, literal_type="number"),
                end=Literal(value=1, literal_type="number"),
                body=[Return(Literal(value=3, literal_type="number"))],
            ),
        ]
    )

    inferred = tc.infer_expression(block)
    assert inferred.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_function_call_wrong_arity_records_error() -> None:
    tc = TypeChecker()
    expr = FunctionCall(
        function_name="sqrt",
        arguments=[Literal(value=1, literal_type="number"), Literal(value=2, literal_type="number")],
    )
    _ = tc.infer_expression(expr)
    assert tc.has_errors()


@pytest.mark.unit
def test_typechecker_sum_of_array_returns_element_type() -> None:
    tc = TypeChecker()
    expr = FunctionCall(
        function_name="sum",
        arguments=[ArrayLiteral(elements=[Literal(value=1, literal_type="number")])],
    )
    inferred = tc.infer_expression(expr)
    assert inferred.type_kind == "Fraction"
