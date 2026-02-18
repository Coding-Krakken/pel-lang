import pytest

from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parser_accepts_string_type_annotation() -> None:
    source = 'model M {\n  param segment: String = "SMB";\n}\n'

    tokens = Lexer(source).tokenize()
    model = Parser(tokens).parse()

    assert model.params[0].type_annotation is not None
    assert model.params[0].type_annotation.type_kind == "String"
