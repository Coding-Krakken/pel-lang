# Tutorial 6: Time-Series Modeling

## Overview

Most business models are **dynamic** - values change over time. Revenue grows, customers churn, cash balances fluctuate. PEL provides **time-series variables** that evolve through **recurrence relations** (formulas that describe how t+1 depends on t).

This tutorial covers:
- Time series syntax (`TimeSeries<T>`)
- Initial conditions (`var[0] = ...`)
- Recurrence relations (`var[t+1] = f(var[t])`)
- Lookback references (`var[t-1]`)
- Common time-series patterns
- Multi-step dependencies

**Time required**: 30 minutes  
**Prerequisites**: Tutorials 1-2  
**Learning outcomes**: 
- Model growth, decay, and accumulation
- Write recurrence relations
- debug time-series logic
- Understand execution semantics

## Why Time-Series Modeling?

### The Spreadsheet Approach: Manual Columns

Typical spreadsheet time series:

| Month | Revenue | Formula |
|-------|---------|---------|
| 0     | $10,000 | (input) |
| 1     | $11,500 | `=B2 * 1.15` |
| 2     | $13,225 | `=B3 * 1.15` |
| 3     | $15,209 | `=B4 * 1.15` |

**Problems**:
- Manual column dragging (error-prone)
- No formal recurrence relation (implicit in formulas)
- Hard to change logic (edit every cell)
- No validation (accidental formula edits)

### The PEL Approach: Declarative Recurrence

```pel
model RevenueGrowth {
  param initial_revenue: Currency<USD> = $10_000 {
    source: "current_metrics",
    method: "observed",
    confidence: 0.95
  }
  
  param growth_rate: Rate per Month = 0.15 / 1mo {
    source: "growth_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  // Time series: value at each time step
  var revenue: TimeSeries<Currency<USD>>
  
  // Initial condition (t=0)
  revenue[0] = initial_revenue
  
  // Recurrence relation (t ≥ 0)
  revenue[t+1] = revenue[t] * (1 + growth_rate)
}
```

**Benefits**:
- **Declarative**: Describe the pattern, not the steps
- **Validated**: Type-checked, constraints applied
- **Auditable**: Clear logic, provenance tracked
- **Extensible**: Change growth_rate → entire series recalculates

## Time-Series Syntax

### Declaration

```pel
var <name>: TimeSeries<<type>>
```

**Examples**:
```pel
var revenue: TimeSeries<Currency<USD>>
var customer_count: TimeSeries<Fraction>
var is_profitable: TimeSeries<Bool>
var monthly_growth_rate: TimeSeries<Rate per Month>
```

### Initial Condition: `var[0] = ...`

Every time series needs a **starting value**:

```pel
var cash_balance: TimeSeries<Currency<USD>>
cash_balance[0] = $100_000  // Starting cash
```

**Without initial condition** → Compile error:
```
Error: Time series 'cash_balance' missing initial condition (var[0] = ...)
```

### Recurrence Relation: `var[t+1] = f(var[t])`

Describes how the **next value** depends on the **current value** (and others):

```pel
var balance: TimeSeries<Currency<USD>>
balance[0] = $100_000
balance[t+1] = balance[t] + monthly_profit[t]
```

**Execution**:
```
t=0: balance[0] = $100,000 (initial)
t=1: balance[1] = balance[0] + monthly_profit[0] = $100,000 + $5,000 = $105,000
t=2: balance[2] = balance[1] + monthly_profit[1] = $105,000 + $5,200 = $110,200
...
```

## Common Time-Series Patterns

### Pattern 1: Growth (Compound)

**Business case**: Revenue, customers, users

```pel
model CompoundGrowth {
  param initial_value: Fraction = 1000.0 {
    source: "current_state",
    method: "observed",
    confidence: 0.99
  }
  
  param growth_rate: Rate per Month = 0.20 / 1mo {
    source: "growth_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  var value: TimeSeries<Fraction>
  value[0] = initial_value
  value[t+1] = value[t] * (1 + growth_rate)
  
  // Result: value[0]=1000, value[1]=1200, value[2]=1440, ...
}
```

**Formula**: $V_{t+1} = V_t \times (1 + r)$

### Pattern 2: Decay (Depreciation, Churn)

**Business case**: Asset value, customer retention

```pel
model CustomerRetention {
  param initial_customers: Fraction = 5000.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_churn: Probability = 0.05 {
    source: "analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] * (1 - monthly_churn)
  
  // Result: customers[0]=5000, customers[1]=4750, customers[2]=4512, ...
}
```

