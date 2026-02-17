# Cashflow Module Guide

The cashflow module provides financial modeling functions for cash flow analysis, working capital management, burn rate calculation, and runway projection.

## Overview

**Module:** `stdlib/cashflow/cashflow.pel`  
**Functions:** 20  
**Categories:**
- Accounts Receivable (4 functions)
- Accounts Payable (3 functions)
- Payroll (3 functions)
- Working Capital (4 functions)
- Cash Waterfall (3 functions)
- Additional Metrics (3 functions)

## Installation

```pel
import stdlib.cashflow as cf
```

## Accounts Receivable Functions

### ar_with_payment_terms

Calculate accounts receivable based on payment terms.

**Signature:**
```pel
func ar_with_payment_terms(
  revenue: Currency<USD> per Month,
  payment_terms_days: Duration<Day>
) -> Currency<USD>
```

**Parameters:**
- `revenue`: Monthly revenue
- `payment_terms_days`: Payment terms (e.g., Net 30, Net 60)

**Returns:** Accounts receivable balance

**Example:**
```pel
var monthly_revenue: Currency<USD> per Month = $500000/1mo
var payment_terms: Duration<Day> = 45day
var ar: Currency<USD> = cf.ar_with_payment_terms(monthly_revenue, payment_terms)
// Result: $750,000 (1.5 months of revenue)
```

**Use Case:** Model cash collection timing when customers pay on credit terms.

---

### days_sales_outstanding

Calculate Days Sales Outstanding (DSO) - average collection period.

**Signature:**
```pel
func days_sales_outstanding(
  accounts_receivable: Currency<USD>,
  revenue: Currency<USD> per Month
) -> Duration<Day>
```

**Parameters:**
- `accounts_receivable`: Current AR balance
- `revenue`: Monthly revenue

**Returns:** Average number of days to collect payment

**Example:**
```pel
var ar: Currency<USD> = $450000
var revenue: Currency<USD> per Month = $300000/1mo
var dso: Duration<Day> = cf.days_sales_outstanding(ar, revenue)
// Result: 45 days
```

**Interpretation:**
- < 30 days: Excellent collection
- 30-45 days: Good (typical Net 30 terms)
- 45-60 days: Acceptable (Net 45 terms)
- \> 60 days: Warning - collection issues

---

### ar_aging_buckets

Calculate aged AR for risk assessment.

**Signature:**
```pel
func ar_aging_buckets(
  total_ar: Currency<USD>,
  current_pct: Fraction,
  aged_30_pct: Fraction,
  aged_60_pct: Fraction,
  aged_90_pct: Fraction
) -> Currency<USD>
```

**Returns:** Total aged AR (30+ days overdue)

**Example:**
```pel
var total_ar: Currency<USD> = $500000
var aged_ar = cf.ar_aging_buckets(total_ar, 0.70, 0.20, 0.07, 0.03)
// Result: $150,000 aged (30% of total AR)
```

---

### bad_debt_reserve

Calculate bad debt reserve for uncollectible accounts.

**Signature:**
```pel
func bad_debt_reserve(
  accounts_receivable: Currency<USD>,
  reserve_rate: Fraction
) -> Currency<USD>
```

**Example:**
```pel
var ar: Currency<USD> = $500000
var reserve_rate: Fraction = 0.02  // 2% expected bad debt
var reserve = cf.bad_debt_reserve(ar, reserve_rate)
// Result: $10,000
```

**Typical Reserve Rates:**
- B2B SaaS: 1-2%
- SMB SaaS: 2-5%
- Consumer: 5-10%

## Accounts Payable Functions

### ap_with_payment_terms

Calculate accounts payable based on payment terms.

**Signature:**
```pel
func ap_with_payment_terms(
  expenses: Currency<USD> per Month,
  payment_terms_days: Duration<Day>
) -> Currency<USD>
```

