# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
PEL Calibration Module - CSV data integration and parameter fitting.

This module enables PEL models to:
- Load data from CSV files
- Fit distribution parameters using MLE
- Detect drift between model predictions and observations
- Generate calibration reports

MVP v0.2.0 supports:
- CSV connector (local files)
- Normal, LogNormal, Beta distribution fitting
- Basic drift detection (MAPE, RMSE, CUSUM)
"""

from .calibrator import CalibrationConfig, CalibrationResult, Calibrator
from .csv_connector import CSVConnector
from .drift_detection import DriftDetector, DriftReport
from .parameter_estimation import FitResult, ParameterEstimator

__all__ = [
    "CalibrationConfig",
    "CalibrationResult",
    "Calibrator",
    "CSVConnector",
    "DriftDetector",
    "DriftReport",
    "FitResult",
    "ParameterEstimator",
]
