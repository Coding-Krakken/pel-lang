# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL linter implementation."""

from __future__ import annotations

import logging
from pathlib import Path

from compiler.lexer import Lexer
from compiler.parser import Parser
from linter.config import LinterConfig, load_linter_config
from linter.rules import AVAILABLE_RULES
from linter.types import LintContext, LintViolation

logger = logging.getLogger(__name__)


class PELLinter:
    """Static analysis linter for PEL."""

    def __init__(self, config: LinterConfig | None = None) -> None:
        self.config = config or load_linter_config()
        logger.info("PEL Linter initialized")

    def lint_file(self, filepath: str) -> list[LintViolation]:
        """Lint a PEL file and return violations."""
        path = Path(filepath)
        source = path.read_text(encoding="utf-8")
        return self.lint_string(source, file_path=path)

    def lint_string(self, source: str, file_path: Path | None = None) -> list[LintViolation]:
        """Lint PEL source code string."""
        lexer = Lexer(source, str(file_path) if file_path else "<input>")
        tokens = lexer.tokenize()

        model = None
        try:
            model = Parser(tokens).parse()
        except Exception as exc:
            logger.warning("Linting parse error: %s", exc)

        context = LintContext(
            source=source,
            model=model,
            tokens=tokens,
            config=self.config,
            file_path=file_path,
        )

        violations: list[LintViolation] = []
        for rule_code in self.config.enabled_rules:
            rule = AVAILABLE_RULES.get(rule_code)
            if not rule:
                continue
            for violation in rule.run(context):
                severity = self.config.rule_severity.get(rule.code, violation.severity)
                violation.severity = severity
                violations.append(violation)

        severity_rank = {"error": 0, "warning": 1, "info": 2}
        return sorted(
            violations,
            key=lambda v: (severity_rank.get(v.severity, 3), v.line, v.column),
        )


if __name__ == "__main__":
    linter = PELLinter()
    print("PEL Linter ready")
