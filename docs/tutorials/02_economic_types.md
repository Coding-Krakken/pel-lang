# Tutorial 2: Understanding Economic Types

## Overview

PEL's **semantic type system** is what prevents "unit conversion bugs" and makes models self-documenting. Unlike spreadsheets (where everything is a number) or Python (where units are comments), PEL enforces dimensional correctness at compile time.

**Time required**: 20 minutes  
**Prerequisites**: Tutorial 1 (Your First Model)  
**Learning outcomes**: 
- Understand PEL's economic type categories
- Use units, scopes, and time-indices correctly
- Avoid common type errors
- Write self-documenting models

## Why Types Matter in Economic Modeling

Consider this spreadsheet formula:
```
=A1*B1*C1  // What units result? Unknown!
```

If A1=10%, B1=$100, C1=5 months, what does the result mean? Is it dollars? Percent-dollars-months? This ambiguity causes real-world errors.

PEL makes units **explicit and checked**:
```pel
var result = 0.10 * $100 * 5mo  // Compile error: incompatible units
```

## The Four Categories of Economic Types

PEL types fall into 4 categories:

| Category | Purpose | Examples |
|----------|---------|----------|
| **Quantities** | Physical/economic measures with units | `Currency<USD>`, `Duration`, `Fraction` |
| **Rates** | Change over time | `Rate per Month`, `Fraction` |
| **Scopes** | Aggregation boundaries | `Dimension`, `Team`, `Region` |
| **Time-Indexed** | Values that change over time | `TimeSeries<Currency<USD>>` |

## 1. Quantities: Values with Units

### Currency Types

```pel
model CurrencyExample {
  // Explicit currency denomination
  param revenue_usd: Currency<USD> = $100_000 {
    source: "finance_system",
    method: "observed",
    confidence: 0.99
  }
  
  param revenue_eur: Currency<EUR> = €80_000 {
    source: "finance_system",
    method: "observed",
    confidence: 0.99
  }
  
  // Compile error: Cannot mix currencies without conversion
  // var total = revenue_usd + revenue_eur  // ❌ ERROR
  
  // Correct: Convert first (when exchange rate feature ships)
  // var total = revenue_usd + convert(revenue_eur, EUR->USD, rate=1.20)
}
```

**Key insight**: PEL prevents accidental mixing of currencies, a common source of financial reporting errors.

### Duration Types

```pel
model DurationExample {
  param project_duration: Duration = 6mo {
    source: "project_plan",
    method: "assumption",
    confidence: 0.70
  }
  
  param sprint_length: Duration = 2wk {
    source: "agile_framework",
    method: "assumption",
    confidence: 1.0
  }
  
  // Automatic unit conversion
  var total_sprints: Fraction = project_duration / sprint_length
  // Result: 13.04 (dimensionless)
  
  // Valid duration arithmetic
  var extended_project: Duration = project_duration + 4wk
  // Result: 6.93mo
}
```

**Supported duration units**: `mo` (month), `wk` (week), `day`, `yr` (year)

### Fractions and Counts

```pel
model CountsExample {
  // Dimensionless numbers
  param employee_count: Fraction = 150.0 {
    source: "hr_system",
    method: "observed",
    confidence: 1.0
  }
  
  // Headcount can be fractional (FTE accounting)
  param contractor_fte: Fraction = 12.5 {
    source: "hr_system",
    method: "observed",
    confidence: 0.95
  }
  
  var total_headcount: Fraction = employee_count + contractor_fte
  // Result: 162.5 FTE
}
```

## 2. Rates: Change Over Time

Rates describe how quantities change:

```pel
model RatesExample {
  // Growth rate: percentage per unit time
  param monthly_growth: Rate per Month = 0.15 / 1mo {
    source: "historical_analysis",
    method: "fitted",
    confidence: 0.75
  }
  
  param initial_customers: Fraction = 1000.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  // Rate × Count = Count/Time
  var customer_growth_rate: Rate per Month 
    = initial_customers * monthly_growth
  // Result: 150 customers/month
  
  // Integrate over time
  param planning_horizon: Duration = 12mo {
    source: "model",
    method: "assumption",
    confidence: 1.0
  }
  
  var total_new_customers: Fraction 
    = customer_growth_rate * planning_horizon
  // Result: 1800 customers
}
```

