# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Formatter idempotency tests."""

from formatter.formatter import PELFormatter


class TestIdempotency:
    """Test that formatting is idempotent: Format(Format(x)) == Format(x)."""

    def test_idempotent_simple_model(self):
        """Test idempotency on simple model."""
        source = "model Test { param x: Int = 10 }"
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)

        assert first.formatted == second.formatted
        assert not second.changed

    def test_idempotent_complex_model(self):
        """Test idempotency on complex model with nesting."""
        source = """model ComplexTest {
    param initial: Int = 100
    var revenue: TimeSeries<Int>
    revenue[0] = initial
    revenue[t+1] = revenue[t] * 1.1
}"""
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)
        third = formatter.format_string(second.formatted)

        assert first.formatted == second.formatted == third.formatted

    def test_idempotent_with_comments(self):
        """Test idempotency preserves comments."""
        source = """// Model comment
model Test {
    // Parameter comment
    param x: Int = 10  // Inline comment
}"""
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)

        assert first.formatted == second.formatted
        assert "// Model comment" in first.formatted
        assert "// Parameter comment" in first.formatted
        assert "// Inline comment" in first.formatted

    def test_idempotent_operators(self):
        """Test idempotency with various operators."""
        source = "model Test { var result = (a + b) * c - d / e }"
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)

        assert first.formatted == second.formatted

    def test_idempotent_arrays(self):
        """Test idempotency with arrays."""
        source = "model Test { var arr = [1, 2, 3, 4, 5] }"
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)

        assert first.formatted == second.formatted

    def test_idempotent_multiple_statements(self):
        """Test idempotency with multiple statements."""
        source = """model Test {
    param a: Int = 1
    param b: Int = 2
    var c = a + b
    var d = c * 2
}"""
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)

        assert first.formatted == second.formatted

    def test_idempotent_blank_lines(self):
        """Test idempotency with blank lines."""
        source = """model Test {
    param x: Int = 10


    var y = x * 2
}"""
        formatter = PELFormatter()

        first = formatter.format_string(source)
        second = formatter.format_string(first.formatted)

        assert first.formatted == second.formatted
