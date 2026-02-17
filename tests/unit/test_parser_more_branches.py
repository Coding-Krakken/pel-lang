from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    Action,
    Assignment,
    BlockExpr,
    Constraint,
    IfStmt,
    Lambda,
    Literal,
    Policy,
    Variable,
)
from compiler.errors import ParseError
from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parser_rejects_invalid_model_item_token() -> None:
    tokens = Lexer("model M { 1 }").tokenize()
    with pytest.raises(ParseError) as ex:
        Parser(tokens).parse()
    assert ex.value.code == "E0701"


@pytest.mark.unit
def test_parser_parses_lambda_with_no_params() -> None:
    src = "model M { var f = () -> 1 }"
    model = Parser(Lexer(src).tokenize()).parse()
    expr = model.vars[0].value
    assert isinstance(expr, Lambda)
    assert expr.params == []


@pytest.mark.unit
def test_parser_parses_policy_emit_event_action_and_constraint_scope_all_timesteps() -> None:
    src = (
        'model M {\n'
        '  constraint c: 1 == 1 { severity: warning, for: all timesteps, message: "m" }\n'
        '  policy p {\n'
        '    when: 1 == 1,\n'
        '    then: emit event("e", x: 1)\n'
        '  }\n'
        '}\n'
    )

    model = Parser(Lexer(src).tokenize()).parse()

    assert len(model.constraints) == 1
    c = model.constraints[0]
    assert isinstance(c, Constraint)
    assert c.severity == "warning"
    assert c.message == "m"
    assert c.scope == "all timesteps"

    assert len(model.policies) == 1
    p = model.policies[0]
    assert isinstance(p, Policy)
    assert isinstance(p.action, Action)
    assert p.action.action_type == "emit_event"
    assert p.action.event_name == "e"
    assert "x" in p.action.args


@pytest.mark.unit
def test_parser_parses_if_statement_inside_block_expression() -> None:
    src = (
        'model M {\n'
        '  var x = {\n'
        '    if 1 < 2 { return 1 } else { return 2 }\n'
        '  }\n'
        '}\n'
    )

    model = Parser(Lexer(src).tokenize()).parse()
    value = model.vars[0].value
    assert isinstance(value, BlockExpr)
    assert len(value.statements) == 1
    assert isinstance(value.statements[0], IfStmt)
    assert value.statements[0].else_body is not None


@pytest.mark.unit
def test_parser_expression_statement_becomes_placeholder_assignment() -> None:
    src = "model M { x; }"
    model = Parser(Lexer(src).tokenize()).parse()

    assert len(model.statements) == 1
    stmt = model.statements[0]
    assert isinstance(stmt, Assignment)
    assert isinstance(stmt.target, Variable)
    assert stmt.target.name == "_"
    assert isinstance(stmt.value, Literal)


@pytest.mark.unit
def test_parser_for_stmt_requires_in_keyword() -> None:
    src = "model M { for t of 0..1 { return 1 } }"
    with pytest.raises(ParseError) as ex:
        Parser(Lexer(src).tokenize()).parse()
    assert ex.value.code == "E0701"
