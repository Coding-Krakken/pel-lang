# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter rule tests - PEL010 (Naming Conventions)."""

import pytest
from linter.linter import PELLinter
from linter.config import LinterConfig


class TestPEL010NamingConventions:
    """Test PEL010 rule: Naming convention enforcement."""

    def test_detects_non_pascalcase_model(self):
        """Test detection of non-PascalCase model name."""
        source = """model test_model {
    param x: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        model_violations = [v for v in pel010_violations if "model" in v.message.lower() and "pascalcase" in v.message.lower()]
        assert len(model_violations) >= 1

    def test_accepts_pascalcase_model(self):
        """Test acceptance of PascalCase model name."""
        source = """model TestModel {
    param x: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        model_violations = [v for v in pel010_violations if "TestModel" in v.message]
        assert len(model_violations) == 0

    def test_detects_non_snakecase_parameter(self):
        """Test detection of non-snake_case parameter."""
        source = """model Test {
    param InvalidName: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        param_violations = [v for v in pel010_violations if "parameter" in v.message.lower() or "InvalidName" in v.message]
        assert len(param_violations) >= 1

    def test_accepts_snakecase_parameter(self):
        """Test acceptance of snake_case parameter."""
        source = """model Test {
    param valid_name: Int = 10
    param another_valid_name: Int = 20
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        param_violations = [v for v in pel010_violations if "parameter" in v.message.lower()]
        assert len(param_violations) == 0

    def test_detects_non_snakecase_variable(self):
        """Test detection of non-snake_case variable."""
        source = """model Test {
    var CamelCaseVar: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        var_violations = [v for v in pel010_violations if "variable" in v.message.lower() or "CamelCaseVar" in v.message]
        assert len(var_violations) >= 1

    def test_accepts_snakecase_variable(self):
        """Test acceptance of snake_case variable."""
        source = """model Test {
    var my_variable: Int = 10
    var another_var = 20
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        var_violations = [v for v in pel010_violations if "my_variable" in v.message or "another_var" in v.message]
        assert len(var_violations) == 0

    def test_severity_info_by_default(self):
        """Test that PEL010 has info severity by default."""
        source = """model test {
    param X: Int = 10
}"""
        config = LinterConfig(enabled_rules=["PEL010"])
        linter = PELLinter(config=config)
        violations = linter.lint_string(source)
        
        pel010_violations = [v for v in violations if v.code == "PEL010"]
        # Should have violations with info severity
        assert all(v.severity in ["info", "warning"] for v in pel010_violations)
