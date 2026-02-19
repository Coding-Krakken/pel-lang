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
| **Rates** | Change over time | `Rate per Month`, `Probability` |
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
- `Probability`: Success rates, risk factors (dimensionless, 0-1)
- `Currency<USD> per Month`: Monthly recurring revenue (MRR)

## 3. Probability: A Special Rate

Probabilities are rates that represent likelihood:

```pel
model ProbabilityExample {
  // Probability is a Fraction constrained to [0, 1]
  param conversion_rate: Probability = 0.12 {
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
  
  param monthly_churn_rate: Probability = 0.05 {
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

## Key Takeaways

1. **Types prevent bugs**: Unit mismatches caught at compile time, not runtime
2. **Self-documenting**: `Currency<USD>` is clearer than `float`
3. **Rates need time units**: Always use `/ 1mo`, `/ 1yr`, etc.
4. **Time series need indices**: Use `[t]`, `[0]`, `[t+1]` syntax
5. **Probabilities are fractions**: Range [0, 1], dimensionless

## Next Steps

- **Tutorial 3**: Learn how to model uncertainty with distributions (`Normal`, `Beta`, `LogNormal`)
- **Tutorial 6**: Deep dive into time-series modeling patterns
- **Reference**: See `/docs/model/types.md` for complete type system specification

## Additional Resources

- [Type System Specification](/docs/model/types.md)
- [Unit Conversion Reference](/docs/model/units.md)
- [Common Type Errors](/docs/troubleshooting/type_errors.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
