from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    ArrayLiteral,
    BinaryOp,
    FunctionCall,
    IfThenElse,
    Indexing,
    Literal,
    UnaryOp,
    Variable,
)
from compiler.errors import TypeError as PELTypeError
from compiler.typechecker import PELType, TypeChecker, TypeEnvironment


@pytest.mark.unit
def test_type_environment_parent_lookup_and_child_scope() -> None:
    parent = TypeEnvironment()
    parent.bind("x", PELType.fraction())

    child = parent.child_scope()
    assert child.lookup("x") is not None
    assert child.lookup("missing") is None


@pytest.mark.unit
def test_peltype_repr_with_and_without_params() -> None:
    assert repr(PELType.fraction()) == "Fraction"
    assert "Currency" in repr(PELType.currency("USD"))


@pytest.mark.unit
def test_typechecker_check_raises_first_error() -> None:
    tc = TypeChecker()
    # Undefined variable should cause an error and `check()` should raise.
    model = type(
        "M",
        (),
        {
            "name": "m",
            "params": [],
            "vars": [],
            "funcs": [],
            "constraints": [],
            "policies": [],
            "statements": [],
        },
    )()

    # Force an error by calling infer_expression on an undefined variable then invoking check().
    tc.infer_expression(Variable(name="nope"))
    with pytest.raises(PELTypeError):
        tc.check(model)  # type: ignore[arg-type]


@pytest.mark.unit
def test_typechecker_infer_literal_currency_symbols_and_default() -> None:
    tc = TypeChecker()

    eur = tc.infer_expression(Literal(value="€1", literal_type="currency"))
    gbp = tc.infer_expression(Literal(value="£1", literal_type="currency"))
    default = tc.infer_expression(Literal(value="¥1", literal_type="currency"))

    assert eur.type_kind == "Currency" and eur.params.get("currency_code") == "EUR"
    assert gbp.type_kind == "Currency" and gbp.params.get("currency_code") == "GBP"
    assert default.type_kind == "Currency" and default.params.get("currency_code") == "USD"


@pytest.mark.unit
def test_typechecker_addition_dimensional_mismatch_records_error() -> None:
    tc = TypeChecker()

    expr = BinaryOp(
        operator="+",
        left=Literal(value="$1", literal_type="currency"),
        right=Literal(value=0.1, literal_type="number"),
    )

    inferred = tc.infer_expression(expr)
    assert inferred.type_kind == "Currency"
    assert any(getattr(e, "code", None) == "E0200" for e in tc.errors)


@pytest.mark.unit
def test_typechecker_duration_times_scalar_preserves_duration() -> None:
    tc = TypeChecker()

    dur = Literal(value="1mo", literal_type="duration")
    scalar = Literal(value=2.0, literal_type="number")

    left = tc.infer_expression(BinaryOp(operator="*", left=dur, right=scalar))
    right = tc.infer_expression(BinaryOp(operator="*", left=scalar, right=dur))

    assert left.type_kind == "Duration"
    assert right.type_kind == "Duration"


@pytest.mark.unit
def test_typechecker_exponent_dimensionless_ok_and_unknown_function_defaults() -> None:
    tc = TypeChecker()

    ok = tc.infer_expression(
        BinaryOp(
            operator="^",
            left=Literal(value=2.0, literal_type="number"),
            right=Literal(value=3.0, literal_type="number"),
        )
    )
    assert ok.type_kind == "Fraction"

    unknown = tc.infer_expression(FunctionCall(function_name="no_such_fn", arguments=[]))
    assert unknown.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_indexing_timeseries_and_array_paths() -> None:
    tc = TypeChecker()

    tc.env.bind("ts", PELType.timeseries(PELType.currency("USD")))
    ts_index = tc.infer_expression(Indexing(expression=Variable(name="ts"), index=Variable(name="t")))
    assert ts_index.type_kind == "Currency"

    arr = ArrayLiteral(elements=[Literal(value="$1", literal_type="currency")])
    arr_index = tc.infer_expression(Indexing(expression=arr, index=Literal(value=0.0, literal_type="number")))
    assert arr_index.type_kind == "Currency"


@pytest.mark.unit
def test_typechecker_array_literal_empty_path() -> None:
    tc = TypeChecker()
    inferred = tc.infer_expression(ArrayLiteral(elements=[]))
    assert inferred.type_kind == "Array"


@pytest.mark.unit
def test_typechecker_unary_not_requires_boolean() -> None:
    tc = TypeChecker()
    inferred = tc.infer_expression(UnaryOp(operator="!", operand=Literal(value=1.0, literal_type="number")))
    assert inferred.type_kind == "Boolean"
    assert any(getattr(e, "code", None) == "E0100" for e in tc.errors)


@pytest.mark.unit
def test_typechecker_if_then_else_mismatch_records_error() -> None:
    tc = TypeChecker()

    expr = IfThenElse(
        condition=Literal(value=1.0, literal_type="number"),
        then_expr=Literal(value=1.0, literal_type="number"),
        else_expr=Literal(value="$1", literal_type="currency"),
    )
    inferred = tc.infer_expression(expr)
    assert inferred.type_kind == "Fraction"
    assert any(getattr(e, "code", None) == "E0100" for e in tc.errors)
