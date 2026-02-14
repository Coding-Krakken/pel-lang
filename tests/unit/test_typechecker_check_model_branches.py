from __future__ import annotations

import pytest

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_typechecker_check_model_records_param_and_var_mismatches_and_non_boolean_conditions() -> None:
    src = (
        'model M {\n'
        '  param p: Fraction = $1 { source: "s", method: "m", confidence: 0.9 }\n'
        '  var x: Fraction = $1\n'
        '  constraint C: 1 { severity: fatal }\n'
        '  policy P { when: 1, then: x = 1 }\n'
        '}\n'
    )

    model = Parser(Lexer(src).tokenize()).parse()
    tc = TypeChecker()
    tc.check_model(model)

    codes = [e.code for e in tc.get_errors()]
    # param mismatch, var mismatch, constraint non-boolean, policy non-boolean
    assert codes.count("E0100") >= 3


@pytest.mark.unit
def test_typechecker_infer_distribution_uses_first_param_type() -> None:
    model = Parser(Lexer("model M { var d = ~Normal(mu=0.1, sigma=0.2) }").tokenize()).parse()
    expr = model.vars[0].value

    tc = TypeChecker()
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Fraction"


@pytest.mark.unit
def test_typechecker_infer_array_literal_mixed_types_records_error() -> None:
    model = Parser(Lexer("model M { var a = [1, $1] }").tokenize()).parse()
    expr = model.vars[0].value

    tc = TypeChecker()
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Array"
    assert any(e.code == "E0100" for e in tc.get_errors())


@pytest.mark.unit
def test_typechecker_division_falls_back_to_quotient_for_generic_dimensions() -> None:
    model = Parser(Lexer("model M { var q = 1mo / $1 }").tokenize()).parse()
    expr = model.vars[0].value

    tc = TypeChecker()
    inferred = tc.infer_expression(expr)

    assert inferred.type_kind == "Quotient"
