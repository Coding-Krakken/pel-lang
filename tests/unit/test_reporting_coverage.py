"""Tests to cover reporting.py uncovered lines."""

import tempfile
from pathlib import Path

from runtime.reporting import ModelReport


class TestModelReportMarkdownGeneration:
    """Test markdown generation edge cases."""

    def test_report_with_empty_variables(self):
        """Test report generation with no variables."""
        results = {
            "model": {"name": "Empty"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 10.5,
            "variables": {},
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)
        md = report.generate_markdown()

        assert "Empty" in md
        assert "No variables recorded" in md

    def test_report_with_non_list_variables(self):
        """Test report with scalar (non-list) variables."""
        results = {
            "model": {"name": "Scalar"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 5.0,
            "variables": {
                "fixed_cost": 1000,  # Scalar value
                "margin": 0.25,  # Another scalar
            },
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)
        md = report.generate_markdown()

        assert "fixed_cost" in md
        assert "1000" in md
        assert "margin" in md

    def test_report_with_none_seed(self):
        """Test report when seed is None."""
        results = {
            "model": {"name": "NoSeed"},
            "status": "success",
            "mode": "monte_carlo",
            "runtime_ms": 100.0,
            "seed": None,
            "variables": {},
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)
        md = report.generate_markdown()

        # Seed line should be omitted when None
        assert "NoSeed" in md
        # The seed should not appear when it's None
        assert "**Seed:** None" not in md

    def test_report_saves_markdown_to_file(self):
        """Test saving markdown report to file."""
        results = {
            "model": {"name": "SaveTest"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 1.0,
            "variables": {"x": [10, 20]},
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.md"
            md = report.generate_markdown(output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert content == md
            assert "SaveTest" in content

    def test_report_with_constraint_violations(self):
        """Test report with constraint violations."""
        results = {
            "model": {"name": "Violations"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 5.0,
            "variables": {},
            "constraint_violations": [
                {"constraint": "positive_profit", "timestep": 2, "message": "Profit is negative"},
                {"constraint": "revenue_target", "timestep": 5, "message": "Revenue below target"},
            ],
            "assumptions": [],
        }

        report = ModelReport(results)
        md = report.generate_markdown()

        assert "positive_profit" in md
        assert "revenue_target" in md
        assert "timestep 2" in md
        assert "Profit is negative" in md

    def test_report_with_assumptions(self):
        """Test report with assumption register."""
        results = {
            "model": {"name": "WithAssumptions"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 2.0,
            "variables": {},
            "constraint_violations": [],
            "assumptions": [
                {
                    "name": "growth_rate",
                    "source": "Historical data",
                    "method": "Linear regression",
                    "confidence": "high",
                },
                {
                    "name": "churn_rate",
                    "source": "Industry benchmark",
                    "method": "Expert judgment",
                    "confidence": "medium",
                },
            ],
        }

        report = ModelReport(results)
        md = report.generate_markdown()

        assert "growth_rate" in md
        assert "churn_rate" in md
        assert "Historical data" in md
        assert "Linear regression" in md


class TestModelReportHTMLGeneration:
    """Test HTML generation."""

    def test_generate_html_basic(self):
        """Test basic HTML generation."""
        results = {
            "model": {"name": "HTMLTest"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 1.0,
            "variables": {"x": [1, 2, 3]},
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)
        html = report.generate_html()

        assert "HTMLTest" in html
        assert "<" in html  # Should have HTML tags

    def test_generate_html_with_output_path(self):
        """Test saving HTML to file."""
        results = {
            "model": {"name": "HTMLSave"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 1.0,
            "variables": {},
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.html"
            html = report.generate_html(output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert content == html

    def test_generate_html_with_charts(self):
        """Test HTML generation with charts enabled."""
        results = {
            "model": {"name": "HTMLCharts"},
            "status": "success",
            "mode": "deterministic",
            "runtime_ms": 1.0,
            "variables": {"x": [1, 2, 3]},
            "constraint_violations": [],
            "assumptions": [],
        }

        report = ModelReport(results)
        # Test with include_charts parameter
        html = report.generate_html(include_charts=True)

        assert "HTMLCharts" in html