**Example:**
```pel
var monthly_expenses: Currency<USD> per Month = $200000/1mo
var payment_terms: Duration<Day> = 60day
var ap: Currency<USD> = cf.ap_with_payment_terms(monthly_expenses, payment_terms)
// Result: $400,000 (2 months of expenses)
```

---

### days_payable_outstanding

Calculate Days Payable Outstanding (DPO) - average payment period.

**Signature:**
```pel
func days_payable_outstanding(
  accounts_payable: Currency<USD>,
  expenses: Currency<USD> per Month
) -> Duration<Day>
```

**Interpretation:**
- Higher DPO = Better cash position (paying suppliers later)
- But: Don't delay so long you damage supplier relationships

## Working Capital Functions

### working_capital

Calculate working capital (current assets - current liabilities).

**Signature:**
```pel
func working_capital(
  current_assets: Currency<USD>,
  current_liabilities: Currency<USD>
) -> Currency<USD>
```

**Example:**
```pel
var assets: Currency<USD> = $1500000
var liabilities: Currency<USD> = $800000
var wc = cf.working_capital(assets, liabilities)
// Result: $700,000
```

**Interpretation:**
- Positive: Good - can cover short-term obligations
- Negative: Warning - liquidity crisis risk

---

### cash_conversion_cycle

Calculate Cash Conversion Cycle (CCC) - time between paying suppliers and collecting from customers.

**Signature:**
```pel
func cash_conversion_cycle(
  days_sales_outstanding: Duration<Day>,
  days_inventory_outstanding: Duration<Day>,
  days_payable_outstanding: Duration<Day>
) -> Duration<Day>
```

**Formula:** CCC = DSO + DIO - DPO

**Example:**
```pel
var dso: Duration<Day> = 45day
var dio: Duration<Day> = 30day  // For product companies
var dpo: Duration<Day> = 60day
var ccc = cf.cash_conversion_cycle(dso, dio, dpo)
// Result: 15 days
```

**Interpretation:**
- Negative CCC: Excellent - collect before paying (e.g., Amazon, Dell)
- 0-30 days: Good
- 30-60 days: Acceptable
- \> 60 days: High working capital needs

---

### burn_rate

Calculate monthly cash burn rate.

**Signature:**
```pel
func burn_rate(
  starting_cash: Currency<USD>,
  ending_cash: Currency<USD>,
  period_months: Count<Month>
) -> Currency<USD> per Month
```

**Example:**
```pel
var start: Currency<USD> = $2000000
var end: Currency<USD> = $1400000
var months: Count<Month> = 3
var burn = cf.burn_rate(start, end, months)
// Result: $200,000/month
```

---

### runway_months

Calculate months of runway remaining.

**Signature:**
```pel
func runway_months(
  current_cash: Currency<USD>,
  monthly_burn_rate: Currency<USD> per Month
) -> Duration<Month>
```

**Example:**
```pel
var cash: Currency<USD> = $1200000
var burn: Currency<USD> per Month = $100000/1mo
var runway = cf.runway_months(cash, burn)
// Result: 12 months
```

**Rule of Thumb:**
- < 6 months: Urgent - raise capital now
- 6-12 months: Start fundraising
- 12-18 months: Comfortable
- \> 18 months: Strong position

## Cash Waterfall Functions

### operating_cash_flow

Calculate operating cash flow (OCF).

**Signature:**
```pel
func operating_cash_flow(
  net_income: Currency<USD> per Month,
  depreciation: Currency<USD> per Month,
  change_in_working_capital: Currency<USD>
) -> Currency<USD> per Month
```

**Formula:** OCF = Net Income + Depreciation - ΔWC

---

### free_cash_flow

Calculate free cash flow (FCF).

**Signature:**
```pel
func free_cash_flow(
  operating_cash_flow: Currency<USD> per Month,
  capital_expenditures: Currency<USD> per Month
) -> Currency<USD> per Month
```

**Formula:** FCF = OCF - CapEx

