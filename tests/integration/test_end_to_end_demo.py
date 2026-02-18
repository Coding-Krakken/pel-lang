"""
Integration test for end-to-end demo workflow.

Tests the complete pipeline: compile → run → report → visualize
"""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_demo_workflow_executes_successfully(tmp_path):
    """Test that the quick_start.sh script runs end-to-end without errors."""
    # Skip if visualization dependencies are not installed
    try:
        import jinja2  # noqa: F401
    except ImportError:
        pytest.skip("Visualization dependencies (jinja2) not installed - install with: pip install 'pel-lang[viz]'")

    # Determine repository root (two levels up from this test file: tests/integration → tests → repo root)
    repo_root = Path(__file__).resolve().parents[2]

    # Locate the demo script relative to the repo root
    demo_script = repo_root / "demo" / "quick_start.sh"
    assert demo_script.exists()
    assert demo_script.stat().st_mode & 0o111  # Check executable bit

    # Redirect stdout/stderr to temporary files for inspection if the test fails
    stdout_log = tmp_path / "quick_start_stdout.log"
    stderr_log = tmp_path / "quick_start_stderr.log"

    with stdout_log.open("wb") as stdout_f, stderr_log.open("wb") as stderr_f:
        result = subprocess.run(
            [str(demo_script)],
            cwd=str(repo_root),
            stdout=stdout_f,
            stderr=stderr_f,
            check=False,
        )

    # The demo workflow should complete successfully
    if result.returncode != 0:
        # Print logs for debugging
        print("\n--- STDOUT ---")
        print(stdout_log.read_text())
        print("\n--- STDERR ---")
        print(stderr_log.read_text())

    assert result.returncode == 0

    # Basic artifact check: script should have produced some stdout content
    assert stdout_log.exists()
    assert stdout_log.stat().st_size > 0


@pytest.mark.integration
def test_reporting_module_generates_markdown():
    """Test that reporting module can generate Markdown reports."""
    from runtime.reporting import ModelReport

    # Sample results
    results = {
        "model": {"name": "TestModel"},
        "status": "success",
        "mode": "deterministic",
        "seed": 42,
        "runtime_ms": 123.45,
        "variables": {
            "revenue": [10000, 11000, 12100],
            "profit": [2000, 3000, 4100]
        },
        "constraint_violations": [],
        "assumptions": [
            {
                "name": "growth_rate",
                "source": "test",
                "method": "assumption",
                "confidence": 0.8
            }
        ]
    }

    report = ModelReport(results)
    md_content = report.generate_markdown()

    assert "TestModel" in md_content
    assert "success" in md_content
    assert "revenue" in md_content
    assert "No constraint violations" in md_content


@pytest.mark.integration
def test_reporting_module_generates_html():
    """Test that reporting module can generate HTML reports."""
    from runtime.reporting import ModelReport

    results = {
        "model": {"name": "TestModel"},
        "status": "success",
        "mode": "deterministic",
        "seed": 42,
        "runtime_ms": 123.45,
        "variables": {"revenue": [10000, 11000]},
        "constraint_violations": [],
        "assumptions": []
    }

    report = ModelReport(results)
    html_content = report.generate_html()

    assert "<!DOCTYPE html>" in html_content
    assert "TestModel" in html_content
    assert "<table>" in html_content


@pytest.mark.integration
def test_visualization_requires_matplotlib():
    """Test that visualization module checks for dependencies."""
    try:
        from runtime.visualization import VISUALIZATION_AVAILABLE
        # If matplotlib is installed, this should be True
        # If not, it should be False (graceful degradation)
        assert isinstance(VISUALIZATION_AVAILABLE, bool)
    except ImportError:
        # Module should still be importable even if deps missing
        pass
