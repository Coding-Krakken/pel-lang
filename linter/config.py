# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter configuration loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LinterConfig:
    enabled_rules: list[str] = field(
        default_factory=lambda: [
            "PEL001",
            "PEL002",
            "PEL004",
            "PEL005",
            "PEL008",
            "PEL010",
        ]
    )
    rule_severity: dict[str, str] = field(default_factory=dict)
    line_length: int = 100
    exclude_paths: list[str] = field(default_factory=list)


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        try:
            import tomli as tomllib
        except ModuleNotFoundError:
            return {}

    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError:
        return {}


def find_linter_config(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent

    while True:
        candidate = current / ".pellint.toml"
        if candidate.exists():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def load_linter_config(start: Path | None = None) -> LinterConfig:
    base = LinterConfig()
    if start is None:
        start = Path.cwd()

    config_path = find_linter_config(start)
    if not config_path:
        return base

    data = _load_toml(config_path)
    section = data.get("linter", {}) if isinstance(data, dict) else {}

    enabled = section.get("enabled_rules")
    if isinstance(enabled, list) and enabled:
        base.enabled_rules = [str(rule) for rule in enabled]

    base.line_length = int(section.get("line_length", base.line_length))
    base.exclude_paths = [str(path) for path in section.get("exclude_paths", [])]

    rules = data.get("rules", {}) if isinstance(data, dict) else {}
    if isinstance(rules, dict):
        for rule_code, rule_settings in rules.items():
            if isinstance(rule_settings, dict) and "severity" in rule_settings:
                base.rule_severity[str(rule_code)] = str(rule_settings["severity"])

    return base
