# Tutorial 7: Stdlib Functions & Modules

## Overview

PEL's **Standard Library (PEL-STD)** provides battle-tested, reusable economic modeling components. Instead of reinventing common patterns (LTV calculations, churn models, cash flow waterfalls), you can use pre-built, validated functions that:

- **Are type-safe**: Dimensionally correct
- **Include provenance**: Explicit assumptions
- **Pass conformance tests**: Validated against real-world data
- **Compose cleanly**: Work together seamlessly

**Time required**: 25 minutes  
**Prerequisites**: Tutorials 1-6  
**Learning outcomes**: 
- Understand stdlib module organization
- Use unit economics functions (LTV, CAC, ratios)
- Apply retention and churn models
- Leverage cash flow and capacity planning
- Compose stdlib functions into full models

## Stdlib Modules Overview

| Module | Purpose | Status |
|--------|---------|--------|
| `unit_econ/` | LTV, CAC, payback, SaaS metrics | ✅ Implemented |
| `retention/` | Churn, cohort analysis, NDR | ✅ Implemented |
| `cashflow/` | AR/AP, burn rate, runway | ✅ Implemented |
| `capacity/` | Utilization, bottlenecks | ✅ Implemented |
| `hiring/` | Headcount, ramps, attrition | ✅ Implemented |
| `funnel/` | Conversion funnels | ✅ Implemented |
| `demand/` | Forecasting, seasonality | 🔜 Planned |
| `pricing/` | Elasticity, willingness-to-pay | 🔜 Planned |
| `shocks/` | Recession, disruptions | 🔜 Planned |

## Module 1: Unit Economics

### Core Functions

```pel
// 1. Simple LTV (infinite horizon)
ltv_simple(arpu: Currency<USD> per Month, churn: Rate per Month) -> Currency<USD>

// 2. Discounted LTV (with time value of money)
ltv_with_discount(
  arpu: Currency<USD> per Month,
  churn: Rate per Month,
  discount_rate: Rate per Month
) -> Currency<USD>

// 3. Payback period (months to recover CAC)
payback_period(
  cac: Currency<USD> per Customer,
  monthly_margin: Currency<USD> per Month
) -> Duration<Month>

// 4. LTV:CAC ratio
ltv_to_cac_ratio(ltv: Currency<USD> per Customer, cac: Currency<USD> per Customer) -> Fraction

// 5. SaaS Magic Number (sales efficiency)
magic_number(
  net_new_arr_this_quarter: Currency<USD> per Quarter,
  sales_marketing_spend_last_quarter: Currency<USD> per Quarter
) -> Fraction

// 6. Rule of 40 (growth + profitability)
rule_of_40(
  revenue_growth_rate: Rate per Year,
  profit_margin: Fraction
) -> Fraction
```

### Example: SaaS Unit Economics Model

```pel
model SaasUnitEconomics {
  // --- Input Parameters ---
  
  param monthly_arpu: Currency<USD> per Month = $125 / 1mo {
    source: "billing_system",
    method: "observed",
    confidence: 0.95,
    notes: "Average revenue per user from Stripe (last 90 days)"
  }
  
  param monthly_churn: Rate per Month = 0.05 / 1mo {
    source: "analytics",
    method: "fitted",
    confidence: 0.80,
    notes: "Fitted from 14 months of churn data"
  }
  
  param customer_acquisition_cost: Currency<USD> = $450 {
    source: "marketing",
    method: "derived",
    confidence: 0.70,
    notes: "Total marketing spend / new customers (Q4 2025)"
  }
  
  param gross_margin: Fraction = 0.75 {
    source: "finance",
    method: "observed",
    confidence: 0.90,
    notes: "Gross profit margin (COGS / Revenue)"
  }
  
  param discount_rate: Rate per Month = 0.01 / 1mo {
    source: "finance",
    method: "assumption",
    confidence: 0.80,
    notes: "12% annual discount rate (1% monthly)"
  }
  
  // --- Unit Economics Calculations ---
  
  // Simple LTV (no discounting)
  var ltv_simple_value: Currency<USD> 
    = ltv_simple(monthly_arpu, monthly_churn)
  // Result: $125 / 0.05 = $2,500
  
  // Discounted LTV (with time value of money)
  var ltv_with_discount_value: Currency<USD>
    = ltv_with_discount(monthly_arpu, monthly_churn, discount_rate)
  // Result: ~$1,875 (lower due to discounting)
  
  // Monthly margin (ARPU × gross margin)
  var monthly_margin: Currency<USD> per Month
    = monthly_arpu * gross_margin
  // Result: $125 × 0.75 = $93.75/mo
  
  // Payback period
  var payback_months: Duration
    = payback_period(customer_acquisition_cost, monthly_margin)
  // Result: $450 / $93.75 = 4.8 months
  
  // LTV:CAC ratio
  var ltv_cac_ratio: Fraction
    = ltv_to_cac_ratio(ltv_simple_value, customer_acquisition_cost)
  // Result: $2,500 / $450 ≈ 5.6
  
  // --- Validation Constraints ---
  
  constraint healthy_ltv_cac {
    ltv_cac_ratio >= 3.0
      with severity(warning)
      with message("LTV:CAC ratio {ltv_cac_ratio} below healthy threshold (3.0)")
  }
  
  constraint acceptable_payback {
    payback_months <= 12mo
      with severity(warning)
      with message("Payback period {payback_months} exceeds 12 months")
  }
}
```

