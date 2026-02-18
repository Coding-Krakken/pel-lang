# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL code formatter implementation."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
import re

from compiler.lexer import Lexer
from compiler.parser import Parser
from formatter.config import FormatterConfig, load_formatter_config

logger = logging.getLogger(__name__)

_STRING_PATTERN = re.compile(r"\"([^\"\\]|\\.)*\"|'([^'\\]|\\.)*'")


@dataclass
class FormatResult:
    formatted: str
    changed: bool


def _split_comment(line: str) -> tuple[str, str | None]:
    in_string = False
    string_char = ""
    escape = False
    for idx, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if in_string:
            if ch == string_char:
                in_string = False
            continue
        if ch in ('"', "'"):
            in_string = True
            string_char = ch
            continue
        if ch == "/" and idx + 1 < len(line) and line[idx + 1] == "/":
            return line[:idx], line[idx:]
    return line, None


def _strip_strings(text: str) -> str:
    return _STRING_PATTERN.sub("", text)


def _brace_delta(code: str) -> int:
    stripped = _strip_strings(code)
    return stripped.count("{") - stripped.count("}")


def _format_code_segment(code: str) -> str:
    if not code.strip():
        return ""

    string_map: dict[str, str] = {}

    def _store_string(match: re.Match[str]) -> str:
        key = f"__PELSTR{len(string_map)}__"
        string_map[key] = match.group(0)
        return key

    working = _STRING_PATTERN.sub(_store_string, code)
    working = re.sub(r"\s+", " ", working).strip()

    working = re.sub(r"\s*\.\.\s*", "..", working)
    working = re.sub(r"(?<!\d)\s*\.\s*(?!\d)", ".", working)

    working = re.sub(r"\s*([,;])\s*", r"\1 ", working)
    working = re.sub(r"\s*:\s*", r": ", working)
    working = re.sub(r"\s*\(\s*", "(", working)
    working = re.sub(r"\s*\)\s*", ")", working)
    working = re.sub(r"\s*\[\s*", "[", working)
    working = re.sub(r"\s*\]\s*", "]", working)
    working = re.sub(r"\s*\{\s*", " { ", working)
    working = re.sub(r"\s*\}\s*", " } ", working)

    working = re.sub(r"\s*(==|!=|<=|>=|&&|\|\|)\s*", r" \1 ", working)
    working = re.sub(r"\s*(->)\s*", r" \1 ", working)
    working = re.sub(r"(?<![=!<>])\s*=\s*(?!=)", " = ", working)
    working = re.sub(r"\s*([+*/%^])\s*", r" \1 ", working)
    working = re.sub(r"\s*-(?!>)\s*", " - ", working)

    working = re.sub(r"\s+", " ", working).strip()

    for key, value in string_map.items():
        working = working.replace(key, value)

    return working


class PELFormatter:
    """Automatic code formatter for PEL."""

    def __init__(
        self,
        line_length: int | None = None,
        indent_size: int | None = None,
        config: FormatterConfig | None = None,
    ) -> None:
        self.config = config or load_formatter_config()
        if line_length is not None:
            self.config.line_length = line_length
        if indent_size is not None:
            self.config.indent_size = indent_size
        logger.info(
            "PEL Formatter initialized (line_length=%s, indent=%s)",
            self.config.line_length,
            self.config.indent_size,
        )

    def format_file(self, filepath: str, in_place: bool = False) -> FormatResult:
        """Format a PEL file and optionally write it back."""
        path = Path(filepath)
        source = path.read_text(encoding="utf-8")
        result = self.format_string(source, file_path=path)
        if in_place and result.changed:
            path.write_text(result.formatted, encoding="utf-8")
        return result

    def format_string(self, source: str, file_path: Path | None = None) -> FormatResult:
        """Format PEL source code string."""
        if self.config.validate_syntax:
            try:
                lexer = Lexer(source, str(file_path) if file_path else "<input>")
                tokens = lexer.tokenize()
                Parser(tokens).parse()
            except Exception as exc:
                logger.warning("Skipping formatting due to parse error: %s", exc)
                return FormatResult(formatted=source, changed=False)

        original_endswith_newline = source.endswith("\n")
        lines = source.splitlines()
        formatted_lines: list[str] = []
        indent_level = 0
        blank_count = 0

        for raw_line in lines:
            code_part, comment_part = _split_comment(raw_line)
            code_part = code_part.strip()

            if not code_part and (comment_part is None or not comment_part.strip()):
                blank_count += 1
                if blank_count <= self.config.max_blank_lines:
                    formatted_lines.append("")
                continue

            blank_count = 0

            brace_delta = _brace_delta(code_part)
            if code_part.startswith("}"):
                indent_level = max(indent_level - 1, 0)
                brace_delta += 1

            formatted_code = _format_code_segment(code_part)
            indent = " " * (self.config.indent_size * indent_level)
            line = f"{indent}{formatted_code}" if formatted_code else indent

            if comment_part:
                comment = comment_part.strip()
                if formatted_code:
                    line = f"{line} {comment}"
                else:
                    line = f"{indent}{comment}"

            formatted_lines.append(line.rstrip())

            indent_level += brace_delta
            if indent_level < 0:
                indent_level = 0

        formatted = "\n".join(formatted_lines)
        if self.config.ensure_final_newline and (original_endswith_newline or formatted):
            formatted += "\n"

        return FormatResult(formatted=formatted, changed=formatted != source)


if __name__ == "__main__":
    formatter = PELFormatter()
    print("PEL Formatter ready")
