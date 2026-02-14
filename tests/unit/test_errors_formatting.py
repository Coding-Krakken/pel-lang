from __future__ import annotations

import pytest

from compiler.errors import (
    SourceLocation,
    CompilerError,
    invalid_number,
    unterminated_string,
)


@pytest.mark.unit
def test_compiler_error_formatting_includes_location_and_hint() -> None:
    err = CompilerError(
        code="E9998",
        message="something bad",
        location=SourceLocation(filename="m.pel", line=2, column=3),
        hint="do the thing",
    )
    text = str(err)
    assert "--> m.pel:2:3" in text
    assert "error[E9998]: something bad" in text
    assert "= hint: do the thing" in text


@pytest.mark.unit
def test_invalid_number_and_unterminated_string_helpers_format() -> None:
    err1 = invalid_number("1.2.3", SourceLocation(filename="m.pel", line=1, column=1))
    assert err1.code == "E0002"
    assert "Invalid number literal" in str(err1)

    err2 = unterminated_string(SourceLocation(filename="m.pel", line=1, column=10))
    assert err2.code == "E0003"
    assert "Unterminated string literal" in str(err2)
