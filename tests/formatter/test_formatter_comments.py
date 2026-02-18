# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Formatter comment handling tests."""

import pytest
from formatter.formatter import PELFormatter


class TestCommentHandling:
    """Test that formatter preserves and properly formats comments."""

    def test_line_comment_preserved(self):
        """Test line comments are preserved."""
        source = "// This is a comment\nmodel Test { param x: Int = 10 }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "// This is a comment" in result.formatted

    def test_inline_comment_preserved(self):
        """Test inline comments are preserved."""
        source = "model Test { param x: Int = 10 // end of line }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "// end of line" in result.formatted

    def test_multiple_comments(self):
        """Test multiple comments are all preserved."""
        source = """// Comment 1
// Comment 2
model Test {
    // Comment 3
    param x: Int = 10  // Comment 4
}"""
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "// Comment 1" in result.formatted
        assert "// Comment 2" in result.formatted
        assert "// Comment 3" in result.formatted
        assert "// Comment 4" in result.formatted

    def test_comment_only_line(self):
        """Test lines with only comments."""
        source = """model Test {
    // Just a comment
    param x: Int = 10
}"""
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "// Just a comment" in result.formatted

    def test_comment_indentation(self):
        """Test comments maintain proper indentation."""
        source = """model Test {
// Comment should be indented
param x: Int = 10
}"""
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        lines = result.formatted.split('\n')
        comment_line = [l for l in lines if 'Comment should be indented' in l][0]
        # Comment should be indented
        assert len(comment_line) - len(comment_line.lstrip()) >= 4

    def test_comment_with_special_chars(self):
        """Test comments with special characters."""
        source = "model Test { param x: Int = 10 // TODO: fix this! @#$% }"
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert "// TODO: fix this! @#$%" in result.formatted

    def test_comment_in_string_not_treated_as_comment(self):
        """Test that // in strings is not treated as comment."""
        source = 'model Test { param url: String = "http://example.com" }'
        formatter = PELFormatter()
        result = formatter.format_string(source)
        
        assert '"http://example.com"' in result.formatted
        # Should not split the string
        assert 'http:' in result.formatted and 'example.com' in result.formatted