**Output**:
```json
{
  "ltv_simple_value": "$2,500",
  "ltv_with_discount_value": "$1,875",
  "payback_months": "4.8mo",
  "ltv_cac_ratio": 5.56,
  "constraints": {
    "healthy_ltv_cac": "PASS",
    "acceptable_payback": "PASS"
  }
}
```

## Module 2: Retention & Churn

### Core Functions

```pel
// 1. Cohort retention at time t
cohort_retention(
  initial_cohort_size: Fraction,
  churn_rate: Rate per Month,
  time: Duration
) -> Fraction

// 2. Net Dollar Retention (expansion - contraction - churn)
net_dollar_retention(
  starting_arr: Currency<USD>,
  expansion_arr: Currency<USD>,
  contraction_arr: Currency<USD>,
  churned_arr: Currency<USD>
) -> Fraction

// 3. Gross Dollar Retention (retention only, no expansion)
gross_dollar_retention(
  starting_arr: Currency<USD>,
  churned_arr: Currency<USD>,
  contracted_arr: Currency<USD>
) -> Fraction

// 4. Quick Ratio (growth efficiency)
quick_ratio(
  new_arr: Currency<USD>,
  expansion_arr: Currency<USD>,
  churned_arr: Currency<USD>,
  contraction_arr: Currency<USD>
) -> Fraction
```

### Example: Retention Analysis

```pel
model RetentionMetrics {
  // --- Cohort Data (Jan 2025 cohort) ---
  
  param initial_cohort: Fraction = 1000.0 {
    source: "crm",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_churn: Rate per Month = 0.05 / 1mo {
    source: "analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  // Retention at 12 months
  var retention_12mo: Fraction
    = cohort_retention(initial_cohort, monthly_churn, 12mo)
  // Result: 1000 × exp(-0.05 × 12) ≈ 549 customers (54.9% retained)
  
  // --- Revenue Retention (NDR/GDR) ---
  
  param starting_arr: Currency<USD> = $1_000_000 {
    source: "billing",
    method: "observed",
    confidence: 0.95
  }
  
  param expansion_arr: Currency<USD> = $150_000 {
    source: "billing",
    method: "observed",
    confidence: 0.90,
    notes: "Upsells and cross-sells"
  }
  
  param contraction_arr: Currency<USD> = $30_000 {
    source: "billing",
    method: "observed",
    confidence: 0.85,
    notes: "Downgrades"
  }
  
  param churned_arr: Currency<USD> = $80_000 {
    source: "billing",
    method: "observed",
    confidence: 0.90,
    notes: "Cancellations"
  }
  
  // Net Dollar Retention
  var ndr: Fraction
    = net_dollar_retention(starting_arr, expansion_arr, contraction_arr, churned_arr)
  // Result: ($1M + $150K - $30K - $80K) / $1M = 104% (good!)
  
  // Gross Dollar Retention
  var gdr: Fraction
    = gross_dollar_retention(starting_arr, churned_arr, contraction_arr)
  // Result: ($1M - $80K - $30K) / $1M = 89%
  
  // --- Validation ---
  
  constraint excellent_ndr {
    ndr >= 1.00
      with severity(warning)
      with message("NDR {ndr} below 100% - losing revenue from existing customers")
  }
}
```

## Module 3: Cash Flow

### Core Functions

