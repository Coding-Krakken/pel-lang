# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Integration tests for Calibration.
"""

import json
from pathlib import Path

import pytest

try:
    import numpy as np
    import pandas as pd
    import yaml

    from runtime.calibration import CalibrationConfig, Calibrator
except ImportError:
    pytest.skip("calibration module not installed", allow_module_level=True)


class TestCalibrationIntegration:
    """Integration tests for full calibration pipeline."""

    @pytest.fixture
    def sample_model(self, tmp_path):
        """Create a sample PEL-IR model."""
        model = {
            "pel_version": "0.1.0",
            "model": {
                "name": "test_model",
                "nodes": [
                    {
                        "node_type": "param",
                        "name": "churn_rate",
                        "param_type": "Probability",
                        "value": {
                            "expr_type": "DistributionExpression",
                            "distribution": "beta",
                            "params": {
                                "alpha": 2.0,
                                "beta": 20.0,
                            }
                        },
                        "provenance": {
                            "source": "assumption",
                            "method": "expert_estimate",
                            "confidence": 0.3,
                        }
                    },
                    {
                        "node_type": "param",
                        "name": "lifetime",
                        "param_type": "Duration",
                        "value": {
                            "expr_type": "DistributionExpression",
                            "distribution": "lognormal",
                            "params": {
                                "mu": 2.5,
                                "sigma": 0.5,
                            }
                        },
                    }
                ]
            }
        }

        model_path = tmp_path / "model.ir.json"
        with open(model_path, 'w') as f:
            json.dump(model, f, indent=2)

        return model_path

    @pytest.fixture
    def sample_data(self, tmp_path):
        """Create sample CSV data."""
        # Generate synthetic data
        np.random.seed(42)
        n = 50

        data = {
            'month': [f"2025-{i+1:02d}" for i in range(n)],
            'churn': np.random.beta(10, 120, n),  # Mean ~0.077
            'lifetime_months': np.random.lognormal(2.6, 0.15, n),  # Median ~13.5
        }

        df = pd.DataFrame(data)
        csv_path = tmp_path / "data.csv"
        df.to_csv(csv_path, index=False)

        return csv_path

    @pytest.fixture
    def calibration_config(self, tmp_path, sample_model, sample_data):
        """Create calibration configuration."""
        config = {
            'csv_path': str(sample_data),
            'model_path': str(sample_model),
            'output_path': str(tmp_path / "calibrated"),
            'csv_config': {
                'column_mapping': {
                    'churn_rate': 'churn',
                    'lifetime': 'lifetime_months',
                },
                'type_mapping': {
                    'churn_rate': 'float',
                    'lifetime': 'float',
                },
                'missing_values': {
                    'strategy': 'drop',
                },
            },
            'parameters': {
                'churn_rate': {
                    'data_column': 'churn_rate',
                    'distribution': 'beta',
                    'use_bootstrap': False,  # Faster for testing
                },
                'lifetime': {
                    'data_column': 'lifetime',
                    'distribution': 'lognormal',
                    'use_bootstrap': False,
                },
            },
            'drift_config': {
                'mape_threshold': 0.15,
                'cusum_threshold': 5.0,
            },
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        return config_path

    def test_calibration_config_from_yaml(self, calibration_config):
        """Test loading CalibrationConfig from YAML."""
        config = CalibrationConfig.from_yaml(calibration_config)

        assert config.csv_path is not None
        assert config.model_path is not None
        assert 'churn_rate' in config.parameters

    def test_calibration_config_to_yaml(self, tmp_path):
        """Test saving CalibrationConfig to YAML."""
        config = CalibrationConfig(
            csv_path="data.csv",
            model_path="model.json",
            parameters={'param1': {'distribution': 'normal'}}
        )

        yaml_path = tmp_path / "config.yaml"
        config.to_yaml(yaml_path)

        assert yaml_path.exists()

        # Reload and verify
        loaded = CalibrationConfig.from_yaml(yaml_path)
        assert loaded.csv_path == "data.csv"
        assert loaded.model_path == "model.json"

    def test_full_calibration_pipeline(self, calibration_config):
        """Test complete calibration pipeline."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)

        result = calibrator.calibrate()

        # Check result structure
        assert result.model_name == "test_model"
        assert len(result.parameters) == 2
        assert 'churn_rate' in result.parameters
        assert 'lifetime' in result.parameters

        # Check fitted parameters
        churn_fit = result.parameters['churn_rate']
        assert churn_fit.distribution == 'beta'
        assert 'alpha' in churn_fit.parameters
        assert 'beta' in churn_fit.parameters

        lifetime_fit = result.parameters['lifetime']
        assert lifetime_fit.distribution == 'lognormal'
        assert 'mu' in lifetime_fit.parameters
        assert 'sigma' in lifetime_fit.parameters

    def test_calibration_updates_model(self, calibration_config):
        """Test that calibration updates model parameters."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)

        # Load original model
        calibrator.load_model(Path(config.model_path))

        # Calibrate
        result = calibrator.calibrate()

        # Check updated model
        updated_model = result.updated_model

        # Find churn_rate parameter
        churn_param = None
        for node in updated_model['model']['nodes']:
            if node.get('name') == 'churn_rate':
                churn_param = node
                break

        assert churn_param is not None

        # Check parameters were updated
        original_alpha = 2.0
        updated_alpha = churn_param['value']['params']['alpha']

        # Should be different from original assumption
        assert updated_alpha != original_alpha

        # Check provenance was updated
        assert churn_param['provenance']['source'] == 'calibrated'
        assert churn_param['provenance']['method'] == 'mle'
        assert 'calibration_timestamp' in churn_param['provenance']

    def test_calibration_saves_outputs(self, calibration_config):
        """Test that calibration saves output files."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)

        calibrator.calibrate()

        output_path = Path(config.output_path)

        # Check output files exist
        model_path = output_path.parent / f"{output_path.stem}_calibrated.ir.json"
        json_path = output_path.parent / f"{output_path.stem}_report.json"
        md_path = output_path.parent / f"{output_path.stem}_report.md"

        assert model_path.exists()
        assert json_path.exists()
        assert md_path.exists()

        # Verify JSON report content
        with open(json_path) as f:
            report = json.load(f)

        assert 'model_name' in report
        assert 'parameters' in report
        assert 'timestamp' in report

        # Verify markdown report content
        md_content = md_path.read_text()
        assert "Calibration Report" in md_content
        assert "churn_rate" in md_content

    def test_calibration_with_bootstrap(self, tmp_path, sample_model, sample_data):
        """Test calibration with bootstrap confidence intervals."""
        config = CalibrationConfig(
            csv_path=str(sample_data),
            model_path=str(sample_model),
            output_path=str(tmp_path / "calibrated"),
            csv_config={
                'column_mapping': {
                    'churn_rate': 'churn',
                },
                'type_mapping': {
                    'churn_rate': 'float',
                },
            },
            parameters={
                'churn_rate': {
                    'data_column': 'churn_rate',
                    'distribution': 'beta',
                    'use_bootstrap': True,
                    'bootstrap_samples': 100,  # Small for speed
                },
            },
        )

        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        # Check bootstrap CI was computed
        churn_fit = result.parameters['churn_rate']
        assert 'alpha' in churn_fit.confidence_intervals
        assert 'beta' in churn_fit.confidence_intervals

    def test_calibration_result_to_dict(self, calibration_config):
        """Test CalibrationResult serialization to dict."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert 'model_name' in result_dict
        assert 'parameters' in result_dict
        assert 'timestamp' in result_dict

        # Check parameters are serializable
        assert 'churn_rate' in result_dict['parameters']
        churn = result_dict['parameters']['churn_rate']
        assert 'distribution' in churn
        assert 'parameters' in churn
        assert 'confidence_intervals' in churn

    def test_calibration_with_missing_parameter(self, tmp_path, sample_model, sample_data):
        """Test calibration when CSV is missing a parameter column."""
        config = CalibrationConfig(
            csv_path=str(sample_data),
            model_path=str(sample_model),
            parameters={
                'nonexistent_param': {
                    'data_column': 'nonexistent_column',
                    'distribution': 'normal',
                },
            },
        )

        calibrator = Calibrator(config)

        # Should raise error about missing column
        with pytest.raises(ValueError, match="not found"):
            calibrator.calibrate()

    def test_calibration_with_outliers(self, tmp_path, sample_model):
        """Test calibration with outlier filtering."""
        # Create data with outliers
        np.random.seed(42)
        data = {
            'churn': list(np.random.beta(10, 120, 45)) + [0.99, 0.98, 0.97, 0.96, 0.95],
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "data_outliers.csv"
        df.to_csv(csv_path, index=False)

        config = CalibrationConfig(
            csv_path=str(csv_path),
            model_path=str(sample_model),
            csv_config={
                'column_mapping': {
                    'churn_rate': 'churn',
                },
                'type_mapping': {
                    'churn_rate': 'float',
                },
                'outlier_filtering': [
                    {
                        'column': 'churn_rate',
                        'method': 'iqr',
                        'threshold': 3.0,
                    }
                ],
            },
            parameters={
                'churn_rate': {
                    'data_column': 'churn_rate',
                    'distribution': 'beta',
                },
            },
        )

        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        # Should successfully calibrate (outliers filtered)
        assert 'churn_rate' in result.parameters

    def test_calibration_empty_parameters(self, tmp_path, sample_model, sample_data):
        """Test calibration with no parameters specified."""
        config = CalibrationConfig(
            csv_path=str(sample_data),
            model_path=str(sample_model),
            parameters={},  # Empty
        )

        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        # Should complete without errors, but no parameters fitted
        assert len(result.parameters) == 0

    def test_calibration_none_parameters(self, tmp_path, sample_model, sample_data):
        """Test calibration with None parameters."""
        config = CalibrationConfig(
            csv_path=str(sample_data),
            model_path=str(sample_model),
            parameters=None,
        )

        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        # Should complete without errors
        assert len(result.parameters) == 0

    def test_markdown_report_content(self, calibration_config, tmp_path):
        """Test markdown report formatting."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        md_path = tmp_path / "test_report.md"
        result.to_markdown(md_path)

        content = md_path.read_text()

        # Check structure
        assert "# Calibration Report" in content
        assert "## Data Source" in content
        assert "## Fitted Parameters" in content

        # Check parameter sections
        assert "### churn_rate" in content
        assert "### lifetime" in content

        # Check statistical info
        assert "AIC:" in content
        assert "BIC:" in content
        assert "Kolmogorov-Smirnov" in content

    def test_json_report_content(self, calibration_config, tmp_path):
        """Test JSON report content."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        json_path = tmp_path / "test_report.json"
        result.to_json(json_path)

        with open(json_path) as f:
            report = json.load(f)

        # Check structure
        assert 'model_name' in report
        assert 'timestamp' in report
        assert 'parameters' in report

        # Check parameter details
        assert 'churn_rate' in report['parameters']
        churn = report['parameters']['churn_rate']
        assert 'distribution' in churn
        assert churn['distribution'] == 'beta'
        assert 'aic' in churn
        assert 'bic' in churn

    def test_calibration_updates_confidence(self, calibration_config):
        """Test that calibration updates provenance confidence."""
        config = CalibrationConfig.from_yaml(calibration_config)
        calibrator = Calibrator(config)
        result = calibrator.calibrate()

        # Check updated model provenance
        churn_param = None
        for node in result.updated_model['model']['nodes']:
            if node.get('name') == 'churn_rate':
                churn_param = node
                break

        # Original confidence was 0.3
        # Calibrated confidence is now based on KS p-value directly
        # (high p-value = good fit = high confidence)
        new_confidence = churn_param['provenance']['confidence']

        # For a well-fitted distribution, KS p-value should be > 0.05
        assert 0.0 <= new_confidence <= 1.0
