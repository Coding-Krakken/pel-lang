# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter reporters for text and JSON outputs."""

from __future__ import annotations

import json
from collections.abc import Iterable

from linter.types import LintViolation


def render_text(violations: Iterable[LintViolation]) -> str:
    lines: list[str] = []
    for violation in violations:
        location = f"{violation.path or '<input>'}:{violation.line}:{violation.column}"
        lines.append(
            f"{location}: {violation.severity.upper()} {violation.code} {violation.message}"
        )
    return "\n".join(lines)


def render_json(violations: Iterable[LintViolation]) -> str:
    payload = [violation.to_dict() for violation in violations]
    return json.dumps(payload, indent=2)