**Common rate patterns**:
- `Rate per Month`: Growth, churn, hiring
- `Fraction`: Success rates, risk factors (dimensionless, 0-1)
- `Currency<USD> per Month`: Monthly recurring revenue (MRR)

## 3. Fractions as Probabilities

Probabilities in PEL are represented using the `Fraction` type, constrained to [0, 1].

> **Note**: There is no `Probability` type in PEL. Use `Fraction` for all probability values and add a constraint to enforce valid bounds.

```pel
model ProbabilityExample {
  // Probability is a Fraction constrained to [0, 1]
  param conversion_rate: Fraction = 0.12 {
    source: "ab_test_results",
    method: "observed",
    confidence: 0.85
  }
  
  param monthly_trials: Fraction = 10000.0 {
    source: "marketing_forecast",
    method: "assumption",
    confidence: 0.70
  }
  
  // Probability × Count = Expected Count
  var expected_conversions: Fraction 
    = conversion_rate * monthly_trials
  // Result: 1200 conversions
  
  // Constraint: Probabilities must be in [0, 1]
  constraint valid_probability {
    conversion_rate >= 0.0 && conversion_rate <= 1.0
      with severity(fatal)
      with message("Conversion rate must be between 0 and 1")
  }
}
```

## 4. Time-Indexed Types: Values That Evolve

```pel
model TimeSeriesExample {
  param initial_balance: Currency<USD> = $50_000 {
    source: "bank_account",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_revenue: Currency<USD> = $20_000 {
    source: "revenue_forecast",
    method: "assumption",
    confidence: 0.65
  }
  
  param monthly_expenses: Currency<USD> = $15_000 {
    source: "budget",
    method: "assumption",
    confidence: 0.80
  }
  
  // Time series: value at each time step
  var cash_balance: TimeSeries<Currency<USD>>
  
  // Initial condition
  cash_balance[0] = initial_balance
  
  // Recurrence relation
  cash_balance[t+1] = cash_balance[t] + monthly_revenue - monthly_expenses
  
  // Result: cash_balance[0] = $50,000
  //         cash_balance[1] = $55,000
  //         cash_balance[2] = $60,000
  //         ...
}
```

**Time-indexed patterns**:
- `[0]`: Initial value
- `[t]`: Current time step
- `[t+1]`: Next time step
- `[t-1]`: Previous time step (lookback)

## Type Compatibility Rules

### What Operations Are Allowed?

| Operation | Example | Result Type | Valid? |
|-----------|---------|-------------|--------|
| Currency + Currency (same) | `$100 + $50` | `Currency<USD>` | ✅ |
| Currency + Currency (different) | `$100 + €50` | N/A | ❌ |
| Currency × Fraction | `$100 * 2.0` | `Currency<USD>` | ✅ |
| Currency × Duration | `$100 * 3mo` | N/A | ❌ |
| Rate × Duration | `(0.1/1mo) * 6mo` | `Fraction` | ✅ |
| Fraction / Fraction | `100.0 / 50.0` | `Fraction` | ✅ |
| Duration / Duration | `6mo / 2mo` | `Fraction` | ✅ |

## Practical Example: SaaS Financial Model

```pel
model SaasFinancials {
  // --- Customer Dynamics ---
  param initial_customers: Fraction = 500.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_customer_growth: Rate per Month = 0.20 / 1mo {
    source: "growth_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  param monthly_churn_rate: Fraction = 0.05 {
    source: "historical_data",
    method: "fitted",
    confidence: 0.80
  }
  
  // --- Revenue Model ---
  param arpu: Currency<USD> = $100 {
    source: "billing_system",
    method: "observed",
    confidence: 0.95,
    notes: "Average Revenue Per User"
  }
  
  // Time series
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] * (1 + monthly_customer_growth - monthly_churn_rate)
  
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = customers[t] * arpu
  
  // --- Cost Model ---
  param cost_per_customer: Currency<USD> = $30 {
    source: "finance",
    method: "assumption",
    confidence: 0.75
  }
  
  var monthly_costs: TimeSeries<Currency<USD>>
  monthly_costs[t] = customers[t] * cost_per_customer
  
  // --- Profitability ---
  var monthly_profit: TimeSeries<Currency<USD>>
  monthly_profit[t] = monthly_revenue[t] - monthly_costs[t]
  
  // Constraint: Must reach profitability within 12 months
  constraint profitability_deadline {
    monthly_profit[12] > $0
      with severity(warning)
      with message("Not profitable by month 12")
  }
}
```

