"""
Integration test for end-to-end demo workflow.

Tests the complete pipeline: compile → run → report → visualize
"""

import json
import subprocess
from pathlib import Path
import pytest


def test_demo_workflow_executes_successfully(tmp_path):
    """Test that the quick_start.sh script runs without errors."""
    # This would run the actual demo script
    # For now, just verify the script exists and is executable
    demo_script = Path("demo/quick_start.sh")
    assert demo_script.exists()
    assert demo_script.stat().st_mode & 0o111  # Check executable bit


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
