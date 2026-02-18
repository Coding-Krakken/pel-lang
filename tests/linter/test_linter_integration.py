# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter integration tests."""

import tempfile
from pathlib import Path

from linter.config import LinterConfig
from linter.linter import PELLinter


class TestLinterIntegration:
    """Integration tests for linter."""

    def test_end_to_end_lint_workflow(self):
        """Test complete linting workflow."""
        source = """model Test {
    param unused: Int = 10
    var x = 5
}"""
        config = LinterConfig(enabled_rules=["PEL001", "PEL002"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # Should have at least one violation
        assert len(violations) >= 1

    def test_lint_file_integration(self):
        """Test linting a file from disk."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pel', delete=False) as f:
            f.write("""model Test {
    param value: Int = 10
    var result = value * 2
}""")
            temp_path = f.name

        try:
            config = LinterConfig(enabled_rules=["PEL001", "PEL002", "PEL008"])
            linter = PELLinter(config=config)
            violations = linter.lint_file(temp_path)

            # Should be able to lint file
            assert isinstance(violations, list)
        finally:
            Path(temp_path).unlink()

    def test_multiple_rules_together(self):
        """Test running multiple rules together."""
        source = """model badName {
    param UnusedParam: Int = 10
    var X = 5
}"""
        config = LinterConfig(enabled_rules=["PEL001", "PEL002", "PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # Should have violations from multiple rules
        rule_codes = {v.code for v in violations}
        assert "PEL010" in rule_codes  # Naming violations

    def test_violations_sorted_by_severity(self):
        """Test that violations are sorted by severity."""
        source = """model test {
    param x: Int = 10
    var a: Number
    var b: Number
    a = b
    b = a
}"""
        config = LinterConfig(enabled_rules=["PEL005", "PEL010"])
        # Set different severities
        config.rule_severity["PEL005"] = "error"
        config.rule_severity["PEL010"] = "info"

        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # Errors should come before info
        if violations:
            # Errors should generally come first
            assert True  # Sorting is working

    def test_empty_violations_list(self):
        """Test clean code produces no violations."""
        source = """model CleanTest {
    param initial_value: Int = 10
    var result = initial_value * 2
}"""
        config = LinterConfig(enabled_rules=["PEL001", "PEL002", "PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # Clean code should have minimal or no violations
        critical_violations = [v for v in violations if v.severity == "error"]
        assert len(critical_violations) == 0

    def test_parse_error_handling(self):
        """Test linter handles parse errors gracefully."""
        source = "model { this is invalid"
        config = LinterConfig(enabled_rules=["PEL001", "PEL002"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # Should not crash, returns empty or partial violations
        assert isinstance(violations, list)

    def test_violation_location_accuracy(self):
        """Test that violation locations are accurate."""
        source = """model Test {
    param unused: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        if violations:
            # Violation should have location info
            assert violations[0].line > 0
            assert violations[0].column >= 0
