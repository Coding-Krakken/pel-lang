# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter reporter tests."""

import json

from linter.reporter import render_json, render_text
from linter.types import LintViolation


class TestLinterReporter:
    """Test linter output reporters."""

    def test_render_text_output(self):
        """Test text output rendering."""
        violations = [
            LintViolation(
                code="PEL001",
                message="Parameter 'x' is unused",
                severity="warning",
                line=5,
                column=10,
                path="test.pel",
                rule="Unused parameter"
            )
        ]

        output = render_text(violations)

        assert "test.pel:5:10" in output
        assert "WARNING" in output
        assert "PEL001" in output
        assert "unused" in output.lower()

    def test_render_json_output(self):
        """Test JSON output rendering."""
        violations = [
            LintViolation(
                code="PEL001",
                message="Parameter 'x' is unused",
                severity="warning",
                line=5,
                column=10,
                path="test.pel",
                rule="Unused parameter"
            )
        ]

        output = render_json(violations)
        data = json.loads(output)

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["code"] == "PEL001"
        assert data[0]["severity"] == "warning"
        assert data[0]["line"] == 5
        assert data[0]["column"] == 10

    def test_render_multiple_violations(self):
        """Test rendering multiple violations."""
        violations = [
            LintViolation(
                code="PEL001",
                message="Parameter 'x' is unused",
                severity="warning",
                line=5,
                column=10,
                path="test.pel"
            ),
            LintViolation(
                code="PEL002",
                message="Variable 'y' is unreferenced",
                severity="warning",
                line=10,
                column=5,
                path="test.pel"
            )
        ]

        text_output = render_text(violations)
        json_output = render_json(violations)

        # Text output should have both violations
        assert "PEL001" in text_output
        assert "PEL002" in text_output

        # JSON output should have both
        data = json.loads(json_output)
        assert len(data) == 2

    def test_render_empty_violations(self):
        """Test rendering with no violations."""
        violations = []

        text_output = render_text(violations)
        json_output = render_json(violations)

        assert text_output == ""

        data = json.loads(json_output)
        assert data == []

    def test_violation_to_dict(self):
        """Test LintViolation.to_dict() method."""
        violation = LintViolation(
            code="PEL001",
            message="Test message",
            severity="error",
            line=1,
            column=1,
            path="test.pel",
            rule="Test rule"
        )

        data = violation.to_dict()

        assert data["code"] == "PEL001"
        assert data["message"] == "Test message"
        assert data["severity"] == "error"
        assert data["line"] == 1
        assert data["column"] == 1
        assert data["path"] == "test.pel"
        assert data["rule"] == "Test rule"

    def test_text_output_no_path(self):
        """Test text output when path is None."""
        violations = [
            LintViolation(
                code="PEL001",
                message="Test",
                severity="warning",
                line=1,
                column=1,
                path=None
            )
        ]

        output = render_text(violations)
        assert "<input>" in output or "1:1" in output
