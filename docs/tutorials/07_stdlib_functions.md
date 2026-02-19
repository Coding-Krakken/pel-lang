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
ltv_discounted(
  arpu: Currency<USD> per Month,
  churn: Rate per Month,
  discount_rate: Rate per Month
) -> Currency<USD>

// 3. Payback period (months to recover CAC)
payback_period(
  cac: Currency<USD>,
  monthly_margin: Currency<USD> per Month
) -> Duration

// 4. LTV:CAC ratio
ltv_to_cac_ratio(ltv: Currency<USD>, cac: Currency<USD>) -> Fraction

// 5. SaaS Magic Number (sales efficiency)
magic_number(
  net_new_arr: Currency<USD>,
  prior_quarter_sales_marketing: Currency<USD>
) -> Fraction

// 6. Rule of 40 (growth + profitability)
rule_of_40(
  revenue_growth_rate: Fraction,
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
  var ltv_discounted_value: Currency<USD>
    = ltv_discounted(monthly_arpu, monthly_churn, discount_rate)
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
  "ltv_discounted_value": "$1,875",
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
  net_burn: Currency<USD>,
  net_new_arr: Currency<USD>
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
  top_of_funnel: Fraction,
  stage_conversion_rates: Array<Probability>
) -> Fraction

// 2. Ramp curve (new hire productivity)
ramp_curve(
  time_since_hire: Duration,
  ramp_duration: Duration,
  shape: String  // "linear", "s_curve", "exponential"
) -> Fraction

// 3. Effective headcount (accounting for ramps)
effective_headcount(
  total_headcount: Fraction,
  avg_tenure: Duration,
  ramp_duration: Duration
) -> Fraction
```

### Example: Engineering Team Growth

```pel
model EngineeringHiring {
  // --- Hiring Funnel ---
  
  param monthly_applicants: Fraction = 200.0 {
    source: "greenhouse_ats",
    method: "observed",
    confidence: 0.90
  }
  
  // Conversion rates: screening → phone → onsite → offer → accept
  param funnel_stages: Array<Probability> = [0.40, 0.50, 0.60, 0.80] {
    source: "recruiting_analytics",
    method: "fitted",
    confidence: 0.75
  }
  
  var monthly_hires: Fraction
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
  
  param total_engineers: Fraction = 50.0 {
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

4. **Why use `ltv_discounted` instead of `ltv_simple`?**
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

- [Stdlib Reference](/stdlib/README.md)
- [Stdlib Source Code](/stdlib/) (see implementation details)
- [Contributing a Stdlib Module](/CONTRIBUTING.md#stdlib-contributions)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
