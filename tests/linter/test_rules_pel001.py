# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter rule tests - PEL001 (Unused Parameter)."""

from linter.config import LinterConfig
from linter.linter import PELLinter


class TestPEL001UnusedParam:
    """Test PEL001 rule: Unused parameter detection."""

    def test_detects_unused_parameter(self):
        """Test detection of unused parameter."""
        source = """model Test {
    param unused: Int = 10
    var used: Int = 5
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # Should detect unused parameter
        pel001_violations = [v for v in violations if v.code == "PEL001"]
        assert len(pel001_violations) == 1
        assert "unused" in pel001_violations[0].message.lower()

    def test_no_violation_when_parameter_used(self):
        """Test no violation when parameter is used."""
        source = """model Test {
    param value: Int = 10
    var result = value * 2
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel001_violations = [v for v in violations if v.code == "PEL001"]
        assert len(pel001_violations) == 0

    def test_ignores_underscore_prefixed_params(self):
        """Test that parameters prefixed with _ are ignored."""
        source = """model Test {
    param _intentionally_unused: Int = 10
    var result: Int = 5
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel001_violations = [v for v in violations if v.code == "PEL001"]
        assert len(pel001_violations) == 0

    def test_multiple_unused_parameters(self):
        """Test detection of multiple unused parameters."""
        source = """model Test {
    param unused1: Int = 10
    param unused2: Int = 20
    param used: Int = 30
    var result = used * 2
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel001_violations = [v for v in violations if v.code == "PEL001"]
        assert len(pel001_violations) == 2

    def test_parameter_used_in_timeseries(self):
        """Test parameter used in timeseries assignment."""
        source = """model Test {
    param initial: Int = 100
    var revenue: TimeSeries<Int>
    revenue[0] = initial
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel001_violations = [v for v in violations if v.code == "PEL001"]
        assert len(pel001_violations) == 0

    def test_parameter_used_in_constraint(self):
        """Test parameter used in constraint."""
        source = """model Test {
    param max_value: Int = 100
    var value: Int = 50
    constraint value <= max_value
}"""
        config = LinterConfig(enabled_rules=["PEL001"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel001_violations = [v for v in violations if v.code == "PEL001"]
        assert len(pel001_violations) == 0
