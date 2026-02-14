import pytest

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_fraction_div_duration_infers_rate() -> None:
    src = """
model m {
  param x: Rate per Month = 0.30/1mo {
    source: "unit",
    method: "unit",
    confidence: 1
  }
}
"""
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    tc = TypeChecker()
    tc.check(model)

    x_decl = next(p for p in model.params if p.name == "x")
    inferred = tc.infer_expression(x_decl.value)
    assert inferred.type_kind == "Rate"
    assert inferred.params.get("per") == "Month"