## Common Type Errors and Fixes

### Error 1: Missing Units

```pel
// ❌ Wrong
param growth_rate: Fraction = 0.10

// ✅ Correct
param growth_rate: Rate per Month = 0.10 / 1mo
```

### Error 2: Incompatible Time Units

```pel
// ❌ Wrong
var result = (0.10 / 1mo) * 5wk  // Rate per Month × weeks?

// ✅ Correct (convert durations)
var weeks_in_months: Fraction = 5wk / 1mo  // ~1.15
var result = (0.10 / 1mo) * weeks_in_months * 1mo  // Dimensionless
```

### Error 3: Missing Time Index

```pel
// ❌ Wrong
var revenue: Currency<USD> = customers * arpu  // Which time step?

// ✅ Correct
var revenue: TimeSeries<Currency<USD>>
revenue[t] = customers[t] * arpu
```

## Quiz: Test Your Understanding

1. **What's wrong with this code?**
   ```pel
   var total = $100 + 0.10
   ```
   <details>
   <summary>Answer</summary>
   Cannot add Currency and Fraction (dimensionless). Must be: `$100 + ($100 * 0.10)` or `$100 * (1 + 0.10)`.
   </details>

2. **What's the result type?**
   ```pel
   var result = (0.05 / 1mo) * 12mo
   ```
   <details>
   <summary>Answer</summary>
   `Fraction` (dimensionless). The months cancel out: (1/month) × months = 1.
   </details>

3. **Fix this code:**
   ```pel
   param price: Currency<USD> = $50
   param growth_rate: Rate per Month = 0.10 / 1mo
   var new_price = price * growth_rate  // Error!
   ```
   <details>
   <summary>Answer</summary>
   ```pel
   var new_price = price * (1 + growth_rate * 1mo)
   ```
   Or define a monthly increment:
   ```pel
   var monthly_increase: Currency<USD> = price * (growth_rate * 1mo)
   var new_price = price + monthly_increase
   ```
   </details>

## Advanced Type System Topics

### Multi-Currency Operations

When working with multiple currencies, PEL prevents accidental mixing:

```pel
model GlobalBusiness {
  param usd_revenue: Currency<USD> = $500_000 {
    source: "us_division",
    method: "observed",
    confidence: 0.95
  }
  
  param eur_revenue: Currency<EUR> = €400_000 {
    source: "eu_division",
    method: "observed",
    confidence: 0.95
  }
  
  // ❌ ERROR: Cannot add different currencies directly
  // var total = usd_revenue + eur_revenue
  
  // ✅ Future: Explicit conversion (when currency conversion feature ships)
  /*
  param usd_eur_rate: Fraction = 1.08 {
    source: "forex_api",
    method: "observed",
    confidence: 0.99,
    notes: "Exchange rate as of 2026-02-19"
  }
  
  var eur_in_usd: Currency<USD> = convert(eur_revenue, EUR->USD, usd_eur_rate)
  var total_usd: Currency<USD> = usd_revenue + eur_in_usd
  */
  
  // ✅ Current workaround: Manual conversion with clear provenance
  var eur_revenue_in_usd: Currency<USD> = $432_000 {
    source: "manual_conversion",
    method: "derived",
    confidence: 0.90,
    notes: "€400,000 × 1.08 exchange rate (2026-02-19)"
  }
  
  var total_revenue: Currency<USD> = usd_revenue + eur_revenue_in_usd
}
```

**Best practice**: Always document exchange rates and conversion dates in provenance.

### Compound Units and Dimensional Analysis

PEL supports complex dimensional analysis:

```pel
model DimensionalAnalysis {
  // Power consumption: kWh per month
  param server_power: Fraction = 500.0 {  // kWh
    source: "datacenter_metrics",
    method: "observed",
    confidence: 0.90,
    notes: "Average kWh per month per server"
  }
  
  // Cost per unit: USD per kWh  
  param electricity_rate: Currency<USD> = $0.12 {  // $/kWh
    source: "utility_bill",
    method: "observed",
    confidence: 0.99
  }
  
  // Dimensional analysis: kWh × ($/kWh) = $
  var monthly_power_cost: Currency<USD> = server_power * electricity_rate
  // Result: 500 × $0.12 = $60
  
  // Server count
  param server_count: Fraction = 200.0 {
    source: "infrastructure",
    method: "observed",
    confidence: 1.0
  }
  
  // Total cost: $ × count = $
  var total_monthly_power_cost: Currency<USD> = monthly_power_cost * server_count
  // Result: $60 × 200 = $12,000
}
```