```pel
// 1. Accounts Receivable balance
accounts_receivable(
  monthly_revenue: Currency<USD>,
  days_sales_outstanding: Duration,
  payment_terms: String
) -> Currency<USD>

// 2. Accounts Payable balance
accounts_payable(
  monthly_expenses: Currency<USD>,
  days_payable_outstanding: Duration
) -> Currency<USD>

// 3. Runway (months until cash runs out)
runway_months(
  current_cash: Currency<USD>,
  monthly_burn: Currency<USD> per Month
) -> Duration

// 4. Burn multiple (capital efficiency)
burn_multiple(
  net_burn: Currency<USD> per Month,
  net_new_arr: Currency<USD> per Month
) -> Fraction
```

### Example: Cash Flow Management

```pel
model CashFlowManagement {
  // --- Revenue & Expenses ---
  
  param monthly_revenue: Currency<USD> = $500_000 {
    source: "billing",
    method: "observed",
    confidence: 0.95
  }
  
  param monthly_expenses: Currency<USD> = $450_000 {
    source: "accounting",
    method: "observed",
    confidence: 0.90
  }
  
  // --- Timing Assumptions ---
  
  param dso: Duration = 45d {
    source: "ar_aging_report",
    method: "observed",
    confidence: 0.85,
    notes: "Days Sales Outstanding - average time to collect payment"
  }
  
  param dpo: Duration = 30d {
    source: "ap_aging_report",
    method: "observed",
    confidence: 0.85,
    notes: "Days Payable Outstanding - average time to pay vendors"
  }
  
  // --- Cash Flow Calculations ---
  
  var ar_balance: Currency<USD>
    = accounts_receivable(monthly_revenue, dso, "net_30")
  // Result: ~$750K (1.5 months of revenue tied up in AR)
  
  var ap_balance: Currency<USD>
    = accounts_payable(monthly_expenses, dpo)
  // Result: ~$450K (1 month of expenses in AP)
  
  var net_working_capital: Currency<USD>
    = ar_balance - ap_balance
  // Result: $300K (cash tied up in operations)
  
  // --- Liquidity Analysis ---
  
  param current_cash: Currency<USD> = $2_000_000 {
    source: "bank_account",
    method: "observed",
    confidence: 0.99
  }
  
  var monthly_burn: Currency<USD> per Month
    = (monthly_expenses - monthly_revenue) / 1mo
  // Result: -$50K/mo (profitable, not burning)
  
  var runway: Duration
    = runway_months(current_cash, monthly_burn)
  // Result: 40 months (no risk if profitable)
  
  // --- Constraints ---
  
  constraint minimum_runway {
    runway >= 12mo
      with severity(warning)
      with message("Runway {runway} below 12 months")
  }
}
```

## Module 4: Capacity Planning

### Core Functions

```pel
// 1. Utilization rate
calculate_utilization(
  current_demand: Rate per Month,
  total_capacity: Rate per Month
) -> Fraction

// 2. Capacity gap
capacity_gap(
  projected_demand: Rate per Month,
  current_capacity: Rate per Month
) -> Rate per Month

// 3. Required capacity (accounting for efficiency)
required_capacity(
  demand: Rate per Month,
  unit_capacity: Rate per Month,
  efficiency: Fraction
) -> Fraction
```

### Example: Infrastructure Capacity

```pel
model InfrastructureCapacity {
  // --- Current State ---
  
  param current_requests: Rate per Month = 1_800_000_000 / 1mo {
    source: "monitoring",
    method: "observed",
    confidence: 0.98
  }
  
  param server_count: Fraction = 500.0 {
    source: "infrastructure_team",
    method: "observed",
    confidence: 1.0
  }
  
  param requests_per_server: Rate per Month = 5_000_000 / 1mo {
    source: "vendor_specs",
    method: "observed",
    confidence: 0.95
  }
  
  param server_efficiency: Fraction = 0.80 {
    source: "ops_metrics",
    method: "derived",
    confidence: 0.92,
    notes: "Average efficiency accounting for downtime, overhead"
  }
  
  // --- Capacity Analysis ---
  
  var total_capacity: Rate per Month
    = server_count * requests_per_server * server_efficiency
  // Result: 500 × 5M × 0.8 = 2B requests/mo
  
  var current_utilization: Fraction
    = calculate_utilization(current_requests, total_capacity)
  // Result: 1.8B / 2B = 90% (high utilization!)
  
  // --- Growth Planning ---
  
  param projected_requests: Rate per Month = 2_500_000_000 / 1mo {
    source: "growth_forecast",
    method: "assumption",
    confidence: 0.75
  }
  
  var shortfall: Rate per Month
    = capacity_gap(projected_requests, total_capacity)
  // Result: 2.5B - 2B = 500M requests/mo gap
  
  var additional_servers_needed: Fraction
    = required_capacity(shortfall, requests_per_server, server_efficiency)
  // Result: 500M / (5M × 0.8) ≈ 125 servers
  
  // --- Constraints ---
  
  constraint utilization_limit {
    current_utilization <= 0.85
      with severity(warning)
      with message("Utilization {current_utilization} exceeds safe threshold (85%)")
  }
}
```