**Formula**: $C_{t+1} = C_t \times (1 - \text{churn})$

### Pattern 3: Accumulation (Integration)

**Business case**: Cash balance, inventory, total revenue

```pel
model CashAccumulation {
  param initial_cash: Currency<USD> = $250_000 {
    source: "bank_account",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_revenue: Currency<USD> = $50_000 {
    source: "revenue_forecast",
    method: "assumption",
    confidence: 0.70
  }
  
  param monthly_expenses: Currency<USD> = $40_000 {
    source: "budget",
    method: "assumption",
    confidence: 0.85
  }
  
  var cash_balance: TimeSeries<Currency<USD>>
  cash_balance[0] = initial_cash
  cash_balance[t+1] = cash_balance[t] + monthly_revenue - monthly_expenses
  
  // Result: cash_balance[0]=$250K, cash_balance[1]=$260K, cash_balance[2]=$270K, ...
}
```

**Formula**: $\text{Cash}_{t+1} = \text{Cash}_t + \text{Inflow} - \text{Outflow}$

### Pattern 4: Net Change (Growth + Churn)

**Business case**: Customer base with acquisition and churn

```pel
model CustomerDynamics {
  param initial_customers: Fraction = 1000.0 {
    source: "subscription_db",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_new_customers: Fraction = 200.0 {
    source: "sales_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  param monthly_churn_rate: Probability = 0.05 {
    source: "analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] + monthly_new_customers - (customers[t] * monthly_churn_rate)
  
  // Result: customers[0]=1000, customers[1]=1150 (1000 + 200 - 50), ...
}
```

**Formula**: $C_{t+1} = C_t + \text{New} - C_t \times \text{Churn}$

### Pattern 5: Lookback (Moving Average)

**Business case**: Smoothing, lagged effects

```pel
model MovingAverage {
  param initial_revenue: Currency<USD> = $100_000 {
    source: "billing",
    method: "observed",
    confidence: 0.95
  }
  
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[0] = initial_revenue
  monthly_revenue[t+1] = monthly_revenue[t] * (1 + growth_rate[t])
  
  // 3-month moving average (lookback)
  var revenue_ma3: TimeSeries<Currency<USD>>
  revenue_ma3[0] = monthly_revenue[0]
  revenue_ma3[1] = monthly_revenue[1]
  revenue_ma3[t] = (monthly_revenue[t] + monthly_revenue[t-1] + monthly_revenue[t-2]) / 3.0
  // Only valid for t ≥ 2
}
```

**Formula**: $\text{MA}_t = \frac{R_t + R_{t-1} + R_{t-2}}{3}$

### Pattern 6: Conditional Logic

**Business case**: Policy changes, phase transitions

```pel
model PricingStrategy {
  param initial_price: Currency<USD> = $50 {
    source: "product_team",
    method: "observed",
    confidence: 0.99
  }
  
  param price_increase_month: Fraction = 12.0 {
    source: "pricing_committee",
    method: "assumption",
    confidence: 0.80
  }
  
  var price: TimeSeries<Currency<USD>>
  price[0] = initial_price
  
  // Increase price by 20% at month 12, hold steady otherwise
  price[t+1] = if t + 1 >= price_increase_month
                 then price[t] * 1.20
                 else price[t]
  
  // Result: price[0-11]=$50, price[12+]=$60
}
```

## Multi-Variable Dependencies

Real models have multiple time series that depend on each other:

```pel
model SaasBusinessModel {
  // --- Parameters ---
  param initial_customers: Fraction = 500.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  param customer_growth_rate: Rate per Month = 0.15 / 1mo {
    source: "sales_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  param churn_rate: Probability = 0.05 {
    source: "analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  param arpu: Currency<USD> = $100 {
    source: "billing",
    method: "observed",
    confidence: 0.95
  }
  
  param cost_per_customer: Currency<USD> = $30 {
    source: "finance",
    method: "assumption",
    confidence: 0.70
  }
  
  // --- Time Series: Customer Count ---
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] * (1 + customer_growth_rate - churn_rate)
  
  // --- Time Series: Monthly Revenue ---
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = customers[t] * arpu
  
  // --- Time Series: Monthly Costs ---
  var monthly_costs: TimeSeries<Currency<USD>>
  monthly_costs[t] = customers[t] * cost_per_customer
  
  // --- Time Series: Profit ---
  var monthly_profit: TimeSeries<Currency<USD>>
  monthly_profit[t] = monthly_revenue[t] - monthly_costs[t]
  
  // --- Time Series: Cumulative Cash ---
  param initial_cash: Currency<USD> = $200_000 {
    source: "bank",
    method: "observed",
    confidence: 0.99
  }
  
  var cash_balance: TimeSeries<Currency<USD>>
  cash_balance[0] = initial_cash
  cash_balance[t+1] = cash_balance[t] + monthly_profit[t]
}
```

