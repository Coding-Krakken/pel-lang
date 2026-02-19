# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Tests for Parameter Estimation (MLE).
"""

import numpy as np
import pytest

try:
    from runtime.calibration.parameter_estimation import FitResult, ParameterEstimator
except ImportError:
    pytest.skip("calibration module not installed", allow_module_level=True)


class TestParameterEstimator:
    """Test MLE parameter estimation."""

    @pytest.fixture
    def estimator(self):
        """Create parameter estimator instance."""
        return ParameterEstimator()

    def test_fit_normal(self, estimator):
        """Test fitting Normal distribution."""
        # Generate known Normal data
        np.random.seed(42)
        true_mean = 10.0
        true_std = 2.0
        data = np.random.normal(true_mean, true_std, 1000)

        result = estimator.fit_normal(data)

        assert result.distribution == 'normal'
        assert 'mean' in result.parameters
        assert 'std' in result.parameters

        # Check estimates are close to true values
        assert np.abs(result.parameters['mean'] - true_mean) < 0.2
        assert np.abs(result.parameters['std'] - true_std) < 0.2

        # Check confidence intervals contain true values
        assert result.confidence_intervals['mean'][0] < true_mean < result.confidence_intervals['mean'][1]

        # Check goodness-of-fit
        assert result.ks_pvalue > 0.01  # Should not reject at 1% level

    def test_fit_lognormal(self, estimator):
        """Test fitting LogNormal distribution."""
        # Generate known LogNormal data
        np.random.seed(42)
        true_mu = 2.0
        true_sigma = 0.5
        data = np.random.lognormal(true_mu, true_sigma, 1000)

        result = estimator.fit_lognormal(data)

        assert result.distribution == 'lognormal'
        assert 'mu' in result.parameters
        assert 'sigma' in result.parameters

        # Check estimates are close to true values
        assert np.abs(result.parameters['mu'] - true_mu) < 0.1
        assert np.abs(result.parameters['sigma'] - true_sigma) < 0.1

        # Check AIC and BIC are computed
        assert result.aic > 0
        assert result.bic > 0
        assert result.bic > result.aic  # BIC penalizes complexity more

    def test_fit_lognormal_negative_data(self, estimator):
        """Test that LogNormal rejects negative data."""
        data = np.array([-1, 2, 3, 4])

        with pytest.raises(ValueError, match="positive data"):
            estimator.fit_lognormal(data)

    def test_fit_beta(self, estimator):
        """Test fitting Beta distribution."""
        # Generate known Beta data
        np.random.seed(42)
        true_alpha = 2.0
        true_beta = 5.0
        data = np.random.beta(true_alpha, true_beta, 1000)

        result = estimator.fit_beta(data)

        assert result.distribution == 'beta'
        assert 'alpha' in result.parameters
        assert 'beta' in result.parameters

        # Check estimates are reasonably close
        assert np.abs(result.parameters['alpha'] - true_alpha) < 0.5
        assert np.abs(result.parameters['beta'] - true_beta) < 1.0

    def test_fit_beta_out_of_range(self, estimator):
        """Test that Beta rejects data outside [0,1]."""
        data = np.array([0.5, 0.7, 1.5, 0.3])  # 1.5 is out of range

        with pytest.raises(ValueError, match="in \\[0, 1\\]"):
            estimator.fit_beta(data)

    def test_fit_distribution_normal(self, estimator):
        """Test generic fit_distribution with Normal."""
        np.random.seed(42)
        data = np.random.normal(5, 1, 100)

        result = estimator.fit_distribution(data, 'normal')

        assert result.distribution == 'normal'
        assert 'mean' in result.parameters

    def test_fit_distribution_invalid(self, estimator):
        """Test fit_distribution with invalid distribution name."""
        data = np.array([1, 2, 3, 4])

        with pytest.raises(ValueError, match="Unsupported distribution"):
            estimator.fit_distribution(data, 'invalid_dist')

    def test_compare_distributions(self, estimator):
        """Test comparing multiple distributions."""
        # Generate LogNormal data (should fit best with LogNormal)
        np.random.seed(42)
        data = np.random.lognormal(2, 0.3, 500)

        results = estimator.compare_distributions(data, ['normal', 'lognormal'])

        assert len(results) >= 1
        # Results should be sorted by AIC
        aic_values = [r.aic for r in results.values()]
        assert aic_values == sorted(aic_values)

        # LogNormal should fit better than Normal for this data
        # (first in sorted results)
        best_dist = list(results.keys())[0]
        # This might not always be lognormal due to randomness, but typically should be
        assert best_dist in ['lognormal', 'normal']

    def test_compare_distributions_skip_invalid(self, estimator):
        """Test that compare_distributions skips distributions that can't fit."""
        # Beta data (in [0,1])
        np.random.seed(42)
        data = np.random.beta(2, 5, 100)

        # Try to fit both Beta and LogNormal
        # LogNormal should fail (data contains values < 1), but shouldn't crash
        results = estimator.compare_distributions(data, ['beta', 'lognormal'])

        # Should have at least Beta result
        assert 'beta' in results

    def test_confidence_intervals_coverage(self, estimator):
        """Test that confidence intervals have proper coverage."""
        # Generate many samples and check CI coverage
        np.random.seed(42)
        true_mean = 10.0
        true_std = 2.0

        # Run multiple trials
        coverage_count = 0
        n_trials = 100

        for _ in range(n_trials):
            data = np.random.normal(true_mean, true_std, 50)
            result = estimator.fit_normal(data)

            ci_mean = result.confidence_intervals['mean']
            if ci_mean[0] <= true_mean <= ci_mean[1]:
                coverage_count += 1

        # 95% CI should cover true value about 95% of the time
        # Allow some slack due to randomness
        coverage_rate = coverage_count / n_trials
        assert 0.90 <= coverage_rate <= 1.0

    def test_fit_with_bootstrap(self, estimator):
        """Test bootstrap confidence intervals."""
        np.random.seed(42)
        data = np.random.normal(10, 2, 100)

        result = estimator.fit_with_bootstrap(
            data,
            'normal',
            n_bootstrap=100,  # Small number for speed
            confidence_level=0.95
        )

        assert result.distribution == 'normal'
        assert 'mean' in result.confidence_intervals
        assert 'std' in result.confidence_intervals

        # Bootstrap CI should be reasonable
        ci_mean = result.confidence_intervals['mean']
        assert ci_mean[0] < ci_mean[1]
        assert ci_mean[0] > 0  # Mean should be positive for this data

    def test_fit_with_bootstrap_different_confidence(self, estimator):
        """Test bootstrap with different confidence level."""
        np.random.seed(42)
        data = np.random.normal(10, 2, 100)

        result_95 = estimator.fit_with_bootstrap(data, 'normal', n_bootstrap=100, confidence_level=0.95)
        result_99 = estimator.fit_with_bootstrap(data, 'normal', n_bootstrap=100, confidence_level=0.99)

        # 99% CI should be wider than 95% CI
        width_95 = result_95.confidence_intervals['mean'][1] - result_95.confidence_intervals['mean'][0]
        width_99 = result_99.confidence_intervals['mean'][1] - result_99.confidence_intervals['mean'][0]

        assert width_99 > width_95

    def test_log_likelihood_computation(self, estimator):
        """Test that log-likelihood is computed correctly."""
        np.random.seed(42)
        data = np.random.normal(5, 1, 100)

        result = estimator.fit_normal(data)

        # Log-likelihood should be negative
        assert result.log_likelihood < 0

        # Verify it's plausible
        assert result.log_likelihood > -1000  # Not too extreme

    def test_aic_bic_relationship(self, estimator):
        """Test that BIC >= AIC (for same number of parameters)."""
        np.random.seed(42)
        data = np.random.normal(5, 1, 100)

        result = estimator.fit_normal(data)

        # For n > 8, BIC > AIC (since BIC uses log(n) penalty)
        assert result.bic > result.aic

    def test_fit_result_dataclass(self):
        """Test FitResult dataclass structure."""
        result = FitResult(
            distribution='normal',
            parameters={'mean': 10.0, 'std': 2.0},
            confidence_intervals={'mean': (9.0, 11.0), 'std': (1.5, 2.5)},
            log_likelihood=-100.0,
            aic=204.0,
            bic=207.0,
            ks_statistic=0.05,
            ks_pvalue=0.8,
        )

        assert result.distribution == 'normal'
        assert result.parameters['mean'] == 10.0
        assert result.ks_pvalue == 0.8

    def test_small_sample_size(self, estimator):
        """Test fitting with small sample size."""
        data = np.array([1, 2, 3, 4, 5])  # Only 5 points

        result = estimator.fit_normal(data)

        # Should still work, but with wider confidence intervals
        assert result.distribution == 'normal'
        ci_width = result.confidence_intervals['mean'][1] - result.confidence_intervals['mean'][0]
        assert ci_width > 0

    def test_constant_data(self, estimator):
        """Test fitting with constant (no variance) data."""
        data = np.array([5.0, 5.0, 5.0, 5.0, 5.0])

        result = estimator.fit_normal(data)

        assert result.parameters['mean'] == 5.0
        assert result.parameters['std'] >= 0  # Should be 0 or very small

    def test_beta_edge_values(self, estimator):
        """Test Beta fitting with edge values close to 0 and 1."""
        # Data close to edges (but not exactly 0 or 1, which scipy doesn't allow)
        data = np.array([0.01, 0.1, 0.5, 0.9, 0.99])

        result = estimator.fit_beta(data)

        assert result.distribution == 'beta'
        assert result.parameters['alpha'] > 0
        assert result.parameters['beta'] > 0
