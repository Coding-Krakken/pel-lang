import pytest

from compiler.ast_nodes import Literal, Model, ParamDecl, TypeAnnotation
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.errors import ParseError
from compiler.provenance_checker import ProvenanceChecker
from compiler.typechecker import TypeChecker


def _parse_model(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


@pytest.mark.unit
def test_param_without_provenance_block_is_parse_error() -> None:
    with pytest.raises(ParseError):
        _parse_model("model M { param x: Fraction = 0.1 }")


@pytest.mark.unit
def test_provenance_missing_required_fields_is_parse_error() -> None:
    with pytest.raises(ParseError):
        _parse_model(
            'model M {\n'
            '  param x: Fraction = 0.1 {\n'
            '    source: "s",\n'
            '  }\n'
            '}\n'
        )


@pytest.mark.unit
def test_provenance_confidence_out_of_range_is_error() -> None:
    model = _parse_model(
        'model M {\n'
        '  param x: Fraction = 0.1 {\n'
        '    source: "s",\n'
        '    method: "observed",\n'
        '    confidence: 1.5\n'
        '  }\n'
        '}\n'
    )
    typed = TypeChecker().check(model)

    checker = ProvenanceChecker()
    checker.check(typed)
    assert checker.has_errors()
    assert any("confidence must be in range" in e.message for e in checker.get_errors())


@pytest.mark.unit
def test_provenance_invalid_method_is_error() -> None:
    model = _parse_model(
        'model M {\n'
        '  param x: Fraction = 0.1 {\n'
        '    source: "s",\n'
        '    method: "not_a_method",\n'
        '    confidence: 0.9\n'
        '  }\n'
        '}\n'
    )
    typed = TypeChecker().check(model)

    checker = ProvenanceChecker()
    checker.check(typed)
    assert checker.has_errors()
    assert any("method must be one of" in e.message for e in checker.get_errors())


@pytest.mark.unit
def test_provenance_checker_empty_model_leaves_score_unchanged() -> None:
    checker = ProvenanceChecker()
    model = Model(name="M")
    checker.check(model)
    assert checker.get_completeness_score() == 0.0
    assert not checker.has_errors()


@pytest.mark.unit
def test_provenance_checker_missing_block_is_error_for_manual_ast() -> None:
    checker = ProvenanceChecker()
    param = ParamDecl(
        name="x",
        type_annotation=TypeAnnotation(type_kind="Fraction"),
        value=Literal(0.1),
        provenance=None,
    )
    model = Model(name="M", params=[param])
    checker.check(model)
    assert checker.has_errors()
    assert any("missing provenance block" in e.message for e in checker.get_errors())


@pytest.mark.unit
def test_provenance_checker_method_and_confidence_type_validation() -> None:
    checker = ProvenanceChecker()
    param = ParamDecl(
        name="x",
        type_annotation=TypeAnnotation(type_kind="Fraction"),
        value=Literal(0.1),
        provenance={
            "source": "unit",
            "method": "",
            "confidence": "not-a-number",
        },
    )
    model = Model(name="M", params=[param])
    checker.check(model)
    assert checker.has_errors()
    msgs = [e.message for e in checker.get_errors()]
    assert any("method must be a non-empty string" in m for m in msgs)
    assert any("confidence must be a number" in m for m in msgs)


@pytest.mark.unit
def test_provenance_checker_counts_recommended_fields_in_score() -> None:
    checker = ProvenanceChecker()
    param = ParamDecl(
        name="x",
        type_annotation=TypeAnnotation(type_kind="Fraction"),
        value=Literal(0.1),
        provenance={
            "source": "unit",
            "method": "observed",
            "confidence": 1,
            "freshness": "2026-01-01",
            "owner": "team",
        },
    )
    model = Model(name="M", params=[param])
    checker.check(model)
    assert not checker.has_errors()
    assert checker.get_completeness_score() == 1.0


@pytest.mark.unit
def test_provenance_checker_missing_required_field_branch_is_covered() -> None:
    checker = ProvenanceChecker()
    param = ParamDecl(
        name="x",
        type_annotation=TypeAnnotation(type_kind="Fraction"),
        value=Literal(0.1),
        provenance={
            "source": "unit",
            # missing "method"
            "confidence": 1,
        },
    )
    model = Model(name="M", params=[param])
    checker.check(model)
    assert checker.has_errors()
    assert any("missing required provenance field" in e.message for e in checker.get_errors())
