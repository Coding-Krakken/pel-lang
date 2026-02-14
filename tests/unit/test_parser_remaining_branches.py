from __future__ import annotations

import pytest

from compiler.ast_nodes import (
    IfThenElse,
    Lambda,
    Literal,
    MemberAccess,
    UnaryOp,
)
from compiler.errors import ParseError
from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parser_param_list_multiple_params_covers_loop() -> None:
    src = "model M { func f(x: Fraction, y: Currency<USD>) -> Fraction { x } }"
    model = Parser(Lexer(src).tokenize()).parse()
    fn = model.funcs[0]
    assert len(fn.parameters) == 2


@pytest.mark.unit
def test_parser_statement_if_falls_back_to_if_expression_when_not_followed_by_block() -> None:
    src = "model M { if 1 == 1 then 1 else 2; }"
    model = Parser(Lexer(src).tokenize()).parse()
    # parse_statement falls back to expression statement => placeholder assignment
    assert len(model.statements) == 1


@pytest.mark.unit
def test_parser_type_error_branch_raises_syntax_error() -> None:
    src = "model M { var x: = 1 }"
    with pytest.raises(ParseError) as exc:
        Parser(Lexer(src).tokenize()).parse()
    assert exc.value.code == "E0701"


@pytest.mark.unit
def test_parser_member_access_and_percentage_literal() -> None:
    src = "model M { var p = 5% var y = x.y }"
    model = Parser(Lexer(src).tokenize()).parse()

    p_expr = model.vars[0].value
    assert isinstance(p_expr, Literal)
    assert p_expr.literal_type == "percentage"
    assert p_expr.value == 0.05

    y_expr = model.vars[1].value
    assert isinstance(y_expr, MemberAccess)
    assert y_expr.member == "y"


@pytest.mark.unit
def test_parser_lambda_with_params_and_if_expression() -> None:
    src = "model M { var f = (x: Fraction) -> x var a = if 1 == 1 then 1 else 2 }"
    model = Parser(Lexer(src).tokenize()).parse()

    lam = model.vars[0].value
    assert isinstance(lam, Lambda)
    assert len(lam.params) == 1

    ite = model.vars[1].value
    assert isinstance(ite, IfThenElse)


@pytest.mark.unit
def test_parser_function_call_multiple_args_and_emit_trailing_comma() -> None:
    src = (
        "model M {\n"
        '  policy P { when: 1 == 1, then: emit event("e",) }\n'
        "  var x = f(1, 2)\n"
        "}\n"
    )
    model = Parser(Lexer(src).tokenize()).parse()
    call = model.vars[0].value
    assert hasattr(call, "arguments") and len(call.arguments) == 2


@pytest.mark.unit
def test_parser_provenance_and_constraint_trailing_commas_and_generic_fields() -> None:
    src = (
        "model M {\n"
        '  param x: Fraction = 1 { source: "s", method: "m", confidence: 0.9, }\n'
        "  constraint C: 1 == 1 { severity: fatal, slack: 1, }\n"
        "}\n"
    )
    model = Parser(Lexer(src).tokenize()).parse()
    prov = model.params[0].provenance
    assert isinstance(prov, dict)

    # slack is parsed as a generic expression field in constraint metadata
    assert model.constraints[0].scope is None


@pytest.mark.unit
def test_parser_correlated_with_trailing_comma_and_scope_all_timesteps() -> None:
    src = (
        "model M {\n"
        "  param x: Fraction = 1 {\n"
        '    source: "s",\n'
        '    method: "m",\n'
        "    confidence: 0.9,\n"
        '    correlated_with: [("y", 0.1),]\n'
        "  }\n"
        "  constraint C: 1 == 1 { severity: fatal, for: all timesteps }\n"
        "}\n"
    )
    model = Parser(Lexer(src).tokenize()).parse()
    assert model.params[0].provenance["correlated_with"] == [("y", 0.1)]
    assert model.constraints[0].scope == "all timesteps"


@pytest.mark.unit
def test_parser_unary_minus_and_not_cover_primary_unary_branch() -> None:
    # Note: parser currently doesn't handle TRUE/FALSE literals.
    src = "model M { var a = -1 var x = 1 var b = !x }"
    model = Parser(Lexer(src).tokenize()).parse()

    a_expr = model.vars[0].value
    assert isinstance(a_expr, UnaryOp)
    assert a_expr.operator == "-"

    b_expr = model.vars[2].value
    assert isinstance(b_expr, UnaryOp)
    assert b_expr.operator == "!"


@pytest.mark.unit
def test_parser_primary_expression_unexpected_token_raises_syntax_error() -> None:
    src = "model M { var x = ; }"
    with pytest.raises(ParseError) as exc:
        Parser(Lexer(src).tokenize()).parse()
    assert exc.value.code == "E0701"


@pytest.mark.unit
def test_parser_paren_or_lambda_backtracks_and_then_errors_when_missing_arrow() -> None:
    # This triggers the (x: T) lambda parse attempt, fails at expecting '->',
    # hits the backtracking branch, and then fails overall.
    src = "model M { var x = (y: Fraction) }"
    with pytest.raises(ParseError) as exc:
        Parser(Lexer(src).tokenize()).parse()
    assert exc.value.code == "E0700"


@pytest.mark.unit
def test_parser_constraint_metadata_invalid_field_name_token_raises() -> None:
    src = "model M { constraint C: 1 == 1 { severity: fatal, 1: 2 } }"
    with pytest.raises(ParseError) as exc:
        Parser(Lexer(src).tokenize()).parse()
    assert exc.value.code == "E0700"


@pytest.mark.unit
def test_parser_scope_spec_breaks_on_non_identifier_and_leaves_token() -> None:
    src = "model M { constraint C: 1 == 1 { severity: fatal, for: all timesteps 1 } }"
    with pytest.raises(ParseError) as exc:
        Parser(Lexer(src).tokenize()).parse()
    assert exc.value.code == "E0700"
