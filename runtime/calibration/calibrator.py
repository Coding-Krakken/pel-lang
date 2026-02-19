# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Main Calibration Orchestrator for PEL.

Coordinates CSV loading, parameter estimation, drift detection,
and report generation.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import yaml

from .csv_connector import CSVConnector
from .drift_detection import DriftDetector, DriftReport
from .parameter_estimation import FitResult, ParameterEstimator


@dataclass
class CalibrationConfig:
    """
    Calibration configuration.
    
    Specifies which parameters to calibrate, data sources,
    and calibration settings.
    """
    csv_path: str
    model_path: str
    output_path: Optional[str] = None
    parameters: Dict[str, Dict[str, Any]] = None  # param_name -> config
    csv_config: Optional[Dict[str, Any]] = None
    drift_config: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'CalibrationConfig':
        """Load configuration from YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def to_yaml(self, yaml_path: Path) -> None:
        """Save configuration to YAML file."""
        with open(yaml_path, 'w') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)


@dataclass
class CalibrationResult:
    """
    Results from calibration process.
    
    Contains fitted parameters, goodness-of-fit metrics,
    and drift analysis.
    """
    model_name: str
    timestamp: str
    parameters: Dict[str, FitResult]
    drift_reports: Dict[str, DriftReport]
    updated_model: Dict[str, Any]
    config: CalibrationConfig
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'model_name': self.model_name,
            'timestamp': self.timestamp,
            'parameters': {
                name: {
                    'distribution': fit.distribution,
                    'parameters': fit.parameters,
                    'confidence_intervals': {
                        k: list(v) for k, v in fit.confidence_intervals.items()
                    },
                    'aic': fit.aic,
                    'bic': fit.bic,
                    'ks_pvalue': fit.ks_pvalue,
                }
                for name, fit in self.parameters.items()
            },
            'drift_reports': {
                name: {
                    'mape': report.mape,
                    'rmse': report.rmse,
                    'cusum_detected': report.cusum_detected,
                    'cusum_changepoint': report.cusum_changepoint,
                    'drift_threshold_exceeded': report.drift_threshold_exceeded,
                    'recommendations': report.recommendations,
                }
                for name, report in self.drift_reports.items()
            },
            'updated_model': self.updated_model,
        }
    
    def to_json(self, json_path: Path) -> None:
        """Save results to JSON file."""
        with open(json_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def to_markdown(self, md_path: Path) -> None:
        """Generate markdown calibration report."""
        lines = [
            f"# Calibration Report: {self.model_name}",
            f"",
            f"**Generated:** {self.timestamp}",
            f"",
            f"## Data Source",
            f"",
            f"- CSV File: `{self.config.csv_path}`",
            f"- Model: `{self.config.model_path}`",
            f"",
            f"## Fitted Parameters",
            f"",
        ]
        
        for param_name, fit in self.parameters.items():
            lines.extend([
                f"### {param_name}",
                f"",
                f"**Distribution:** {fit.distribution}",
                f"",
                f"**Fitted Parameters:**",
            ])
            
            for pname, pvalue in fit.parameters.items():
                ci = fit.confidence_intervals[pname]
                lines.append(f"- {pname}: {pvalue:.6f} (95% CI: [{ci[0]:.6f}, {ci[1]:.6f}])")
            
            lines.extend([
                f"",
                f"**Goodness of Fit:**",
                f"- AIC: {fit.aic:.2f}",
                f"- BIC: {fit.bic:.2f}",
                f"- Kolmogorov-Smirnov p-value: {fit.ks_pvalue:.4f}",
                f"",
            ])
        
        if self.drift_reports:
            lines.extend([
                f"## Drift Detection",
                f"",
            ])
            
            for param_name, report in self.drift_reports.items():
                lines.extend([
                    f"### {param_name}",
                    f"",
                    f"- MAPE: {report.mape:.2%}",
                    f"- RMSE: {report.rmse:.4f}",
                    f"- CUSUM Detected: {'Yes' if report.cusum_detected else 'No'}",
                ])
                
                if report.cusum_changepoint is not None:
                    lines.append(f"- Changepoint: Observation {report.cusum_changepoint}")
                
                lines.extend([
                    f"",
                    f"**Recommendations:**",
                ])
                
                for rec in report.recommendations:
                    lines.append(f"- {rec}")
                
                lines.append("")
        
        lines.extend([
            f"## Summary",
            f"",
            f"Calibration completed successfully. Updated model parameters have been",
            f"fitted using Maximum Likelihood Estimation on historical data.",
            f"",
        ])
        
        with open(md_path, 'w') as f:
            f.write('\n'.join(lines))


class Calibrator:
    """
    Main calibration orchestrator.
    
    Coordinates the full calibration pipeline:
    1. Load CSV data
    2. Fit distributions to observed data
    3. Update model parameters
    4. Detect drift (if predictions provided)
    5. Generate reports
    """

    def __init__(self, config: CalibrationConfig):
        """
        Initialize calibrator.
        
        Args:
            config: CalibrationConfig object
        """
        self.config = config
        self.csv_connector = CSVConnector()
        self.param_estimator = ParameterEstimator()
        self.drift_detector = DriftDetector(
            **(config.drift_config or {})
        )

    def load_model(self, model_path: Path) -> Dict[str, Any]:
        """Load PEL-IR model."""
        with open(model_path, 'r') as f:
            return json.load(f)

    def save_model(self, model: Dict[str, Any], output_path: Path) -> None:
        """Save updated PEL-IR model."""
        with open(output_path, 'w') as f:
            json.dump(model, f, indent=2)

    def calibrate(self) -> CalibrationResult:
        """
        Execute full calibration pipeline.
        
        Returns:
            CalibrationResult with fitted parameters and reports
        """
        # Load model
        model = self.load_model(Path(self.config.model_path))
        model_name = model.get('model', {}).get('name', 'Unknown')
        
        # Load and prepare CSV data
        df = self.csv_connector.load_and_prepare(
            Path(self.config.csv_path),
            config=self.config.csv_config,
        )
        
        # Fit parameters
        fitted_params = {}
        drift_reports = {}
        
        if not self.config.parameters:
            self.config.parameters = {}
        
        for param_name, param_config in self.config.parameters.items():
            # Extract data column
            data_column = param_config.get('data_column', param_name)
            data = self.csv_connector.extract_column(df, data_column)
            
            # Fit distribution
            distribution = param_config.get('distribution', 'normal')
            
            if param_config.get('use_bootstrap', False):
                fit_result = self.param_estimator.fit_with_bootstrap(
                    data,
                    distribution,
                    n_bootstrap=param_config.get('bootstrap_samples', 1000),
                )
            else:
                fit_result = self.param_estimator.fit_distribution(data, distribution)
            
            fitted_params[param_name] = fit_result
            
            # Drift detection (if predictions provided)
            if 'predicted_column' in param_config:
                predicted_column = param_config['predicted_column']
                predicted = self.csv_connector.extract_column(df, predicted_column)
                
                # Ensure same length
                min_len = min(len(data), len(predicted))
                drift_report = self.drift_detector.detect_drift(
                    data[:min_len],
                    predicted[:min_len],
                )
                drift_reports[param_name] = drift_report
        
        # Update model with fitted parameters
        updated_model = self.update_model_parameters(model, fitted_params)
        
        # Create result
        result = CalibrationResult(
            model_name=model_name,
            timestamp=datetime.now().isoformat(),
            parameters=fitted_params,
            drift_reports=drift_reports,
            updated_model=updated_model,
            config=self.config,
        )
        
        # Save outputs
        if self.config.output_path:
            output_path = Path(self.config.output_path)
            
            # Save updated model
            model_path = output_path.parent / f"{output_path.stem}_calibrated.ir.json"
            self.save_model(updated_model, model_path)
            
            # Save JSON report
            json_path = output_path.parent / f"{output_path.stem}_report.json"
            result.to_json(json_path)
            
            # Save markdown report
            md_path = output_path.parent / f"{output_path.stem}_report.md"
            result.to_markdown(md_path)
        
        return result

    def update_model_parameters(
        self,
        model: Dict[str, Any],
        fitted_params: Dict[str, FitResult],
    ) -> Dict[str, Any]:
        """
        Update model with fitted parameters.
        
        Args:
            model: Original PEL-IR model
            fitted_params: Fitted distribution parameters
            
        Returns:
            Updated model dict
        """
        import copy
        updated_model = copy.deepcopy(model)
        
        # Update parameter nodes
        for node in updated_model.get('model', {}).get('nodes', []):
            if node.get('node_type') == 'param' and node.get('name') in fitted_params:
                param_name = node['name']
                fit = fitted_params[param_name]
                
                # Update the value expression with fitted distribution
                if fit.distribution == 'normal':
                    node['value'] = {
                        'expr_type': 'DistributionExpression',
                        'distribution': 'normal',
                        'params': {
                            'mean': fit.parameters['mean'],
                            'std': fit.parameters['std'],
                        }
                    }
                elif fit.distribution == 'lognormal':
                    node['value'] = {
                        'expr_type': 'DistributionExpression',
                        'distribution': 'lognormal',
                        'params': {
                            'mu': fit.parameters['mu'],
                            'sigma': fit.parameters['sigma'],
                        }
                    }
                elif fit.distribution == 'beta':
                    node['value'] = {
                        'expr_type': 'DistributionExpression',
                        'distribution': 'beta',
                        'params': {
                            'alpha': fit.parameters['alpha'],
                            'beta': fit.parameters['beta'],
                        }
                    }
                
                # Add calibration metadata
                node['provenance'] = {
                    'source': 'calibrated',
                    'method': 'mle',
                    'confidence': 1.0 - fit.ks_pvalue,  # Inverse of p-value
                    'calibration_timestamp': datetime.now().isoformat(),
                    'aic': fit.aic,
                    'bic': fit.bic,
                }
        
        return updated_model
