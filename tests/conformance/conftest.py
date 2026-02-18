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
    """Return PEL compiler instance.

    NOTE: this fixture performs parsing and *lightweight* static checks so
    conformance tests that expect compile-time detection of certain runtime
    errors (e.g. division by zero in constant expressions) will fail early.
    """
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    from compiler.typechecker import TypeChecker

    def _compile(source: str):
        """Compile PEL source to AST (parser + lightweight static checks)."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Run type checker to catch static/runtime-detectable errors early
        checker = TypeChecker()
        # If checking fails this will raise — conformance tests expect that.
        try:
            checker.check(ast)
        except Exception:
            # Re-raise so conformance harness can inspect the message
            raise

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
