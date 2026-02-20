# Tutorial 3: Uncertainty & Distributions

## Overview

Real-world business models contain **irreducible uncertainty**. Spreadsheets handle this poorly (single point estimates), while Monte Carlo tools require manual distribution setup. PEL makes uncertainty a **first-class language feature** with:

- Built-in probability distributions (`Normal`, `Beta`, `LogNormal`, `Uniform`)
- Automatic uncertainty propagation through calculations
- Correlation modeling between parameters
- Two simulation modes: deterministic (fast) and Monte Carlo (realistic)

**Time required**: 25 minutes  
**Prerequisites**: Tutorials 1-2  
**Learning outcomes**: 
- Model uncertainty with appropriate distributions
- Understand when to use each distribution type
- Specify correlations between parameters
- Interpret Monte Carlo simulation results

## Why Model Uncertainty?

### The Problem with Point Estimates

Consider a product launch forecast:

```pel
// ❌ Overconfident: pretends we know exact values
param launch_date_delay: Duration = 0mo  // Launches exactly on time? Unlikely.
param conversion_rate: Fraction = 0.15  // Exactly 15%? Impossible.
param viral_coefficient: Fraction = 1.8  // Precise to 0.1? Doubtful.
```

**Issues**:
- Ignores known uncertainty (launches often delay)
- Creates false precision (conversion varies by cohort, time, channel)
- Prevents risk analysis (what if conversion is only 10%?)

### The PEL Approach: Probabilistic Modeling

```pel
// ✅ Realistic: acknowledges uncertainty
param launch_date_delay: Duration ~ Normal(μ=0mo, σ=1.5mo) {
  source: "historical_launches",
  method: "fitted",
  confidence: 0.70
}

param conversion_rate: Fraction ~ Beta(alpha: 15, beta: 85) {
  source: "industry_benchmarks",
  method: "expert_estimate",
  confidence: 0.50
}

param viral_coefficient: Fraction ~ LogNormal(μ=0.59, σ=0.30) {
  source: "similar_products",
  method: "assumption",
  confidence: 0.40
}
```

**Benefits**:
- Captures true uncertainty range
- Enables risk quantification (P5, P50, P95 scenarios)
- Supports sensitivity analysis
- More honest with stakeholders

## The Four Core Distributions

PEL provides distributions suited to common business parameters:

| Distribution | Best For | Typical Use Cases | Properties |
|--------------|----------|-------------------|------------|
| `Normal` | Symmetric, unbounded | Growth rates, errors, delays | Can go negative |
| `Beta` | Bounded [0,1] | Probabilities, success rates | Always in valid range |
| `LogNormal` | Positive, right-skewed | Revenues, customer lifetime | Always positive |
| `Uniform` | Equal likelihood | Complete ignorance | Flat probability |

## 1. Normal Distribution: Symmetric Uncertainty

Use when values cluster around a mean with symmetric spread.

```pel
model ProductDevelopment {
  // Development time: typically 6 months, ±2 months
  param dev_duration: Duration ~ Normal(μ=6mo, σ=2mo) {
    source: "engineering_estimates",
    method: "expert_estimate",
    confidence: 0.65
  }
  
  // Team productivity: 10 story points/week, ±3 variance
  param team_velocity: Rate per Week ~ Normal(μ=10.0/1wk, σ=3.0/1wk) {
    source: "sprint_retrospectives",
    method: "fitted",
    confidence: 0.75
  }
  
  // Total scope: 240 story points (known requirements)
  param total_scope: Fraction = 240.0 {
    source: "product_backlog",
    method: "observed",
    confidence: 0.90
  }
  
  // Expected completion time
  var estimated_completion: TimeSeries<Duration>
  estimated_completion[t] = total_scope / team_velocity[t]
}
```

**Parameters**:
- `μ` (mu): Mean value (center of distribution)
- `σ` (sigma): Standard deviation (spread)
- Approximately 68% of values within μ±σ
- Approximately 95% of values within μ±2σ

**Warning**: Normal distributions can produce negative values. For strictly positive quantities, use `LogNormal`.

## 2. Beta Distribution: Probabilities & Rates

Use for parameters bounded between 0 and 1 (probabilities, rates, percentages).

```pel
model MarketingFunnel {
  // Website conversion rate: typically 8-15%, most likely 12%
  param website_conversion: Fraction ~ Beta(alpha: 12, beta: 88) {
    source: "google_analytics",
    method: "fitted",
    confidence: 0.80
  }
  
  // Email open rate: 20-30% range
  param email_open_rate: Fraction ~ Beta(alpha: 25, beta: 75) {
    source: "mailchimp_data",
    method: "observed",
    confidence: 0.85
  }
  
  // Customer churn (monthly): low churn ~5%
  param monthly_churn: Fraction ~ Beta(alpha: 2, beta: 38) {
    source: "subscription_analytics",
    method: "fitted",
    confidence: 0.70,
    notes: "High uncertainty - limited historical data"
  }
  
  // Funnel calculation
  param monthly_visitors: Fraction = 50000.0 {
    source: "marketing_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  var monthly_conversions: TimeSeries<Fraction>
  monthly_conversions[t] = monthly_visitors * website_conversion[t]
}
```

