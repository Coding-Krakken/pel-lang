# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter rule tests - PEL002 (Unreferenced Variable)."""

from linter.config import LinterConfig
from linter.linter import PELLinter


class TestPEL002UnreferencedVar:
    """Test PEL002 rule: Unreferenced variable detection."""

    def test_detects_unreferenced_variable(self):
        """Test detection of unreferenced variable."""
        source = """model Test {
    var unused: Int = 10
    var used: Int = 5
}"""
        config = LinterConfig(enabled_rules=["PEL002"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel002_violations = [v for v in violations if v.code == "PEL002"]
        assert len(pel002_violations) >= 1
        assert any("unused" in v.message.lower() for v in pel002_violations)

    def test_no_violation_when_variable_referenced(self):
        """Test no violation when variable is referenced."""
        source = """model Test {
    var base: Int = 10
    var result = base * 2
}"""
        config = LinterConfig(enabled_rules=["PEL002"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # base is used, but result might be unreferenced
        base_violations = [v for v in violations if v.code == "PEL002" and "base" in v.message.lower()]
        assert len(base_violations) == 0

    def test_ignores_underscore_prefixed_vars(self):
        """Test that variables prefixed with _ are ignored."""
        source = """model Test {
    var _temp: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL002"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        pel002_violations = [v for v in violations if v.code == "PEL002" and "_temp" in v.message]
        assert len(pel002_violations) == 0

    def test_variable_used_in_another_variable(self):
        """Test variable used in another variable definition."""
        source = """model Test {
    var a: Int = 10
    var b = a * 2
    var c = b + 1
}"""
        config = LinterConfig(enabled_rules=["PEL002"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)

        # a and b should not be flagged as unused
        a_violations = [v for v in violations if v.code == "PEL002" and " a " in v.message.lower() or "'a'" in v.message.lower()]
        b_violations = [v for v in violations if v.code == "PEL002" and " b " in v.message.lower() or "'b'" in v.message.lower()]

        assert len(a_violations) == 0
        assert len(b_violations) == 0
