from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    ArrayLiteral,
    BinaryOp,
    Distribution,
    FuncDecl,
    FunctionCall,
)
from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parser_function_decl_uses_parse_block() -> None:
    src = (
        "model M {\n"
        "  func f(x: Fraction) -> Fraction { x + 1; x + 2 }\n"
        "}\n"
    )

    model = Parser(Lexer(src).tokenize()).parse()
    assert len(model.funcs) == 1
    fn = model.funcs[0]
    assert isinstance(fn, FuncDecl)
    # Function body is now a BlockExpr
    from compiler.ast_nodes import BlockExpr
    assert isinstance(fn.body, BlockExpr)
    assert len(fn.body.statements) == 2


@pytest.mark.unit
def test_parser_distribution_can_have_empty_params_and_trailing_comma() -> None:
    m1 = Parser(Lexer("model M { var x = ~Normal() }").tokenize()).parse()
    d1 = m1.vars[0].value
    assert isinstance(d1, Distribution)
    assert d1.params == {}

    m2 = Parser(Lexer("model M { var x = ~Normal(mu=0.1,) }").tokenize()).parse()
    d2 = m2.vars[0].value
    assert isinstance(d2, Distribution)
    assert set(d2.params.keys()) == {"mu"}


@pytest.mark.unit
def test_parser_array_literal_empty_and_trailing_comma() -> None:
    m1 = Parser(Lexer("model M { var xs = [] }").tokenize()).parse()
    xs1 = m1.vars[0].value
    assert isinstance(xs1, ArrayLiteral)
    assert xs1.elements == []

    m2 = Parser(Lexer("model M { var xs = [1, 2,] }").tokenize()).parse()
    xs2 = m2.vars[0].value
    assert isinstance(xs2, ArrayLiteral)
    assert len(xs2.elements) == 2


@pytest.mark.unit
def test_parser_function_call_trailing_comma() -> None:
    model = Parser(Lexer("model M { var x = f(1,) }").tokenize()).parse()
    call = model.vars[0].value
    assert isinstance(call, FunctionCall)
    assert len(call.arguments) == 1


@pytest.mark.unit
def test_parser_emit_action_with_no_args() -> None:
    src = 'model M { policy P { when: 1 == 1, then: emit event("e") } }'
    model = Parser(Lexer(src).tokenize()).parse()
    action = model.policies[0].action
    assert action.action_type == "emit_event"
    assert action.event_name == "e"
    assert action.args == {}


@pytest.mark.unit
def test_parser_scope_spec_as_expression() -> None:
    src = 'model M { constraint C: 1 == 1 { severity: fatal, for: t >= 1 } }'
    model = Parser(Lexer(src).tokenize()).parse()
    scope = model.constraints[0].scope
    assert scope is not None
    # In this parser, non-"all ..." scopes are stored as an expression.
    assert isinstance(scope, BinaryOp)
    assert scope.operator == ">="
