import pytest

from compiler.ast_nodes import Distribution
from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parse_distribution_named_args() -> None:
    source = "model M { var x = ~Normal(mu=0.12, sigma=0.03) }"
    tokens = Lexer(source).tokenize()
    model = Parser(tokens).parse()

    assert len(model.vars) == 1
    expr = model.vars[0].value
    assert isinstance(expr, Distribution)
    assert expr.dist_type == "Normal"
    assert set(expr.params.keys()) == {"mu", "sigma"}


@pytest.mark.unit
def test_parse_distribution_named_args_with_currency_values() -> None:
    source = "model M { var x = ~LogNormal(mu=$450, sigma=$120) }"
    tokens = Lexer(source).tokenize()
    model = Parser(tokens).parse()

    assert len(model.vars) == 1
    expr = model.vars[0].value
    assert isinstance(expr, Distribution)
    assert expr.dist_type == "LogNormal"
    assert set(expr.params.keys()) == {"mu", "sigma"}
