from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    Action,
    ArrayLiteral,
    BinaryOp,
    Constraint,
    Distribution,
    Expression,
    FunctionCall,
    IfThenElse,
    Indexing,
    Lambda,
    Literal,
    MemberAccess,
    Policy,
    Provenance,
    Trigger,
    TypeAnnotation,
    UnaryOp,
    Variable,
)
from compiler.ir_generator import IRGenerator


@pytest.mark.unit
def test_ir_generator_extract_dependencies_covers_all_expression_kinds() -> None:
    expr = IfThenElse(
        condition=Variable(name="cond"),
        then_expr=FunctionCall(
            function_name="f",
            arguments=[
                UnaryOp(operator="-", operand=Variable(name="x")),
                Distribution(
                    dist_type="Normal",
                    params={
                        "mu": Variable(name="m"),
                        "sigma": Variable(name="s"),
                    },
                ),
            ],
        ),
        else_expr=MemberAccess(
            expression=Indexing(
                expression=ArrayLiteral(elements=[Variable(name="a"), Variable(name="b")]),
                index=Variable(name="i"),
            ),
            member="field",
        ),
    )

    gen = IRGenerator(source_path="memory")
    deps = set(gen.extract_dependencies(expr))

    # Note: lambda params are not excluded from dependency extraction.
    deps |= set(
        gen.extract_dependencies(
            Lambda(
                params=[("p", TypeAnnotation(type_kind="Fraction"))],
                body=BinaryOp(
                    operator="+",
                    left=Variable(name="p"),
                    right=Variable(name="z"),
                ),
            )
        )
    )

    assert deps.issuperset({"cond", "x", "m", "s", "a", "b", "i", "z"})


@pytest.mark.unit
def test_ir_generator_generate_expression_covers_fallback_unknown() -> None:
    gen = IRGenerator(source_path="memory")

    unknown: Expression = Expression()
    assert gen.generate_expression(unknown) == {"expr_type": "Unknown"}


@pytest.mark.unit
def test_ir_generator_generate_provenance_from_dataclass_includes_optional_fields() -> None:
    prov = Provenance(
        source="unit",
        method="observed",
        confidence=0.9,
        freshness="P30D",
        owner="team",
        notes="n",
    )

    gen = IRGenerator(source_path="memory")
    out = gen.generate_provenance(prov)

    assert out["source"] == "unit"
    assert out["method"] == "observed"
    assert out["confidence"] == 0.9
    assert out["freshness"] == "P30D"
    assert out["owner"] == "team"
    assert out["notes"] == "n"


@pytest.mark.unit
def test_ir_generator_generates_constraint_and_policy_nodes_smoke() -> None:
    gen = IRGenerator(source_path="memory")

    const = Constraint(
        name="c",
        condition=BinaryOp(
            operator="==",
            left=Literal(value=1, literal_type="number"),
            right=Literal(value=1, literal_type="number"),
        ),
        severity="warning",
        message=None,
        scope=None,
    )
    out_c = gen.generate_constraint(const)
    assert out_c["constraint_id"] == "const_c"
    assert out_c["severity"] == "warning"

    policy = Policy(
        name="p",
        trigger=Trigger(trigger_type="condition", condition=Literal(value=True, literal_type="number")),
        action=Action(action_type="assign", target="x", value=Literal(value=2, literal_type="number")),
    )
    out_p = gen.generate_policy(policy)
    assert out_p["policy_id"] == "policy_p"
    assert out_p["action"]["action_type"] == "assign"


@pytest.mark.unit
def test_ir_generator_generate_expression_covers_remaining_expression_kinds() -> None:
    gen = IRGenerator(source_path="memory")

    unary = UnaryOp(operator="-", operand=Literal(value=1, literal_type="number"))
    out_unary = gen.generate_expression(unary)
    assert out_unary["expr_type"] == "UnaryOp"

    call = FunctionCall(function_name="f", arguments=[Literal(value=1, literal_type="number")])
    out_call = gen.generate_expression(call)
    assert out_call["expr_type"] == "FunctionCall"
    assert out_call["function_name"] == "f"

    ite = IfThenElse(
        condition=Literal(value=True, literal_type="boolean"),
        then_expr=Literal(value=1, literal_type="number"),
        else_expr=Literal(value=2, literal_type="number"),
    )
    out_ite = gen.generate_expression(ite)
    assert out_ite["expr_type"] == "IfThenElse"

    arr = ArrayLiteral(elements=[Literal(value=1, literal_type="number")])
    out_arr = gen.generate_expression(arr)
    assert out_arr["expr_type"] == "ArrayLiteral"
    assert len(out_arr["elements"]) == 1

    lam = Lambda(
        params=[("x", TypeAnnotation(type_kind="Fraction"))],
        body=Variable(name="x"),
    )
    out_lam = gen.generate_expression(lam)
    assert out_lam["expr_type"] == "Lambda"
    assert out_lam["params"][0][0] == "x"

    mem = MemberAccess(expression=Variable(name="obj"), member="field")
    out_mem = gen.generate_expression(mem)
    assert out_mem["expr_type"] == "MemberAccess"
    assert out_mem["member"] == "field"
