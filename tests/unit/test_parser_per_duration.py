import pytest

from compiler.ast_nodes import BinaryOp, Literal
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_parse_currency_div_duration_expression() -> None:
    source = "model M { var rate = $500/1mo }"
    tokens = Lexer(source).tokenize()
    model = Parser(tokens).parse()

    assert len(model.vars) == 1
    expr = model.vars[0].value
    assert isinstance(expr, BinaryOp)
    assert expr.operator == "/"
    assert isinstance(expr.left, Literal)
    assert expr.left.literal_type == "currency"
    assert isinstance(expr.right, Literal)
    assert expr.right.literal_type == "duration"
    assert expr.right.value == "1mo"


@pytest.mark.unit
@pytest.mark.parametrize(
    "duration,expected_per",
    [
        ("1d", "Day"),
        ("2w", "Week"),
        ("1mo", "Month"),
        ("1q", "Quarter"),
        ("1yr", "Year"),
    ],
)
def test_typecheck_currency_div_duration_infers_rate(duration: str, expected_per: str) -> None:
    source = f"model M {{ var rate = $500/{duration} }}"
    tokens = Lexer(source).tokenize()
    model = Parser(tokens).parse()

    checker = TypeChecker()
    typed = checker.check_model(model)
    assert not checker.has_errors(), [str(e) for e in checker.get_errors()]

    var = typed.vars[0]
    assert var.type_annotation is not None
    assert var.type_annotation.type_kind == "Rate"
    assert var.type_annotation.params.get("per") == expected_per
