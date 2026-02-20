from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest


@pytest.mark.unit
def test_check_baseline_age_fresh_baseline(tmp_path: Path) -> None:
    """Test that fresh baselines pass without warnings."""
    baseline = tmp_path / "baseline.json"
    today = date.today()
    created = today - timedelta(days=30)  # 30 days old
    
    baseline.write_text(
        json.dumps({"target_id": "test", "created_at": created.isoformat(), "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    result = subprocess.run(
        [sys.executable, str(script), str(baseline), "--today", today.isoformat()],
        capture_output=True,
        text=True,
        check=False,
    )
    
    assert result.returncode == 0, result.stderr or result.stdout
    output = result.stdout + result.stderr  # Log output goes to stderr
    assert "OK: Baseline is fresh (30 days old)" in output


@pytest.mark.unit
def test_check_baseline_age_warning_threshold(tmp_path: Path) -> None:
    """Test that baselines older than warning threshold produce warnings."""
    baseline = tmp_path / "baseline.json"
    today = date.today()
    created = today - timedelta(days=100)  # 100 days old (> 90 day default)
    
    baseline.write_text(
        json.dumps({"target_id": "test", "created_at": created.isoformat(), "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    result = subprocess.run(
        [sys.executable, str(script), str(baseline), "--today", today.isoformat()],
        capture_output=True,
        text=True,
        check=False,
    )
    
    # Returns 0 by default (warning doesn't fail)
    assert result.returncode == 0, result.stderr or result.stdout
    output = result.stdout + result.stderr
    assert "WARNING: Baseline is 100 days old" in output


@pytest.mark.unit
def test_check_baseline_age_error_threshold(tmp_path: Path) -> None:
    """Test that baselines older than error threshold produce errors."""
    baseline = tmp_path / "baseline.json"
    today = date.today()
    created = today - timedelta(days=200)  # 200 days old (> 180 day default)
    
    baseline.write_text(
        json.dumps({"target_id": "test", "created_at": created.isoformat(), "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    result = subprocess.run(
        [sys.executable, str(script), str(baseline), "--today", today.isoformat()],
        capture_output=True,
        text=True,
        check=False,
    )
    
    # Returns 2 for critical errors
    assert result.returncode == 2, result.stderr or result.stdout
    output = result.stdout + result.stderr
    assert "CRITICAL: Baseline is 200 days old" in output


@pytest.mark.unit
def test_check_baseline_age_fail_on_warning(tmp_path: Path) -> None:
    """Test that --fail-on-warning causes warnings to return exit code 1."""
    baseline = tmp_path / "baseline.json"
    today = date.today()
    created = today - timedelta(days=100)  # 100 days old (warning threshold)
    
    baseline.write_text(
        json.dumps({"target_id": "test", "created_at": created.isoformat(), "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    result = subprocess.run(
        [sys.executable, str(script), str(baseline), "--today", today.isoformat(), "--fail-on-warning"],
        capture_output=True,
        text=True,
        check=False,
    )
    
    assert result.returncode == 1, result.stderr or result.stdout


@pytest.mark.unit
def test_check_baseline_age_custom_thresholds(tmp_path: Path) -> None:
    """Test that custom warning/error thresholds work correctly."""
    baseline = tmp_path / "baseline.json"
    today = date.today()
    created = today - timedelta(days=70)  # 70 days old
    
    baseline.write_text(
        json.dumps({"target_id": "test", "created_at": created.isoformat(), "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    
    # With default thresholds (90/180), should be fresh
    result_default = subprocess.run(
        [sys.executable, str(script), str(baseline), "--today", today.isoformat()],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result_default.returncode == 0
    output_default = result_default.stdout + result_default.stderr
    assert "OK: Baseline is fresh" in output_default
    
    # With custom thresholds (60/120), should warn
    result_custom = subprocess.run(
        [
            sys.executable, str(script), str(baseline),
            "--warning-days", "60",
            "--error-days", "120",
            "--today", today.isoformat(),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result_custom.returncode == 0  # Doesn't fail by default
    output_custom = result_custom.stdout + result_custom.stderr
    assert "WARNING: Baseline is 70 days old" in output_custom


@pytest.mark.unit
def test_check_baseline_age_missing_timestamp(tmp_path: Path) -> None:
    """Test that baselines without timestamps produce warnings."""
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps({"target_id": "test", "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    result = subprocess.run(
        [sys.executable, str(script), str(baseline)],
        capture_output=True,
        text=True,
        check=False,
    )
    
    output = result.stdout + result.stderr
    assert "has no created_at or generated_at timestamp" in outp
    assert result.returncode == 1, result.stderr or result.stdout
    assert "has no created_at or generated_at timestamp" in result.stdout


@pytest.mark.unit
def test_check_baseline_age_iso_datetime_format(tmp_path: Path) -> None:
    """Test that ISO datetime format with timezone is parsed correctly."""
    baseline = tmp_path / "baseline.json"
    today = date.today()
    created = today - timedelta(days=50)
    created_iso = f"{created.isoformat()}T12:00:00Z"
    
    baseline.write_text(
        json.dumps({"target_id": "test", "created_at": created_iso, "overall_score": 3.5}),
        encoding="utf-8"
    )
    
    script = Path(".language-eval/scripts/check_baseline_age.py")
    result = subprocess.run(
        [sys.executable, str(script), str(baseline), "--today", today.isoformat()],
        capture_output=True,
        text=True,
        check=False,
    )
    
    output = result.stdout + result.stderr
    assert "OK: Baseline is fresh (50 days old)" in output
    assert "OK: Baseline is fresh (50 days old)" in result.stdout
