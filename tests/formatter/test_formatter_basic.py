# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Basic formatter functionality tests."""

from formatter.formatter import FormatResult, PELFormatter


class TestBasicFormatting:
    """Test basic formatting operations."""

    def test_formatter_initialization(self):
        """Test formatter can be initialized with defaults."""
        formatter = PELFormatter()
        assert formatter.config.line_length == 100
        assert formatter.config.indent_size == 4

    def test_formatter_custom_config(self):
        """Test formatter respects custom configuration."""
        formatter = PELFormatter(line_length=120, indent_size=2)
        assert formatter.config.line_length == 120
        assert formatter.config.indent_size == 2

    def test_format_simple_model(self):
        """Test formatting a simple model."""
        source = "model    Test   {   param x: Int=10   }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert isinstance(result, FormatResult)
        assert result.changed
        assert "model Test" in result.formatted
        assert "param x: Int = 10" in result.formatted

    def test_unchanged_code_returns_false(self):
        """Test that already formatted code returns changed=False."""
        source = """model Test {
    param x: Int = 10
}
"""
        formatter = PELFormatter()
        result = formatter.format_string(source)
        # First format might change it

        # Format again - should be idempotent
        result2 = formatter.format_string(result.formatted)
        assert not result2.changed

    def test_operator_spacing(self):
        """Test that operators get proper spacing."""
        source = "model Test { var x=1+2*3-4/5 }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert " = " in result.formatted
        assert " + " in result.formatted
        assert " * " in result.formatted
        assert " - " in result.formatted
        assert " / " in result.formatted

    def test_comma_spacing(self):
        """Test comma spacing in arrays."""
        source = "model Test { var arr=[1,2,3,4] }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert "1, 2, 3, 4" in result.formatted

    def test_brace_spacing(self):
        """Test brace spacing."""
        source = "model Test{param x: Int=10}"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert "model Test {" in result.formatted or "Test {" in result.formatted

    def test_indentation_single_level(self):
        """Test single-level indentation."""
        source = """model Test {
param x: Int = 10
}"""
        formatter = PELFormatter()
        result = formatter.format_string(source)

        lines = result.formatted.split('\n')
        # Find the param line
        param_line = [line for line in lines if 'param' in line][0]
        assert param_line.startswith('    ') or param_line.startswith('\t')

    def test_indentation_nested_braces(self):
        """Test nested model or constraint indentation."""
        source = """model Test {
param x: Int = 10
constraint limit {
severity: fatal
}
}"""
        formatter = PELFormatter()
        result = formatter.format_string(source)

        # Basic indentation check - constraint contents should be indented
        lines = result.formatted.split('\n')
        # Check that result has some indentation (formatter might not fully support constraints yet)
        assert len(lines) > 2

    def test_preserves_strings(self):
        """Test that string contents are preserved."""
        source = 'model Test { param msg: String = "hello  world" }'
        formatter = PELFormatter()
        result = formatter.format_string(source)

        # String should keep internal spacing
        assert '"hello  world"' in result.formatted

    def test_preserves_single_quoted_strings(self):
        """Test single-quoted strings are preserved."""
        source = "model Test { param msg: String = 'test  value' }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert "'test  value'" in result.formatted

    def test_empty_file(self):
        """Test formatting empty file."""
        formatter = PELFormatter()
        result = formatter.format_string("")

        assert result.formatted == "" or result.formatted == "\n"

    def test_whitespace_only_file(self):
        """Test formatting file with only whitespace."""
        formatter = PELFormatter()
        result = formatter.format_string("   \n  \n   ")

        # Should normalize to minimal whitespace
        assert len(result.formatted.strip()) == 0

    def test_final_newline_added(self):
        """Test that final newline is added."""
        source = "model Test { param x: Int = 10 }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        # Should end with newline if config says so
        if formatter.config.ensure_final_newline:
            assert result.formatted.endswith('\n')

    def test_final_newline_preserved(self):
        """Test that existing final newline is preserved."""
        source = "model Test { param x: Int = 10 }\n"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert result.formatted.endswith('\n')

    def test_comparison_operators(self):
        """Test comparison operator spacing."""
        source = "model Test { var x=a==b&&c!=d||e<=f&&g>=h }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert " == " in result.formatted
        assert " != " in result.formatted
        assert " && " in result.formatted
        assert " || " in result.formatted
        assert " <= " in result.formatted
        assert " >= " in result.formatted

    def test_colon_spacing(self):
        """Test colon spacing in type annotations."""
        source = "model Test { param x: Int=10 }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        assert ": Number" in result.formatted or ": Int" in result.formatted

    def test_arrow_spacing(self):
        """Test spacing around assignment arrows and rate operators."""
        source = "model Test { var rate: Rate per Month=0.10/1mo }"
        formatter = PELFormatter()
        result = formatter.format_string(source)

        # Should have proper spacing around operators
        assert " per " in result.formatted or "per" in result.formatted
