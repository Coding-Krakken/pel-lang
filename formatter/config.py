# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Formatter configuration loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FormatterConfig:
    line_length: int = 100
    indent_size: int = 4
    max_blank_lines: int = 2
    ensure_final_newline: bool = True
    validate_syntax: bool = True


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # type: ignore
        except ModuleNotFoundError:
            return {}

    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError:
        return {}


def find_formatter_config(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    while True:
        candidate = current / ".pelformat.toml"
        if candidate.exists():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def load_formatter_config(start: Path | None = None) -> FormatterConfig:
    base = FormatterConfig()
    if start is None:
        start = Path.cwd()
    config_path = find_formatter_config(start)
    if not config_path:
        return base

    data = _load_toml(config_path)
    section = data.get("format", {}) if isinstance(data, dict) else {}

    def _get_int(name: str, default: int) -> int:
        value = section.get(name, default)
        return int(value) if isinstance(value, (int, float)) else default

    base.line_length = _get_int("line_length", base.line_length)
    base.indent_size = _get_int("indent_size", base.indent_size)
    base.max_blank_lines = _get_int("max_blank_lines", base.max_blank_lines)
    base.ensure_final_newline = bool(section.get("ensure_final_newline", base.ensure_final_newline))
    base.validate_syntax = bool(section.get("validate_syntax", base.validate_syntax))

    return base
