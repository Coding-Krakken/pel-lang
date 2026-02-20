"""Tests to cover visualization.py uncovered lines."""

import pytest

from runtime.visualization import VISUALIZATION_AVAILABLE, ModelVisualizer


class TestModelVisualizerWithResults:
    """Test ModelVisualizer with actual result objects."""

    def test_visualizer_with_simple_results(self):
        """Test visualization with simple deterministic results."""
        if not VISUALIZATION_AVAILABLE:
            pytest.skip("Visualization not available")

        results = {
            "model": {"name": "TestModel"},
            "status": "success",
            "variables": {"revenue": [100, 110, 121, 133], "cost": [60, 65, 70, 75]},
        }

        viz = ModelVisualizer(results)
        # Test plot_time_series
        viz.plot_time_series("revenue")

    def test_visualizer_missing_variable(self):
        """Test Error handling for missing variable."""
        if not VISUALIZATION_AVAILABLE:
            pytest.skip("Visualization not available")

        results = {"model": {"name": "Test"}, "variables": {"x": [1, 2, 3]}}

        viz = ModelVisualizer(results)
        with pytest.raises(ValueError, match="not found"):
            viz.plot_time_series("nonexistent")

    def test_visualizer_non_list_variable(self):
        """Test error handling for non-list variables."""
        if not VISUALIZATION_AVAILABLE:
            pytest.skip("Visualization not available")

        results = {"model": {"name": "Test"}, "variables": {"scalar": 42}}

        viz = ModelVisualizer(results)
        with pytest.raises(ValueError, match="not a time series"):
            viz.plot_time_series("scalar")

    def test_visualizer_with_confidence_intervals(self):
        """Test visualization with Monte Carlo confidence intervals."""
        if not VISUALIZATION_AVAILABLE:
            pytest.skip("Visualization not available")

        results = {
            "model": {"name": "MCModel"},
            "mode": "monte_carlo",
            "aggregates": {
                "profit": {"mean": [50, 55, 60], "p10": [40, 44, 48], "p90": [60, 66, 72]}
            },
            "variables": {"profit": [50, 55, 60]},  # Mean values
        }

        viz = ModelVisualizer(results)
        # Should not raise even though show_ci is True
        viz.plot_time_series("profit", show_ci=True)

    @pytest.mark.skipif(not VISUALIZATION_AVAILABLE, reason="Viz not available")
    def test_plot_distribution(self):
        """Test distribution plotting."""
        results = {
            "model": {"name": "MCTest"},
            "aggregates": {"x": {"p10": [10], "p50": [50], "p90": [90]}},
        }

        viz = ModelVisualizer(results)
        viz.plot_distribution("x", timestep=0)

    @pytest.mark.skipif(not VISUALIZATION_AVAILABLE, reason="Viz not available")
    def test_plot_tornado(self):
        """Test tornado chart plotting."""
        results = {
            "model": {"name": "Sensitivity"},
            "sensitivity": {
                "base_case": {"npv": 1000},
                "parameters": {
                    "growth_rate": {"low": {"npv": 800}, "high": {"npv": 1200}},
                    "discount_rate": {"low": {"npv": 900}, "high": {"npv": 1100}},
                },
            },
        }

        viz = ModelVisualizer(results)
        viz.plot_tornado("npv")

    @pytest.mark.skipif(not VISUALIZATION_AVAILABLE, reason="Viz not available")
    def test_plot_correlation_matrix(self):
        """Test correlation matrix plotting."""
        results = {
            "model": {"name": "Correlation"},
            "correlations": {
                "revenue": {"revenue": 1.0, "cost": 0.8},
                "cost": {"revenue": 0.8, "cost": 1.0},
            },
        }

        viz = ModelVisualizer(results)
        viz.plot_correlation_matrix()


class TestVisualizationNotAvailable:
    """Test behavior when matplotlib is not available."""

    def test_visualizer_raises_import_error_without_matplotlib(self):
        """Test that ModelVisualizer raises ImportError when matplotlib unavailable."""
        if VISUALIZATION_AVAILABLE:
            # Cannot test this when matplotlib IS available
            pytest.skip("Matplotlib is available")

        results = {"model": {"name": "Test"}, "variables": {}}

        with pytest.raises(ImportError, match="matplotlib"):
            ModelVisualizer(results)
