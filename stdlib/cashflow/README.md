# Cashflow Module

Functions for cash flow timing, accounts receivable/payable, burn rate, and runway analysis.

## Key Functions

### AR/AP Management
- `days_sales_outstanding()` - Calculate DSO metric
- `days_payable_outstanding()` - Calculate DPO metric
- `accounts_receivable()` - AR balance calculation
- `accounts_payable()` - AP balance calculation
- `cash_conversion_cycle()` - CCC = DSO + Inventory Days - DPO

### Cash Analysis
- `cash_waterfall()` - Opening → ending cash balance
- `burn_rate()` - Monthly cash burn calculation
- `runway_months()` - Months until cash depletion
- `runway_to_target()` - Months to specific cash target

### Payroll Timing
- `payroll_timing_semi_monthly()` - Semi-monthly payroll schedule
- `payroll_timing_monthly()` - Monthly payroll schedule

### Working Capital
- `working_capital_change()` - Change in NWC
- `free_cash_flow()` - Operating CF - CapEx

## Example Usage

```pel
// Note: Import syntax is aspirational/future feature
// Currently use direct function calls

model SaaS_Cashflow {
  // Parameters
  param monthly_revenue: Currency<USD> = $100_000 {
    source: "stripe",
    method: "observed",
    confidence: 0.95
  }
  
  param dso: Duration<Day> = 45d {
    source: "ar_aging_report",
    method: "derived",
    confidence: 0.85
  }
  
  param monthly_opex: Currency<USD> = $80_000 {
    source: "budget",
    method: "assumption",
    confidence: 0.80
  }
  
  param current_cash: Currency<USD> = $500_000 {
    source: "bank_balance",
    method: "observed",
    confidence: 1.0
  }
  
  // Calculations
  var ar_balance: Currency<USD> = accounts_receivable(
    monthly_revenue,
    dso,
    30d  // Standard payment terms
  )
  
  var burn: Currency<USD> per Month = burn_rate(
    monthly_revenue,
    monthly_opex
  )
  
  var runway: Duration<Month> = runway_months(
    current_cash,
    burn
  )
  
  // Constraint: At least 6 months runway
  constraint minimum_runway: runway >= 6mo {
    severity: warning,
    message: "Runway below 6 months - fundraise or cut costs"
  }
}
```

## Common Patterns

### Track Cash vs Revenue
```pel
var revenue_recognized: Currency<USD> = compute_revenue()
var cash_collected: Currency<USD> = revenue_recognized * (1 - dso/30d)
var cash_delta: Currency<USD> = cash_collected - monthly_opex
```

### Model Payment Terms Impact
```pel
var baseline_dso: Duration<Day> = 45d
var optimized_dso: Duration<Day> = 30d

var cash_freed: Currency<USD> = 
  accounts_receivable(mrr, baseline_dso, 30d) -
  accounts_receivable(mrr, optimized_dso, 30d)
```

### Runway Planning
```pel
var current_runway: Duration<Month> = runway_months(cash, burn)
var target_runway: Duration<Month> = 12mo

var fundraise_target: Currency<USD> = 
  (target_runway - current_runway) * burn * -1
```

## Edge Cases

- **DSO = 0**: Immediate cash collection (rare, like usage-based SaaS)
- **Burn >= 0**: Profitable business = infinite runway
- **Negative cash**: Model allows but likely constraint violation

## Related Modules

- `unit_econ` - For LTV, CAC, payback period
- `retention` - For MRR forecasting inputs to cashflow
