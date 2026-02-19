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

## Advanced Time-Series Patterns

### Multi-Variable Dependencies

Complex models have multiple time series that depend on each other:

```pel
model SaaSEcosystem {
  // Inputs
  param initial_customers: Fraction = 1000.0
  param monthly_growth_rate: Rate per Month = 0.15 / 1mo
  param monthly_churn_rate: Probability = 0.05
  param avg_revenue_per_user: Currency<USD> = $99
  
  // Time series 1: Customers
  var customers: TimeSeries<Fraction>
  customers[0] = initial_customers
  customers[t+1] = customers[t] * (1 + monthly_growth_rate - monthly_churn_rate)
  
  // Time series 2: Revenue (depends on customers)
  var revenue: TimeSeries<Currency<USD>>
  revenue[t] = customers[t] * avg_revenue_per_user
  
  // Time series 3: Costs (depends on revenue)
  var costs: TimeSeries<Currency<USD>>
  costs[t] = $50_000 + (0.30 * revenue[t])  // Fixed + variable
  
  // Time series 4: Cash (depends on revenue and costs)
  var cash_balance: TimeSeries<Currency<USD>>
  cash_balance[0] = $500_000
  cash_balance[t+1] = cash_balance[t] + revenue[t] - costs[t]
  
  // Time series 5: Runway (depends on cash and costs)
  var runway: TimeSeries<Duration>
  runway[t] = (cash_balance[t] / costs[t]) * 1mo
}
```

**Execution order**: PEL automatically determines correct evaluation order using dependency graph.

### Moving Averages and Smoothing

```pel
model MovingAverages {
  var daily_sales: TimeSeries<Currency<USD>>
  // ... populate daily_sales ...
  
  // 7-day moving average
  var sales_ma7: TimeSeries<Currency<USD>>
  sales_ma7[t] = if t < 6
    then daily_sales[t]  // Not enough history yet
    else (
      daily_sales[t] + daily_sales[t-1] + daily_sales[t-2] +
      daily_sales[t-3] + daily_sales[t-4] + daily_sales[t-5] +
      daily_sales[t-6]
    ) / 7.0
  
  // Exponential moving average (EMA)
  var sales_ema: TimeSeries<Currency<USD>>
  param alpha: Fraction = 0.3  // Smoothing factor
  sales_ema[0] = daily_sales[0]
  sales_ema[t+1] = alpha * daily_sales[t+1] + (1 - alpha) * sales_ema[t]
}
```

### Seasonal Patterns

```pel
model SeasonalRevenue {
  param base_revenue: Currency<USD> = $100_000 / 1mo
  
  // Monthly seasonality factors (retail example)
  param seasonality: List<Fraction> = [
    0.80,  // Jan (post-holiday slump)
    0.85,  // Feb
    0.95,  // Mar
    1.00,  // Apr
    1.05,  // May
    1.10,  // Jun
    1.05,  // Jul
    1.00,  // Aug
    0.95,  // Sep
    1.00,  // Oct
    1.10,  // Nov (pre-holiday)
    1.40   // Dec (holiday peak)
  ]
  
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = base_revenue * seasonality[t % 12]
  // Uses modulo to cycle through 12-month pattern
}
```

### Cohort-Based Modeling

```pel
model CohortRetention {
  // Track users by acquisition month
  var cohort_size: TimeSeries<Fraction>
  param monthly_new_users: Fraction = 1000.0
  
  cohort_size[t] = monthly_new_users  // New cohort each month
  
  // Retention curve: percentage of cohort still active after k months
  param retention_curve: List<Probability> = [
    1.00,  // Month 0 (100% active)
    0.60,  // Month 1 (60% retained)
    0.40,  // Month 2
    0.30,  // Month 3
    0.25,  // Month 4
    0.22,  // Month 5+
  ]
  
  // Active users at time t = sum of all cohorts, weighted by retention
  var active_users: TimeSeries<Fraction>
  active_users[t] = sum(
    cohort_size[t-k] * retention_curve[min(k, 5)]
    for k in 0..t
  )
}
```

### State Transitions (Markov Chains)