**Execution order**:
1. `customers[t]` (depends on `customers[t-1]`)
2. `monthly_revenue[t]` (depends on `customers[t]`)
3. `monthly_costs[t]` (depends on `customers[t]`)
4. `monthly_profit[t]` (depends on `monthly_revenue[t]`, `monthly_costs[t]`)
5. `cash_balance[t]` (depends on `cash_balance[t-1]`, `monthly_profit[t-1]`)

## Advanced Patterns

### Sigmoid Growth (S-Curve)

**Business case**: Market saturation, viral growth limits

```pel
model MarketPenetration {
  param market_size: Fraction = 100_000.0 {
    source: "market_research",
    method: "external_research",
    confidence: 0.65
  }
  
  param growth_rate: Rate per Month = 0.30 / 1mo {
    source: "assumption",
    method: "expert_estimate",
    confidence: 0.50
  }
  
  var customers: TimeSeries<Fraction>
  customers[0] = 100.0
  
  // Logistic growth: slows as market saturates
  var market_penetration: TimeSeries<Fraction>
  market_penetration[t] = customers[t] / market_size
  
  customers[t+1] = customers[t] + 
                   customers[t] * growth_rate * (1 - market_penetration[t])
  
  // Early: fast growth (low penetration)
  // Late: slow growth (high penetration)
}
```

### Seasonality

**Business case**: Retail, subscriptions with seasonal patterns

```pel
model SeasonalRevenue {
  param base_revenue: Currency<USD> = $100_000 {
    source: "finance",
    method: "observed",
    confidence: 0.90
  }
  
  // Holiday boost in Dec (month 11, 0-indexed)
  var seasonal_multiplier: TimeSeries<Fraction>
  seasonal_multiplier[t] = if (t % 12) == 11
                             then 1.50  // +50% in December
                             else 1.00
  
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = base_revenue * seasonal_multiplier[t]
}
```

### Feedback Loops

**Business case**: Viral growth (customers recruit customers)

```pel
model ViralGrowth {
  param initial_users: Fraction = 100.0 {
    source: "product_launch",
    method: "observed",
    confidence: 0.99
  }
  
  param viral_coefficient: Fraction = 1.2 {
    source: "product_analytics",
    method: "fitted",
    confidence: 0.60,
    notes: "Average invites per user that convert"
  }
  
  param cycle_time: Duration = 1mo {
    source: "assumption",
    method: "assumption",
    confidence: 0.70
  }
  
  var users: TimeSeries<Fraction>
  users[0] = initial_users
  
  // Each user recruits viral_coefficient new users
  var new_users_via_referral: TimeSeries<Fraction>
  new_users_via_referral[t] = users[t] * (viral_coefficient - 1.0)
  
  users[t+1] = users[t] + new_users_via_referral[t]
  
  // If viral_coefficient > 1.0: exponential growth
  // If viral_coefficient < 1.0: decay
  // If viral_coefficient = 1.0: linear growth
}
```

## Debugging Time-Series Models

### Problem: Unexpected Values

**Symptoms**: Revenue at month 6 is $0 (should be $150K)

**Debug steps**:

1. **Run deterministic mode with --debug**
   ```bash
   pel run model.ir.json --mode deterministic --debug -o debug.json
   ```

2. **Inspect time series values**
   ```json
   {
     "revenue": [
       {"t": 0, "value": 100000},
       {"t": 1, "value": 115000},
       ...
       {"t": 5, "value": 142000},
       {"t": 6, "value": 0}  // ❌ Problem here
     ]
   }
   ```

3. **Trace dependencies**
   Check what `revenue[6]` depends on:
   ```pel
   revenue[t] = customers[t] * arpu[t]
   ```
   
   Inspect `customers[6]` and `arpu[6]`:
   ```json
   {
     "customers": [{"t": 6, "value": 0}],  // ❌ Zero customers!
     "arpu": [{"t": 6, "value": 100}]
   }
   ```

4. **Find root cause**
   ```pel
   customers[t+1] = customers[t] * (1 + growth_rate - churn_rate)
   ```
   
   If `growth_rate - churn_rate = -1.0`, then `customers[t+1] = 0`.

