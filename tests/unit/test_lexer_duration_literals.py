import pytest

from compiler.lexer import Lexer, TokenType


@pytest.mark.unit
@pytest.mark.parametrize(
    "literal",
    [
        "1mo",
        "30d",
        "2w",
        "1q",
        "1yr",
    ],
)
def test_duration_literals_tokenize_as_duration(literal: str) -> None:
    tokens = Lexer(literal).tokenize()
    assert tokens[0].type == TokenType.DURATION
    assert tokens[0].value == literal
    assert tokens[-1].type == TokenType.EOF


def test_duration_literal_does_not_split_into_number_and_identifier() -> None:
    tokens = Lexer("1mo").tokenize()
    assert [t.type for t in tokens[:-1]] == [TokenType.DURATION]


def test_number_suffix_m_is_still_supported() -> None:
    tokens = Lexer("1m").tokenize()
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == "1m"


def test_rate_per_duration_token_stream() -> None:
    tokens = Lexer("$500/1mo").tokenize()
    assert [t.type for t in tokens[:-1]] == [TokenType.CURRENCY, TokenType.SLASH, TokenType.DURATION]
    assert tokens[2].value == "1mo"
