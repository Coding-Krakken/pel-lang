# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Drift Detection for PEL Calibration.

Compare model predictions vs actual observations to detect when models
drift from reality.

Implements:
- MAPE (Mean Absolute Percentage Error)
- RMSE (Root Mean Squared Error)
- CUSUM (Cumulative Sum Control Chart)
"""

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    """
    Drift detection results.

    Attributes:
        mape: Mean Absolute Percentage Error
        rmse: Root Mean Squared Error
        cusum_detected: Whether CUSUM detected drift
        cusum_changepoint: Index of detected changepoint (if any)
        cusum_statistic: CUSUM test statistic values
        drift_threshold_exceeded: Whether drift exceeds configured threshold
        recommendations: List of recommended actions
    """
    mape: float
    rmse: float
    cusum_detected: bool
    cusum_changepoint: int | None
    cusum_statistic: np.ndarray
    drift_threshold_exceeded: bool
    recommendations: list[str]


class DriftDetector:
    """
    Detect drift between model predictions and observations.

    Uses multiple metrics to assess model accuracy and detect
    structural changes.
    """

    def __init__(
        self,
        mape_threshold: float = 0.15,  # 15%
        rmse_threshold: float | None = None,
        cusum_threshold: float = 5.0,
        cusum_slack: float = 0.5,
    ):
        """
        Initialize drift detector.

        Args:
            mape_threshold: MAPE threshold for drift alert
            rmse_threshold: RMSE threshold (optional)
            cusum_threshold: CUSUM decision threshold
            cusum_slack: CUSUM slack parameter
        """
        self.mape_threshold = mape_threshold
        self.rmse_threshold = rmse_threshold
        self.cusum_threshold = cusum_threshold
        self.cusum_slack = cusum_slack

    def compute_mape(
        self,
        observed: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """
        Compute Mean Absolute Percentage Error.

        MAPE = mean(|observed - predicted| / |observed|)

        Args:
            observed: Actual observed values
            predicted: Model predictions

        Returns:
            MAPE value (0-1 scale, where 0.15 = 15% error)
        """
        # Avoid division by zero
        mask = observed != 0
        if not np.any(mask):
            return np.inf

        errors = np.abs((observed[mask] - predicted[mask]) / observed[mask])
        return np.mean(errors)

    def compute_rmse(
        self,
        observed: np.ndarray,
        predicted: np.ndarray,
    ) -> float:
        """
        Compute Root Mean Squared Error.

        RMSE = sqrt(mean((observed - predicted)^2))

        Args:
            observed: Actual observed values
            predicted: Model predictions

        Returns:
            RMSE value
        """
        return np.sqrt(np.mean((observed - predicted) ** 2))

    def cusum_test(
        self,
        observed: np.ndarray,
        predicted: np.ndarray,
        threshold: float | None = None,
        slack: float | None = None,
    ) -> tuple[bool, int | None, np.ndarray]:
        """
        CUSUM (Cumulative Sum) test for changepoint detection.

        Detects when cumulative errors exceed threshold, indicating
        a persistent shift in model accuracy.

        Args:
            observed: Actual observed values
            predicted: Model predictions
            threshold: Decision threshold (default: self.cusum_threshold)
            slack: Slack parameter (default: self.cusum_slack)

        Returns:
            Tuple of (detected, changepoint_index, cusum_values)
        """
        threshold = threshold or self.cusum_threshold
        slack = slack or self.cusum_slack

        # Compute residuals
        residuals = observed - predicted

        # Standardize residuals
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)

        if std_residual == 0:
            return False, None, np.zeros_like(residuals)

        standardized = (residuals - mean_residual) / std_residual

        # CUSUM statistic (two-sided)
        cusum_pos = np.zeros(len(standardized))
        cusum_neg = np.zeros(len(standardized))

        for i in range(1, len(standardized)):
            cusum_pos[i] = max(0, cusum_pos[i-1] + standardized[i] - slack)
            cusum_neg[i] = max(0, cusum_neg[i-1] - standardized[i] - slack)

        # Check for threshold exceedance
        cusum_max = np.maximum(cusum_pos, cusum_neg)
        detected = np.any(cusum_max > threshold)

        changepoint = None
        if detected:
            changepoint = int(np.argmax(cusum_max > threshold))

        return bool(detected), changepoint, cusum_max

    def detect_drift(
        self,
        observed: np.ndarray,
        predicted: np.ndarray,
    ) -> DriftReport:
        """
        Full drift detection analysis.

        Args:
            observed: Actual observed values
            predicted: Model predictions

        Returns:
            DriftReport with all metrics and recommendations
        """
        # Validate inputs
        if len(observed) != len(predicted):
            raise ValueError("Observed and predicted arrays must have same length")

        if len(observed) == 0:
            raise ValueError("Cannot detect drift with empty arrays")

        # Compute metrics
        mape = self.compute_mape(observed, predicted)
        rmse = self.compute_rmse(observed, predicted)

        # CUSUM test
        cusum_detected, changepoint, cusum_stat = self.cusum_test(observed, predicted)

        # Check thresholds
        drift_exceeded = mape > self.mape_threshold
        if self.rmse_threshold is not None:
            drift_exceeded = drift_exceeded or (rmse > self.rmse_threshold)

        # Generate recommendations
        recommendations = []

        if drift_exceeded:
            recommendations.append(
                f"Model drift detected: MAPE={mape:.1%} exceeds threshold {self.mape_threshold:.1%}"
            )

        if cusum_detected:
            recommendations.append(
                f"CUSUM test detected changepoint at observation {changepoint}"
            )
            recommendations.append(
                "Consider recalibrating model with recent data only"
            )

        if mape > 0.25:  # 25%
            recommendations.append(
                "High prediction error - model may need structural changes"
            )
        elif mape > self.mape_threshold:
            recommendations.append(
                "Moderate prediction error - recalibration recommended"
            )

        if not recommendations:
            recommendations.append("Model predictions are accurate - no action needed")

        return DriftReport(
            mape=mape,
            rmse=rmse,
            cusum_detected=cusum_detected,
            cusum_changepoint=changepoint,
            cusum_statistic=cusum_stat,
            drift_threshold_exceeded=drift_exceeded,
            recommendations=recommendations,
        )

    def rolling_drift_analysis(
        self,
        observed: np.ndarray,
        predicted: np.ndarray,
        window_size: int = 30,
    ) -> list[DriftReport]:
        """
        Perform rolling window drift analysis.

        Args:
            observed: Actual observed values
            predicted: Model predictions
            window_size: Size of rolling window

        Returns:
            List of DriftReports for each window
        """
        if len(observed) < window_size:
            raise ValueError(f"Data length {len(observed)} < window size {window_size}")

        reports = []

        for i in range(len(observed) - window_size + 1):
            window_obs = observed[i:i+window_size]
            window_pred = predicted[i:i+window_size]

            report = self.detect_drift(window_obs, window_pred)
            reports.append(report)

        return reports

    def format_report(self, report: DriftReport) -> str:
        """
        Format drift report as readable text.

        Args:
            report: DriftReport to format

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "DRIFT DETECTION REPORT",
            "=" * 60,
            "",
            "Accuracy Metrics:",
            f"  MAPE: {report.mape:.2%}",
            f"  RMSE: {report.rmse:.4f}",
            "",
            "Drift Detection:",
            f"  CUSUM Test: {'DETECTED' if report.cusum_detected else 'NOT DETECTED'}",
        ]

        if report.cusum_changepoint is not None:
            lines.append(f"  Changepoint: Observation {report.cusum_changepoint}")

        lines.extend([
            f"  Threshold Exceeded: {'YES' if report.drift_threshold_exceeded else 'NO'}",
            "",
            "Recommendations:",
        ])

        for rec in report.recommendations:
            lines.append(f"  - {rec}")

        lines.append("=" * 60)

        return "\n".join(lines)
