# PEL Calibration Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Canonical URL:** https://spec.pel-lang.org/v0.1/calibration

---

## 1. Introduction

**Calibration** is the process of fitting PEL model parameters to observed data, enabling models to reflect reality rather than speculation.

**Calibration loop:**
1. Run model with initial parameters → predictions
2. Compare predictions to actual data → residuals
3. Adjust parameters to minimize residuals
4. Detect drift (model degrades over time)
5. Trigger re-calibration when drift detected

---

## 2. Data Connectors

### 2.1 Data Source Interface

**Abstract interface for ingesting data:**

```python
class DataSource:
    def load(self, query: str) -> pd.DataFrame:
        """Load data matching query."""
        raise NotImplementedError
    
    def schema(self) -> dict:
        """Return schema (column names + types)."""
        raise NotImplementedError
```

**Implementations:**
- `CSVDataSource`: Load from CSV files
- `SQLDataSource`: Query SQL databases (Postgres, MySQL, Snowflake)
- `DataWarehouseSource`: BigQuery, Redshift, Databricks
- `APIDataSource`: REST/GraphQL APIs (Stripe, Salesforce, etc.)

### 2.2 Example Usage

```python
from pel.calibration import CSVDataSource, calibrate

# Load historical data
datasource = CSVDataSource("data/actual_revenue.csv")
actual_data = datasource.load("SELECT month, revenue FROM cohorts WHERE cohort = '2025-01'")

# Load model
model = pel.load_model("model.pel")

# Calibrate specified parameters
calibration_result = calibrate(
    model=model,
    data=actual_data,
    target_variable="revenue",
    fit_params=["churnRate", "expansionRate"],
    method="mle"  # Maximum likelihood estimation
)

print(calibration_result.fitted_params)
# {'churnRate': 0.048, 'expansionRate': 0.12}
```

---

## 3. Parameter Estimation Methods

### 3.1 Maximum Likelihood Estimation (MLE)

**Objective:** Find parameters $\theta$ maximizing likelihood of observed data.

$$\hat{\theta}_{\text{MLE}} = \arg\max_\theta \mathcal{L}(\theta | D)$$

where $D = \{x_1, \ldots, x_n\}$ is observed data.

**For distributions:**
- **Normal:** $\mu = \frac{1}{n}\sum x_i$, $\sigma^2 = \frac{1}{n}\sum (x_i - \mu)^2$
- **LogNormal:** Fit to $\log(x_i) \sim N(\mu_{\log}, \sigma_{\log}^2)$
- **Beta:** Numerical optimization (scipy.optimize.minimize)

**Algorithm:**
1. Define likelihood function $\mathcal{L}(\theta | D)$
2. Optimize using L-BFGS-B or Nelder-Mead
3. Return $\hat{\theta}$ and standard errors

### 3.2 Bayesian Fitting

**Objective:** Compute posterior distribution $p(\theta | D)$.

$$p(\theta | D) \propto p(D | \theta) \cdot p(\theta)$$

**Process:**
1. Specify prior $p(\theta)$ (e.g., weakly informative)
2. Compute likelihood $p(D | \theta)$
3. Sample posterior using MCMC (PyMC3, Stan)
4. Return posterior mean/median as point estimate

**Example (PyMC3):**
```python
import pymc3 as pm

with pm.Model() as model:
    # Prior
    churn_rate = pm.Beta("churn_rate", alpha=2, beta=20)  # Prior belief: ~10%
    
    # Likelihood
    observed_churns = pm.Binomial("obs", n=cohort_size, p=churn_rate, observed=actual_churns)
    
    # Sample posterior
    trace = pm.sample(2000, tune=1000)
    
# Posterior mean
churn_rate_fitted = trace["churn_rate"].mean()
```

### 3.3 Method of Moments

**Objective:** Match sample moments to theoretical moments.

**Example (LogNormal):**
Given data $D = \{x_1, \ldots, x_n\}$:

1. Compute sample mean: $\bar{x} = \frac{1}{n}\sum x_i$
2. Compute sample variance: $s^2 = \frac{1}{n}\sum (x_i - \bar{x})^2$
3. Solve for LogNormal parameters:

$$\mu_{\log} = \log\left(\frac{\bar{x}^2}{\sqrt{s^2 + \bar{x}^2}}\right)$$

$$\sigma_{\log} = \sqrt{\log\left(1 + \frac{s^2}{\bar{x}^2}\right)}$$

---

## 4. Distribution Fitting Quality

### 4.1 Kolmogorov-Smirnov (K-S) Test

**Tests if data matches fitted distribution.**

**Test statistic:**
$$D_n = \sup_x |F_n(x) - F(x)|$$

where:
- $F_n(x)$ = empirical CDF
- $F(x)$ = theoretical CDF

