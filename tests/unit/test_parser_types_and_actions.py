from __future__ import annotations

import pytest

from compiler.ast_nodes import Action, Model
from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parser_covers_many_type_annotations_and_var_forms() -> None:
    src = (
        'model M {\n'
        '  var mut a: Fraction\n'
        '  var b: Currency<USD> = $1\n'
        '  var c: Rate per Month = 0.1\n'
        '  var d: Duration = 1mo\n'
        '  var e: Capacity<Compute>\n'
        '  var f: Count<Customer>\n'
        '  var g: TimeSeries<Fraction>\n'
        '  var h: Distribution<Currency<USD>>\n'
        '  var i: CustomType\n'
        '}\n'
    )

    model = Parser(Lexer(src).tokenize()).parse()
    assert isinstance(model, Model)

    names = {v.name for v in model.vars}
    assert {"a", "b", "c", "d", "e", "f", "g", "h", "i"} <= names

    # Spot-check that the Rate per Month parsing worked.
    rate_var = next(v for v in model.vars if v.name == "c")
    assert rate_var.type_annotation is not None
    assert rate_var.type_annotation.type_kind == "Rate"
    assert rate_var.type_annotation.params.get("per") == "Month"


@pytest.mark.unit
def test_parser_action_block_and_fallback_expression_action() -> None:
    src = (
        'model M {\n'
        '  var x = 0\n'
        '  policy P1 { when: 1 == 1, then: { x = 1; emit event("e", a: 1) } }\n'
        '  policy P2 { when: 1 == 1, then: 1 }\n'
        '}\n'
    )

    model = Parser(Lexer(src).tokenize()).parse()
    assert len(model.policies) == 2

    a1 = model.policies[0].action
    assert isinstance(a1, Action)
    assert a1.action_type == "block"
    assert a1.statements is not None
    assert any(s.action_type == "emit_event" for s in a1.statements)

    a2 = model.policies[1].action
    assert a2.action_type == "block"
    assert a2.value is not None


@pytest.mark.unit
def test_parser_provenance_optional_fields_cover_number_and_expression() -> None:
    src = (
        'model M {\n'
        '  param x: Fraction = 1 {\n'
        '    source: "s",\n'
        '    method: "m",\n'
        '    confidence: 0.9,\n'
        '    quality: 0.7,\n'
        '    budget: $10\n'
        '  }\n'
        '}\n'
    )

    model = Parser(Lexer(src).tokenize()).parse()
    prov = model.params[0].provenance
    assert isinstance(prov, dict)
    assert prov["quality"] == 0.7
    # budget is parsed as an expression (currency literal)
    assert "budget" in prov