### Working with Percentages and Basis Points

```pel
model PercentagesExample {
  param base_price: Currency<USD> = $1000 {
    source: "pricing",
    method: "observed",
    confidence: 1.0
  }
  
  // Percentage as Fraction (0-1)
  param discount_rate: Fraction = 0.15 {  // 15%
    source: "promotion",
    method: "assumption",
    confidence: 1.0
  }
  
  // Calculate discount amount
  var discount_amount: Currency<USD> = base_price * discount_rate
  // Result: $1000 × 0.15 = $150
  
  var final_price: Currency<USD> = base_price - discount_amount
  // Result: $1000 - $150 = $850
  
  // Alternative: Direct calculation
  var final_price_alt: Currency<USD> = base_price * (1 - discount_rate)
  // Result: $1000 × 0.85 = $850
  
  // Basis points (1 bp = 0.01% = 0.0001)
  param credit_spread_bps: Fraction = 0.0250 {  // 250 basis points = 2.5%
    source: "bond_market",
    method: "observed",
    confidence: 0.95,
    notes: "Corporate credit spread over risk-free rate"
  }
  
  param loan_amount: Currency<USD> = $10_000_000 {
    source: "credit_agreement",
    method: "observed",
    confidence: 1.0
  }
  
  var annual_credit_cost: Currency<USD> = loan_amount * credit_spread_bps
  // Result: $10M × 0.025 = $250,000/year
}
```

### Duration Arithmetic and Calendar Effects

```pel
model DurationCalculations {
  // Different duration units
  param sprint_length: Duration = 2wk {
    source: "agile_process",
    method: "assumption",
    confidence: 1.0
  }
  
  param project_duration: Duration = 6mo {
    source: "project_plan",
    method: "assumption",
    confidence: 0.70
  }
  
  // Convert to common unit for comparison
  var project_weeks: Duration = project_duration  // Implicit conversion
  
  // Calculate number of sprints
  var sprint_count: Fraction = project_duration / sprint_length
  // Result: ~13 sprints (6 months ≈ 26 weeks ÷ 2 weeks/sprint)
  
  // Duration addition
  var extended_timeline: Duration = project_duration + 4wk
  // Result: ~6.93 months
  
  // Working with annual periods
  param annual_revenue: Currency<USD> = $1_200_000 {
    source: "finance",
    method: "observed",
    confidence: 0.95
  }
  
  var monthly_revenue: Currency<USD> = annual_revenue / 12.0
  // Note: Dividing by 12 converts annual to monthly
  // Result: $100,000/month
  
  // Calendar quirks: Month != 30 days
  // PEL uses: 1mo ≈ 30.44 days (average including leap years)
  var days_in_6mo: Fraction = (6mo / 1day)
  // Result: ~182.64 days (not 180)
}
```

### Type Inference and Explicit Typing

```pel
model TypeInference {
  // Explicit types (recommended for clarity)
  param price: Currency<USD> = $100 {
    source: "pricing_table",
    method: "observed",
    confidence: 1.0
  }
  
  param quantity: Fraction = 10.0 {
    source: "order",
    method: "observed",
    confidence: 1.0
  }
  
  // Type inference: result type inferred from operands
  var total = price * quantity
  // Inferred type: Currency<USD> (because USD × dimensionless = USD)
  
  // Explicit type annotation (catches errors)
  var total_explicit: Currency<USD> = price * quantity
  // Same as above, but type mismatch would fail compilation
  
  // Type inference with rates
  param growth: Rate per Month = 0.10 / 1mo {
    source: "forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  var growth_factor = 1 + growth
  // Inferred type: Dimensionless (1 + rate_per_month gets normalized)
  
  var new_price = price * growth_factor
  // Inferred type: Currency<USD>
}
```

## Troubleshooting Type Errors

### Error: "Cannot add incompatible types"

**Problem**:
```pel
var result = $100 + 0.15  // ERROR
```

