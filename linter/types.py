# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Shared linter types."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from compiler.ast_nodes import Model
from compiler.lexer import Token
from linter.config import LinterConfig


@dataclass
class LintViolation:
    code: str
    message: str
    severity: str
    line: int
    column: int
    path: str | None = None
    rule: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "line": self.line,
            "column": self.column,
            "path": self.path,
            "rule": self.rule,
        }


@dataclass
class LintContext:
    source: str
    model: Model | None
    tokens: list[Token]
    config: LinterConfig
    file_path: Path | None = None

    @property
    def source_lines(self) -> list[str]:
        return self.source.splitlines()
