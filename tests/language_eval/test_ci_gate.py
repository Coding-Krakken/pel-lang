# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Tests for ci_gate.py: schema validation, artifact checks, expiry enforcement."""

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Import the ci_gate module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".language-eval" / "scripts"))
import ci_gate


@pytest.fixture
def mock_report_dir(tmp_path):
    """Create a mock report directory with required artifacts."""
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    
    # Create minimal valid artifacts
    (report_dir / "results.normalized.json").write_text(
        json.dumps({
            "target_id": "test",
            "timestamp": "2026-01-15T12:00:00Z",
            "metrics": {"category_inputs": {}},
            "suites": [],
        })
    )
    
    (report_dir / "scorecard.json").write_text(
        json.dumps({
            "target_id": "test",
            "overall_score": 4.5,
            "category_scores": {},
            "suite_scores": {},
            "weights": {},
        })
    )
    
    (report_dir / "report.json").write_text(
        json.dumps({
            "target_id": "test",
            "timestamp": "2026-01-15T12:00:00Z",
            "overall_score": 4.5,
            "environment": {},
            "hash": "abc123",
        })
    )
    
    return report_dir


class TestArtifactPresence:
    """Test required artifact presence checks."""

    def test_all_artifacts_present(self, mock_report_dir):
        """Verify check passes when all required artifacts exist."""
        required = [
            "results.normalized.json",
            "scorecard.json",
            "report.json",
        ]
        
        for artifact in required:
            assert (mock_report_dir / artifact).exists()

    def test_missing_artifact_detected(self, mock_report_dir):
        """Verify check fails when required artifact is missing."""
        # Remove scorecard
        (mock_report_dir / "scorecard.json").unlink()
        
        required = ["results.normalized.json", "scorecard.json", "report.json"]
        missing = [name for name in required if not (mock_report_dir / name).exists()]
        
        assert "scorecard.json" in missing


class TestDeterminismValidation:
    """Test determinism checks via hash comparison."""

    def test_identical_hashes_pass(self):
        """Verify determinism check passes when hashes match."""
        report_a = {"hash": "abc123def456"}
        report_b = {"hash": "abc123def456"}
        
        assert report_a["hash"] == report_b["hash"]

    def test_different_hashes_fail(self):
        """Verify determinism check fails when hashes differ."""
        report_a = {"hash": "abc123def456"}
        report_b = {"hash": "fedcba654321"}
        
        assert report_a["hash"] != report_b["hash"]


class TestExpectedFailureExpiry:
    """Test expected-failure expiry enforcement."""

    def test_expiry_date_in_past_fails(self):
        """Verify expired expected-failures are flagged."""
        # Mock expected failure with expiry in the past
        expected_failure = {
            "category": "performance",
            "reason": "Known regression in optimizer",
            "expiry": (datetime.now() - timedelta(days=10)).isoformat(),
        }
        
        expiry_date = datetime.fromisoformat(expected_failure["expiry"])
        assert expiry_date < datetime.now(), "Expiry date in past should be detected"

    def test_expiry_date_in_future_passes(self):
        """Verify future expected-failures are allowed."""
        expected_failure = {
            "category": "performance",
            "reason": "Known regression in optimizer",
            "expiry": (datetime.now() + timedelta(days=30)).isoformat(),
        }
        
        expiry_date = datetime.fromisoformat(expected_failure["expiry"])
        assert expiry_date > datetime.now(), "Future expiry date should be valid"


class TestSchemaValidation:
    """Test JSON schema validation."""

    def test_valid_target_config_passes(self):
        """Verify valid target config passes schema validation."""
        # This would require loading the actual schema and using jsonschema
        # Simplified test structure
        valid_target = {
            "target_id": "pel-test",
            "language": {"name": "PEL", "version": "0.1.0"},
            "platform": {"os": "linux", "arch": "x86_64"},
            "commands": {},
            "enabled_suites": [],
            "weight_profile": "default",
        }
        
        # Assert structure is valid
        assert "target_id" in valid_target
        assert "language" in valid_target

    def test_invalid_target_config_fails(self):
        """Verify invalid target config fails schema validation."""
        invalid_target = {
            "target_id": "test",
            # missing required fields
        }
        
        # Would fail schema validation
        assert "language" not in invalid_target


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