## Module 5: Hiring & Headcount

### Core Functions

```pel
// 1. Hiring funnel (multi-stage conversion)
hiring_funnel(
  applicants: Count<Applicant>,
  stage_conversion_rates: Array<Fraction>
) -> Count<Person>

// 2. Ramp curve (new hire productivity)
ramp_curve(
  time_since_hire: Duration,
  ramp_duration: Duration,
  shape: String  // "linear", "s_curve", "exponential"
) -> Fraction

// 3. Effective headcount (accounting for ramps)
effective_headcount(
  total_headcount: Count<Person>,
  avg_tenure: Duration,
  ramp_duration: Duration
) -> Count<Person>
```

### Example: Engineering Team Growth

```pel
model EngineeringHiring {
  // --- Hiring Funnel ---
  
  param monthly_applicants: Count<Applicant> = 200 {
    source: "greenhouse_ats",
    method: "observed",
    confidence: 0.90
  }
  
  // Conversion rates: screening → phone → onsite → offer → accept
  param funnel_stages: Array<Fraction> = [0.40, 0.50, 0.60, 0.80] {
    source: "recruiting_analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  var monthly_hires: Count<Person>
    = hiring_funnel(monthly_applicants, funnel_stages)
  // Result: 200 × 0.4 × 0.5 × 0.6 × 0.8 = 19.2 hires/month
  
  // --- Ramp Modeling ---
  
  param engineering_ramp_time: Duration = 3mo {
    source: "hiring_manager",
    method: "expert_estimate",
    confidence: 0.70,
    notes: "Time to full productivity for engineers"
  }
  
  var productivity_at_1mo: Fraction
    = ramp_curve(1mo, engineering_ramp_time, "linear")
  // Result: 1mo / 3mo = 33% productive
  
  var productivity_at_3mo: Fraction
    = ramp_curve(3mo, engineering_ramp_time, "linear")
  // Result: 100% productive
  
  // --- Effective Headcount ---
  
  param total_engineers: Count<Person> = 50 {
    source: "hr_system",
    method: "observed",
    confidence: 1.0
  }
  
  param avg_tenure: Duration = 18mo {
    source: "hr_analytics",
    method: "fitted",
    confidence: 0.80
  }
  
  var effective_engineers: Fraction
    = effective_headcount(total_engineers, avg_tenure, engineering_ramp_time)
  // Result: ~47 FTE (accounting for ramps)
}
```

## Composing Stdlib Functions

Real models combine multiple stdlib modules:

```pel
model FullBusinessModel {
  // --- Unit Economics (from unit_econ/) ---
  var ltv = ltv_simple(arpu, churn)
  var ltv_cac = ltv_to_cac_ratio(ltv, cac)
  
  // --- Retention (from retention/) ---
  var ndr = net_dollar_retention(starting_arr, expansion, contraction, churned)
  
  // --- Cash Flow (from cashflow/) ---
  var runway = runway_months(current_cash, monthly_burn)
  
  // --- Capacity (from capacity/) ---
  var utilization = calculate_utilization(demand, capacity)
  
  // --- Hiring (from hiring/) ---
  var new_hires = hiring_funnel(applicants, conversion_rates)
  
  // --- Constraints across modules ---
  constraint healthy_business {
    ltv_cac >= 3.0 &&
    ndr >= 1.00 &&
    runway >= 12mo &&
    utilization <= 0.85
      with severity(warning)
      with message("Business health check failed")
  }
}
```

## Quiz: Test Your Understanding

1. **What's the formula for simple LTV?**
   <details>
   <summary>Answer</summary>
   `LTV = ARPU / Churn Rate`
   
   Example: $100/mo ARPU, 5% monthly churn → LTV = $100 / 0.05 = $2,000
   </details>

2. **What's a healthy LTV:CAC ratio?**
   <details>
   <summary>Answer</summary>
   Generally 3:1 or higher. Below 3:1 indicates high customer acquisition costs relative to lifetime value.
   </details>

