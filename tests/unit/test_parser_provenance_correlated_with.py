import pytest

from compiler.lexer import Lexer
from compiler.parser import Parser


@pytest.mark.unit
def test_parse_provenance_correlated_with_allows_negative_coefficients() -> None:
    source = (
        'model M {\n'
        '  param x: Rate per Month = 0.1 {\n'
        '    source: "s",\n'
        '    method: "m",\n'
        '    confidence: 0.9,\n'
        '    correlated_with: [("y", -0.4), ("z", 0.6)]\n'
        '  }\n'
        '}\n'
    )

    tokens = Lexer(source).tokenize()
    model = Parser(tokens).parse()

    assert len(model.params) == 1
    prov = model.params[0].provenance
    from compiler.ast_nodes import Provenance
    assert isinstance(prov, Provenance)
    assert prov.correlated_with == [("y", -0.4), ("z", 0.6)]