**Error message**:
```
Type error: Cannot add Currency<USD> to Fraction
  Left operand:  Currency<USD> ($100)
  Right operand: Fraction (0.15)
  Suggestion: Did you mean $100 * (1 + 0.15)?
```

**Solutions**:

```pel
// ✅ Option 1: Percentage increase
var result = $100 * (1 + 0.15)  // $115

// ✅ Option 2: Absolute addition
var result = $100 + ($100 * 0.15)  // $115

// ✅ Option 3: Extract increment
var increment: Currency<USD> = $100 * 0.15
var result = $100 + increment  // $115
```

### Error: "Rate missing time unit"

**Problem**:
```pel
param growth_rate: Rate per Month = 0.15  // ERROR
```

**Error message**:
```
Type error: Rate requires explicit time unit
  Expected: Rate per Month
  Got: Fraction (dimensionless)
  Fix: Use 0.15 / 1mo
```

**Solution**:
```pel
// ✅ Correct
param growth_rate: Rate per Month = 0.15 / 1mo
```

### Error: "Time index out of bounds"

**Problem**:
```pel
var moving_avg[t] = (revenue[t] + revenue[t-1] + revenue[t-2]) / 3.0
// ERROR at t=0: revenue[-2] doesn't exist
```

**Error message**:
```
Runtime error: Time index out of bounds
  Variable: revenue[t-2]
  Time step: t=0
  Index: -2 (negative index invalid)
```

**Solutions**:

```pel
// ✅ Option 1: Conditional guard
var moving_avg: TimeSeries<Currency<USD>>
moving_avg[t] = if t < 2
                  then revenue[t]  // Use current value for first 2 steps
                  else (revenue[t] + revenue[t-1] + revenue[t-2]) / 3.0

// ✅ Option 2: Explicit initial values
var moving_avg: TimeSeries<Currency<USD>>
moving_avg[0] = revenue[0]
moving_avg[1] = (revenue[0] + revenue[1]) / 2.0
moving_avg[t] = (revenue[t] + revenue[t-1] + revenue[t-2]) / 3.0  // t >= 2
```

### Error: "Circular dependency detected"

**Problem**:
```pel
var revenue[t] = customers[t] * avg_revenue_per_customer[t]
var avg_revenue_per_customer[t] = revenue[t] / customers[t]  // ERROR: Circular!
```

**Error message**:
```
Compilation error: Circular dependency detected
  revenue[t] depends on avg_revenue_per_customer[t]
  avg_revenue_per_customer[t] depends on revenue[t]
  
  Dependency cycle: revenue -> avg_revenue_per_customer -> revenue
```

**Solution**:
```pel
// ✅ Define ARPU as independent parameter
param arpu: Currency<USD> = $100 {
  source: "billing_analysis",
  method: "observed",
  confidence: 0.95
}

var revenue[t] = customers[t] * arpu

// Or if ARPU changes over time, define its evolution independently
var arpu: TimeSeries<Currency<USD>>
arpu[0] = $100
arpu[t+1] = arpu[t] * (1 + price_growth_rate)

var revenue[t] = customers[t] * arpu[t]
```

### Warning: "Implicit unit conversion may lose precision"

**Problem**:
```pel
param weeks: Duration = 7.5wk
param months: Duration = 3mo

var total = weeks + months
```

**Warning message**:
```
Warning: Duration arithmetic with different units
  7.5wk + 3mo may lose precision
  Internally: 52.5 days + 91.32 days = 143.82 days
  Consider: Convert to common unit explicitly
```

**Best practice**:
```pel
// ✅ Explicit conversion
var weeks_duration: Duration = 7.5wk
var months_duration: Duration = 3mo

// Convert to days for clarity
var total_days: Fraction = (weeks_duration / 1day) + (months_duration / 1day)
// Or just accept the automatic conversion
var total_duration: Duration = weeks_duration + months_duration
```

## Performance Considerations

### Type Checking is Compile-Time

**Good news**: Type checking happens at compilation, not runtime.

```pel
// This model compiles once
model PerformanceExample {
  param initial: Currency<USD> = $1000
  param rate: Rate per Month = 0.10 / 1mo
  
  var revenue: TimeSeries<Currency<USD>>
  revenue[0] = initial
  revenue[t+1] = revenue[t] * (1 + rate)
  
  // Type checking happens here ⬆ (compile time)
}
```