3. **What does NDR > 100% mean?**
   <details>
   <summary>Answer</summary>
   Net Dollar Retention above 100% means existing customers are expanding faster than they're churning - you're growing revenue even without new customers.
   </details>

4. **Why use `ltv_with_discount` instead of `ltv_simple`?**
   <details>
   <summary>Answer</summary>
   To account for time value of money - a dollar today is worth more than a dollar in 2 years. Discounted LTV is more conservative and financially accurate.
   </details>

## Best Practices

### ✅ Do This

1. **Use stdlib functions for standard calculations**
   ```pel
   var ltv = ltv_simple(arpu, churn)  // ✅ Use stdlib
   ```
   
   Instead of:
   ```pel
   var ltv = arpu / churn  // ❌ Reimplementing stdlib (error-prone)
   ```

2. **Compose functions for complex models**
   ```pel
   var effective_capacity = total_capacity * efficiency
   var utilization = calculate_utilization(demand, effective_capacity)
   ```

3. **Add constraints for validation**
   ```pel
   constraint healthy_metrics {
     ltv_cac >= 3.0 && payback_months <= 12mo
   }
   ```

### ❌ Avoid This

1. **Don't reinvent stdlib functions**
   ```pel
   // ❌ Reimplementing payback_period
   var payback = cac / monthly_margin
   
   // ✅ Use stdlib
   var payback = payback_period(cac, monthly_margin)
   ```

2. **Don't skip validation**
   ```pel
   var ltv_cac_ratio = ltv / cac  // ❌ No validation
   
   // ✅ Add constraints
   constraint healthy_ratio {
     ltv_cac_ratio >= 3.0 with severity(warning)
   }
   ```

## Complete Stdlib Reference

### `unit_econ` Module (Detailed)

#### `ltv(arpu, churn_rate, margin)`

Calculates customer lifetime value.

**Formula**: `LTV = (ARPU × margin) / churn_rate`

**Parameters**:
- `arpu: Currency<C>` - Average revenue per user (monthly or annual)
- `churn_rate: Fraction` - Monthly churn rate (0-1)
- `margin: Fraction` - Gross margin (0-1)

**Returns**: `Currency<C>`

**Example**:
```pel
var customer_ltv = ltv(
  arpu: $99,
  churn_rate: 0.05,
  margin: 0.70
)
// Result: ($99 × 0.70) / 0.05 = $1,386
```

**Edge cases**:
- `churn_rate = 0` → ERROR (division by zero)
- `churn_rate < 0 or > 1` → ERROR (invalid probability)
- `margin < 0 or > 1` → ERROR (invalid probability)

#### `cac(marketing_spend, sales_spend, new_customers)`

Calculates customer acquisition cost.

**Formula**: `CAC = (marketing + sales) / customers`

**Parameters**:
- `marketing_spend: Currency<C>`
- `sales_spend: Currency<C>`
- `new_customers: Fraction`

**Returns**: `Currency<C>`

**Example**:
```pel
var acquisition_cost = cac(
  marketing_spend: $50_000,
  sales_spend: $30_000,
  new_customers: 200.0
)
// Result: ($50K + $30K) / 200 = $400
```

#### `payback_period(cac, monthly_margin)`

Months to recover customer acquisition cost.

**Formula**: `Payback = CAC / monthly_margin`

**Parameters**:
- `cac: Currency<C>`
- `monthly_margin: Currency<C>` - Monthly profit per customer

**Returns**: `Fraction` (months)

**Example**:
```pel
var payback_months = payback_period(
  cac: $600,
  monthly_margin: $50
)
// Result: $600 / $50 = 12 months
```

### `retention` Module (Detailed)

#### `cohort_retention(initial_size, retention_rates)`

Tracks cohort size over time.

**Parameters**:
- `initial_size: Fraction` - Starting cohort size
- `retention_rates: List<Fraction>` - Retention rate for each period

**Returns**: `TimeSeries<Fraction>`

**Example**:
```pel
var cohort = cohort_retention(
  initial_size: 1000.0,
  retention_rates: [1.0, 0.60, 0.40, 0.30, 0.25]
)
// cohort[0] = 1000, cohort[1] = 600, cohort[2] = 400, ...
```

#### `nrr(starting_mrr, expansion, contraction, churn)`

Net Revenue Retention.

**Formula**: `NRR = (starting + expansion - contraction - churn) / starting`

**Parameters**:
- `starting_mrr: Currency<C>`
- `expansion: Currency<C>` - Upsells, cross-sells
- `contraction: Currency<C>` - Downgrades
- `churn: Currency<C>` - Churned revenue