5. **Fix**
   ```pel
   // Add constraint to catch this
   constraint positive_growth {
     growth_rate > churn_rate
       with severity(fatal)
       with message("Churn exceeds growth - customer base will collapse")
   }
   ```

### Problem: Circular Dependencies

**Symptoms**: Compile error: "Circular dependency detected"

```pel
// ❌ Wrong: A depends on B, B depends on A
var revenue[t] = customers[t] * price[t]
var customers[t] = revenue[t] / arpu  // ❌ Circular!
```

**Fix**: Break the cycle
```pel
// ✅ Correct: Independent definitions
var revenue[t] = customers[t] * price[t]
var arpu[t] = price[t]  // ARPU is just price (per-customer)
```

### Problem: Index Out of Bounds

**Symptoms**: Runtime error: "Index t-2 is negative"

```pel
// ❌ Wrong: Lookback 2 steps from t=0
var ma3[t] = (revenue[t] + revenue[t-1] + revenue[t-2]) / 3.0
// At t=0: revenue[-2] doesn't exist!
```

**Fix**: Guard with conditionals
```pel
// ✅ Correct: Handle early time steps
var ma3: TimeSeries<Currency<USD>>
ma3[0] = revenue[0]
ma3[1] = (revenue[0] + revenue[1]) / 2.0
ma3[t] = (revenue[t] + revenue[t-1] + revenue[t-2]) / 3.0  // t ≥ 2
```

Or use conditional:
```pel
var ma3[t] = if t < 2
               then revenue[t]
               else (revenue[t] + revenue[t-1] + revenue[t-2]) / 3.0
```

## Execution Semantics

### Time Step Ordering

PEL evaluates time series **forward in time**:

```
1. Compute all [0] initial conditions
2. For t = 0, 1, 2, ..., t_max:
   a. Evaluate all [t] expressions
   b. Evaluate all [t+1] recurrence relations
3. Return full time series
```

### Dependency Resolution

Within each time step, PEL evaluates in **dependency order**:

```pel
var revenue[t] = customers[t] * arpu
var profit[t] = revenue[t] - costs[t]
var cash[t+1] = cash[t] + profit[t]
```

**Execution at t=5**:
1. `customers[5]` (depends on `customers[4]`)
2. `revenue[5]` (depends on `customers[5]`)
3. `profit[5]` (depends on `revenue[5]`)
4. `cash[6]` (depends on `cash[5]`, `profit[5]`)

### Simulation Horizon

Default: 24 time steps (configurable)

```bash
pel run model.ir.json --mode deterministic --steps 36  # 36 months
```

## Quiz: Test Your Understanding

1. **What's wrong with this code?**
   ```pel
   var balance: TimeSeries<Currency<USD>>
   balance[t+1] = balance[t] + $1000
   ```
   <details>
   <summary>Answer</summary>
   Missing initial condition `balance[0] = ...`. Compiler will reject.
   </details>

2. **What does this model do?**
   ```pel
   var x[0] = 100.0
   x[t+1] = x[t] * 0.90
   ```
   <details>
   <summary>Answer</summary>
   Exponential decay: 10% reduction each time step. Models depreciation, churn, etc.
   </details>

3. **How do you reference "2 months ago"?**
   <details>
   <summary>Answer</summary>
   `var[t-2]` (lookback by 2). Must ensure `t ≥ 2` or use conditionals.
   </details>

4. **Can time series contain distributions?**
   <details>
   <summary>Answer</summary>
   Yes! Example:
   ```pel
   var revenue: TimeSeries<Currency<USD>>
   revenue[0] = $100_000
   revenue[t+1] = revenue[t] * (1 + ~Normal(μ=0.15, σ=0.05))
   ```
   Each time step samples a new growth rate.
   </details>

## Key Takeaways

1. **Time series are declared**: `var name: TimeSeries<Type>`
2. **Initial condition required**: `var[0] = ...`
3. **Recurrence relations**: `var[t+1] = f(var[t])`
4. **Lookback with `[t-k]`**: Reference previous values
5. **Dependencies auto-resolved**: PEL evaluates in correct order

## Next Steps

- **Tutorial 7**: Stdlib Functions & Modules - reusable time-series patterns
- **Tutorial 4**: Add constraints to time-series values
- **Reference**: See `/docs/model/time_series.md` for complete specification

## Additional Resources

- [Time-Series Specification](/docs/model/time_series.md)
- [Execution Model](/docs/runtime/execution.md)
- [Common Patterns Library](/docs/patterns/time_series_patterns.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