**Decision rule:**
- If $D_n < D_{\text{critical}}$: Accept fit (fail to reject)
- If $D_n \geq D_{\text{critical}}$: Reject fit (poor match)

**P-value interpretation:**
- $p > 0.05$: Good fit
- $p \leq 0.05$: Distribution mismatch (try different family)

### 4.2 Anderson-Darling Test

**More sensitive to tail deviations than K-S.**

$$A^2 = -n - \sum_{i=1}^n \frac{2i-1}{n} \left[\log F(x_i) + \log(1 - F(x_{n+1-i}))\right]$$

**Recommended for financial data** (tail risk matters).

### 4.3 Quantile-Quantile (Q-Q) Plot

**Visual diagnostic:**
- Plot empirical quantiles vs theoretical quantiles
- If points lie on diagonal → good fit
- Deviations indicate mismatch

**Generate in PEL:**
```bash
pel calibrate model.pel --data actual.csv --qq-plot churnRate
# Outputs qq_plot_churnRate.png
```

---

## 5. Model-Data Reconciliation

### 5.1 Residual Analysis

**Residuals:** Difference between model prediction and actual observation.

$$r_t = y_t^{\text{actual}} - y_t^{\text{model}}$$

**Diagnostics:**
1. **Mean residual:** Should be ≈0 (unbiased)
2. **Residual std dev:** Should be small (accurate)
3. **Autocorrelation:** Should be low (no systematic error)

### 5.2 MAPE (Mean Absolute Percentage Error)

$$\text{MAPE} = \frac{100\%}{n} \sum_{t=1}^n \left|\frac{y_t^{\text{actual}} - y_t^{\text{model}}}{y_t^{\text{actual}}}\right|$$

**Interpretation:**
- < 10%: Excellent fit
- 10-20%: Good fit
- 20-50%: Reasonable fit
- > 50%: Poor fit (re-examine model structure)

### 5.3 Calibration Commands

```bash
# Fit parameters to data
pel calibrate model.pel --data revenue.csv --target revenue --fit churnRate,arpu

# Output:
Fitted Parameters:
  churnRate: 0.048 (±0.003) [confidence: 0.85]
  arpu: $127.50 (±$8.20) [confidence: 0.78]
  
Goodness of Fit:
  MAPE: 12.3%
  R²: 0.87
  K-S test: p=0.23 (accept fit)
  
Residual Analysis:
  Mean residual: $1,240 (0.5% of mean)
  Max residual: $45,000 (month 18)
```

---

## 6. Drift Detection

### 6.1 Concept Drift

**Model degrades over time** as real-world changes (market shifts, product changes, competition, seasonality).

**Detection strategy:** Monitor prediction error over rolling window.

### 6.2 Sequential K-S Test

**Compare recent data distribution to historical:**

1. Historical data: $D_{\text{hist}} = \{x_1, \ldots, x_m\}$
2. Recent data: $D_{\text{recent}} = \{x_{m+1}, \ldots, x_n\}$
3. Compute K-S statistic between empirical CDFs
4. If $p < 0.05$: Distribution has shifted → drift detected

**Example:**
```python
from scipy.stats import ks_2samp

historical_churn = [0.045, 0.047, 0.043, ...]  # Months 1-12
recent_churn = [0.062, 0.058, 0.065, ...]      # Months 13-15

ks_stat, p_value = ks_2samp(historical_churn, recent_churn)

if p_value < 0.05:
    print(f"Drift detected! Churn distribution shifted (p={p_value:.4f})")
    print("Recommendation: Re-calibrate model with recent data")
```

### 6.3 CUSUM (Cumulative Sum Control Chart)

**Detect shifts in mean:**

$$S_t = \max(0, S_{t-1} + (x_t - \mu_0 - k))$$

where:
- $\mu_0$ = historical mean
- $k$ = allowable deviation (slack)
- Alarm threshold: $S_t > h$

**When $S_t$ exceeds threshold:** Mean has shifted upward.

### 6.4 Automated Drift Monitoring

```bash
# Monitor model accuracy over time
pel monitor model.pel --data live_data.csv --target revenue --window 30d

# Output:
Drift Detection Report (2026-02-13):
  ✓ churnRate: No drift (p=0.42)
  ✗ conversionRate: Drift detected (p=0.003)
    Historical mean: 0.032
    Recent mean: 0.041 (+28%)
    Recommendation: Re-fit conversionRate
  
  ✓ arpu: No drift (p=0.18)
```

---

## 7. Sensitivity-Driven Measurement Prioritization

### 7.1 Problem

**Not all parameters are equally important.** Some have large impact on outputs (high sensitivity), others negligible.

**Question:** Which parameters should we measure first?

### 7.2 Sensitivity Analysis

**Tornado chart:** One-at-a-time sensitivity (see runtime spec).

**Sobol indices:** Variance decomposition (see runtime spec).

### 7.3 Measurement Prioritization Algorithm