**Returns**: `Fraction` (typically 0.7 - 1.3)

**Example**:
```pel
var net_retention = nrr(
  starting_mrr: $1_000_000,
  expansion: $150_000,
  contraction: $50_000,
  churn: $80_000
)
// Result: (1M + 150K - 50K - 80K) / 1M = 1.02 (102%)
```

### `cashflow` Module (Detailed)

#### `fcf(operating_income, capex, change_in_nwc)`

Free Cash Flow calculation.

**Formula**: `FCF = operating_income - capex - Δ(NWC)`

**Parameters**:
- `operating_income: Currency<C>` - EBITDA or operating profit
- `capex: Currency<C>` - Capital expenditures
- `change_in_nwc: Currency<C>` - Change in net working capital

**Returns**: `Currency<C>`

**Example**:
```pel
var free_cash_flow = fcf(
  operating_income: $500_000,
  capex: $100_000,
  change_in_nwc: -$20_000  // Negative = cash inflow
)
// Result: $500K - $100K - (-$20K) = $420K
```

#### `npv(cash_flows, discount_rate)`

Net Present Value.

**Formula**: `NPV = Σ(CF_t / (1 + r)^t)`

**Parameters**:
- `cash_flows: List<Currency<C>>` - Cash flow each period
- `discount_rate: Fraction` - Annual discount rate

**Returns**: `Currency<C>`

**Example**:
```pel
var project_npv = npv(
  cash_flows: [-$1_000_000, $300_000, $400_000, $500_000],
  discount_rate: 0.10
)
// NPV = -1M + 300K/1.1 + 400K/1.1² + 500K/1.1³
//     = -1M + 272.7K + 330.6K + 375.7K = -$21K (reject project)
```

### `capacity` Module (Detailed)

#### `server_capacity(requests_per_second, servers, capacity_per_server)`

Infrastructure capacity planning.

**Parameters**:
- `requests_per_second: Fraction`
- `servers: Fraction`
- `capacity_per_server: Fraction` - RPS per server

**Returns**: `Fraction` (utilization, 0-1)

**Example**:
```pel
var utilization = server_capacity(
  requests_per_second: 15_000,
  servers: 20.0,
  capacity_per_server: 1_000
)
// Utilization = 15,000 / (20 × 1,000) = 0.75 (75%)

constraint capacity_headroom {
  utilization <= 0.80  // Keep below 80% for safety
    with severity(warning)
}
```

### `hiring` Module (Detailed)

#### `hiring_plan(current_headcount, growth_rate, attrition_rate)`

Calculates required hiring to achieve growth targets.

**Parameters**:
- `current_headcount: Fraction`
- `growth_rate: Rate per Month` - Desired headcount growth
- `attrition_rate: Fraction` - Monthly attrition rate

**Returns**: `Fraction` (hires per month)

**Example**:
```pel
var monthly_hires = hiring_plan(
  current_headcount: 100.0,
  growth_rate: 0.10 / 1mo,  // Grow 10% per month
  attrition_rate: 0.02  // 2% monthly attrition
)
// Hires = 100 × (0.10 + 0.02) = 12 hires/month
```

### `funnel` Module (Detailed)

#### `conversion_funnel(visitors, stages, conversion_rates)`

Multi-stage conversion funnel.

**Parameters**:
- `visitors: Fraction` - Top-of-funnel traffic
- `stages: List<String>` - Stage names (for reporting)
- `conversion_rates: List<Fraction>` - Conversion rate at each stage

**Returns**: `List<Fraction>` - Count at each stage

**Example**:
```pel
var funnel_counts = conversion_funnel(
  visitors: 10_000,
  stages: ["Visit", "Signup", "Trial", "Paid"],
  conversion_rates: [1.0, 0.15, 0.40, 0.25]
)
// Result: [10000, 1500, 600, 150]
// Visit: 10,000
// Signup: 10,000 × 0.15 = 1,500
// Trial: 1,500 × 0.40 = 600
// Paid: 600 × 0.25 = 150
```

## Advanced Stdlib Patterns

### Composing Multiple Modules

