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
param conversion_rate: Probability = 0.15  // Exactly 15%? Impossible.
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

param conversion_rate: Probability ~ Beta(alpha: 15, beta: 85) {
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
  param website_conversion: Probability ~ Beta(alpha: 12, beta: 88) {
    source: "google_analytics",
    method: "fitted",
    confidence: 0.80
  }
  
  // Email open rate: 20-30% range
  param email_open_rate: Probability ~ Beta(alpha: 25, beta: 75) {
    source: "mailchimp_data",
    method: "observed",
    confidence: 0.85
  }
  
  // Customer churn (monthly): low churn ~5%
  param monthly_churn: Probability ~ Beta(alpha: 2, beta: 38) {
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
  param market_share: Probability ~ Uniform(min: 0.05, max: 0.25) {
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
    ~ Normal(μ=0.15/1mo, σ=0.05/1mo) 
    with correlation(customer_retention_rate: 0.7) {
      source: "growth_model",
      method: "assumption",
      confidence: 0.50
    }
  
  param customer_retention_rate: Probability 
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
    ~ Normal(μ=0.20/1mo, σ=0.05/1mo) 
    with correlation(churn_rate: -0.3) {
      source: "marketing_forecast",
      method: "assumption",
      confidence: 0.50,
      notes: "Negative correlation: good growth often means lower churn"
    }
  
  // Monthly churn: typically 3-7%, mean 5%
  param churn_rate: Probability ~ Beta(alpha: 5, beta: 95) {
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
param churn_rate: Probability ~ Normal(μ=0.05, σ=0.02)

// ✅ Correct: Beta is bounded [0, 1]
param churn_rate: Probability ~ Beta(alpha: 5, beta: 95)
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
- **Reference**: See `/docs/model/distributions.md` for mathematical details

## Additional Resources

- [Distribution Reference](/docs/model/distributions.md)
- [Monte Carlo Execution](/docs/runtime/monte_carlo.md)
- [Statistical Interpretation Guide](/docs/tutorials/interpreting_results.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
