# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Formatter configuration tests."""

import pytest
from pathlib import Path
import tempfile
from formatter.config import FormatterConfig, load_formatter_config, find_formatter_config


class TestFormatterConfig:
    """Test formatter configuration loading."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FormatterConfig()
        assert config.line_length == 100
        assert config.indent_size == 4
        assert config.max_blank_lines == 2
        assert config.ensure_final_newline is True
        assert config.validate_syntax is True

    def test_custom_config_values(self):
        """Test custom configuration values."""
        config = FormatterConfig(
            line_length=120,
            indent_size=2,
            max_blank_lines=1,
            ensure_final_newline=False,
            validate_syntax=False
        )
        assert config.line_length == 120
        assert config.indent_size == 2
        assert config.max_blank_lines == 1
        assert config.ensure_final_newline is False
        assert config.validate_syntax is False

    def test_load_config_no_file(self):
        """Test loading config when no .pelformat.toml exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_formatter_config(Path(tmpdir))
            # Should return defaults
            assert config.line_length == 100
            assert config.indent_size == 4

    def test_load_config_from_file(self):
        """Test loading config from .pelformat.toml file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".pelformat.toml"
            config_path.write_text("""
[format]
line_length = 120
indent_size = 2
max_blank_lines = 1
ensure_final_newline = false
""")
            config = load_formatter_config(Path(tmpdir))
            assert config.line_length == 120
            assert config.indent_size == 2
            assert config.max_blank_lines == 1
            assert config.ensure_final_newline is False

    def test_find_config_in_parent(self):
        """Test finding config file in parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parent = Path(tmpdir)
            child = parent / "subdir"
            child.mkdir()
            
            config_path = parent / ".pelformat.toml"
            config_path.write_text("[format]\nline_length = 88")
            
            found = find_formatter_config(child)
            assert found == config_path

    def test_find_config_not_found(self):
        """Test when config file is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            found = find_formatter_config(Path(tmpdir))
            assert found is None

    def test_partial_config(self):
        """Test config file with only some values set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".pelformat.toml"
            config_path.write_text("""
[format]
line_length = 120
""")
            config = load_formatter_config(Path(tmpdir))
            # Should have custom line_length
            assert config.line_length == 120
            # Should have default indent_size
            assert config.indent_size == 4

    def test_invalid_config_values(self):
        """Test config with invalid values falls back to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".pelformat.toml"
            config_path.write_text("""
[format]
line_length = "not a number"
indent_size = -5
""")
            config = load_formatter_config(Path(tmpdir))
            # Should fall back to defaults for invalid values
            assert isinstance(config.line_length, int)
            assert isinstance(config.indent_size, int)