```pel
model CustomerStates {
  // State: Trial, Active, Churned
  var trial: TimeSeries<Fraction>
  var active: TimeSeries<Fraction>
  var churned: TimeSeries<Fraction>
  
  // Initial state
  trial[0] = 1000.0
  active[0] = 5000.0
  churned[0] = 0.0
  
  // Transition probabilities
  param trial_to_active: Probability = 0.40
  param trial_to_churned: Probability = 0.60
  param active_to_churned: Probability = 0.05
  
  // State transitions
  trial[t+1] = 1000.0  // New trials each month
  
  active[t+1] = active[t] * (1 - active_to_churned) + 
                trial[t] * trial_to_active
  
  churned[t+1] = churned[t] + 
                 trial[t] * trial_to_churned + 
                 active[t] * active_to_churned
  
  // Validation: total should be conserved
  constraint conservation {
    trial[t] + active[t] + churned[t] == 
    trial[0] + active[0] + churned[0] + 1000.0 * t
      with severity(fatal)
  }
}
```

## Performance Optimization

### Limiting Time Horizon

```pel
model PerformanceAware {
  // ❌ Expensive: 120-month forecast
  var revenue: TimeSeries<Currency<USD>>[0..119]
  
  // ✅ Efficient: 36-month forecast (3 years)
  var revenue: TimeSeries<Currency<USD>>[0..35]
  
  // Tradeoff: Longer horizons = more execution time
  // Rule of thumb: Use minimum horizon needed for decision
}
```

### Sparse Time Series

```pel
model QuarterlyReporting {
  // Only compute quarterly values, not monthly
  var quarterly_revenue: TimeSeries<Currency<USD>>
  
  quarterly_revenue[t] = if (t % 3 == 0)
    then compute_revenue(t)  // Only quarters
    else $0  // Skip off-quarter months
}
```

### Memoization (Avoiding Recomputation)

```pel
model Memoization {
  // ❌ Inefficient: Recomputes sum each time
  var cumulative_revenue: TimeSeries<Currency<USD>>
  cumulative_revenue[t] = sum(revenue[k] for k in 0..t)
  // O(t²) complexity!
  
  // ✅ Efficient: Incremental update
  var cumulative_revenue: TimeSeries<Currency<USD>>
  cumulative_revenue[0] = revenue[0]
  cumulative_revenue[t+1] = cumulative_revenue[t] + revenue[t+1]
  // O(t) complexity
}
```

## Debugging Time-Series Models

### Tracing Execution

```bash
# Enable detailed tracing
pel run model.ir.json --mode deterministic --trace revenue,customers,costs
```

Output:
```
t=0:  revenue=$100K, customers=1000, costs=$80K
t=1:  revenue=$115K (+15%), customers=1150 (+15%), costs=$84.5K (+5.6%)
t=2:  revenue=$132K (+15%), customers=1322 (+15%), costs=$89.6K (+6.0%)
...
```

### Plotting Time Series

```python
import json
import matplotlib.pyplot as plt

with open('results.json') as f:
    data = json.load(f)

# Extract time series
revenue = data['variables']['revenue']['time_series']
costs = data['variables']['costs']['time_series']

t = list(range(len(revenue)))

plt.figure(figsize=(10, 6))
plt.plot(t, revenue, label='Revenue', linewidth=2)
plt.plot(t, costs, label='Costs', linewidth=2)
plt.fill_between(t, 0, revenue, alpha=0.2)
plt.xlabel('Month')
plt.ylabel('USD')
plt.title('Revenue vs Costs Over Time')
plt.legend()
plt.grid(True)
plt.savefig('revenue_vs_costs.png')
```

### Identifying Divergence

```pel
model DivergenceDetection {
  var x: TimeSeries<Fraction>
  x[0] = 1.0
  x[t+1] = x[t] * 1.10  // 10% growth
  
  // Constraint: Detect if growth becomes unbounded
  constraint no_divergence {
    x[t] <= 1_000_000.0
      with severity(warning)
      with message("x[{t}] = {x[t]} is growing unbounded")
  }
}
```

## Real-World Case Studies

### Case Study 1: Supply Chain Inventory

```pel
model InventoryManagement {
  // Input parameters
  param daily_demand_mean: Fraction = 100.0
  param daily_demand_std: Fraction = 20.0
  param lead_time: Duration = 7day
  param reorder_point: Fraction = 800.0
  param reorder_quantity: Fraction = 1000.0
  
  // Time series
  var demand: TimeSeries<Fraction>
  demand[t] = ~Normal(μ=daily_demand_mean, σ=daily_demand_std)
  
  var orders_placed: TimeSeries<Fraction>
  var orders_arriving: TimeSeries<Fraction>
  var inventory: TimeSeries<Fraction>
  
  // Initial inventory
  inventory[0] = 2000.0
  
  // Ordering logic
  orders_placed[t] = if inventory[t] < reorder_point
    then reorder_quantity
    else 0.0
  
  // Orders arrive after lead time
  orders_arriving[t] = if t >= 7
    then orders_placed[t-7]
    else 0.0
  
  // Inventory evolution
  inventory[t+1] = max(0.0, inventory[t] - demand[t] + orders_arriving[t])
  
  // Service level: avoid stockouts
  var stockout: TimeSeries<Bool>
  stockout[t] = inventory[t] < demand[t]
  
  var service_level: Fraction = 
    (1.0 - sum(stockout[t] for t in 0..365) / 365.0)
  
  constraint target_service_level {
    service_level >= 0.95
      with severity(warning)
      with message("Service level {service_level} below 95% target")
  }
}
```

