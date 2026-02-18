# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter rule tests - PEL008 (Style Violations)."""

import pytest
from linter.linter import PELLinter
from linter.config import LinterConfig


class TestPEL008StyleViolations:
    """Test PEL008 rule: Style violation detection."""

    def test_detects_line_too_long(self):
        """Test detection of lines exceeding length limit."""
        # Create a line that's definitely too long
        long_line = "model Test { var x = " + " + ".join(str(i) for i in range(50)) + " }"
        
        config = LinterConfig(enabled_rules=["PEL008"], line_length=100)
        linter = PELLinter(config=config)
        violations = linter.lint_string(long_line)
        
        pel008_violations = [v for v in violations if v.code == "PEL008"]
        line_length_violations = [v for v in pel008_violations if "exceeds" in v.message.lower()]
        assert len(line_length_violations) >= 1

    def test_detects_trailing_whitespace(self):
        """Test detection of trailing whitespace."""
        source = "model Test {    \n    param x: Int = 10   \n}"
        
        config = LinterConfig(enabled_rules=["PEL008"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel008_violations = [v for v in violations if v.code == "PEL008"]
        trailing_violations = [v for v in pel008_violations if "trailing" in v.message.lower()]
        assert len(trailing_violations) >= 1

    def test_no_violation_for_short_clean_lines(self):
        """Test no violation for properly formatted code."""
        source = """model Test {
    param x: Int = 10
    var y = x * 2
}"""
        config = LinterConfig(enabled_rules=["PEL008"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel008_violations = [v for v in violations if v.code == "PEL008"]
        assert len(pel008_violations) == 0

    def test_configurable_line_length(self):
        """Test that line length limit is configurable."""
        source = "model Test { var x = 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 }"
        
        # With short limit, should violate
        config = LinterConfig(enabled_rules=["PEL008"], line_length=50)
        linter = PELLinter(config=config)
        violations_short = linter.lint_string(source)
        
        # With long limit, should pass
        config = LinterConfig(enabled_rules=["PEL008"], line_length=200)
        linter = PELLinter(config=config)
        violations_long = linter.lint_string(source)
        
        short_line_violations = [v for v in violations_short if v.code == "PEL008" and "exceeds" in v.message.lower()]
        long_line_violations = [v for v in violations_long if v.code == "PEL008" and "exceeds" in v.message.lower()]
        
        assert len(short_line_violations) >= 1
        assert len(long_line_violations) == 0