**Parameters**:
- `alpha`: Number of "successes" (higher = shift right toward 1)
- `beta`: Number of "failures" (higher = shift left toward 0)
- Mean ≈ alpha / (alpha + beta)
- More total counts (alpha + beta) = tighter distribution

**Rule of thumb**:
- `Beta(alpha: 1, beta: 1)`: Uniform [0, 1]
- `Beta(alpha: 2, beta: 8)`: Mean ~20%, moderate uncertainty
- `Beta(alpha: 20, beta: 80)`: Mean ~20%, high confidence (more data)

## 3. LogNormal Distribution: Positive, Right-Skewed

Use for quantities that must be positive and may have long right tails (large outliers).

```pel
model RevenueForecasting {
  // Customer lifetime value: median $500, some customers worth $5000+
  param customer_ltv: Currency<USD> ~ LogNormal(μ=6.2, σ=0.8) {
    source: "customer_cohort_analysis",
    method: "fitted",
    confidence: 0.75,
    notes: "μ and σ are in log-space"
  }
  
  // Monthly revenue per customer: $50-$200 range, right-skewed
  param arpu: Currency<USD> ~ LogNormal(μ=4.0, σ=0.5) {
    source: "billing_data",
    method: "fitted",
    confidence: 0.85
  }
  
  // Time to close deal: typically 30-60 days, occasionally 180+ days
  param sales_cycle_days: Duration ~ LogNormal(μ=3.8, σ=0.4) {
    source: "crm_pipeline",
    method: "fitted",
    confidence: 0.80
  }
  
  // Revenue projection
  param customer_count: Fraction = 1000.0 {
    source: "current_subscriptions",
    method: "observed",
    confidence: 0.99
  }
  
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = customer_count * arpu[t]
}
```

**Parameters** (tricky!):
- `μ` (mu): Mean of the **log** of the variable (NOT the mean of the variable)
- `σ` (sigma): Standard deviation of the **log**
- Actual median ≈ exp(μ)
- Actual mean ≈ exp(μ + σ²/2)

**Converting from natural units**:
- If you know median = M and want moderate spread: `μ = ln(M)`, `σ = 0.5`
- Example: Median $100, moderate uncertainty
  - `μ = ln(100) ≈ 4.6`
  - `σ = 0.5` (factor of ~1.6x spread)