**Rank parameters by:**
1. **Sensitivity:** Higher Sobol index → higher priority
2. **Confidence:** Lower confidence → higher priority
3. **Freshness:** Older data → higher priority

**Score function:**
$$\text{Priority}(p) = w_1 \cdot \text{Sobol}_p + w_2 \cdot (1 - \text{Confidence}_p) + w_3 \cdot \text{Age}_p$$

Default weights: $w_1 = 0.5$, $w_2 = 0.3$, $w_3 = 0.2$

**Example output:**
```bash
pel prioritize model.pel --target ltv

# Measurement Priority Report:
1. churnRate (score: 0.87)
   Sobol index: 0.62 (high impact on LTV)
   Confidence: 0.45 (low confidence)
   Freshness: 8 months old
   → Recommendation: Survey customers, analyze cohort data

2. expansionRate (score: 0.71)
   Sobol index: 0.45
   Confidence: 0.55
   Freshness: 5 months old
   → Recommendation: Track expansion conversions

3. cac (score: 0.34)
   Sobol index: 0.15 (low impact on LTV)
   Confidence: 0.85 (high confidence)
   Freshness: 1 month old
   → Recommendation: No action needed (already well-measured)
```

---

## 8. Calibration Workflow Summary

**End-to-end process:**

```bash
# 1. Initial model (expert estimates)
cat > model.pel <<EOF
param churnRate: Rate per Month = 0.05/1mo {
  source: "expert_estimate",
  method: "assumption",
  confidence: 0.40
}
EOF

# 2. Collect data
# (Export from analytics DB, CRM, etc.)

# 3. Calibrate
pel calibrate model.pel --data cohorts.csv --target active_users --fit churnRate

# 4. Model updated with fitted value
cat model.pel  # Now: churnRate = 0.048/1mo, confidence: 0.85

# 5. Monitor for drift
pel monitor model.pel --data live_data.csv --alert-if-drift

# 6. Re-calibrate when drift detected
# (Repeat step 3)
```

---

## 9. Calibration Metadata

### 9.1 Embedding Fit Results in Provenance

**After calibration, update provenance block:**

```pel
param churnRate: Rate per Month = 0.048/1mo {
  source: "cohort_analysis_2025Q4",
  method: "fitted",
  confidence: 0.85,
  freshness: "P1M",
  fit_details: {
    data_points: 12,
    fit_method: "mle",
    standard_error: 0.003,
    ks_test_p: 0.23,
    fitted_at: "2026-02-13"
  }
}
```

### 9.2 Calibration Artifact

**Store calibration history:**

```json
{
  "calibration_id": "cal-2026-02-13-001",
  "model_hash": "sha256:...",
  "parameters_fitted": ["churnRate", "expansionRate"],
  "data_source": "cohorts.csv",
  "data_range": "2025-01-01 to 2025-12-31",
  "method": "mle",
  "results": {
    "churnRate": {
      "before": 0.05,
      "after": 0.048,
      "standard_error": 0.003,
      "confidence": 0.85
    }
  },
  "goodness_of_fit": {
    "mape": 0.123,
    "r_squared": 0.87,
    "ks_test_p": 0.23
  }
}
```

---

## 10. Limitations and Non-Goals

### 10.1 Not Automated Machine Learning

**PEL calibration is NOT:**
- Hyperparameter tuning
- Feature engineering
- Model architecture search

**PEL assumes model structure is correct** (mechanistic, not black-box).

### 10.2 Structural Misspecification

**If model structure is wrong, calibration won't save you.**

**Example:**
- True process: $\text{churn}_t = f(\text{feature usage}_t, \text{support tickets}_t)$
- Model: $\text{churn}_t = \text{constant}$

No amount of fitting will make constant model accurate.

**Solution:** Rethink model structure (add variables, change equations).

---

## Appendix A: Supported Fit Methods

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **MLE** | Large samples, well-behaved distributions | Simple, fast, optimal (asymptotically) | Requires optimization, can fail with poor init |
| **Bayesian** | Small samples, prior knowledge available | Incorporates uncertainty, robust | Slower (MCMC), requires prior specification |
| **Method of Moments** | Quick estimates, simple distributions | Closed-form, no optimization | Less efficient than MLE, sensitive to outliers |
| **Least Squares** | Regression-style params (y = f(x, θ)) | Standard, well-understood | Assumes normal errors |

---

## Appendix B: Drift Detection Algorithms

| Algorithm | Detects | Speed | Sensitivity |
|-----------|---------|-------|-------------|
| **K-S Test** | Distribution shift | Fast | Moderate |
| **Anderson-Darling** | Distribution shift (tail-sensitive) | Fast | High (tails) |
| **CUSUM** | Mean shift | Very fast | High (mean) |
| **EWMA** | Gradual drift | Fast | Moderate |
| **Sequential Test** | Online drift | Real-time | High |

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)
