# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Formatter edge case tests."""

import pytest
from formatter.formatter import PELFormatter


class TestEdgeCases:
    """Test formatter edge cases and error handling."""

    def test_syntax_error_returns_original(self):
        """Test that syntax errors return original source."""
        source = "model { this is invalid syntax"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Should return original when syntax is invalid
        assert result.formatted == source
        assert not result.changed

    def test_disable_syntax_validation(self):
        """Test disabling syntax validation."""
        source = "model { invalid }"
        formatter = PELFormatter()
        formatter.config.validate_syntax = False
        result = formatter.format_string(source)
        
        # Should attempt formatting even with invalid syntax
        # Changed flag may vary
        assert isinstance(result.formatted, str)

    def test_very_long_line(self):
        """Test handling very long lines."""
        source = "model Test { param x: Int = " + " + ".join(str(i) for i in range(100)) + " }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Should not crash
        assert isinstance(result.formatted, str)

    def test_deeply_nested_braces(self):
        """Test deeply nested brace structures."""
        source = "model Test { var a = { b: { c: { d: 1 } } } }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Should handle nesting without crashing
        assert isinstance(result.formatted, str)
        assert "{" in result.formatted

    def test_empty_braces(self):
        """Test empty brace blocks."""
        source = "model Test { }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "model Test {" in result.formatted
        assert "}" in result.formatted

    def test_only_comments(self):
        """Test file with only comments."""
        source = """// Comment 1
// Comment 2
// Comment 3"""
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "// Comment 1" in result.formatted
        assert "// Comment 2" in result.formatted
        assert "// Comment 3" in result.formatted

    def test_unicode_characters(self):
        """Test handling unicode characters."""
        source = 'model Test { param msg: String = "Hello 世界 🌍" }'
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "世界" in result.formatted
        assert "🌍" in result.formatted

    def test_escape_sequences_in_strings(self):
        """Test escape sequences are preserved."""
        source = r'model Test { param msg: String = "Line 1\nLine 2\tTabbed" }'
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert r"\n" in result.formatted
        assert r"\t" in result.formatted

    def test_mixed_quotes(self):
        """Test mixed single and double quotes."""
        source = '''model Test {
    param single: String = 'single quoted'
    param double: String = "double quoted"
}'''
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "'single quoted'" in result.formatted
        assert '"double quoted"' in result.formatted

    def test_consecutive_operators(self):
        """Test consecutive operators."""
        source = "model Test { var x = a++--b }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Should not crash
        assert isinstance(result.formatted, str)

    def test_max_blank_lines_enforcement(self):
        """Test that excessive blank lines are limited."""
        source = """model Test {
    param x: Int = 10



    var y = x * 2
}"""
        formatter = PELFormatter()
        formatter.config.max_blank_lines = 2
        result = formatter.format_string(source)
        
        # Count consecutive blank lines
        lines = result.formatted.split('\n')
        max_consecutive_blanks = 0
        current_blanks = 0
        for line in lines:
            if line.strip() == '':
                current_blanks += 1
                max_consecutive_blanks = max(max_consecutive_blanks, current_blanks)
            else:
                current_blanks = 0
        
        assert max_consecutive_blanks <= 2

    def test_trailing_whitespace_removed(self):
        """Test that trailing whitespace is removed."""
        source = "model Test {   \n    param x: Int = 10    \n}   "
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Lines should not end with spaces
        for line in result.formatted.split('\n'):
            if line:  # Skip empty lines
                assert line == line.rstrip()

    def test_range_operator(self):
        """Test range operator formatting."""
        source = "model Test { var range = 1..10 }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Range operator should not have spaces
        assert "1..10" in result.formatted

    def test_member_access(self):
        """Test member access formatting."""
        source = "model Test { var val = obj . field }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        # Member access should have no spaces
        assert "obj.field" in result.formatted