**Use cases**:
- Revenue, prices, costs (must be positive)
- Durations, lifetimes (time can't be negative)
- Customer counts in viral growth models
- Multiplier effects

## 4. Uniform Distribution: Complete Uncertainty

Use when all values in a range are equally likely (rare, but useful for extreme uncertainty).

```pel
model NewMarketEntry {
  // Regulatory approval delay: could be 0-12 months, no idea which
  param regulatory_delay: Duration ~ Uniform(min: 0mo, max: 12mo) {
    source: "legal_team",
    method: "assumption",
    confidence: 0.30,
    notes: "New regulatory environment - no precedent"
  }
  
  // Market share: wild guess between 5-25%
  param market_share: Fraction ~ Uniform(min: 0.05, max: 0.25) {
    source: "market_research",
    method: "expert_estimate",
    confidence: 0.20
  }
  
  // Total addressable market
  param tam: Currency<USD> = $50_000_000 {
    source: "analyst_report",
    method: "assumption",
    confidence: 0.60
  }
  
  var revenue_estimate: TimeSeries<Currency<USD>>
  revenue_estimate[t] = tam * market_share[t]
}
```

**Parameters**:
- `min`: Lower bound (inclusive)
- `max`: Upper bound (inclusive)
- Mean = (min + max) / 2
- Use sparingly - uniform often overestimates uncertainty

## Correlations: Modeling Dependencies

Real parameters are often correlated. PEL allows explicit correlation modeling:

```pel
model CorrelatedGrowth {
  // Customer acquisition and retention tend to move together
  // (good products acquire AND retain customers)
  
  param customer_acquisition_rate: Rate per Month 
    ~ Normal(μ=0.15/1mo, σ=0.05/1mo) {
      source: "growth_model",
      method: "assumption",
      confidence: 0.50,
      correlated_with: [
        { param: "customer_retention_rate", coefficient: 0.7 }
      ]
    }
  
  param customer_retention_rate: Fraction 
    ~ Beta(alpha: 90, beta: 10) {
      source: "churn_analysis",
      method: "fitted",
      confidence: 0.75
    }
  
  // When acquisition_rate is high, retention_rate tends to be high too
  // Correlation: -1 (perfect negative) to +1 (perfect positive)
}
```

**Correlation values**:
- `0.0`: Independent (default)
- `0.7`: Strong positive correlation
- `-0.5`: Moderate negative correlation
- `±1.0`: Perfect correlation (rarely true)

**Common correlated pairs**:
- Revenue growth ↔ Cost growth (positive)
- Customer acquisition ↔ CAC (negative - good marketing lowers CAC)
- Market size ↔ Competition (positive - big markets attract competitors)

## Deterministic vs. Monte Carlo Execution

### Deterministic Mode (Fast Validation)

Uses **mean values** for all distributions:

```bash
pel run model.ir.json --mode deterministic --seed 42
```

```json
{
  "exec_mode": "deterministic",
  "seed": 42,
  "results": {
    "monthly_revenue": [
      {"t": 0, "value": 54321.50, "unit": "USD"}
    ]
  }
}
```

**Use when**:
- Quick validation during development
- Unit testing
- CI/CD pipelines
- You need reproducible results

### Monte Carlo Mode (Realistic Risk Analysis)

Samples distributions **10,000 times** (default):

```bash
pel run model.ir.json --mode monte_carlo --samples 10000 --seed 42
```

```json
{
  "exec_mode": "monte_carlo",
  "samples": 10000,
  "seed": 42,
  "results": {
    "monthly_revenue": [
      {
        "t": 0,
        "unit": "USD",
        "statistics": {
          "mean": 54321.50,
          "median": 52100.00,
          "std_dev": 8500.00,
          "p5": 41000.00,
          "p25": 48000.00,
          "p75": 60000.00,
          "p95": 70000.00
        }
      }
    ]
  }
}
```

**Use when**:
- Risk analysis (what's the worst case?)
- Communicating uncertainty to stakeholders
- Sensitivity analysis
- Production forecasts

**Interpreting percentiles**:
- **P5**: 5% chance actual is below this (pessimistic)
- **P50** (median): Middle value (50% above, 50% below)
- **P95**: 95% chance actual is below this (optimistic)
- **Mean**: Average across all scenarios (often higher than median for right-skewed distributions)

## Practical Example: SaaS Growth Model with Uncertainty

```pel
model SaasGrowthUncertain {
  // --- Initial Conditions (known) ---
  param initial_customers: Fraction = 500.0 {
    source: "subscription_database",
    method: "observed",
    confidence: 0.99
  }
  
  param initial_mrr: Currency<USD> = $50_000 {
    source: "billing_system",
    method: "observed",
    confidence: 0.99
  }
  
  // --- Uncertain Growth Drivers ---
  
  // Monthly customer growth: 10-30%, most likely 20%
  param customer_growth_rate: Rate per Month 
    ~ Normal(μ=0.20/1mo, σ=0.05/1mo) {
      source: "marketing_forecast",
      method: "assumption",
      confidence: 0.50,
      notes: "Negative correlation: good growth often means lower churn",
      correlated_with: [
        { param: "churn_rate", coefficient: -0.3 }
      ]
    }
  
  // Monthly churn: typically 3-7%, mean 5%
  param churn_rate: Fraction ~ Beta(alpha: 5, beta: 95) {
    source: "subscription_analytics",
    method: "fitted",
    confidence: 0.70
  }
  
  // ARPU increases over time (upsells, plan upgrades)
  param arpu_growth_rate: Rate per Month ~ Normal(μ=0.02/1mo, σ=0.01/1mo) {
    source: "revenue_analysis",
    method: "fitted",
    confidence: 0.65
  }
  
  // --- Time Series Calculations ---
  
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] * (1 + customer_growth_rate[t] - churn_rate[t])
  
  var arpu: TimeSeries<Currency<USD>>
  arpu[0] = initial_mrr / initial_customers
  arpu[t+1] = arpu[t] * (1 + arpu_growth_rate[t])
  
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = customers[t] * arpu[t]
  
  // --- Risk Metrics ---
  
  // Constraint: Must maintain at least 400 customers
  constraint minimum_customer_base {
    customers[t] >= 400.0
      with severity(warning)
      with message("Customer base below minimum viable threshold")
  }
  
  // Constraint: Revenue should double within 12 months
  constraint growth_target {
    monthly_revenue[12] >= 2.0 * initial_mrr
      with severity(warning)
      with message("Revenue growth below target (2x in 12 months)")
  }
}
```

**Running this model**:

```bash
# Quick sanity check (deterministic)
pel compile saas_growth_uncertain.pel
pel run saas_growth_uncertain.ir.json --mode deterministic

# Full risk analysis (Monte Carlo)
pel run saas_growth_uncertain.ir.json \
  --mode monte_carlo \
  --samples 10000 \
  --seed 42 \
  -o saas_risk_analysis.json

# Generate report
pel report saas_risk_analysis.json -o saas_report.html
```

## Distribution Selection Guide

| Parameter Type | Recommended Distribution | Rationale |
|----------------|-------------------------|-----------|
| Conversion rates, probabilities | `Beta` | Bounded [0,1], flexible shape |
| Revenue, prices | `LogNormal` | Positive, right-skewed |
| Growth rates (small) | `Normal` | Symmetric around mean |
| Durations, lifetimes | `LogNormal` | Positive, occasional outliers |
| Headcount, integers | `Normal` (then round) | Symmetric, central limit theorem |
| Complete ignorance | `Uniform` | No information to favor specific values |

## Common Mistakes

### Mistake 1: Wrong Distribution for Bounded Values

```pel
// ❌ Wrong: Normal can produce negative churn or >100%
param churn_rate: Fraction ~ Normal(μ=0.05, σ=0.02)

// ✅ Correct: Beta is bounded [0, 1]
param churn_rate: Fraction ~ Beta(alpha: 5, beta: 95)
```

### Mistake 2: LogNormal Parameter Confusion

```pel
// ❌ Wrong: μ=100 means median ≈ exp(100) = huge number
param revenue: Currency<USD> ~ LogNormal(μ=100, σ=20)

// ✅ Correct: μ is in log-space, so μ=ln(100)≈4.6 for median $100
param revenue: Currency<USD> ~ LogNormal(μ=4.6, σ=0.5)
```

### Mistake 3: Over-Specificity

```pel
// ❌ Wrong: False precision (σ=0.0001 implies near-certainty)
param growth_rate: Rate per Month ~ Normal(μ=0.15234/1mo, σ=0.0001/1mo)

// ✅ Correct: Acknowledge real uncertainty
param growth_rate: Rate per Month ~ Normal(μ=0.15/1mo, σ=0.05/1mo)
```

## Quiz: Test Your Understanding

1. **Which distribution for customer churn (monthly cancellation rate)?**
   <details>
   <summary>Answer</summary>
   `Beta` - churn is a probability (0-1), and Beta ensures valid range.
   </details>

2. **Why not use `Normal` for revenue?**
   <details>
   <summary>Answer</summary>
   Normal distributions can produce negative values. Revenue must be positive, so use `LogNormal`.
   </details>

3. **What does `LogNormal(μ=5.0, σ=0.5)` mean?**
   <details>
   <summary>Answer</summary>
   Median value ≈ exp(5.0) ≈ $148 (if units are currency). The μ and σ parameters are in log-space.
   </details>

4. **When should parameters be correlated?**
   <details>
   <summary>Answer</summary>
   When they have a causal or common-cause relationship. Examples: marketing spend ↔ customer acquisition, product quality ↔ retention rate.
   </details>

## Advanced Distribution Techniques

### Mixture Distributions (Simulation Pattern)

When a parameter has multiple possible regimes:

```pel
model ProductLaunchScenarios {
  // Scenario probability
  param success_probability: Fraction = 0.60 {
    source: "expert_panel",
    method: "assumption",
    confidence: 0.50
  }
  
  // Success scenario: high growth
  param growth_if_success: Rate per Month ~ Normal(μ=0.25/1mo, σ=0.05/1mo) {
    source: "successful_launches",
    method: "fitted",
    confidence: 0.70
  }
  
  // Failure scenario: low/negative growth
  param growth_if_failure: Rate per Month ~ Normal(μ=-0.05/1mo, σ=0.10/1mo) {
    source: "failed_launches",
    method: "fitted",
    confidence: 0.70
  }
  
  // Mixture: weighted by scenario probability
  // Note: PEL doesn't have built-in mixture distributions,
  // so we model this via conditional logic in Monte Carlo
  var actual_growth: Rate per Month = 
    if Random() < success_probability
      then growth_if_success
      else growth_if_failure
  
  // Time series evolution
  var customers: TimeSeries<Fraction>
  customers[0] = 1000.0
  customers[t+1] = customers[t] * (1 + actual_growth)
}
```

**Result**: Monte Carlo will sample from the mixture, producing bimodal outcomes.

### Truncated Distributions

Constrain distributions to valid ranges:

```pel
model TruncatedExamples {
  // ❌ Problem: Beta can be extreme
  param churn_rate_unconstrained: Fraction ~ Beta(alpha: 2, beta: 18) {
    source: "industry",
    method: "assumption",
    confidence: 0.60
  }
  // P5 might be 0.02, P95 might be 0.25 (too wide for decisions)
  
  // ✅ Solution: Add constraints (Tutorial 4) or use narrower Beta
  param churn_rate_constrained: Fraction ~ Beta(alpha: 20, beta: 180) {
    source: "industry",
    method: "assumption",
    confidence: 0.70,
    notes: "Tighter distribution: same mean (0.10), less variance"
  }
  // P5 ≈ 0.07, P95 ≈ 0.13 (more realistic)
}
```

**Rule of thumb**: Higher alpha/beta values = tighter distribution around mean.

### Derived Distributions

Distributions propagate through arithmetic:

```pel
model DerivedDistributions {
  param monthly_revenue: Currency<USD> ~ LogNormal(μ=5.0, σ=0.3) {
    source: "forecast",
    method: "assumption",
    confidence: 0.60
  }
  // Median: exp(5.0) ≈ $148, P5 ≈ $94, P95 ≈ $233
  
  param cost_percentage: Fraction ~ Beta(alpha: 60, beta: 40) {
    source: "historical_cogs",
    method: "fitted",
    confidence: 0.85
  }
  // Median: 0.60, P5 ≈ 0.52, P95 ≈ 0.68
  
  // Derived: Uncertainty propagates automatically
  var monthly_costs: Currency<USD> = monthly_revenue * cost_percentage
  // Distribution is complex (LogNormal × Beta)
  // Monte Carlo samples it correctly
  
  var monthly_profit: Currency<USD> = monthly_revenue - monthly_costs
  // Also derived distribution
  
  // Result (example Monte Carlo):
  // monthly_profit P50 ≈ $59, P5 ≈ $15, P95 ≈ $120
}
```

**Key insight**: You don't specify distributions for derived variables—PEL propagates them.

### Time-Varying Uncertainty

Uncertainty often changes over time:

```pel
model TimeVaryingUncertainty {
  // Year 1: High uncertainty (new product)
  param year1_conversion: Fraction ~ Beta(alpha: 5, beta: 45) {
    source: "similar_products",
    method: "expert_estimate",
    confidence: 0.40
  }
  // Wide: P5 ≈ 0.04, P95 ≈ 0.22
  
  // Year 2: Lower uncertainty (data collected)
  param year2_conversion: Fraction ~ Beta(alpha: 50, beta: 450) {
    source: "cohort_analysis",
    method: "fitted",
    confidence: 0.80
  }
  // Narrow: P5 ≈ 0.08, P95 ≈ 0.12
  
  var conversion: TimeSeries<Fraction>
  conversion[t] = if t < 12 then year1_conversion else year2_conversion
  
  // Interpretation: Forecast uncertainty decreases over time (realistic)
}
```

## Calibration Techniques

### Method 1: Historical Data Fitting

If you have historical data, fit distributions statistically:

```bash
# Assume you have churn_history.csv:
# month,churn_rate
# 2024-01,0.048
# 2024-02,0.052
# ...
# 2025-12,0.061

# Use Python/R to fit
python3 << EOF
import numpy as np
from scipy import stats
import csv

# Load data
rates = []
with open('churn_history.csv') as f:
    reader = csv.DictReader(f)
    rates = [float(row['churn_rate']) for row in reader]

# Fit Beta distribution (churn is probability)
# Transform to (0,1) if needed, then fit
alpha, beta, loc, scale = stats.beta.fit(rates, floc=0, fscale=1)

print(f"param churn_rate: Fraction ~ Beta(alpha: {alpha:.1f}, beta: {beta:.1f})")
EOF

# Output:
# param churn_rate: Fraction ~ Beta(alpha: 12.3, beta: 231.7)
```

Then use in PEL:

```pel
param churn_rate: Fraction ~ Beta(alpha: 12.3, beta: 231.7) {
  source: "churn_history_2024-2025",
  method: "fitted",
  confidence: 0.85,
  notes: "Fitted via scipy.stats.beta to 24 months of data"
}
```

### Method 2: Expert Elicitation (Three-Point Estimate)

Ask domain experts for P10, P50, P90 values:

**Expert input**:
- P10 (pessimistic): $80K
- P50 (median): $150K
- P90 (optimistic): $280K

**Fit LogNormal** (assume revenue is log-normally distributed):

```python
import numpy as np
from scipy import stats

# Expert estimates
p10, p50, p90 = 80_000, 150_000, 280_000

# LogNormal parameters from percentiles
# p50 = exp(μ) => μ = log(p50)
mu = np.log(p50)

# p90/p10 ≈ exp(2.56 × σ) => σ ≈ log(p90/p10) / 2.56
sigma = np.log(p90 / p10) / 2.56

print(f"μ={mu:.2f}, σ={sigma:.2f}")
# Output: μ=11.92, σ=0.50
```

PEL model:

```pel
param monthly_revenue: Currency<USD> ~ LogNormal(μ=11.92, σ=0.50) {
  source: "cfo_estimate",
  method: "expert_estimate",
  confidence: 0.60,
  notes: "Three-point elicitation: P10=$80K, P50=$150K, P90=$280K"
}
```

### Method 3: Sensitivity Analysis

If you're unsure about distribution parameters, test sensitivity:

```pel
model SensitivityTest {
  // Test low, medium, high variance scenarios
  
  // Low variance (confident)
  param conversion_low_var: Fraction ~ Beta(alpha: 50, beta: 450) {
    source: "test",
    method: "assumption",
    confidence: 0.90
  }
  // P5 ≈ 0.08, P95 ≈ 0.12
  
  // Medium variance (moderate)
  param conversion_med_var: Fraction ~ Beta(alpha: 15, beta: 135) {
    source: "test",
    method: "assumption",
    confidence: 0.70
  }
  // P5 ≈ 0.06, P95 ≈ 0.15
  
  // High variance (uncertain)
  param conversion_high_var: Fraction ~ Beta(alpha: 5, beta: 45) {
    source: "test",
    method: "assumption",
    confidence: 0.40
  }
  // P5 ≈ 0.04, P95 ≈ 0.22
  
  // Run model 3 times with each variant, compare outcomes
}
```

```bash
# Test each scenario
pel run model.ir.json --mode monte_carlo --samples 5000 \
  --set conversion=conversion_low_var > results_low.json

pel run model.ir.json --mode monte_carlo --samples 5000 \
  --set conversion=conversion_med_var > results_med.json

pel run model.ir.json --mode monte_carlo --samples 5000 \
  --set conversion=conversion_high_var > results_high.json

# Compare: If decision doesn't change, uncertainty level doesn't matter
```

## Working with Correlations

### When to Use Correlations

**Use correlations when**:
- Variables share a common cause (economy affects multiple metrics)
- One directly influences another (price → demand)
- Historical data shows co-movement

**Don't use correlations when**:
- No plausible mechanism links variables
- You're guessing the correlation strength
- Variables are in different causal chains

### Specifying Correlation Strength

```pel
model CorrelationStrengths {
  // Strong positive correlation (0.8): CAC and churn often move together
  // (poor targeting → high CAC + high churn)
  param cac: Currency<USD> ~ LogNormal(μ=6.0, σ=0.4) {
    source: "marketing",
    method: "assumption",
    confidence: 0.70
  }
  
  param churn_rate: Fraction ~ Beta(alpha: 10, beta: 90) {
    source: "analytics",
    method: "assumption",
    confidence: 0.70,
    correlation: [(cac, 0.80)]
  }
  // When CAC is high, churn tends to be high
  
  // Moderate negative correlation (-0.5): better product → higher price, lower churn
  param price: Currency<USD> ~ Normal(μ=$99, σ=$15) {
    source: "pricing",
    method: "assumption",
    confidence: 0.60
  }
  
  param churn: Fraction ~ Beta(alpha: 8, beta: 72) {
    source: "analytics",
    method: "assumption",
    confidence: 0.70,
    correlation: [(price, -0.50)]
  }
  // Higher price → slightly lower churn (premium positioning)
}
```

**Correlation guidelines**:
- **0.9 to 1.0**: Nearly deterministic (rare)
- **0.7 to 0.9**: Strong relationship
- **0.4 to 0.7**: Moderate relationship
- **0.1 to 0.4**: Weak relationship
- **0.0**: Independent
- Negative values: inverse relationship

### Multi-Variate Correlations

```pel
model MultiVariate {
  // Macroeconomic factor (unobserved)
  param market_strength: Fraction ~ Normal(μ=1.0, σ=0.2) {
    source: "assumption",
    method: "assumption",
    confidence: 0.50,
    notes: "Latent variable: 1.0 = normal market, >1 = strong, <1 = weak"
  }
  
  // All these correlate with market strength
  param customer_growth: Rate per Month ~ Normal(μ=0.15/1mo, σ=0.08/1mo) {
    source: "forecast",
    method: "assumption",
    confidence: 0.60,
    correlation: [(market_strength, 0.75)]
  }
  
  param conversion_rate: Fraction ~ Beta(alpha: 12, beta: 88) {
    source: "forecast",
    method: "assumption",
    confidence: 0.60,
    correlation: [(market_strength, 0.70)]
  }
  
  param churn_rate: Fraction ~ Beta(alpha: 8, beta: 92) {
    source: "forecast",
    method: "assumption",
    confidence: 0.60,
    correlation: [(market_strength, -0.65)]
  }
  // Negative: strong market → lower churn
  
  // Result: growth, conversion, and churn all move together
  // (realistic during boom/bust cycles)
}
```

## Interpreting Monte Carlo Results

### Reading Percentile Outputs

```json
{
  "variable": "revenue[12]",
  "deterministic": 125000,
  "monte_carlo": {
    "p05": 87500,
    "p25": 105000,
    "p50": 125000,
    "p75": 148000,
    "p95": 175000,
    "mean": 127500,
    "std_dev": 28000
  }
}
```

**Interpretation**:
- **p50 (median)**: 50% chance revenue ≥ $125K (central estimate)
- **p05**: 5% chance revenue < $87.5K (pessimistic, "bad luck")
- **p95**: 5% chance revenue > $175K (optimistic, "good luck")
- **p25-p75**: Interquartile range (50% of outcomes fall here)
- **mean vs p50**: Mean = $127.5K > p50 = $125K → Right-skewed distribution

**Decision-making**:
- Conservative: Plan for P25 ($105K)
- Moderate: Plan for P50 ($125K)
- Aggressive: Target P75 ($148K)
- Risk management: Ensure viability even at P05 ($87.5K)

### Understanding Distribution Shapes

Run this analysis:

```bash
pel run model.ir.json --mode monte_carlo --samples 10000 -o results.json

# Visualize distribution
python3 << EOF
import json
import matplotlib.pyplot as plt

with open('results.json') as f:
    data = json.load(f)

# Extract samples (if PEL outputs them)
samples = data['variables']['revenue[12]']['samples']

plt.hist(samples, bins=50, alpha=0.7, edgecolor='black')
plt.axvline(data['variables']['revenue[12]']['monte_carlo']['p50'], 
            color='red', label='P50')
plt.axvline(data['variables']['revenue[12]']['monte_carlo']['p05'], 
            color='orange', linestyle='--', label='P05')
plt.axvline(data['variables']['revenue[12]']['monte_carlo']['p95'], 
            color='orange', linestyle='--', label='P95')
plt.xlabel('Revenue at Month 12')
plt.ylabel('Frequency')
plt.legend()
plt.title('Monte Carlo Distribution')
plt.savefig('revenue_distribution.png')
EOF
```

**Shapes and their meanings**:
- **Symmetric (normal-ish)**: Balanced upside/downside risk
- **Right-skewed**: Long tail of high outcomes (LogNormal common)
- **Left-skewed**: Long tail of low outcomes (downside risk)
- **Bimodal**: Two distinct scenarios (success/failure regimes)

### Correlation in Results

Check if outputs are correlated:

```json
{
  "correlations": {
    "revenue[12] vs profit[12]": 0.92,
    "cac vs ltv": -0.35,
    "churn_rate vs retention_rate": -0.99
  }
}
```

**Interpretation**:
- **revenue ↔ profit (0.92)**: Strong positive → profit uncertainty driven by revenue
- **cac ↔ ltv (-0.35)**: Weak negative → higher acquisition cost slightly reduces lifetime value
- **churn ↔ retention (-0.99)**: Perfect negative → redundant (retention = 1 - churn)

## Monte Carlo Best Practices

### 1. Sample Size Selection

```bash
# Quick test: 100 samples
pel run model.ir.json --mode monte_carlo --samples 100
# Fast (~1 sec), unstable percentiles

# Standard: 1,000 samples
pel run model.ir.json --mode monte_carlo --samples 1000
# Moderate speed (~5 sec), stable P5/P50/P95

# High precision: 10,000 samples
pel run model.ir.json --mode monte_carlo --samples 10000
# Slower (~30 sec), very stable percentiles

# Publication: 100,000 samples
pel run model.ir.json --mode monte_carlo --samples 100000
# Slow (~5 min), extreme percentiles (P01, P99) stable
```

**Rule of thumb**: Use 1,000+ for decisions, 10,000+ for reporting.

### 2. Reproducibility

```bash
# Set random seed for reproducible results
pel run model.ir.json --mode monte_carlo --samples 5000 --seed 42

# Same seed = same samples = same results
pel run model.ir.json --mode monte_carlo --samples 5000 --seed 42
# Identical output
```

**Use cases**: 
- Debugging (consistent results)
- A/B testing models (fair comparison)
- Version control (deterministic outputs)

### 3. Variance Reduction Techniques

```pel
model VarianceReduction {
  // ❌ High variance: independent samples for each cohort
  param cohort_1_conversion: Fraction ~ Beta(alpha: 10, beta: 90)
  param cohort_2_conversion: Fraction ~ Beta(alpha: 10, beta: 90)
  param cohort_3_conversion: Fraction ~ Beta(alpha: 10, beta: 90)
  
  // Each cohort samples independently → high variance in total
  var total_conversions = cohort_1_conversion + cohort_2_conversion + cohort_3_conversion
  
  // ✅ Lower variance: common random variable
  param base_conversion: Fraction ~ Beta(alpha: 10, beta: 90) {
    source: "baseline",
    method: "assumption",
    confidence: 0.70
  }
  
  param cohort_1_lift: Fraction ~ Normal(μ=1.0, σ=0.1) {
    source: "test",
    method: "assumption",
    confidence: 0.60
  }
  
  param cohort_2_lift: Fraction ~ Normal(μ=1.0, σ=0.1) {
    source: "test",
    method: "assumption",
    confidence: 0.60
  }
  
  param cohort_3_lift: Fraction ~ Normal(μ=1.0, σ=0.1) {
    source: "test",
    method: "assumption",
    confidence: 0.60
  }
  
  var cohort_1_conv = base_conversion * cohort_1_lift
  var cohort_2_conv = base_conversion * cohort_2_lift
  var cohort_3_conv = base_conversion * cohort_3_lift
  
  var total = cohort_1_conv + cohort_2_conv + cohort_3_conv
  // Lower variance: cohorts move together (shared base)
}
```

## Common Pitfalls

### Pitfall 1: Over-Fitting Distributions

**Problem**: Using too many parameters creates false precision.

```pel
// ❌ Over-engineered
param revenue: Currency<USD> ~ 
  TruncatedLogNormal(μ=5.2, σ=0.37, min=$50K, max=$500K)
  // Where did μ=5.2 (not 5.0 or 5.5) come from? False precision.
```

**Fix**: Round to sensible precision.

```pel
// ✅ Honest uncertainty
param revenue: Currency<USD> ~ LogNormal(μ=5.0, σ=0.4) {
  source: "rough_estimate",
  method: "expert_estimate",
  confidence: 0.50
}
```

### Pitfall 2: Ignoring Parameter Uncertainty

**Problem**: Using deterministic parameters when uncertainty exists.

```pel
// ❌ Overconfident: churn rate is never exactly known
param churn_rate: Fraction = 0.05 {
  source: "last_month",
  method: "observed",
  confidence: 0.95
}
```

**Fix**: Model measurement error.

```pel
// ✅ Acknowledges measurement noise
param churn_rate: Fraction ~ Beta(alpha: 95, beta: 1805) {
  source: "last_month",
  method: "fitted",
  confidence: 0.95,
  notes: "95 churned out of 1900 customers → Beta(95, 1805)"
}
// Mean ≈ 0.05, but with uncertainty
```

### Pitfall 3: Misinterpreting Correlation

**Problem**: Confusing correlation with causation.

```pel
// ❌ Wrong: Implies ice cream causes drowning
param ice_cream_sales: Currency<USD> ~ LogNormal(μ=10.0, σ=0.5)
param drowning_incidents: Fraction ~ LogNormal(μ=2.0, σ=0.3) {
  correlation: [(ice_cream_sales, 0.95)]
}
// Both correlate, but common cause is summer weather
```

**Fix**: Model the common cause.

```pel
// ✅ Correct: Model the confounder
param is_summer: Fraction = 0.25  // 3 months / 12 months
param ice_cream_sales: Currency<USD> ~ 
  if is_summer 
    then LogNormal(μ=11.0, σ=0.3)  // High in summer
    else LogNormal(μ=9.0, σ=0.3)   // Low otherwise

param drowning_incidents: Fraction ~
  if is_summer
    then LogNormal(μ=2.5, σ=0.2)   // High in summer
    else LogNormal(μ=1.5, σ=0.2)   // Low otherwise
// No direct correlation, but both driven by season
```

## Distribution Reference Table

| Distribution | Type | Use Case | Parameter Guidance |
|--------------|------|----------|-------------------|
| `Normal(μ, σ)` | Any | Symmetric uncertainty, can go negative | μ = mean, σ = std dev |
| `LogNormal(μ, σ)` | Positive | Revenue, costs (must be > 0) | μ, σ in log-space (use fitting tool) |
| `Beta(α, β)` | Fraction [0,1] | Conversion rates, churn, probabilities | Higher α,β = tighter dist |
| `Uniform(min, max)` | Any | No prior knowledge, bounded range | Lazy: use when you don't know shape |

### Distribution Selection Flowchart

```
Can variable be negative?
├─ YES → Normal(μ, σ)
└─ NO → Is it a probability (0-1)?
    ├─ YES → Beta(α, β)
    └─ NO → Is it bounded?
        ├─ YES, know bounds → Uniform(min, max)
        └─ NO / unbounded positive → LogNormal(μ, σ)
```

## Practice Exercises

### Exercise 1: Fit Beta Distribution

Given historical churn data: 150 churned, 2850 retained.

**Task**: Specify appropriate Beta distribution.

```pel
param churn_rate: Fraction ~ Beta(alpha: ???, beta: ???) {
  source: "historical_data",
  method: "fitted",
  confidence: ???
}
```

<details>
<summary>Solution</summary>

```pel
param churn_rate: Fraction ~ Beta(alpha: 150, beta: 2850) {
  source: "historical_data_q4_2025",
  method: "fitted",
  confidence: 0.95,
  notes: "150 churned, 2850 retained out of 3000 total customers"
}
// Mean: 150 / (150 + 2850) = 0.05
// But with realistic uncertainty around that estimate
```
</details>

### Exercise 2: Model Correlated Variables

Revenue and profit both affected by market conditions.

```pel
model Exercise2 {
  param revenue: Currency<USD> ~ LogNormal(μ=12.0, σ=0.4) {
    source: "forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  param cost_of_goods_pct: Fraction ~ Beta(alpha: 60, beta: 40) {
    source: "vendor_quotes",
    method: "assumption",
    confidence: 0.70
  }
  
  // TODO: Should these be correlated? If so, what sign and strength?
  // Hint: In strong markets, revenue is high AND vendors charge more
}
```

<details>
<summary>Solution</summary>

```pel
param cost_of_goods_pct: Fraction ~ Beta(alpha: 60, beta: 40) {
  source: "vendor_quotes",
  method: "assumption",
  confidence: 0.70,
  correlation: [(revenue, 0.50)]
  // Positive correlation: strong market → high revenue, high costs
  // Moderate strength (0.50): relationship exists but not deterministic
}
```
</details>

### Exercise 3: Interpret Monte Carlo Output

Given results:
- P05: $80K
- P25: $110K  
- P50: $140K
- P75: $185K
- P95: $250K

**Questions**:
1. What's the probability revenue exceeds $140K?
2. What's the interquartile range?
3. Is this distribution symmetric or skewed?

<details>
<summary>Answers</summary>

1. **50%** (P50 = $140K means 50% of outcomes above, 50% below)
2. **$75K** (P75 - P25 = $185K - $110K = $75K)
3. **Right-skewed** (P95 - P50 = $110K vs P50 - P05 = $60K; upper tail is longer)
</details>

## Key Takeaways

1. **Model uncertainty explicitly**: Distributions > point estimates
2. **Choose appropriate distributions**: Beta for probabilities, LogNormal for positive values
3. **Use correlations sparingly**: Only when clear causal relationship exists
4. **Deterministic mode for testing**: Fast, reproducible
5. **Monte Carlo for decisions**: Captures risk, provides percentiles
6. **Interpret percentiles correctly**: P5/P50/P95 = pessimistic/median/optimistic

## Next Steps

- **Tutorial 4**: Add constraints and policies to enforce business rules
- **Tutorial 8**: Calibrate distributions from real data (CSV import)
- **Reference**: See `spec/pel_uncertainty_spec.md` for mathematical details

## Additional Resources

- [Uncertainty Specification](../../spec/pel_uncertainty_spec.md)
- [Language Specification (Distributions)](../../spec/pel_language_spec.md#distributions)
- [Examples with Distributions](../../examples/)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