```bash
# Compilation: type checking happens here (once)
pel compile model.pel -o model.ir.json  # ~0.1 seconds

# Execution: no type checking overhead (just arithmetic)
pel run model.ir.json --mode deterministic  # ~0.01 seconds
pel run model.ir.json --mode monte_carlo --samples 10000  # ~2 seconds
```

**Impact**: Type safety has **zero runtime cost**.

### Avoiding Unnecessary Conversions

```pel
// ❌ Inefficient: Repeated conversions
var result[t] = (revenue[t] / 1mo) * (1mo / 1day) * 30.44

// ✅ Efficient: Pre-calculate conversion factor
param days_per_month: Fraction = 30.44
var daily_revenue[t] = revenue[t] / days_per_month
```

## Real-World Case Studies

### Case Study 1: SaaS Revenue Model with Multiple Currencies

**Scenario**: Company operates in US (USD), EU (EUR), and UK (GBP).

```pel
model MultiCurrencySaaS {
  // Revenue by region (different currencies)
  param us_mrr: Currency<USD> = $500_000 {
    source: "stripe_us",
    method: "observed",
    confidence: 0.99
  }
  
  param eu_mrr: Currency<EUR> = €350_000 {
    source: "stripe_eu",
    method: "observed",
    confidence: 0.99
  }
  
  param uk_mrr: Currency<GBP> = £280_000 {
    source: "stripe_uk",
    method: "observed",
    confidence: 0.99
  }
  
  // Exchange rates (to USD)
  param eur_to_usd: Fraction = 1.08 {
    source: "forex_api",
    method: "observed",
    confidence: 0.98,
    notes: "ECB reference rate 2026-02-19"
  }
  
  param gbp_to_usd: Fraction = 1.27 {
    source: "forex_api",
    method: "observed",
    confidence: 0.98,
    notes: "BoE reference rate 2026-02-19"
  }
  
  // Convert all to USD for consolidated reporting
  var eu_mrr_usd: Currency<USD> = $378_000 {
    source: "manual_conversion",
    method: "derived",
    confidence: 0.95,
    notes: "€350K × 1.08"
  }
  
  var uk_mrr_usd: Currency<USD> = $355_600 {
    source: "manual_conversion",
    method: "derived",
    confidence: 0.95,
    notes: "£280K × 1.27"
  }
  
  // Total MRR in USD
  var total_mrr_usd: Currency<USD> = us_mrr + eu_mrr_usd + uk_mrr_usd
  // Result: $1,233,600
  
  // Growth rates by region (dimensionless)
  param us_growth: Rate per Month = 0.12 / 1mo
  param eu_growth: Rate per Month = 0.18 / 1mo
  param uk_growth: Rate per Month = 0.08 / 1mo
  
  // Time series forecast (in USD)
  var us_mrr_ts: TimeSeries<Currency<USD>>
  us_mrr_ts[0] = us_mrr
  us_mrr_ts[t+1] = us_mrr_ts[t] * (1 + us_growth)
  
  var eu_mrr_usd_ts: TimeSeries<Currency<USD>>
  eu_mrr_usd_ts[0] = eu_mrr_usd
  eu_mrr_usd_ts[t+1] = eu_mrr_usd_ts[t] * (1 + eu_growth)
  
  var uk_mrr_usd_ts: TimeSeries<Currency<USD>>
  uk_mrr_usd_ts[0] = uk_mrr_usd
  uk_mrr_usd_ts[t+1] = uk_mrr_usd_ts[t] * (1 + uk_growth)
  
  var total_mrr_ts: TimeSeries<Currency<USD>>
  total_mrr_ts[t] = us_mrr_ts[t] + eu_mrr_usd_ts[t] + uk_mrr_usd_ts[t]
}
```

### Case Study 2: Blended Metrics (Weighted Averages)

**Scenario**: Calculate blended customer acquisition cost across channels.

