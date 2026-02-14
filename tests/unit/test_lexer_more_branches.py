from __future__ import annotations

import pytest

from compiler.errors import LexicalError
from compiler.lexer import Lexer, TokenType


@pytest.mark.unit
def test_lexer_skips_whitespace_and_line_comments() -> None:
    tokens = Lexer("  // hi\nmodel M { }").tokenize()
    assert tokens[0].type == TokenType.MODEL
    assert tokens[0].value == "model"

    # If the input is only whitespace/comment, tokenization should terminate cleanly.
    tokens2 = Lexer("   // only comment").tokenize()
    assert [t.type for t in tokens2] == [TokenType.EOF]


@pytest.mark.unit
def test_lexer_string_escape_sequences() -> None:
    tokens = Lexer('"a\\n\\t\\"b\\\\c"').tokenize()
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == 'a\n\t"b\\c'

    # Unknown escapes are preserved as backslash+char.
    tokens2 = Lexer('"a\\qb"').tokenize()
    assert tokens2[0].type == TokenType.STRING
    assert tokens2[0].value == "a\\qb"


@pytest.mark.unit
def test_lexer_unterminated_string_raises_lexical_error() -> None:
    with pytest.raises(LexicalError) as ex:
        Lexer('"abc').tokenize()
    assert ex.value.code == "E0003"


@pytest.mark.unit
def test_lexer_unexpected_character_raises_lexical_error() -> None:
    with pytest.raises(LexicalError) as ex:
        Lexer("@").tokenize()
    assert ex.value.code == "E0001"


@pytest.mark.unit
def test_lexer_advance_returns_none_at_end_of_input() -> None:
    lex = Lexer("a")
    assert lex.advance() == "a"
    assert lex.advance() is None


@pytest.mark.unit
def test_lexer_multi_char_operators_are_tokenized() -> None:
    src = "a==b!=c<=d>=e&&f||g->h"
    tokens = Lexer(src).tokenize()
    types = [t.type for t in tokens[:-1]]
    assert types == [
        TokenType.IDENTIFIER,
        TokenType.EQ,
        TokenType.IDENTIFIER,
        TokenType.NE,
        TokenType.IDENTIFIER,
        TokenType.LE,
        TokenType.IDENTIFIER,
        TokenType.GE,
        TokenType.IDENTIFIER,
        TokenType.AND,
        TokenType.IDENTIFIER,
        TokenType.OR,
        TokenType.IDENTIFIER,
        TokenType.ARROW,
        TokenType.IDENTIFIER,
    ]


@pytest.mark.unit
def test_lexer_currency_decimal_and_suffix() -> None:
    tokens = Lexer("$1.25k").tokenize()
    assert tokens[0].type == TokenType.CURRENCY
    assert tokens[0].value == "$1.25k"


@pytest.mark.unit
def test_lexer_percentage_literal_and_percent_operator() -> None:
    tokens1 = Lexer("5%" ).tokenize()
    assert tokens1[0].type == TokenType.PERCENTAGE
    assert tokens1[0].value == "5%"

    tokens2 = Lexer("%" ).tokenize()
    assert tokens2[0].type == TokenType.PERCENT
    assert tokens2[0].value == "%"


@pytest.mark.unit
def test_lexer_caret_and_not_tokens() -> None:
    tokens = Lexer("^!").tokenize()
    assert [t.type for t in tokens[:-1]] == [TokenType.CARET, TokenType.NOT]
