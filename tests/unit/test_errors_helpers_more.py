from __future__ import annotations

import pytest

from compiler.errors import (
    CompilerError,
    InternalError,
    SourceLocation,
    contradictory_constraints,
    correlation_matrix_not_psd,
    currency_mismatch,
    cyclic_dependency,
    dimensional_mismatch,
    future_reference,
    invalid_confidence,
    invalid_constraint_condition,
    invalid_correlation,
    invalid_distribution_param,
    lexical_error,
    missing_provenance,
    missing_provenance_field,
    rate_unit_mismatch,
    syntax_error,
    type_mismatch,
    undefined_variable,
    unexpected_token,
)


@pytest.mark.unit
def test_error_helpers_set_codes_and_formatting_variants() -> None:
    loc = SourceLocation(filename="m.pel", line=1, column=2)

    err = CompilerError("EXXXX", "msg")
    assert "error[EXXXX]: msg" in str(err)

    err_loc = CompilerError("EXXXX", "msg", location=loc)
    assert "--> m.pel:1:2" in str(err_loc)

    e1 = lexical_error("bad", loc)
    assert e1.code == "E0001"

    e2 = type_mismatch("A", "B", loc)
    assert e2.code == "E0100"

    e3 = undefined_variable("x", loc)
    assert e3.code == "E0101"

    e4 = dimensional_mismatch("add", "Currency", "Rate", loc)
    assert e4.code == "E0200"
    assert "hint" in str(e4)

    e5 = currency_mismatch("USD", "EUR", loc)
    assert e5.code == "E0203"

    e6 = rate_unit_mismatch("Month", "Year", loc)
    assert e6.code == "E0204"

    e7 = future_reference("revenue", loc)
    assert e7.code == "E0300"

    e8 = cyclic_dependency("x", "x -> y -> x", loc)
    assert e8.code == "E0301"

    e9 = missing_provenance("p", loc)
    assert e9.code == "E0400"

    e10 = missing_provenance_field("p", "method", loc)
    assert e10.code == "E0401"

    e11 = invalid_confidence(1.2, loc)
    assert e11.code == "E0402"

    e12 = invalid_constraint_condition("nope", loc)
    assert e12.code == "E0500"
    assert "hint" in str(e12)

    e13 = contradictory_constraints("c1", "c2", loc)
    assert e13.code == "E0501"

    e14 = invalid_distribution_param("Normal", "sigma", "must be > 0", loc)
    assert e14.code == "E0600"

    e15 = invalid_correlation("a", "b", 2.0, loc)
    assert e15.code == "E0601"

    e16 = correlation_matrix_not_psd(loc)
    assert e16.code == "E0602"
    assert "hint" in str(e16)

    e17 = unexpected_token("RBRACE", "NUMBER", loc)
    assert e17.code == "E0700"

    e18 = syntax_error("broken", loc)
    assert e18.code == "E0701"

    e19 = InternalError("boom", loc)
    assert e19.code == "E9999"
    assert "Internal compiler error" in str(e19)
