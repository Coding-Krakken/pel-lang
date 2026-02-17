# Your First PEL Model in 15 Minutes

Learn to build, run, and analyze an economic model using PEL.

## Prerequisites

- PEL installed (`pip install pel-lang` or local setup)
- Basic understanding of business metrics (revenue, growth, costs)
- 15 minutes of focused time

## Step 1: Write a Simple Growth Model (5 minutes)

Create a file called `my_growth_model.pel`:

```pel
model SimpleGrowth {
  // Starting revenue
  param initial_revenue: Currency<USD> = $10_000 {
    source: "current_metrics",
    method: "observed",
    confidence: 0.95
  }
  
  // Monthly growth rate (with uncertainty)
  param growth_rate: Rate per Month = ~Normal(μ=0.10/1mo, σ=0.02/1mo) {
    source: "historical_analysis",
    method: "fitted",
    confidence: 0.70,
    notes: "Fitted from last 12 months"
  }
  
  // Operating costs per month
  param monthly_opex: Currency<USD> = $6_000 {
    source: "budget_2026",
    method: "assumption",
    confidence: 0.80
  }
  
  // Calculated: Revenue over time
  var revenue: TimeSeries<Currency<USD>>
  revenue[0] = initial_revenue
  revenue[t+1] = revenue[t] * (1 + growth_rate[t])
  
  // Calculated: Profit
  var profit: TimeSeries<Currency<USD>>
  profit[t] = revenue[t] - monthly_opex
  
  // Constraint: Must stay profitable by month 12
  constraint profitability: profit[12] > $0 {
    severity: warning,
    message: "Not profitable by month 12"
  }
}
```

**What you just wrote:**
- **Parameters** with provenance (where numbers come from)
- **Variables** that calculate over time
- **Distributions** to model uncertainty
- **Constraints** to check assumptions

## Step 2: Compile Your Model (2 minutes)

```bash
pel compile my_growth_model.pel
```

**Expected output:**
```
Compiling my_growth_model.pel...
  [1/5] Lexical analysis...
        Generated 87 tokens
  [2/5] Parsing...
        Parsed model 'SimpleGrowth'
  [3/5] Type checking...
        Type checking passed
  [4/5] Provenance validation...
        Completeness: 100.0%
  [5/5] Generating IR...
        Model hash: sha256:a3f2b1c4...

✓ Compilation successful!
  Output: my_growth_model.ir.json
  Parameters: 3
  Variables: 2
  Constraints: 1
```

**What just happened:**
- PEL checked your units (can't add $ to %)
- Verified all assumptions have sources
- Generated portable IR (Intermediate Representation)

## Step 3: Run Deterministic Simulation (2 minutes)

```bash
pel run my_growth_model.ir.json --mode deterministic --seed 42
```

**What this does:**
- Uses mean values for all distributions
- Same seed = same results (reproducible)
- Fast execution for quick validation

**Example output:**
```json
{
  "status": "success",
  "mode": "deterministic",
  "seed": 42,
  "variables": {
    "revenue": [10000, 11000, 12100, 13310, ...],
    "profit": [4000, 5000, 6100, 7310, ...]
  },
  "constraint_violations": []
}
```

**Interpretation:**
- Revenue grows from $10K to ~$34K in 12 months
- Profit positive throughout (constraint satisfied)

## Step 4: Run Monte Carlo Simulation (3 minutes)

```bash
pel run my_growth_model.ir.json --mode monte_carlo --runs 1000 --seed 42 -o results.json
```

**What this does:**
- Runs model 1,000 times with sampled growth rates
- Shows range of possible outcomes
- Quantifies uncertainty

**Output includes:**
- `p50` (median outcome)
- `p95` (95th percentile - optimistic case)
- `p5` (5th percentile - pessimistic case)

## Step 5: Generate a Report (3 minutes)

```bash
# Markdown report
python3 runtime/reporting.py results.json markdown report.md

# HTML report (open in browser)
python3 runtime/reporting.py results.json html report.html
open report.html
```

**Your report includes:**
- Executive summary (status, runtime, seed)
- Key metrics table
- Assumption register (where every number came from)
- Constraint violations (if any)

## What Makes This Different from a Spreadsheet?

| Feature | Spreadsheet | PEL |
|---------|-------------|-----|
| **Units** | No checking (can add $ + days) | ✅ Type-safe (compile error) |
| **Uncertainty** | Manual, implicit | ✅ First-class syntax |
| **Provenance** | Comments (if you remember) | ✅ Required metadata |
| **Reproducibility** | "Works on my machine" | ✅ Model hash + seed |
| **Constraints** | External validation | ✅ Built-in checks |

## Next Steps

### Enhance Your Model

Add more realism:

```pel
// Seasonal growth
param seasonality: Array<Fraction> = [1.2, 1.1, 0.9, 0.8, ...] {
  source: "historical_patterns",
  method: "observed",
  confidence: 0.85
}

// Churn
param churn_rate: Rate per Month = 0.05/1mo {
  source: "retention_analysis",
  method: "derived",
  confidence: 0.75
}

var net_revenue_growth: Rate per Month
net_revenue_growth[t] = growth_rate[t] - churn_rate
```

### Add Policies

Make your model adaptive:

```pel
policy cut_costs_if_unprofitable {
  when: profit[t] < $0
  then: monthly_opex *= 0.8  // 20% cost cut
}
```

### Use Standard Library

Import reusable functions:

```pel
import pel.stdlib.unit_econ as econ

var ltv: Currency<USD> = econ.ltv_simple(revenue_per_customer, churn_rate)
var ltv_to_cac: Fraction = econ.ltv_to_cac_ratio(ltv, cac)
```

## Common Pitfalls

### 1. Missing Provenance
```pel
// ❌ Won't compile
param growth: Rate per Month = 0.10/1mo

// ✅ Correct
param growth: Rate per Month = 0.10/1mo {
  source: "assumption",
  method: "guess",
  confidence: 0.5
}
```

### 2. Unit Errors
```pel
// ❌ Type error: can't add Currency to Rate
var broken = revenue + growth_rate

// ✅ Correct
var new_revenue = revenue * (1 + growth_rate)
```

### 3. Time Causality
```pel
// ❌ Can't use future value
revenue[t] = revenue[t+1] * 0.9

// ✅ Correct
revenue[t+1] = revenue[t] * 1.1
```

## Resources

- **Examples:** `examples/` directory
- **Standard Library:** `stdlib/` modules
- **Specifications:** `spec/` for deep dives
- **Community:** GitHub Discussions

## Congratulations!

You've built, compiled, run, and analyzed your first PEL model. You now understand:

- ✅ How to declare parameters with provenance
- ✅ How to express uncertainty with distributions
- ✅ How to define constraints
- ✅ How to run deterministic and stochastic simulations
- ✅ How to generate stakeholder reports

**You're ready to model real business problems in PEL!**

---

**Time invested:** 15 minutes  
**Value gained:** Reproducible, type-safe, auditable economic model  
**Next model:** < 10 minutes (you know the pattern)
