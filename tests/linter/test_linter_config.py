# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Linter configuration tests."""

import tempfile
from pathlib import Path

from linter.config import LinterConfig, find_linter_config, load_linter_config


class TestLinterConfig:
    """Test linter configuration loading."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LinterConfig()

        assert "PEL001" in config.enabled_rules
        assert "PEL002" in config.enabled_rules
        assert config.line_length == 100
        assert isinstance(config.exclude_paths, list)

    def test_custom_enabled_rules(self):
        """Test custom enabled rules."""
        config = LinterConfig(enabled_rules=["PEL001", "PEL010"])

        assert len(config.enabled_rules) == 2
        assert "PEL001" in config.enabled_rules
        assert "PEL010" in config.enabled_rules

    def test_rule_severity_override(self):
        """Test rule severity overrides."""
        config = LinterConfig()
        config.rule_severity["PEL010"] = "error"

        assert config.rule_severity["PEL010"] == "error"

    def test_load_config_no_file(self):
        """Test loading config when no .pellint.toml exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_linter_config(Path(tmpdir))

            # Should return defaults
            assert "PEL001" in config.enabled_rules

    def test_load_config_from_file(self):
        """Test loading config from .pellint.toml file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".pellint.toml"
            config_path.write_text("""
[linter]
line_length = 120
enabled_rules = ["PEL001", "PEL010"]

[rules.PEL010]
severity = "error"
""")
            config = load_linter_config(Path(tmpdir))

            assert config.line_length == 120
            assert "PEL001" in config.enabled_rules
            assert "PEL010" in config.enabled_rules
            assert config.rule_severity["PEL010"] == "error"

    def test_find_config_in_parent(self):
        """Test finding config file in parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parent = Path(tmpdir)
            child = parent / "subdir"
            child.mkdir()

            config_path = parent / ".pellint.toml"
            config_path.write_text("[linter]\nline_length = 88")

            found = find_linter_config(child)
            assert found == config_path

    def test_find_config_not_found(self):
        """Test when config file is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            found = find_linter_config(Path(tmpdir))
            assert found is None

    def test_exclude_paths(self):
        """Test exclude paths configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".pellint.toml"
            config_path.write_text("""
[linter]
exclude_paths = ["tests/**", "*.generated.pel"]
""")
            config = load_linter_config(Path(tmpdir))

            assert "tests/**" in config.exclude_paths
            assert "*.generated.pel" in config.exclude_paths

    def test_partial_config(self):
        """Test config file with only some values set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".pellint.toml"
            config_path.write_text("""
[linter]
line_length = 120
""")
            config = load_linter_config(Path(tmpdir))

            # Should have custom line_length
            assert config.line_length == 120
            # Should have default enabled_rules
            assert len(config.enabled_rules) > 0