**Example:**
```pel
var ocf: Currency<USD> per Month = $150000/1mo
var capex: Currency<USD> per Month = $30000/1mo
var fcf = cf.free_cash_flow(ocf, capex)
// Result: $120,000/month
```

**Interpretation:**
- Positive FCF: Self-sustainable, can fund growth internally
- Negative FCF: Need external capital for growth

---

### cash_balance_projection

Project future cash balance.

**Signature:**
```pel
func cash_balance_projection(
  starting_cash: Currency<USD>,
  operating_cash_flow: Currency<USD> per Month,
  financing_cash_flow: Currency<USD> per Month,
  projection_months: Count<Month>
) -> Currency<USD>
```

## Additional Metrics

### current_ratio

**Formula:** Current Assets / Current Liabilities

**Healthy Range:** 1.5 - 2.0

### quick_ratio_cashflow

**Formula:** (Cash + AR) / Current Liabilities

More conservative than current ratio (excludes inventory).

**Healthy Range:** ≥ 1.0

### net_working_capital_ratio

**Formula:** Working Capital / Monthly Revenue

Measures efficiency of working capital usage.

## Complete Example: SaaS Company Cash Analysis

```pel
model saas_cash_analysis {
  // Revenue & Collections
  param mrr: Currency<USD> per Month = $500000/1mo {
    source: "billing_system",
    method: "observed",
    confidence: 0.95
  }
  
  param payment_terms: Duration<Day> = 30day {
    source: "contracts",
    method: "assumption",
    confidence: 1.0
  }
  
  var ar: Currency<USD> = cf.ar_with_payment_terms(mrr, payment_terms)
  var dso: Duration<Day> = cf.days_sales_outstanding(ar, mrr)
  
  // Expenses & Payments
  param monthly_expenses: Currency<USD> per Month = $400000/1mo {
    source: "accounting",
    method: "observed",
    confidence: 0.95
  }
  
  param vendor_terms: Duration<Day> = 45day {
    source: "contracts",
    method: "assumption",
    confidence: 1.0
  }
  
  var ap: Currency<USD> = cf.ap_with_payment_terms(monthly_expenses, vendor_terms)
  var dpo: Duration<Day> = cf.days_payable_outstanding(ap, monthly_expenses)
  
  // Working Capital
  var current_assets: Currency<USD> = $1500000
  var current_liabilities: Currency<USD> = $900000
  var wc: Currency<USD> = cf.working_capital(current_assets, current_liabilities)
  
  var ccc: Duration<Day> = cf.cash_conversion_cycle(dso, 0day, dpo)
  
  // Runway
  var cash: Currency<USD> = $2000000
  var net_burn: Currency<USD> per Month = monthly_expenses - mrr
  var runway: Duration<Month> = cf.runway_months(cash, net_burn)
  
  // Constraints
  constraint positive_runway: runway >= 6mo {
    severity: fatal,
    message: "Runway below 6 months - immediate action required"
  }
  
  constraint healthy_ccc: ccc <= 45day {
    severity: warning,
    message: "Cash conversion cycle exceeds 45 days"
  }
}
```

## Best Practices

1. **Monitor DSO/DPO Ratio**: Aim for DPO > DSO to maintain positive cash position
2. **Track CCC Trends**: Decreasing CCC = improving cash efficiency
3. **Maintain Runway Buffer**: Keep ≥ 12 months runway for safety
4. **Model Payment Terms**: Different customer segments may have different terms
5. **Bad Debt Reserves**: Set reserves based on historical data, not guesses
6. **Seasonal Adjustments**: Adjust burn rate for seasonal cash flow patterns

## Related Modules

- **unit_econ**: Calculate LTV, CAC, payback period
- **retention**: Model churn impact on future cash flows
- **hiring**: Forecast payroll growth and timing

## References

- "Cash Flow Analysis" - Corporate Finance textbooks
- SaaS Financial Model templates
- GAAP/IFRS cash flow standards

---

**Version:** 0.1.0  
**Last Updated:** 2026-02-16  
**Maintainer:** PEL Project Contributors