```pel
model IntegratedModel {
  // Marketing metrics
  param monthly_visitors: Fraction = 50_000
  var funnel = conversion_funnel(
    visitors: monthly_visitors,
    stages: ["Visit", "Signup", "Paid"],
    conversion_rates: [1.0, 0.10, 0.20]
  )
  var new_customers: Fraction = funnel[2]  // Paid customers
  
  // Unit economics
  param marketing_spend: Currency<USD> = $50_000
  var customer_cac = cac(
    marketing_spend: marketing_spend,
    sales_spend: $0,
    new_customers: new_customers
  )
  
  param arpu: Currency<USD> = $99
  param churn: Fraction = 0.05
  param margin: Fraction = 0.70
  
  var customer_ltv = ltv(
    arpu: arpu,
    churn_rate: churn,
    margin: margin
  )
  
  var ltv_cac_ratio = customer_ltv / customer_cac
  
  // Constraint: LTV:CAC must be ≥ 3:1
  constraint unit_economics {
    ltv_cac_ratio >= 3.0
      with severity(warning)
      with message("LTV:CAC is {ltv_cac_ratio}, below 3:1")
  }
  
  // Cash flow
  var revenue: TimeSeries<Currency<USD>>
  var operating_expenses: TimeSeries<Currency<USD>>
  var free_cash_flow: TimeSeries<Currency<USD>>
  
  revenue[t] = total_customers[t] * arpu
  operating_expenses[t] = marketing_spend + $100_000  // COGS + fixed costs
  
  free_cash_flow[t] = fcf(
    operating_income: revenue[t] - operating_expenses[t],
    capex: $20_000,
    change_in_nwc: $0
  )
  
  // Capacity planning
  var api_rps: Fraction = total_customers[t] * 2.0  // 2 RPS per customer
  var server_util = server_capacity(
    requests_per_second: api_rps,
    servers: 50.0,
    capacity_per_server: 1_000
  )
  
  constraint infrastructure_headroom {
    server_util <= 0.75
      with severity(warning)
      with message("Server utilization {server_util} too high")
  }
}
```

### Custom Stdlib Extensions

When stdlib doesn't have what you need, build on top:

```pel
// Custom: Magic Number (Rule of 40)
function rule_of_40(
  arr: Currency<USD>,
  arr_last_year: Currency<USD>,
  net_income: Currency<USD>
) -> Fraction {
  var growth_rate = (arr - arr_last_year) / arr_last_year
  var profit_margin = net_income / arr
  return growth_rate + profit_margin
}

model SaaSMetrics {
  var arr: TimeSeries<Currency<USD>>
  var net_income: TimeSeries<Currency<USD>>
  
  var rule_of_40_score: TimeSeries<Fraction>
  rule_of_40_score[t] = if t >= 12
    then rule_of_40(
      arr: arr[t],
      arr_last_year: arr[t-12],
      net_income: net_income[t]
    )
    else 0.0
  
  constraint healthy_saas {
    rule_of_40_score[t] >= 0.40
      with severity(warning)
  }
}
```

### Time-Series Stdlib Functions

Some stdlib functions return time series:

```pel
model TimeSeriesStdlib {
  // Cohort retention over time
  var retention_curve = cohort_retention(
    initial_size: 1000.0,
    retention_rates: [1.0, 0.60, 0.40, 0.30, 0.25, 0.22]
  )
  
  // retention_curve is a TimeSeries<Fraction>
  // retention_curve[0] = 1000
  // retention_curve[1] = 600
  // retention_curve[2] = 400
  // ...
  
  // Can use in further calculations
  var monthly_revenue: TimeSeries<Currency<USD>>
  monthly_revenue[t] = retention_curve[t] * $99
  
  // Can apply constraints
  constraint min_cohort_size {
    retention_curve[t] >= 200.0
      with severity(warning)
      with message("Cohort dropped below 200 at t={t}")
  }
}
```

## Testing Stdlib Functions

### Unit Tests for Stdlib Calls

```pel
// tests/stdlib_unit_economics_test.pel
model TestLTV {
  // Known-good test case
  var result = ltv(
    arpu: $100,
    churn_rate: 0.05,
    margin: 0.70
  )
  
  constraint test_ltv_calculation {
    result == $1_400  // ($100 × 0.70) / 0.05 = $1,400
      with severity(fatal)
      with message("LTV calculation failed: expected $1,400, got {result}")
  }
}

model TestPayback {
  var payback = payback_period(
    cac: $600,
    monthly_margin: $50
  )
  
  constraint test_payback_period {
    payback == 12.0  // $600 / $50 = 12 months
      with severity(fatal)
  }
}
```

Run tests:
```bash
pel compile tests/stdlib_*.pel -o stdlib_tests.ir.json
pel run stdlib_tests.ir.json --mode deterministic || exit 1
echo "All stdlib tests passed"
```

