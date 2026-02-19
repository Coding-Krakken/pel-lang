# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Parameter Estimation for PEL Calibration.

Maximum Likelihood Estimation (MLE) for distributions:
- Normal
- LogNormal
- Beta

Includes goodness-of-fit tests and confidence intervals.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class FitResult:
    """
    Results from distribution fitting.

    Attributes:
        distribution: Distribution name (normal, lognormal, beta)
        parameters: Fitted parameters
        confidence_intervals: 95% confidence intervals for parameters
        log_likelihood: Log-likelihood of fit
        aic: Akaike Information Criterion
        bic: Bayesian Information Criterion
        ks_statistic: Kolmogorov-Smirnov test statistic
        ks_pvalue: Kolmogorov-Smirnov p-value
        chi2_statistic: Chi-squared test statistic (if applicable)
        chi2_pvalue: Chi-squared p-value (if applicable)
    """
    distribution: str
    parameters: dict[str, float]
    confidence_intervals: dict[str, tuple[float, float]]
    log_likelihood: float
    aic: float
    bic: float
    ks_statistic: float
    ks_pvalue: float
    chi2_statistic: float | None = None
    chi2_pvalue: float | None = None


class ParameterEstimator:
    """
    Maximum Likelihood Estimation for distribution parameters.

    Supports Normal, LogNormal, and Beta distributions with
    goodness-of-fit testing.
    """

    def fit_normal(self, data: np.ndarray) -> FitResult:
        """
        Fit Normal distribution to data.

        Args:
            data: Observed values

        Returns:
            FitResult with fitted parameters and diagnostics
        """
        # MLE estimates
        mean = np.mean(data)
        std = np.std(data, ddof=1)  # Sample std

        n = len(data)

        # Confidence intervals (95%)
        se_mean = std / np.sqrt(n)
        ci_mean = (
            mean - 1.96 * se_mean,
            mean + 1.96 * se_mean,
        )

        # Std confidence interval using chi-squared
        chi2_lower = stats.chi2.ppf(0.025, n - 1)
        chi2_upper = stats.chi2.ppf(0.975, n - 1)
        ci_std = (
            std * np.sqrt((n - 1) / chi2_upper),
            std * np.sqrt((n - 1) / chi2_lower),
        )

        # Log-likelihood
        log_likelihood = -n/2 * np.log(2 * np.pi) - n * np.log(std) - np.sum((data - mean)**2) / (2 * std**2)

        # AIC and BIC (2 parameters: mean, std)
        k = 2
        aic = 2 * k - 2 * log_likelihood
        bic = k * np.log(n) - 2 * log_likelihood

        # Kolmogorov-Smirnov test
        ks_stat, ks_pval = stats.kstest(data, lambda x: stats.norm.cdf(x, mean, std))

        return FitResult(
            distribution='normal',
            parameters={'mean': mean, 'std': std},
            confidence_intervals={'mean': ci_mean, 'std': ci_std},
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            ks_statistic=ks_stat,
            ks_pvalue=ks_pval,
        )

    def fit_lognormal(self, data: np.ndarray) -> FitResult:
        """
        Fit LogNormal distribution to data.

        Args:
            data: Observed values (must be positive)

        Returns:
            FitResult with fitted parameters and diagnostics
        """
        if np.any(data <= 0):
            raise ValueError("LogNormal distribution requires positive data")

        # Transform to log space
        log_data = np.log(data)

        # MLE estimates
        mu = np.mean(log_data)
        sigma = np.std(log_data, ddof=1)

        n = len(data)

        # Confidence intervals
        se_mu = sigma / np.sqrt(n)
        ci_mu = (
            mu - 1.96 * se_mu,
            mu + 1.96 * se_mu,
        )

        chi2_lower = stats.chi2.ppf(0.025, n - 1)
        chi2_upper = stats.chi2.ppf(0.975, n - 1)
        ci_sigma = (
            sigma * np.sqrt((n - 1) / chi2_upper),
            sigma * np.sqrt((n - 1) / chi2_lower),
        )

        # Log-likelihood
        log_likelihood = -n/2 * np.log(2 * np.pi) - n * np.log(sigma) - np.sum(log_data) - np.sum((log_data - mu)**2) / (2 * sigma**2)

        # AIC and BIC
        k = 2
        aic = 2 * k - 2 * log_likelihood
        bic = k * np.log(n) - 2 * log_likelihood

        # Kolmogorov-Smirnov test
        ks_stat, ks_pval = stats.kstest(data, lambda x: stats.lognorm.cdf(x, sigma, scale=np.exp(mu)))

        return FitResult(
            distribution='lognormal',
            parameters={'mu': mu, 'sigma': sigma},
            confidence_intervals={'mu': ci_mu, 'sigma': ci_sigma},
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            ks_statistic=ks_stat,
            ks_pvalue=ks_pval,
        )

    def fit_beta(self, data: np.ndarray) -> FitResult:
        """
        Fit Beta distribution to data.

        Args:
            data: Observed values (must be in [0, 1])

        Returns:
            FitResult with fitted parameters and diagnostics
        """
        if np.any(data < 0) or np.any(data > 1):
            raise ValueError("Beta distribution requires data in [0, 1]")

        # MLE using scipy
        alpha, beta, loc, scale = stats.beta.fit(data, floc=0, fscale=1)

        n = len(data)

        # Approximate confidence intervals using Fisher information
        # (simplified - full CI requires numerical Hessian)
        np.mean(data)
        np.var(data, ddof=1)

        # Method of moments for CI approximation
        se_alpha = alpha / np.sqrt(n)
        se_beta = beta / np.sqrt(n)

        ci_alpha = (max(0.01, alpha - 1.96 * se_alpha), alpha + 1.96 * se_alpha)
        ci_beta = (max(0.01, beta - 1.96 * se_beta), beta + 1.96 * se_beta)

        # Log-likelihood
        log_likelihood = np.sum(stats.beta.logpdf(data, alpha, beta))

        # AIC and BIC
        k = 2
        aic = 2 * k - 2 * log_likelihood
        bic = k * np.log(n) - 2 * log_likelihood

        # Kolmogorov-Smirnov test
        ks_stat, ks_pval = stats.kstest(data, lambda x: stats.beta.cdf(x, alpha, beta))

        return FitResult(
            distribution='beta',
            parameters={'alpha': alpha, 'beta': beta},
            confidence_intervals={'alpha': ci_alpha, 'beta': ci_beta},
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            ks_statistic=ks_stat,
            ks_pvalue=ks_pval,
        )

    def fit_distribution(
        self,
        data: np.ndarray,
        distribution: str,
    ) -> FitResult:
        """
        Fit specified distribution to data.

        Args:
            data: Observed values
            distribution: 'normal', 'lognormal', or 'beta'

        Returns:
            FitResult with fitted parameters and diagnostics
        """
        if distribution == 'normal':
            return self.fit_normal(data)
        elif distribution == 'lognormal':
            return self.fit_lognormal(data)
        elif distribution == 'beta':
            return self.fit_beta(data)
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")

    def compare_distributions(
        self,
        data: np.ndarray,
        distributions: list[str],
    ) -> dict[str, FitResult]:
        """
        Fit multiple distributions and compare using AIC/BIC.

        Args:
            data: Observed values
            distributions: List of distribution names to try

        Returns:
            Dict mapping distribution names to FitResults, sorted by AIC
        """
        results = {}

        for dist in distributions:
            try:
                results[dist] = self.fit_distribution(data, dist)
            except ValueError as e:
                # Skip distributions that can't fit the data
                print(f"Warning: Could not fit {dist}: {e}")
                continue

        # Sort by AIC (lower is better)
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1].aic))

        return sorted_results

    def fit_with_bootstrap(
        self,
        data: np.ndarray,
        distribution: str,
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95,
    ) -> FitResult:
        """
        Fit distribution with bootstrap confidence intervals.

        Args:
            data: Observed values
            distribution: Distribution name
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence level for intervals

        Returns:
            FitResult with bootstrap confidence intervals
        """
        # Original fit
        result = self.fit_distribution(data, distribution)

        # Bootstrap
        n = len(data)
        param_samples: dict[str, list[float]] = {key: [] for key in result.parameters.keys()}

        rng = np.random.RandomState(42)
        for _ in range(n_bootstrap):
            # Resample with replacement
            bootstrap_sample = rng.choice(data, size=n, replace=True)

            # Fit to bootstrap sample
            try:
                bootstrap_result = self.fit_distribution(bootstrap_sample, distribution)
                for key, value in bootstrap_result.parameters.items():
                    param_samples[key].append(value)
            except (ValueError, RuntimeError):
                continue

        # Compute percentile confidence intervals
        alpha = 1 - confidence_level
        ci: dict[str, tuple[float, float]] = {}
        for key, samples in param_samples.items():
            if samples:
                lower = float(np.percentile(samples, 100 * alpha / 2))
                upper = float(np.percentile(samples, 100 * (1 - alpha / 2)))
                ci[key] = (lower, upper)
            else:
                ci[key] = result.confidence_intervals[key]

        # Update confidence intervals
        result.confidence_intervals = ci

        return result
