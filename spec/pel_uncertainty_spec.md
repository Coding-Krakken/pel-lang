# PEL Uncertainty Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Authors:** PEL Core Team  
**Canonical URL:** https://spec.pel-lang.org/v0.1/uncertainty

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Distribution Types](#2-distribution-types)
3. [Correlation Semantics](#3-correlation-semantics)
4. [Sampling Methods](#4-sampling-methods)
5. [Mixture Distributions](#5-mixture-distributions)
6. [Fat-Tail Modeling](#6-fat-tail-modeling)
7. [Shock Scenarios](#7-shock-scenarios)
8. [Unknown Unknowns](#8-unknown-unknowns)
9. [Variance Propagation](#9-variance-propagation)
10. [Reproducibility Guarantees](#10-reproducibility-guarantees)

---

## 1. Introduction

### 1.1 Purpose

PEL makes **uncertainty first-class** in economic modeling. Unlike tools where uncertainty is bolted on (sensitivity tables, scenario dropdowns), PEL enforces explicit modeling of:

- Parameter uncertainty (distributions)
- Correlation structures (multivariate dependencies)
- Fat-tail events (kurtosis, extreme outcomes)
- Shock scenarios (discrete regime changes)
- Unknown unknowns (epistemic uncertainty envelopes)

### 1.2 Design Philosophy

**Principles:**

1. **Explicit over implicit:** Every uncertain parameter **MUST** declare its distribution
2 **Correlation required:** If parameters correlate, specify correlation coefficient
3. **No fake precision:** Single-point estimates **ARE** distributions (degenerate Dirac delta)
4. **Tail awareness:** Heavy-tail distributions supported natively
5. **Reproducible randomness:** Same seed → identical Monte Carlo results

---

## 2. Distribution Types

### 2.1 Beta Distribution

**Purpose:** Bounded uncertainty on [0, 1] (rates, probabilities, fractions)

**Syntax:**
```pel
~ Beta(α=2, β=8)
```

**Parameters:**
- α > 0 (shape parameter 1)
- β > 0 (shape parameter 2)

**Properties:**
- Support: [0, 1]
- Mean: α / (α + β)
- Mode: (α - 1) / (α + β - 2) if α, β > 1
- Variance: αβ / [(α + β)² (α + β + 1)]

**Use cases:**
- Conversion rates
- Churn rates
- Click-through rates
- Compliance probabilities

**Example:**
```pel
param conversionRate: Fraction ~ Beta(α=10, β=40) {
  source: "funnel_analysis_2025Q4",
  method: "fitted",
  confidence: 0.75
}
// Mean ≈ 0.20, concentrated around 20% with bounded support
```

### 2.2 Normal Distribution

**Purpose:** Unbounded symmetric uncertainty

**Syntax:**
```pel
~ Normal(μ=100, σ=15)
```

**Parameters:**
- μ ∈ ℝ (mean)
- σ > 0 (standard deviation)

**Properties:**
- Support: (-∞, +∞)
- Mean: μ
- Median: μ
- Variance: σ²

**Use cases:**
- Normally distributed errors
- Central-limit-theorem scenarios
- Additive noise

**Example:**
```pel
param growthRate: Rate per Month ~ Normal(μ=0.05/1mo, σ=0.02/1mo) {
  source: "historical_growth",
  method: "fitted",
  confidence: 0.60
}
```

**Warning:** Normal distributions allow negative values. For economic quantities that MUST be positive (prices, costs), use LogNormal instead.

### 2.3 LogNormal Distribution

**Purpose:** Positive-only uncertainty with right skew

**Syntax:**
```pel
~ LogNormal(μ=$500, σ=$150)
```

**Parameters:**
- μ > 0 (scale parameter, **not** the mean of the lognormal)
- σ > 0 (shape parameter)

**Properties:**
- Support: (0, +∞)
- Mean: exp(μ + σ²/2)
- Median: exp(μ)
- Variance: [exp(σ²) - 1] exp(2μ + σ²)

**Use cases:**
- Customer acquisition cost (CAC)
- Deal sizes
- Salaries
- Asset prices

**Example:**
```pel
param cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150) {
  source: "marketing_dashboard_2025",
  method: "fitted",
  confidence: 0.65,
  notes: "Right-skewed due to occasional high-cost channels"
}
```

### 2.4 Uniform Distribution

**Purpose:** Equal probability over bounded interval

**Syntax:**
```pel
~ Uniform(low=0.10, high=0.30)
```

**Parameters:**
- low < high (bounds)

**Properties:**
- Support: [low, high]
- Mean: (low + high) / 2
- Variance: (high - low)² / 12

**Use cases:**
- Maximum ignorance (no information beyond bounds)
- Sensitivity ranges

**Example:**
```pel
param priceElasticity: Fraction ~ Uniform(low=-2.0, high=-0.5) {
  source: "expert_estimate",
  method: "assumption",
  confidence: 0.40,
  notes: "Wide uncertainty; requires measurement"
}
```

### 2.5 Triangular Distribution

**Purpose:** Bounded with most likely value (mode)

**Syntax:**
```pel
~ Triangular(low=50, mode=100, high=200)
```

**Parameters:**
- low < mode < high

**Properties:**
- Support: [low, high]
- Mode: mode
- Mean: (low + mode + high) / 3

**Use cases:**
- Three-point estimates (pessimistic, likely, optimistic)
- PERT-style project estimation

**Example:**
```pel
param implementationTime: Duration ~ Triangular(low=30d, mode=60d, high=120d) {
  source: "engineering_estimate",
  method: "expert_estimate",
  confidence: 0.50
}
```

### 2.6 Pareto Distribution (Power Law)

**Purpose:** Heavy-tail phenomena ("80/20 rule")

**Syntax:**
```pel
~ Pareto(xₘ=10, α=1.5)
```

**Parameters:**
- xₘ > 0 (scale, minimum value)
- α > 0 (shape, tail heaviness; smaller α = heavier tail)

**Properties:**
- Support: [xₘ, +∞)
- Mean: α xₘ / (α - 1) if α > 1 (undefined if α ≤ 1)
- Tail: P(X > x) ~ x^(-α) as x → ∞

**Use cases:**
- Viral growth (user distribution)
- Deal size distribution
- Wealth distribution
- Platform effects

**Example:**
```pel
param viralCoefficient: Fraction ~ Pareto(xₘ=1.0, α=2.0) {
  source: "network_effects_model",
  method: "external_research",
  confidence: 0.30,
  notes: "Heavy-tail potential for viral breakout"
}
```

---

## 3. Correlation Semantics

### 3.1 Correlation Declaration

**Syntax:**
```pel
param cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150) {
  source: "...",
  method: "...",
  confidence: 0.65,
  correlated_with: [conversionRate, -0.4]
}
```

**Semantics:**
- `correlated_with: [var_name, correlation_coefficient]`
- Correlation coefficient ρ ∈ [-1, 1]
- ρ = +1: perfect positive correlation
- ρ = 0: independent
- ρ = -1: perfect negative correlation

**Multiple correlations:**
```pel
correlated_with: [
  [conversionRate, -0.4],
  [brandSpend, 0.3],
  [seasonality, 0.25]
]
```

### 3.2 Correlation Matrix Construction

PEL compiler constructs **correlation matrix** $\mathbf{C}$:

$$\mathbf{C}_{ij} = \begin{cases}
1 & \text{if } i = j \\
\rho_{ij} & \text{if correlation declared} \\
0 & \text{otherwise (assumed independent)}
\end{cases}$$

**Validation:** Compiler **MUST** verify $\mathbf{C}$ is **positive semi-definite** (all eigenvalues ≥ 0).

**Error if invalid:**
```
error[E0430]: Correlation matrix not positive semi-definite
  --> model.pel:25:3
   |
25 |   correlated_with: [x, 0.9], [y, 0.9], [z, 0.9]
   |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: Specified correlations are mathematically impossible
   = help: Reduce correlation magnitudes or remove conflicting correlations
```

### 3.3 Sampling Correlated Variables

**Gaussian Copula Method (default):**

1. Compile correlation matrix $\mathbf{C}$
2. Compute Cholesky decomposition: $\mathbf{C} = \mathbf{L}\mathbf{L}^T$
3. Sample independent standard normals: $\mathbf{z} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$
4. Transform: $\mathbf{x} = \mathbf{L}\mathbf{z}$ (now $\mathbf{x} \sim \mathcal{N}(\mathbf{0}, \mathbf{C})$)
5. Apply inverse CDF of marginals: $v_i = F_i^{-1}(\Phi(x_i))$

where $\Phi$ is standard normal CDF, $F_i$ is CDF of variable $i$'s marginal distribution.

**Result:** Preserves **rank correlation** (Spearman's ρ) exactly, Pearson correlation approximately (exact for Gaussian marginals).

### 3.4 Correlation Validation

Runtime **MUST** verify empirical correlation converges to specified:

For N Monte Carlo runs:
$$|\hat{\rho}_{\text{empirical}} - \rho_{\text{specified}}| < \text{tolerance}$$

**Default tolerance:** 0.02 for N ≥ 1,000

**Runtime warning if violated:**
```
warning: Empirical correlation out of tolerance
  variable pair: (cac, conversionRate)
  specified: -0.40
  empirical: -0.35
  N: 1000 runs
```

---

## 4. Sampling Methods

### 4.1 Deterministic Mode

**Semantics:** Sample at **central tendency** (mean for symmetric, median for skewed)

**Rules:**
```
Beta(α, β)         → α / (α + β)
Normal(μ, σ)       → μ
LogNormal(μ, σ)    → exp(μ)  (median, NOT mean)
Uniform(low, high) → (low + high) / 2
Triangular(l,m,h)  → m  (mode)
```

**Use case:** Fast single-run simulation for central scenario

**Example:**
```bash
pel run model.pel --deterministic --seed 42
```

### 4.2 Monte Carlo Mode

**Semantics:** Sample from full distribution using PRNG

**Algorithm:**
1. Initialize PRNG with seed
2. For each run $i = 1, \ldots, N$:
   - Sample all distributional parameters
   - Execute full simulation
   - Record outputs
3. Aggregate statistics (mean, median, percentiles)

**Use case:** Full uncertainty quantification

**Example:**
```bash
pel run model.pel --monte-carlo --runs 10000 --seed 42
```

### 4.3 Latin Hypercube Sampling (Optional Extension)

**Purpose:** Stratified sampling for better coverage with fewer samples

**Not required for conformance**, but recommended for efficiency.

### 4.4 Sobol Sequences (Optional Extension)

**Purpose:** Quasi-random low-discrepancy sequences

**Not required for conformance**, but useful for variance-based sensitivity analysis.

---

## 5. Mixture Distributions

### 5.1 Syntax

```pel
~ Mixture(
  distributions: [Beta(α=2, β=8), Beta(α=8, β=2)],
  weights: [0.7, 0.3]
)
```

**Semantics:**
- Sample from distribution $D_i$ with probability $w_i$
- Weights **MUST** sum to 1.0
- All distributions **MUST** have same type

### 5.2 Use Cases

**Bimodal outcomes:**
```pel
param conversionRate: Fraction ~ Mixture(
  distributions: [
    Beta(α=2, β=18),   // low conversion (most of the time)
    Beta(α=10, β=10)   // high conversion (when campaign successful)
  ],
  weights: [0.8, 0.2]
) {
  source: "A/B_test_history",
  method: "fitted",
  confidence: 0.70,
  notes: "Bimodal: base vs campaign-driven conversion"
}
```

**Regime changes:**
```pel
param economyState: Fraction ~ Mixture(
  distributions: [
    Normal(μ=0.03, σ=0.01),  // expansion
    Normal(μ=-0.02, σ=0.02)  // recession
  ],
  weights: [0.85, 0.15]
) {
  source: "macro_model",
  method: "external_research",
  confidence: 0.50
}
```

---

## 6. Fat-Tail Modeling

### 6.1 Kurtosis Awareness

PEL encourages modeling **heavy-tail risks** explicitly:

**Gaussian (thin tails):**
- Kurtosis = 3 (excess kurtosis = 0)
- P(|X - μ| > 3σ) ≈ 0.003 (0.3%)

**LogNormal (moderate fat tails):**
- Excess kurtosis > 0

**Pareto (heavy tails):**
- Tail index α controls heaviness
- Small α → extreme outliers likely

### 6.2 Tail Risk Metrics

PEL runtimes **SHOULD** report:

- **VaR (Value at Risk):** $P(X \leq \text{VaR}_\alpha) = \alpha$ (e.g., 95th percentile)
- **CVaR (Conditional VaR):** Expected value beyond VaR (tail mean)
- **Kurtosis:** Fourth moment, tail heaviness indicator

**Example output:**
```
Monte Carlo Results (N=10,000):
  Variable: cashBalance[T=36]
  Mean: $250,000
  Median: $280,000
  VaR_95: $50,000  (5% chance of dropping below)
  CVaR_95: $20,000 (expected value if worst 5% occurs)
  Kurtosis: 4.2 (heavy tail)
```

### 6.3 Stress Testing

**Tail scenario specification:**
```pel
scenario recession_stress {
  override: {
    demandGrowth ~ Normal(μ=-0.10, σ=0.05),  // negative growth
    churnRate ~ Beta(α=8, β=12)               // elevated churn
  }
}

simulate monte_carlo with runs 1000 under scenario recession_stress
```

---

## 7. Shock Scenarios

### 7.1 Discrete Shocks

**Syntax:**
```pel
shock platform_policy_change at t=12 {
  virality_coefficient *= 0.3,  // 70% reduction
  cac *= 2.0                    // CAC doubles
}
```

**Semantics:**
- Instantaneous parameter changes at specified time
- Models regime breaks (policy changes, platform shocks, regulatory shifts)

### 7.2 Shock Probability

**Stochastic shocks:**
```pel
shock recession {
  probability: 0.15 per Year,
  when_triggered: {
    demandGrowth = -0.20,
    churnRate *= 1.5
  }
}
```

**Monte Carlo handling:**
- Each run samples whether shock occurs
- If triggered, shock time sampled from probability distribution

### 7.3 Shock Library

PEL standard library includes pre-defined shocks:

- `stdlib.shocks.Recession(severity: Fraction)`
- `stdlib.shocks.PlatformPolicyChange(impact: Fraction)`
- `stdlib.shocks.SupplyShortage(duration: Duration, severity: Fraction)`
- `stdlib.shocks.TechDisruption(adoption_rate: Rate per Month)`

---

## 8. Unknown Unknowns

### 8.1 Epistemic Uncertainty

**Known unknowns:** Modeled with distributions (parametric uncertainty)

**Unknown unknowns:** Things we don't know we don't know (model uncertainty, "black swans")

### 8.2 Uncertainty Envelope

**Syntax:**
```pel
param cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150) {
  source: "...",
  method: "...",
  confidence: 0.65,
  unknown_unknown_envelope: 2.0  // 2x multiplier on sigma for robustness
}
```

**Semantics:**
- Inflates uncertainty to account for model mis-specification
- **NOT a prediction**, but a **robustness stress test**

**Example:**
If σ = $150, envelope = 2.0:
- Standard Monte Carlo: σ = $150
- Robustness mode: σ = $300 (2× wider distribution)

**Use case:** Scenario planning under radical uncertainty

### 8.3 Robustness Commands

```bash
pel run model.pel --robustness-mode --envelope-multiplier 2.0
```

Outputs:
- Standard Monte Carlo results
- Robustness-adjusted results (wider uncertainty)
- "Survival probability" under envelope scenarios

---

## 9. Variance Propagation

### 9.1 Analytic Propagation (Delta Method)

For small uncertainties, PEL **MAY** use **first-order Taylor approximation**:

If $Y = f(X_1, \ldots, X_n)$ and $X_i$ has variance $\sigma_i^2$:

$$\text{Var}(Y) \approx \sum_{i=1}^n \left(\frac{\partial f}{\partial X_i}\right)^2 \sigma_i^2 + 2\sum_{i<j} \frac{\partial f}{\partial X_i}\frac{\partial f}{\partial X_j} \text{Cov}(X_i, X_j)$$

**Use case:** Fast approximate uncertainty quantification

**Limitation:** Inaccurate for large uncertainties or nonlinear functions

### 9.2 Monte Carlo Propagation (Exact)

**True variance:** Computed empirically from Monte Carlo samples

$$\text{Var}(Y) = \frac{1}{N-1}\sum_{i=1}^N (Y_i - \bar{Y})^2$$

**Advantage:** Exact for any function, any distribution

**Cost:** Requires many samples (N ≥ 1,000 recommended)

---

## 10. Reproducibility Guarantees

### 10.1 Deterministic Seeding

**Requirement:** Given same seed, **bit-identical** results across all runs and all conformant implementations.

**Mechanism:**
- Seed initializes PRNG (e.g., Mersenne Twister, PCG, xoshiro256**)
- PRNG state evolves deterministically
- Sampling order **MUST** be deterministic (declaration order)

**Test:**
```bash
pel run model.pel --seed 42 > run1.json
pel run model.pel --seed 42 > run2.json
diff run1.json run2.json  # MUST be empty
```

### 10.2 Monte Carlo Ensemble Reproducibility

**For N runs with base seed $s$:**

Run $i$ uses seed $s_i = \text{hash}(s, i)$

**Guarantee:** Ensemble statistics (mean, variance, percentiles) **MUST** be deterministic.

### 10.3 Version Tagging

Run artifacts **MUST** include:
- PEL runtime version
- PRNG algorithm and version
- Seed
- Number of runs

**Reproducibility policy:**
- Conformant runtimes **MUST** reproduce results within same major version
- Cross-version reproducibility **NOT guaranteed** (PRNG may improve)

---

## Appendix A: Distribution Properties Reference

| Distribution | Support | Parameters | Mean | Variance | Skewness |
|--------------|---------|------------|------|----------|----------|
| Beta | [0,1] | α, β > 0 | α/(α+β) | αβ/[(α+β)²(α+β+1)] | Varies |
| Normal | ℝ | μ, σ > 0 | μ | σ² | 0 |
| LogNormal | ℝ+ | μ, σ > 0 | exp(μ+σ²/2) | [exp(σ²)-1]exp(2μ+σ²) | Positive |
| Uniform | [a,b] | a < b | (a+b)/2 | (b-a)²/12 | 0 |
| Triangular | [a,b] | a<m<b | (a+m+b)/3 | (a²+b²+m²-ab-am-bm)/18 | Varies |
| Pareto | [xₘ,∞) | xₘ, α > 0 | αxₘ/(α-1) if α>1 | Depends on α | Positive |

---

## Appendix B: Correlation Strength Interpretation

| |ρ| | Interpretation | Example |
|------|----------------|---------|
| 0.0-0.2 | Negligible | Independent or near-independent |
| 0.2-0.4 | Weak | CAC and conversion (weak negative) |
| 0.4-0.6 | Moderate | Churn and support load |
| 0.6-0.8 | Strong | Price and demand (negative) |
| 0.8-1.0 | Very strong | Nearly deterministic relationship |

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)  
**Canonical URL:** https://spec.pel-lang.org/v0.1/uncertainty