### Regression Tests

```bash
# Save expected outputs
pel run model.pel --mode deterministic > expected_output.json
git add expected_output.json
git commit -m "Baseline outputs"

# Later: Verify outputs haven't changed
pel run model.pel --mode deterministic > actual_output.json
diff expected_output.json actual_output.json || {
  echo "ERROR: Model outputs changed unexpectedly"
  exit 1
}
```

## Stdlib Performance Characteristics

### Computational Complexity

| Function | Complexity | Notes |
|----------|------------|-------|
| `ltv()` | O(1) | Simple arithmetic |
| `cac()` | O(1) | Simple arithmetic |
| `payback_period()` | O(1) | Simple division |
| `npv()` | O(n) | n = length of cash_flows list |
| `cohort_retention()` | O(n) | n = number of periods |
| `conversion_funnel()` | O(k) | k = number of stages |
| `fcf()` | O(1) | Simple arithmetic |

**Recommendation**: All stdlib functions are fast; no performance concerns for typical models (<10,000 time steps).

### Memory Usage

Time-series stdlib functions allocate memory for results:

```pel
// Memory = sizeof(Fraction) × time_horizon
var cohort = cohort_retention(
  initial_size: 1000.0,
  retention_rates: [1.0, 0.60, ...]  // 120 periods
)
// Memory: ~960 bytes (8 bytes/value × 120)
```

**Rule of thumb**: 1,000 time steps ≈ 8 KB per time series.

## Practice Exercises

### Exercise 1: Calculate Rule of 40

Given:
- ARR (t=12): $5M
- ARR (t=0): $3M
- Net income (t=12): $500K

**Task**: Calculate Rule of 40 score using LTV.

```pel
model Exercise1 {
  param arr_t12: Currency<USD> = $5_000_000
  param arr_t0: Currency<USD> = $3_000_000
  param net_income: Currency<USD> = $500_000
  
  // TODO: Calculate growth rate and profit margin
  var growth_rate: Fraction = ???
  var profit_margin: Fraction = ???
  var rule_of_40: Fraction = ???
}
```

<details>
<summary>Solution</summary>

```pel
var growth_rate: Fraction = (arr_t12 - arr_t0) / arr_t0
// (5M - 3M) / 3M = 0.667 (66.7%)

var profit_margin: Fraction = net_income / arr_t12
// 500K / 5M = 0.10 (10%)

var rule_of_40: Fraction = growth_rate + profit_margin
// 0.667 + 0.10 = 0.767 (76.7%) ✅ Above 40%
```
</details>

### Exercise 2: Multi-Stage Funnel Optimization

Optimize funnel to achieve 500 paid customers:

```pel
model Exercise2 {
  param target_customers: Fraction = 500.0
  param visitor_to_signup: Fraction = 0.12
  param signup_to_trial: Fraction = 0.35
  param trial_to_paid: Fraction = 0.22
  
  // TODO: Calculate required visitors
  var required_visitors: Fraction = ???
}
```

<details>
<summary>Solution</summary>

```pel
// Work backwards from target
var overall_conversion = visitor_to_signup * signup_to_trial * trial_to_paid
// 0.12 × 0.35 × 0.22 = 0.00924 (0.924%)

var required_visitors: Fraction = target_customers / overall_conversion
// 500 / 0.00924 = 54,113 visitors needed

// Verify with funnel
var funnel = conversion_funnel(
  visitors: required_visitors,
  stages: ["Visit", "Signup", "Trial", "Paid"],
  conversion_rates: [1.0, 0.12, 0.35, 0.22]
)
// funnel[3] ≈ 500 ✅
```
</details>

## Key Takeaways

1. **Stdlib provides 6 core modules**: unit_econ, retention, cashflow, capacity, hiring, funnel
2. **Functions are type-safe**: Dimensionally correct, validated
3. **Compose for complex models**: Combine multiple stdlib modules
4. **Add constraints**: Validate stdlib outputs against thresholds
5. **Import syntax coming**: Currently use direct function calls

## Next Steps

- **Tutorial 8**: Calibration - fit stdlib parameters to real data
- **Tutorial 9**: Migration from Spreadsheets - convert Excel models using stdlib
- **Reference**: See `/stdlib/README.md` for complete function reference

## Additional Resources

- [Stdlib Reference](../../stdlib/README.md)
- [Stdlib Source Code](../../stdlib/) (see implementation details)
- [Contributing a Stdlib Module](../../CONTRIBUTING.md#stdlib-contributions)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