```pel
model BlendedCAC {
  // Channel-specific metrics
  param organic_customers: Fraction = 500.0 {
    source: "analytics",
    method: "observed",
    confidence: 0.99
  }
  
  param paid_search_customers: Fraction = 200.0 {
    source: "analytics",
    method: "observed",
    confidence: 0.99
  }
  
  param paid_social_customers: Fraction = 150.0 {
    source: "analytics",
    method: "observed",
    confidence: 0.99
  }
  
  // CAC by channel
  param organic_cac: Currency<USD> = $50 {
    source: "marketing",
    method: "derived",
    confidence: 0.85,
    notes: "Content + SEO costs amortized"
  }
  
  param paid_search_cac: Currency<USD> = $450 {
    source: "google_ads",
    method: "observed",
    confidence: 0.95
  }
  
  param paid_social_cac: Currency<USD> = $380 {
    source: "facebook_ads",
    method: "observed",
    confidence: 0.95
  }
  
  // Total customers
  var total_customers: Fraction = 
    organic_customers + paid_search_customers + paid_social_customers
  // Result: 850
  
  // Weighted average CAC
  var total_acquisition_cost: Currency<USD> =
    (organic_customers * organic_cac) +
    (paid_search_customers * paid_search_cac) +
    (paid_social_customers * paid_social_cac)
  // Result: $25,000 + $90,000 + $57,000 = $172,000
  
  var blended_cac: Currency<USD> = total_acquisition_cost / total_customers
  // Result: $172,000 / 850 = $202.35
  
  // Channel mix (for reporting)
  var organic_mix: Fraction = organic_customers / total_customers
  // Result: 58.8%
  
  var paid_search_mix: Fraction = paid_search_customers / total_customers
  // Result: 23.5%
  
  var paid_social_mix: Fraction = paid_social_customers / total_customers
  // Result: 17.6%
}
```

## Type System Reference

### Complete Type Hierarchy

```
Type
├── Scalar
│   ├── Currency<C>
│   │   ├── Currency<USD>
│   │   ├── Currency<EUR>
│   │   ├── Currency<GBP>
│   │   └── ... (ISO 4217 codes)
│   ├── Duration
│   │   └── Units: mo, wk, day, yr
│   ├── Fraction (dimensionless, use for probabilities ∈ [0,1])
│   └── Rate per T
│       ├── Rate per Month
│       ├── Rate per Day
│       └── ... (any duration unit)
├── TimeSeries<T>
│   └── T can be any Scalar type
└── Distribution<T>
    ├── Normal<T>
    ├── Beta (Fraction [0,1])
    ├── LogNormal<T>
    └── Uniform<T>
```

### Type Compatibility Matrix

| Operation | Left Type | Right Type | Result Type | Valid? |
|-----------|-----------|------------|-------------|--------|
| `+` | `Currency<USD>` | `Currency<USD>` | `Currency<USD>` | ✅ |
| `+` | `Currency<USD>` | `Currency<EUR>` | N/A | ❌ |
| `+` | `Currency<USD>` | `Fraction` | N/A | ❌ |
| `*` | `Currency<USD>` | `Fraction` | `Currency<USD>` | ✅ |
| `*` | `Fraction` | `Fraction` | `Fraction` | ✅ |
| `/` | `Currency<USD>` | `Fraction` | `Currency<USD>` | ✅ |
| `/` | `Currency<USD>` | `Currency<USD>` | `Fraction` | ✅ |
| `/` | `Duration` | `Duration` | `Fraction` | ✅ |
| `*` | `Rate per Month` | `Duration` | `Fraction` | ✅ |
| `+` | `Duration` | `Duration` | `Duration` | ✅ |
| `+` | `Fraction` | `Fraction` | N/A | ❌ (use formula) |

### Duration Unit Conversions

| From | To | Factor |
|------|----|----|
| 1 year | months | 12 |
| 1 year | weeks | 52.18 |
| 1 year | days | 365.25 |
| 1 month | weeks | 4.35 |
| 1 month | days | 30.44 |
| 1 week | days | 7 |

**Note**: PEL uses average values to handle calendar irregularities (leap years, month lengths).

## Practice Exercises

### Exercise 1: Unit Economics

Calculate LTV and payback period:

```pel
model Exercise1 {
  param monthly_subscription: Currency<USD> = $99 {
    source: "pricing",
    method: "observed",
    confidence: 1.0
  }
  
  param monthly_churn_rate: Fraction = 0.05 {
    source: "analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  param customer_acquisition_cost: Currency<USD> = $450 {
    source: "marketing",
    method: "derived",
    confidence: 0.70
  }
  
  // TODO: Calculate LTV (hint: subscription / churn_rate)
  var ltv: Currency<USD> = ???
  
  // TODO: Calculate LTV:CAC ratio
  var ltv_cac_ratio: Fraction = ???
  
  // TODO: Calculate payback period in months (hint: CAC / monthly_subscription)
  var payback_months: Fraction = ???
}
```

