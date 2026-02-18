from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    BinaryOp,
    Expression,
    FunctionCall,
    Literal,
    Model,
    TypeAnnotation,
    UnaryOp,
    VarDecl,
    Variable,
)
from compiler.typechecker import PELType, TypeChecker


@pytest.mark.unit
def test_typechecker_ast_type_to_pel_type_capacity_boolean_distribution_and_fallback() -> None:
    tc = TypeChecker()

    cap = tc.ast_type_to_pel_type(TypeAnnotation(type_kind="Capacity", params={"resource": "CPU"}))
    assert cap.type_kind == "Capacity"
    assert cap.dimension.units == {"capacity": "CPU"}

    # Backward compatibility: parser may produce `entity` for Capacity generic arg.
    cap_entity = tc.ast_type_to_pel_type(TypeAnnotation(type_kind="Capacity", params={"entity": "Seat"}))
    assert cap_entity.type_kind == "Capacity"
    assert cap_entity.dimension.units == {"capacity": "Seat"}

    # No generic arg should still map to non-dimensionless Capacity.
    cap_default = tc.ast_type_to_pel_type(TypeAnnotation(type_kind="Capacity", params={}))
    assert cap_default.dimension.units == {"capacity": "Units"}

    int_type = tc.infer_expression(Literal(value=1, literal_type="integer"))
    assert not tc.types_compatible(cap_entity, int_type)

    boo = tc.ast_type_to_pel_type(TypeAnnotation(type_kind="Boolean", params={}))
    assert boo.type_kind == "Boolean"

    dist = tc.ast_type_to_pel_type(
        TypeAnnotation(
            type_kind="Distribution",
            params={"inner": TypeAnnotation(type_kind="Fraction", params={})},
        )
    )
    assert dist.type_kind == "Distribution"
    assert dist.params["inner"].type_kind == "Fraction"

    other = tc.ast_type_to_pel_type(TypeAnnotation(type_kind="Weird", params={"x": 1}))
    assert other.type_kind == "Weird"


@pytest.mark.unit
def test_typechecker_var_without_type_and_value_defaults_to_fraction() -> None:
    tc = TypeChecker()
    model = Model(name="M", vars=[VarDecl(name="x", type_annotation=None, value=None)])
    out = tc.check_model(model)
    assert out.vars[0].type_annotation is not None
    assert out.vars[0].type_annotation.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_infer_expression_fallback_for_unknown_expression() -> None:
    tc = TypeChecker()
    t = tc.infer_expression(Expression())
    assert t.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_infer_literal_percentage_string_and_unknown_fallback() -> None:
    tc = TypeChecker()

    pct = tc.infer_expression(Literal(value=0.05, literal_type="percentage"))
    assert pct.type_kind == "Fraction"

    s = tc.infer_expression(Literal(value="hi", literal_type="string"))
    assert s.type_kind == "String"

    unk = tc.infer_expression(Literal(value=1, literal_type="weird"))
    assert unk.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_binary_multiply_generic_product_type() -> None:
    tc = TypeChecker()
    tc.env.bind("a", PELType.count("User"))
    tc.env.bind("b", PELType.rate("Month"))

    expr = BinaryOp(operator="*", left=Variable(name="a"), right=Variable(name="b"))
    t = tc.infer_expression(expr)
    assert t.type_kind == "Product"
    assert t.dimension.units == {"count": "User", "rate": "Month"}


@pytest.mark.unit
def test_typechecker_binary_multiply_dimensionless_result_returns_fraction() -> None:
    tc = TypeChecker()
    tc.env.bind("u", PELType.currency("USD"))
    tc.env.bind("v", PELType.currency("USD"))

    # Dimension.multiply has a special-case that returns dimensionless for matching currencies.
    expr = BinaryOp(operator="*", left=Variable(name="u"), right=Variable(name="v"))
    t = tc.infer_expression(expr)
    assert t.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_unary_minus_and_unknown_unary_operator_return_operand_type() -> None:
    tc = TypeChecker()
    tc.env.bind("usd", PELType.currency("USD"))
    tc.env.bind("x", PELType.fraction())

    neg = tc.infer_expression(UnaryOp(operator="-", operand=Variable(name="usd")))
    assert neg.type_kind == "Currency"
    assert neg.dimension.units == {"currency": "USD"}

    other = tc.infer_expression(UnaryOp(operator="?", operand=Variable(name="x")))
    assert other.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_sum_wrong_arity_adds_error_and_sum_scalar_returns_scalar() -> None:
    tc1 = TypeChecker()
    out = tc1.infer_expression(
        FunctionCall(
            function_name="sum",
            arguments=[
                Literal(value=1, literal_type="number"),
                Literal(value=2, literal_type="number"),
            ],
        )
    )
    assert out.type_kind == "Fraction"
    assert tc1.has_errors()
    assert any("sum expects 1 argument" in e.message for e in tc1.get_errors())

    tc2 = TypeChecker()
    out2 = tc2.infer_expression(FunctionCall(function_name="sum", arguments=[Literal(value=1, literal_type="number")]))
    assert out2.type_kind == "Fraction"
    assert not tc2.has_errors()


@pytest.mark.unit
def test_typechecker_types_compatible_currency_dim_mismatch_and_warnings_getter() -> None:
    tc = TypeChecker()
    assert not tc.types_compatible(PELType.currency("USD"), PELType.currency("EUR"))
    assert tc.get_warnings() == []
