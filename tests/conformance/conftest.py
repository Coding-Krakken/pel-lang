"""Pytest configuration and fixtures for conformance tests."""

from pathlib import Path
from typing import Any

import pytest
import yaml


@pytest.fixture
def testcases_dir():
    """Return path to testcases directory."""
    return Path(__file__).parent / "testcases"


@pytest.fixture
def load_yaml_test():
    """Load YAML test case file."""
    def _loader(test_path: Path) -> dict[str, Any]:
        with open(test_path) as f:
            return yaml.safe_load(f)
    return _loader


@pytest.fixture
def pel_compiler():
    """Return PEL compiler instance."""
    from compiler.lexer import Lexer
    from compiler.parser import Parser

    def _compile(source: str):
        """Compile PEL source to AST."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return ast

    return _compile


@pytest.fixture
def pel_lexer():
    """Return PEL lexer for token-level tests."""
    from compiler.lexer import Lexer

    def _tokenize(source: str):
        """Tokenize PEL source."""
        lexer = Lexer(source)
        return lexer.tokenize()

    return _tokenize


@pytest.fixture
def pel_typechecker():
    """Return PEL type checker."""
    from compiler.typechecker import TypeChecker

    def _check(ast):
        """Type check AST."""
        checker = TypeChecker()
        checker.check(ast)
        return ast

    return _check


@pytest.fixture
def pel_runtime():
    """Return PEL runtime instance."""
    from runtime.interpreter import Interpreter

    def _evaluate(ast):
        """Evaluate AST."""
        interpreter = Interpreter()
        return interpreter.evaluate(ast)

    return _evaluate