### Case Study 2: Workforce Planning

```pel
model WorkforcePlanning {
  var headcount: TimeSeries<Fraction>
  var hiring: TimeSeries<Fraction>
  var attrition: TimeSeries<Fraction>
  var capacity: TimeSeries<Fraction>
  var revenue_capacity: TimeSeries<Currency<USD>>
  
  param avg_attrition_rate: Probability = 0.10 / 12.0  // Annual → monthly
  param revenue_per_employee: Currency<USD> = $150_000 / 12.0
  param hiring_ramp_time: Duration = 3mo
  
  // Initialize
  headcount[0] = 100.0
  
  // Attrition: lose some employees each month
  attrition[t] = headcount[t] * avg_attrition_rate
  
  // Hiring plan: grow 10% per quarter
  hiring[t] = if (t % 3 == 0) 
    then headcount[t] * 0.10
    else 0.0
  
  // Headcount evolution
  headcount[t+1] = headcount[t] + hiring[t] - attrition[t]
  
  // Capacity: new hires take 3 months to be fully productive
  var productive_headcount: TimeSeries<Fraction>
  productive_headcount[t] = headcount[t] - (
    if t >= 3 then 0.0
    else if t >= 2 then 0.33 * hiring[t-2]
    else if t >= 1 then 0.67 * hiring[t-1]
    else hiring[t]
  )
  
  // Revenue capacity
  revenue_capacity[t] = productive_headcount[t] * revenue_per_employee
}
```

## Practice Exercises

### Exercise 1: Compound Growth with Cap

Model customer growth with 15% monthly growth, capped at 10,000 customers:

```pel
model Exercise1 {
  var customers: TimeSeries<Fraction>
  customers[0] = 1000.0
  
  // TODO: Add recurrence with growth cap
  customers[t+1] = ???
}
```

<details>
<summary>Solution</summary>

```pel
customers[t+1] = min(10_000.0, customers[t] * 1.15)
// Grows 15% per month until hitting 10K cap
```
</details>

### Exercise 2: Revenue with Expansion

Model revenue where existing customers expand 5% per year:

```pel
model Exercise2 {
  var customers: TimeSeries<Fraction>
  var arpu: TimeSeries<Currency<USD>>  // Average revenue per user
  var revenue: TimeSeries<Currency<USD>>
  
  customers[0] = 1000.0
  customers[t+1] = customers[t] * 1.10  // 10% customer growth
  
  arpu[0] = $100
  // TODO: ARPU grows 5% annually (0.41% monthly)
  arpu[t+1] = ???
  
  revenue[t] = customers[t] * arpu[t]
}
```

<details>
<summary>Solution</summary>

```pel
arpu[t+1] = arpu[t] * 1.0041  // (1.05)^(1/12) ≈ 1.0041
// 5% annual growth = 0.41% monthly compound growth

// Alternative: Exact calculation
param annual_expansion: Fraction = 0.05
param monthly_expansion: Fraction = (1 + annual_expansion) ** (1/12) - 1
arpu[t+1] = arpu[t] * (1 + monthly_expansion)
```
</details>

### Exercise 3: Cash Runway Calculation

Calculate how many months of runway remain:

```pel
model Exercise3 {
  var cash: TimeSeries<Currency<USD>>
  var burn_rate: TimeSeries<Currency<USD>>
  var runway: TimeSeries<Duration>
  
  cash[0] = $500_000
  burn_rate[t] = $50_000 / 1mo  // Constant burn
  
  cash[t+1] = cash[t] - burn_rate[t]
  
  // TODO: Calculate runway (months until cash = 0)
  runway[t] = ???
}
```

<details>
<summary>Solution</summary>

```pel
runway[t] = (cash[t] / burn_rate[t]) * 1mo
// Example: $500K / $50K/mo = 10 months

// Alternative: Account for time passing
runway[t] = if cash[t] > $0
  then (cash[t] / burn_rate[t]) * 1mo
  else 0mo  // Out of cash
```
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
