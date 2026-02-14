import pytest

from compiler.lexer import Lexer, TokenType


@pytest.mark.unit
def test_range_operator_does_not_get_lexed_into_number() -> None:
    tokens = Lexer("0..time_horizon").tokenize()
    assert [t.type for t in tokens[:-1]] == [
        TokenType.NUMBER,
        TokenType.DOT,
        TokenType.DOT,
        TokenType.IDENTIFIER,
    ]
    assert tokens[0].value == "0"
    assert tokens[3].value == "time_horizon"
