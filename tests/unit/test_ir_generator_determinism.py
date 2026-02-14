import pytest

from compiler.ir_generator import IRGenerator
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


@pytest.mark.unit
def test_ir_generator_model_hash_stable_across_runs() -> None:
    src = (
        "model M {\n"
        "  param x: Fraction = 0.1 {\n"
        '    source: "unit",\n'
        '    method: "observed",\n'
        "    confidence: 1\n"
        "  }\n"
        "  var y: Fraction = x + 0.2\n"
        "}\n"
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)

    ir1 = IRGenerator(source_path="memory").generate(typed)
    ir2 = IRGenerator(source_path="memory").generate(typed)

    assert ir1["metadata"]["model_hash"] == ir2["metadata"]["model_hash"]


@pytest.mark.unit
def test_ir_generator_compiled_at_is_utc_z_timestamp() -> None:
    src = (
        "model M {\n"
        "  param x: Fraction = 0.1 {\n"
        '    source: "unit",\n'
        '    method: "observed",\n'
        "    confidence: 1\n"
        "  }\n"
        "}\n"
    )
    tokens = Lexer(src).tokenize()
    model = Parser(tokens).parse()
    typed = TypeChecker().check(model)

    ir = IRGenerator(source_path="memory").generate(typed)
    compiled_at = ir["metadata"]["compiled_at"]
    assert isinstance(compiled_at, str)
    assert compiled_at.endswith("Z")
