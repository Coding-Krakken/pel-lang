from pathlib import Path

import pytest

from compiler.lexer import Lexer
from compiler.parser import Parser

BENCH_DIR = Path(__file__).parent.parent / "benchmarks" / "pel_100"


@pytest.mark.parametrize("pel_file", sorted(BENCH_DIR.rglob("*.pel")))
def test_benchmark_models_compile(pel_file: Path):
    """All benchmark PEL files should parse to an AST without errors."""
    source = pel_file.read_text()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert ast is not None
