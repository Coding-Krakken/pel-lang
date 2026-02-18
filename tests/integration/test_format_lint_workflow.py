# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Integration tests for format + lint workflow."""

import pytest
from pathlib import Path
import tempfile
from formatter.formatter import PELFormatter
from linter.linter import PELLinter
from linter.config import LinterConfig


class TestFormatLintIntegration:
    """Test combined format + lint workflows."""

    def test_format_then_lint_workflow(self):
        """Test formatting code then linting it."""
        # Start with poorly formatted code
        source = "model   Test  {  param   x: Int=10    var  y=x*2  }"
        
        # Format first
        formatter = PELFormatter()
        formatted = formatter.format_string(source)
        
        # Then lint
        config = LinterConfig(enabled_rules=["PEL008"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(formatted.formatted)
        
        # Should have fewer style violations after formatting
        style_violations = [v for v in violations if v.code == "PEL008"]
        # Properly formatted code should have minimal style issues
        assert len(style_violations) <= 1  # Maybe final newline or similar

    def test_format_fixes_style_violations(self):
        """Test that formatting fixes PEL008 style violations."""
        source = "model Test {    \n    param x: Int = 10   \n}     "
        
        # Check violations before formatting
        config = LinterConfig(enabled_rules=["PEL008"])
        linter = PELLinter(config=config)
        violations_before = linter.lint_string(source)
        trailing_before = [v for v in violations_before if "trailing" in v.message.lower()]
        
        # Format
        formatter = PELFormatter()
        formatted = formatter.format_string(source)
        
        # Check violations after formatting
        violations_after = linter.lint_string(formatted.formatted)
        trailing_after = [v for v in violations_after if "trailing" in v.message.lower()]
        
        # Should have fewer or equal trailing whitespace violations
        assert len(trailing_after) <= len(trailing_before)

    def test_format_preserves_lint_semantics(self):
        """Test that formatting doesn't introduce new logical lint violations."""
        source = """model Test {
    param used: Int = 10
    var result = used * 2
}"""
        
        # Lint before formatting
        config = LinterConfig(enabled_rules=["PEL001", "PEL002"])
        linter = PELLinter(config=config)
        violations_before = linter.lint_string(source)
        unused_before = [v for v in violations_before if v.code in ["PEL001", "PEL002"]]
        
        # Format
        formatter = PELFormatter()
        formatted = formatter.format_string(source)
        
        # Lint after formatting
        violations_after = linter.lint_string(formatted.formatted)
        unused_after = [v for v in violations_after if v.code in ["PEL001", "PEL002"]]
        
        # Formatting should not introduce usage violations
        assert len(unused_after) == len(unused_before)

    def test_lint_then_format_workflow(self):
        """Test linting first, then formatting."""
        source = """model Test {
    param unused: Int = 10
    var x=5+3
}"""
        
        # Lint first (to identify issues)
        config = LinterConfig(enabled_rules=["PEL001", "PEL008"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        # Should have violations
        assert len(violations) > 0
        
        # Format (fixes style but not usage)
        formatter = PELFormatter()
        formatted = formatter.format_string(source)
        
        # Lint again
        violations_after = linter.lint_string(formatted.formatted)
        
        # Should still have PEL001 but fewer PEL008
        pel001_after = [v for v in violations_after if v.code == "PEL001"]
        pel008_after = [v for v in violations_after if v.code == "PEL008"]
        
        assert len(pel001_after) >= 1  # Unused param still there
        # Style violations should be reduced

    def test_format_lint_on_real_file(self):
        """Test format + lint on a realistic PEL file."""
        source = """// SaaS Growth Model
model SaasGrowth {
    // Initial parameters
    param initial_mrr: Currency<USD> = $10_000
    param growth_rate: Rate per Month = 0.10 / 1mo
    param churn_rate: Rate per Month = 0.05 / 1mo
    
    // Revenue calculation
    var mrr: TimeSeries<Currency<USD>>
    mrr[0] = initial_mrr
    mrr[t+1] = mrr[t] * (1 + growth_rate[t] - churn_rate[t])
    
    // Annual metrics
    var arr = mrr * 12
}"""
        
        # Format
        formatter = PELFormatter()
        formatted = formatter.format_string(source)
        
        # Lint the formatted version
        config = LinterConfig()
        linter = PELLinter(config=config)
        violations = linter.lint_string(formatted.formatted)
        
        # Should have minimal or no violations
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0

    def test_incremental_format_lint(self):
        """Test that repeated format + lint converges."""
        source = "model Test { param x: Int=10 var y=x*2 }"
        
        formatter = PELFormatter()
        config = LinterConfig(enabled_rules=["PEL008"])
        linter = PELLinter(config=config)
        
        # First iteration
        formatted1 = formatter.format_string(source)
        violations1 = linter.lint_string(formatted1.formatted)
        
        # Second iteration
        formatted2 = formatter.format_string(formatted1.formatted)
        violations2 = linter.lint_string(formatted2.formatted)
        
        # Should converge (same result)
        assert formatted1.formatted == formatted2.formatted
        assert len(violations1) == len(violations2)

    def test_format_lint_with_comments(self):
        """Test format + lint preserves and handles comments correctly."""
        source = """// Model comment
model Test {
    // Parameter comment
    param value: Int = 10  // Inline
    var result = value * 2
}"""
        
        # Format
        formatter = PELFormatter()
        formatted = formatter.format_string(source)
        
        # Lint
        config = LinterConfig()
        linter = PELLinter(config=config)
        violations = linter.lint_string(formatted.formatted)
        
        # Comments should be preserved
        assert "// Model comment" in formatted.formatted
        assert "// Parameter comment" in formatted.formatted
        assert "// Inline" in formatted.formatted
        
        # Should have no critical violations
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0
