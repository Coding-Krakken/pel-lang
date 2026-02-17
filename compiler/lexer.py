# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
PEL Lexer - Tokenization
Converts source code to sequence of tokens
"""

import re
from dataclasses import dataclass
from enum import Enum, auto

from compiler.errors import (
    SourceLocation,
    lexical_error,
    unterminated_string,
)


class TokenType(Enum):
    """Token types from PEL grammar."""

    # Literals
    NUMBER = auto()
    STRING = auto()
    CURRENCY = auto()  # $100
    PERCENTAGE = auto()  # 5%
    DURATION = auto()  # 30d
    TRUE = auto()  # true
    FALSE = auto()  # false

    # Keywords
    MODEL = auto()
    PARAM = auto()
    VAR = auto()
    MUT = auto()  # mut (mutable)
    FUNC = auto()
    CONSTRAINT = auto()
    POLICY = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    FOR = auto()
    WHEN = auto()
    PER = auto()  # per (Rate per Month)
    IMPORT = auto()
    AS = auto()
    EMIT = auto()
    EVENT = auto()
    RETURN = auto()
    SIMULATE = auto()

    # Types
    CURRENCY_TYPE = auto()  # Currency
    RATE_TYPE = auto()  # Rate
    DURATION_TYPE = auto()  # Duration
    CAPACITY_TYPE = auto()  # Capacity
    COUNT_TYPE = auto()  # Count
    FRACTION_TYPE = auto()  # Fraction
    TIMESERIES_TYPE = auto()  # TimeSeries
    DISTRIBUTION_TYPE = auto()  # Distribution

    # Operators
    PLUS = auto()  # +
    MINUS = auto()  # -
    STAR = auto()  # *
    SLASH = auto()  # /
    PERCENT = auto()  # %
    CARET = auto()  # ^
    TILDE = auto()  # ~

    # Comparisons
    EQ = auto()  # ==
    NE = auto()  # !=
    LT = auto()  # <
    LE = auto()  # <=
    GT = auto()  # >
    GE = auto()  # >=

    # Logical
    AND = auto()  # &&
    OR = auto()  # ||
    NOT = auto()  # !

    # Punctuation
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COLON = auto()  # :
    SEMICOLON = auto()  # ;
    COMMA = auto()  # ,
    DOT = auto()  # .
    ASSIGN = auto()  # =
    ARROW = auto()  # ->

    # Special
    IDENTIFIER = auto()
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    """Single lexical token."""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class Lexer:
    """
    Tokenize PEL source code.

    Implements lexical rules from spec/pel_language_spec.md
    """

    KEYWORDS = {
        "model": TokenType.MODEL,
        "param": TokenType.PARAM,
        "var": TokenType.VAR,
        "mut": TokenType.MUT,
        "func": TokenType.FUNC,
        "constraint": TokenType.CONSTRAINT,
        "policy": TokenType.POLICY,
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "else": TokenType.ELSE,
        "for": TokenType.FOR,
        "when": TokenType.WHEN,
        "per": TokenType.PER,
        "import": TokenType.IMPORT,
        "as": TokenType.AS,
        "emit": TokenType.EMIT,
        "event": TokenType.EVENT,
        "return": TokenType.RETURN,
        "simulate": TokenType.SIMULATE,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        # Types
        "Currency": TokenType.CURRENCY_TYPE,
        "Rate": TokenType.RATE_TYPE,
        "Duration": TokenType.DURATION_TYPE,
        "Capacity": TokenType.CAPACITY_TYPE,
        "Count": TokenType.COUNT_TYPE,
        "Fraction": TokenType.FRACTION_TYPE,
        "TimeSeries": TokenType.TIMESERIES_TYPE,
        "Distribution": TokenType.DISTRIBUTION_TYPE,
    }

    # Longest units first so "day" matches before "d"
    DURATION_UNITS = ("mo", "yr", "day", "d", "q", "w")

    def __init__(self, source: str, filename: str = "<input>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def current_location(self) -> SourceLocation:
        return SourceLocation(self.filename, self.line, self.column)

    def peek(self, offset: int = 0) -> str | None:
        """Peek at character without consuming."""
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else None

    def advance(self) -> str | None:
        """Consume and return current character."""
        if self.pos >= len(self.source):
            return None

        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self) -> None:
        """Skip spaces and tabs (not newlines)."""
        while True:
            ch = self.peek()
            if ch is None or ch not in " \t":
                break
            self.advance()

    def skip_comment(self) -> None:
        """Skip // comments."""
        if self.peek() == "/" and self.peek(1) == "/":
            while True:
                ch = self.peek()
                if ch is None or ch == "\n":
                    break
                self.advance()

    def read_number(self) -> Token:
        """Read number literal (integer or decimal)."""
        start_line, start_col = self.line, self.column
        num_str = ""

        # Integer part (allow '_' as a separator).
        while True:
            ch = self.peek()
            if ch is None or not (ch.isdigit() or ch == "_"):
                break
            num_str += ch
            self.advance()

        # Decimal part: only treat '.' as decimal if followed by a digit.
        # This avoids lexing `0..time_horizon` as NUMBER("0.."), which should be
        # NUMBER("0") DOT DOT IDENTIFIER(...).
        p1 = self.peek(1)
        if self.peek() == "." and p1 is not None and p1.isdigit():
            # consume '.'
            num_str += self.advance() or ""
            while True:
                ch = self.peek()
                if ch is None or not (ch.isdigit() or ch == "_"):
                    break
                num_str += ch
                self.advance()

        # Check for numeric suffix (k, m, M, B, T)
        # NOTE: 'd' is reserved for duration literals (e.g., 30d).
        ch = self.peek()
        if ch is not None and ch in "kmМMBТ":
            num_str += self.advance() or ""

        # Percentage literal (e.g., 5%)
        ch = self.peek()
        if ch == "%":
            self.advance()
            return Token(TokenType.PERCENTAGE, num_str + "%", start_line, start_col)

        return Token(TokenType.NUMBER, num_str, start_line, start_col)

    def read_number_or_duration(self) -> Token:
        """Read either a duration literal (e.g., 30d, 1mo) or a number literal."""
        start_line, start_col = self.line, self.column

        # Duration literals are integer + unit, and must be delimited (not followed by identifier chars).
        # Match longest units first to avoid consuming 'm' as numeric suffix when 'mo' is intended.
        remaining = self.source[self.pos :]
        unit_pattern = "|".join(self.DURATION_UNITS)
        match = re.match(rf"(\d+)({unit_pattern})(?![A-Za-z0-9_])", remaining)
        if match:
            literal = match.group(0)
            for _ in range(len(literal)):
                self.advance()
            return Token(TokenType.DURATION, literal, start_line, start_col)

        # Fallback: ordinary number literal (may include decimals and numeric suffixes)
        return self.read_number()

    def read_currency(self) -> Token:
        """Read currency literal ($100, €50)."""
        start_line, start_col = self.line, self.column
        symbol = self.advance() or ""  # $, €, £, ¥

        # Read amount
        amount = ""
        while True:
            ch = self.peek()
            if ch is None or not (ch.isdigit() or ch == "_"):
                break
            amount += ch
            self.advance()

        p1 = self.peek(1)
        if self.peek() == "." and p1 is not None and p1.isdigit():
            amount += self.advance() or ""  # '.'
            while True:
                ch = self.peek()
                if ch is None or not (ch.isdigit() or ch == "_"):
                    break
                amount += ch
                self.advance()

        # Check for unit suffix (k, m, M, B)
        ch = self.peek()
        if ch is not None and ch in "kmМMBТ":
            amount += self.advance() or ""

        value = symbol + amount
        return Token(TokenType.CURRENCY, value, start_line, start_col)

    def read_identifier(self) -> Token:
        """Read identifier or keyword."""
        start_line, start_col = self.line, self.column
        ident = ""

        while True:
            ch = self.peek()
            if ch is None or not (ch.isalnum() or ch in "_"):
                break
            ident += ch
            self.advance()

        # Check if keyword
        token_type = self.KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, start_line, start_col)

    def read_string(self) -> Token:
        """Read string literal."""
        start_line, start_col = self.line, self.column
        quote = self.advance()  # " or '

        string_val = ""
        while True:
            ch = self.peek()
            if ch is None or ch == quote:
                break
            char = self.advance() or ""
            if char == "\\":
                next_ch = self.peek()
                if next_ch is None:
                    break
                next_char = self.advance() or ""
                if next_char == "n":
                    string_val += "\n"
                elif next_char == "t":
                    string_val += "\t"
                elif next_char in "\"\\'":
                    string_val += next_char
                else:
                    string_val += "\\" + next_char
            else:
                string_val += char

        if self.peek() != quote:
            raise unterminated_string(self.current_location())

        self.advance()  # Closing quote
        return Token(TokenType.STRING, string_val, start_line, start_col)

    def tokenize(self) -> list[Token]:
        """Tokenize entire source."""
        while self.pos < len(self.source):
            self.skip_whitespace()
            self.skip_comment()

            char = self.peek()
            if char is None:
                break

            # Newlines (statement terminators)
            if char == "\n":
                self.advance()
                continue

            # Currency literals
            if char in "$€£¥":
                self.tokens.append(self.read_currency())

            # Numbers
            elif char.isdigit():
                self.tokens.append(self.read_number_or_duration())

            # Identifiers and keywords
            elif char.isalpha() or char == "_":
                self.tokens.append(self.read_identifier())

            # Strings
            elif char in "\"'":
                self.tokens.append(self.read_string())

            # Operators (two-char first)
            elif char == "=" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQ, "==", self.line, self.column - 2))
            elif char == "!" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NE, "!=", self.line, self.column - 2))
            elif char == "<" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LE, "<=", self.line, self.column - 2))
            elif char == ">" and self.peek(1) == "=":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GE, ">=", self.line, self.column - 2))
            elif char == "&" and self.peek(1) == "&":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.AND, "&&", self.line, self.column - 2))
            elif char == "|" and self.peek(1) == "|":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.OR, "||", self.line, self.column - 2))
            elif char == "-" and self.peek(1) == ">":
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, "->", self.line, self.column - 2))

            # Single-char operators
            elif char == "+":
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, "+", self.line, self.column - 1))
            elif char == "-":
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, "-", self.line, self.column - 1))
            elif char == "*":
                self.advance()
                self.tokens.append(Token(TokenType.STAR, "*", self.line, self.column - 1))
            elif char == "/":
                self.advance()
                self.tokens.append(Token(TokenType.SLASH, "/", self.line, self.column - 1))
            elif char == "%":
                self.advance()
                self.tokens.append(Token(TokenType.PERCENT, "%", self.line, self.column - 1))
            elif char == "^":
                self.advance()
                self.tokens.append(Token(TokenType.CARET, "^", self.line, self.column - 1))
            elif char == "~":
                self.advance()
                self.tokens.append(Token(TokenType.TILDE, "~", self.line, self.column - 1))
            elif char == "<":
                self.advance()
                self.tokens.append(Token(TokenType.LT, "<", self.line, self.column - 1))
            elif char == ">":
                self.advance()
                self.tokens.append(Token(TokenType.GT, ">", self.line, self.column - 1))
            elif char == "!":
                self.advance()
                self.tokens.append(Token(TokenType.NOT, "!", self.line, self.column - 1))

            # Punctuation
            elif char == "(":
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, "(", self.line, self.column - 1))
            elif char == ")":
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ")", self.line, self.column - 1))
            elif char == "{":
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, "{", self.line, self.column - 1))
            elif char == "}":
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, "}", self.line, self.column - 1))
            elif char == "[":
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, "[", self.line, self.column - 1))
            elif char == "]":
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, "]", self.line, self.column - 1))
            elif char == ":":
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ":", self.line, self.column - 1))
            elif char == ";":
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ";", self.line, self.column - 1))
            elif char == ",":
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ",", self.line, self.column - 1))
            elif char == ".":
                self.advance()
                self.tokens.append(Token(TokenType.DOT, ".", self.line, self.column - 1))
            elif char == "=":
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, "=", self.line, self.column - 1))

            else:
                raise lexical_error(f"Unexpected character: '{char}'", self.current_location())

        # EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
