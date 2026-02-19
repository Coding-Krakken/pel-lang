# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Tests for Drift Detection.
"""

import numpy as np
import pytest

try:
    from runtime.calibration.drift_detection import DriftDetector, DriftReport
except ImportError:
    pytest.skip("calibration module not installed", allow_module_level=True)


class TestDriftDetector:
    """Test drift detection functionality."""

    @pytest.fixture
    def detector(self):
        """Create drift detector instance."""
        return DriftDetector(
            mape_threshold=0.15,
            cusum_threshold=5.0,
            cusum_slack=0.5,
        )

    def test_compute_mape_perfect(self, detector):
        """Test MAPE with perfect predictions."""
        observed = np.array([100, 200, 300, 400])
        predicted = np.array([100, 200, 300, 400])
        
        mape = detector.compute_mape(observed, predicted)
        
        assert mape == 0.0

    def test_compute_mape_nonzero(self, detector):
        """Test MAPE with some error."""
        observed = np.array([100, 200, 300, 400])
        predicted = np.array([110, 190, 330, 380])
        
        mape = detector.compute_mape(observed, predicted)
        
        # MAPE = mean(|100-110|/100, |200-190|/200, etc.)
        # = mean(0.10, 0.05, 0.10, 0.05) = 0.075
        assert np.isclose(mape, 0.075)

    def test_compute_mape_with_zeros(self, detector):
        """Test MAPE with zero values in observed."""
        observed = np.array([0, 100, 200])
        predicted = np.array([10, 110, 190])
        
        mape = detector.compute_mape(observed, predicted)
        
        # Should skip zero values
        # MAPE = mean(|100-110|/100, |200-190|/200) = mean(0.10, 0.05) = 0.075
        assert np.isclose(mape, 0.075)

    def test_compute_mape_all_zeros(self, detector):
        """Test MAPE with all zeros in observed."""
        observed = np.array([0, 0, 0])
        predicted = np.array([10, 20, 30])
        
        mape = detector.compute_mape(observed, predicted)
        
        # Should return infinity
        assert mape == np.inf

    def test_compute_rmse_perfect(self, detector):
        """Test RMSE with perfect predictions."""
        observed = np.array([100, 200, 300])
        predicted = np.array([100, 200, 300])
        
        rmse = detector.compute_rmse(observed, predicted)
        
        assert rmse == 0.0

    def test_compute_rmse_nonzero(self, detector):
        """Test RMSE with some error."""
        observed = np.array([100, 200, 300])
        predicted = np.array([110, 190, 310])
        
        rmse = detector.compute_rmse(observed, predicted)
        
        # RMSE = sqrt(mean((10)^2, (-10)^2, (10)^2)) = sqrt(100) = 10
        assert np.isclose(rmse, 10.0)

    def test_cusum_no_drift(self, detector):
        """Test CUSUM with no drift."""
        # Predictions match observations (with small noise)
        np.random.seed(42)
        observed = np.random.normal(100, 5, 50)
        predicted = observed + np.random.normal(0, 1, 50)
        
        detected, changepoint, cusum = detector.cusum_test(observed, predicted)
        
        assert detected == False
        assert changepoint is None

    def test_cusum_with_drift(self, detector):
        """Test CUSUM with clear drift."""
        # First half: good predictions
        # Second half: systematic bias
        observed = np.concatenate([
            np.full(25, 100),
            np.full(25, 150),  # Jump at point 25
        ])
        predicted = np.full(50, 100)  # Constant prediction
        
        detected, changepoint, cusum = detector.cusum_test(observed, predicted)
        
        assert detected == True
        assert changepoint is not None
        # CUSUM may detect a bit before the actual jump, so check it's within range
        assert 10 <= changepoint <= 35  # Should detect somewhere around the jump

    def test_cusum_constant_residuals(self, detector):
        """Test CUSUM with constant residuals (zero variance)."""
        observed = np.array([100, 100, 100, 100])
        predicted = np.array([100, 100, 100, 100])
        
        detected, changepoint, cusum = detector.cusum_test(observed, predicted)
        
        # Should not detect drift with zero variance
        assert detected == False

    def test_detect_drift_no_drift(self, detector):
        """Test full drift detection with no drift."""
        observed = np.array([100, 105, 102, 98, 101])
        predicted = np.array([100, 103, 101, 99, 102])
        
        report = detector.detect_drift(observed, predicted)
        
        assert report.mape < 0.15  # Below threshold
        assert report.drift_threshold_exceeded == False
        assert "accurate" in report.recommendations[0].lower()

    def test_detect_drift_with_drift(self, detector):
        """Test full drift detection with significant drift."""
        # Create data with significant systematic error (>15% MAPE)
        observed = np.array([100, 100, 100, 100, 100])
        predicted = np.array([70, 75, 80, 85, 90])  # Consistently 20-30% off
        
        report = detector.detect_drift(observed, predicted)
        
        assert report.mape > 0.15  # Should exceed 15% threshold
        assert report.drift_threshold_exceeded == True
        assert len(report.recommendations) > 0

    def test_detect_drift_mismatched_length(self, detector):
        """Test drift detection with mismatched array lengths."""
        observed = np.array([100, 200, 300])
        predicted = np.array([100, 200])
        
        with pytest.raises(ValueError, match="same length"):
            detector.detect_drift(observed, predicted)

    def test_detect_drift_empty_arrays(self, detector):
        """Test drift detection with empty arrays."""
        observed = np.array([])
        predicted = np.array([])
        
        with pytest.raises(ValueError, match="empty"):
            detector.detect_drift(observed, predicted)

    def test_rolling_drift_analysis(self, detector):
        """Test rolling window drift analysis."""
        # Create data with drift starting at point 30
        observed = np.concatenate([
            np.random.normal(100, 5, 30),
            np.random.normal(150, 5, 30),  # Shift up
        ])
        predicted = np.full(60, 100)
        
        reports = detector.rolling_drift_analysis(observed, predicted, window_size=20)
        
        assert len(reports) > 0
        # Later windows should detect drift
        last_report = reports[-1]
        assert last_report.drift_threshold_exceeded == True

    def test_rolling_drift_window_too_large(self, detector):
        """Test rolling drift with window larger than data."""
        observed = np.array([100, 200, 300])
        predicted = np.array([100, 190, 310])
        
        with pytest.raises(ValueError, match="window size"):
            detector.rolling_drift_analysis(observed, predicted, window_size=10)

    def test_format_report(self, detector):
        """Test drift report formatting."""
        observed = np.array([100, 105, 102])
        predicted = np.array([100, 103, 101])
        
        report = detector.detect_drift(observed, predicted)
        formatted = detector.format_report(report)
        
        assert "DRIFT DETECTION REPORT" in formatted
        assert "MAPE" in formatted
        assert "RMSE" in formatted
        assert "CUSUM" in formatted
        assert "Recommendations" in formatted

    def test_drift_report_dataclass(self):
        """Test DriftReport dataclass structure."""
        report = DriftReport(
            mape=0.12,
            rmse=5.0,
            cusum_detected=False,
            cusum_changepoint=None,
            cusum_statistic=np.array([0, 0.1, 0.2]),
            drift_threshold_exceeded=False,
            recommendations=["Model is accurate"],
        )
        
        assert report.mape == 0.12
        assert report.cusum_detected == False
        assert len(report.recommendations) == 1

    def test_high_mape_recommendation(self, detector):
        """Test that high MAPE generates appropriate recommendation."""
        observed = np.array([100, 200, 300, 400])
        predicted = np.array([50, 100, 150, 200])  # 50% error
        
        report = detector.detect_drift(observed, predicted)
        
        assert report.mape > 0.25
        # Should recommend structural changes for very high error
        assert any("structural" in rec.lower() for rec in report.recommendations)

    def test_moderate_mape_recommendation(self, detector):
        """Test moderate MAPE recommendation."""
        # Create data with moderate error (15-25% MAPE)
        observed = np.array([100, 100, 100, 100])
        predicted = np.array([80, 85, 80, 85])  # ~18% error
        
        report = detector.detect_drift(observed, predicted)
        
        assert 0.15 < report.mape < 0.25
        # Should recommend recalibration
        assert any("recalibration" in rec.lower() for rec in report.recommendations)

    def test_cusum_recommendation(self, detector):
        """Test CUSUM changepoint recommendation."""
        # Create clear changepoint
        observed = np.concatenate([
            np.full(20, 100),
            np.full(20, 150),
        ])
        predicted = np.full(40, 100)
        
        report = detector.detect_drift(observed, predicted)
        
        assert report.cusum_detected == True
        # Should recommend recent data only
        assert any("recent data" in rec.lower() for rec in report.recommendations)

    def test_rmse_threshold(self):
        """Test drift detection with RMSE threshold."""
        detector = DriftDetector(
            mape_threshold=1.0,  # Very high, won't trigger
            rmse_threshold=5.0,  # RMSE threshold
        )
        
        observed = np.array([100, 200, 300])
        predicted = np.array([110, 210, 310])  # RMSE = 10
        
        report = detector.detect_drift(observed, predicted)
        
        # Should exceed RMSE threshold
        assert report.rmse > 5.0
        assert report.drift_threshold_exceeded == True

    def test_cusum_custom_threshold(self):
        """Test CUSUM with custom threshold."""
        detector = DriftDetector(cusum_threshold=2.0)  # Lower threshold
        
        observed = np.concatenate([
            np.full(10, 100),
            np.full(10, 120),  # Moderate shift
        ])
        predicted = np.full(20, 100)
        
        detected, changepoint, cusum = detector.cusum_test(observed, predicted)
        
        # Lower threshold should detect moderate shifts
        assert detected == True

    def test_cusum_slack_parameter(self):
        """Test CUSUM with different slack parameters."""
        # Larger slack is less sensitive
        detector_tight = DriftDetector(cusum_slack=0.1)
        detector_loose = DriftDetector(cusum_slack=1.0)
        
        observed = np.concatenate([
            np.full(15, 100),
            np.full(15, 115),
        ])
        predicted = np.full(30, 100)
        
        detected_tight, _, _ = detector_tight.cusum_test(observed, predicted)
        detected_loose, _, _ = detector_loose.cusum_test(observed, predicted)
        
        # Tight slack should be more sensitive
        # (though both might detect this obvious shift)
        assert detected_tight == True

    def test_cusum_statistic_values(self, detector):
        """Test that CUSUM statistic is computed correctly."""
        observed = np.concatenate([
            np.full(10, 100),
            np.full(10, 150),
        ])
        predicted = np.full(20, 100)
        
        detected, changepoint, cusum_stat = detector.cusum_test(observed, predicted)
        
        # CUSUM should increase after changepoint
        assert len(cusum_stat) == 20
        assert np.max(cusum_stat) > 0
        # Maximum should be after the changepoint
        assert np.argmax(cusum_stat) >= 10

    def test_zero_variance_data(self, detector):
        """Test with zero variance (all same values)."""
        observed = np.full(20, 100.0)
        predicted = np.full(20, 100.0)
        
        report = detector.detect_drift(observed, predicted)
        
        assert report.mape == 0.0
        assert report.rmse == 0.0
        assert report.cusum_detected == False