<details>
<summary>Solution</summary>

```pel
var ltv: Currency<USD> = monthly_subscription / monthly_churn_rate
// Result: $99 / 0.05 = $1,980

var ltv_cac_ratio: Fraction = ltv / customer_acquisition_cost
// Result: $1,980 / $450 = 4.4

var payback_months: Fraction = customer_acquisition_cost / monthly_subscription
// Result: $450 / $99 = 4.5 months
```
</details>

### Exercise 2: Time-Series Growth

Model compounding growth with churn:

```pel
model Exercise2 {
  param initial_customers: Fraction = 1000.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_growth_rate: Rate per Month = 0.20 / 1mo {
    source: "forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  param monthly_churn_rate: Fraction = 0.05 {
    source: "analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  var customers: TimeSeries<Fraction>
  
  // TODO: Set initial condition
  customers[???] = ???
  
  // TODO: Define recurrence (growth - churn)
  customers[???] = customers[???] * (1 + ??? - ???)
}
```

<details>
<summary>Solution</summary>

```pel
var customers: TimeSeries<Fraction>
customers[0] = initial_customers

customers[t+1] = customers[t] * (1 + monthly_growth_rate - monthly_churn_rate)
// Net growth: 20% - 5% = 15% per month
// Month 1: 1000 × 1.15 = 1150
// Month 2: 1150 × 1.15 = 1322.5
```
</details>

### Exercise 3: Multi-Currency Consolidation

Convert and sum revenues from different regions:

```pel
model Exercise3 {
  param us_revenue: Currency<USD> = $1_000_000 {
    source: "us_finance",
    method: "observed",
    confidence: 0.99
  }
  
  param japan_revenue_jpy: Fraction = 120_000_000 {  // JPY
    source: "japan_finance",
    method: "observed",
    confidence: 0.99,
    notes: "¥120M"
  }
  
  param jpy_to_usd_rate: Fraction = 0.0067 {
    source: "forex",
    method: "observed",
    confidence: 0.98,
    notes: "1 JPY = $0.0067 USD"
  }
  
  // TODO: Convert JPY to USD
  var japan_revenue_usd: Currency<USD> = ???
  
  // TODO: Calculate total
  var total_revenue_usd: Currency<USD> = ???
}
```

<details>
<summary>Solution</summary>

```pel
var japan_revenue_usd: Currency<USD> = $(japan_revenue_jpy * jpy_to_usd_rate) {
  source: "manual_conversion",
  method: "derived",
  confidence: 0.95,
  notes: "¥120M × 0.0067 = $804,000"
}
// Explicit amount: $804_000

var total_revenue_usd: Currency<USD> = us_revenue + japan_revenue_usd
// Result: $1,000,000 + $804,000 = $1,804,000
```
</details>

## Key Takeaways

1. **Types prevent bugs**: Unit mismatches caught at compile time, not runtime
2. **Self-documenting**: `Currency<USD>` is clearer than `float`
3. **Rates need time units**: Always use `/ 1mo`, `/ 1yr`, etc.
4. **Time series need indices**: Use `[t]`, `[0]`, `[t+1]` syntax
5. **Probabilities are fractions**: Range [0, 1], dimensionless
6. **Type checking is free**: Zero runtime performance cost
7. **Multi-currency requires conversion**: Document exchange rates in provenance
8. **Duration arithmetic is calendar-aware**: 1mo ≈ 30.44 days (average)

## Next Steps

- **Tutorial 3**: Learn how to model uncertainty with distributions (`Normal`, `Beta`, `LogNormal`)
- **Tutorial 6**: Deep dive into time-series modeling patterns
- **Reference**: See [Type System](../../spec/pel_type_system.md) and [Language Spec](../../spec/pel_language_spec.md) for complete type system specification

## Additional Resources

- [Type System Specification](../../spec/pel_type_system.md)
- [Language Specification (Types Section)](../../spec/pel_language_spec.md#3-type-system)
- [Examples](../../examples/)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
