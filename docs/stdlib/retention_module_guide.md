# Retention Module Guide

The retention module provides customer retention, churn analysis, expansion revenue tracking, and lifetime value calculations for subscription and recurring revenue businesses.

## Overview

**Module:** `stdlib/retention/retention.pel`  
**Functions:** 20  
**Categories:**
- Cohort Analysis (3 functions)
- Churn Metrics (4 functions)
- Expansion & Contraction (3 functions)
- Dollar Retention (3 functions)
- Retention Curves (3 functions)
- Lifetime Value (2 functions)
- Advanced Metrics (2 functions)

## Installation

```pel
import stdlib.retention as ret
```

## Cohort Analysis Functions

### cohort_retention_curve

Calculate retention rate for a cohort at a specific period.

**Signature:**
```pel
func cohort_retention_curve(
  initial_customers: Count<Customer>,
  retained_customers: Count<Customer>,
  period: Count<Month>
) -> Fraction
```

**Example:**
```pel
var initial: Count<Customer> = 1000
var month_6_retained: Count<Customer> = 850
var retention_6mo = ret.cohort_retention_curve(initial, month_6_retained, 6)
// Result: 0.85 (85% retention)
```

**Interpretation:**
- Month 1: 95%+ is excellent
- Month 6: 80%+ is good for SaaS
- Month 12: 70%+ is healthy

---

### cohort_survival_rate

Calculate percentage of customers still active.

**Signature:**
```pel
func cohort_survival_rate(
  initial_customers: Count<Customer>,
  surviving_customers: Count<Customer>
) -> Fraction
```

**Use Case:** Track long-term cohort health over years.

---

### cohort_half_life

Calculate time for cohort to lose half its customers.

**Signature:**
```pel
func cohort_half_life(
  monthly_churn_rate: Rate per Month
) -> Duration<Month>
```

**Formula:** Approximately 0.693 / churn_rate

**Example:**
```pel
var churn: Rate per Month = 0.05/1mo  // 5% monthly churn
var half_life = ret.cohort_half_life(churn)
// Result: ~13.86 months
```

**Interpretation:**
- \> 24 months: Excellent (consumer apps)
- 12-24 months: Good (SMB SaaS)
- 6-12 months: Acceptable (high-churn segments)
- < 6 months: Warning - fix retention

## Churn Metrics

### customer_churn_rate

Calculate monthly customer churn rate (logo churn).

**Signature:**
```pel
func customer_churn_rate(
  churned_customers: Count<Customer>,
  starting_customers: Count<Customer>
) -> Rate per Month
```

**Example:**
```pel
var churned: Count<Customer> = 50
var starting: Count<Customer> = 1000
var churn_rate = ret.customer_churn_rate(churned, starting)
// Result: 0.05/1mo (5% monthly churn)
```

**Benchmarks by Segment:**
- Enterprise: 0.5-1.5% monthly (~6-18% annual)
- Mid-market: 2-3% monthly (~24-36% annual)
- SMB: 3-7% monthly (~36-84% annual)
- Consumer: 5-10% monthly

---

### revenue_churn_rate

Calculate monthly revenue churn (MRR churn).

**Signature:**
```pel
func revenue_churn_rate(
  churned_mrr: Currency<USD> per Month,
  starting_mrr: Currency<USD> per Month
) -> Rate per Month
```

**Example:**
```pel
var churned_mrr: Currency<USD> per Month = $5000/1mo
var starting_mrr: Currency<USD> per Month = $100000/1mo
var revenue_churn = ret.revenue_churn_rate(churned_mrr, starting_mrr)
// Result: 0.05/1mo (5% monthly revenue churn)
```

**Key Insight:** Revenue churn < Customer churn means larger customers stay longer.

---

### logo_churn

Calculate logo churn rate (account-level churn).

**Signature:**
```pel
func logo_churn(
  churned_accounts: Count<Account>,
  starting_accounts: Count<Account>,
  period_months: Count<Month>
) -> Rate per Month
```

**Use Case:** B2B companies tracking at account level, not individual user.

---

### churn_rate_from_retention

Convert retention rate to churn rate.

**Signature:**
```pel
func churn_rate_from_retention(
  retention_rate: Fraction
) -> Rate per Month
```

**Example:**
```pel
var retention: Fraction = 0.95  // 95% retention
var churn = ret.churn_rate_from_retention(retention)
// Result: 0.05/1mo (5% churn)
```

## Expansion & Contraction

### expansion_mrr

Calculate total expansion MRR from upsells and cross-sells.

**Signature:**
```pel
func expansion_mrr(
  upsell_mrr: Currency<USD> per Month,
  cross_sell_mrr: Currency<USD> per Month
) -> Currency<USD> per Month
```

**Example:**
```pel
var upsells: Currency<USD> per Month = $15000/1mo
var cross_sells: Currency<USD> per Month = $5000/1mo
var expansion = ret.expansion_mrr(upsells, cross_sells)
// Result: $20,000/month expansion
```

---

### contraction_mrr

Calculate total contraction MRR from downgrades and partial churn.

**Signature:**
```pel
func contraction_mrr(
  downgrade_mrr: Currency<USD> per Month,
  partial_churn_mrr: Currency<USD> per Month
) -> Currency<USD> per Month
```

**Use Case:** Track revenue lost from customers staying but spending less.

---

### reactivation_mrr

Calculate MRR from reactivated (win-back) customers.

**Signature:**
```pel
func reactivation_mrr(
  reactivated_customers: Count<Customer>,
  average_mrr_per_customer: Currency<USD> per Month per Customer
) -> Currency<USD> per Month
```

**Example:**
```pel
var reactivated: Count<Customer> = 20
var avg_mrr: Currency<USD> per Month per Customer = $150/1mo
var reactivation = ret.reactivation_mrr(reactivated, avg_mrr)
// Result: $3,000/month from win-backs
```

## Dollar Retention Metrics

### net_dollar_retention

Calculate Net Dollar Retention (NDR) - the holy grail SaaS metric.

**Signature:**
```pel
func net_dollar_retention(
  starting_mrr: Currency<USD> per Month,
  expansion_mrr: Currency<USD> per Month,
  contraction_mrr: Currency<USD> per Month,
  churned_mrr: Currency<USD> per Month
) -> Fraction
```

**Formula:** NDR = (Starting + Expansion - Contraction - Churned) / Starting

**Example:**
```pel
var start: Currency<USD> per Month = $100000/1mo
var expansion: Currency<USD> per Month = $20000/1mo
var contraction: Currency<USD> per Month = $5000/1mo
var churned: Currency<USD> per Month = $10000/1mo
var ndr = ret.net_dollar_retention(start, expansion, contraction, churned)
// Result: 1.05 (105% NDR)
```

**Benchmarks:**
- \> 120%: Best-in-class (Snowflake, Datadog)
- 110-120%: Excellent (top quartile public SaaS)
- 100-110%: Good (median public SaaS)
- 90-100%: Acceptable (growth stage)
- < 90%: Warning - expansion < churn

**Why NDR Matters:**
- NDR > 100%: Grow without new customers
- High NDR = pricing power, product value, low churn
- Public SaaS companies trade on NDR multiples

---

### gross_dollar_retention

Calculate Gross Dollar Retention (GDR) - measures retention without expansion.

**Signature:**
```pel
func gross_dollar_retention(
  starting_mrr: Currency<USD> per Month,
  contraction_mrr: Currency<USD> per Month,
  churned_mrr: Currency<USD> per Month
) -> Fraction
```

**Formula:** GDR = (Starting - Contraction - Churned) / Starting

**Example:**
```pel
var start: Currency<USD> per Month = $100000/1mo
var contraction: Currency<USD> per Month = $5000/1mo
var churned: Currency<USD> per Month = $10000/1mo
var gdr = ret.gross_dollar_retention(start, contraction, churned)
// Result: 0.85 (85% GDR)
```

**Benchmarks:**
- \> 95%: Excellent (enterprise)
- 90-95%: Good (mid-market)
- 85-90%: Acceptable (SMB)
- < 85%: Warning - high churn

---

### quick_ratio_retention

Calculate quick ratio (growth efficiency).

**Signature:**
```pel
func quick_ratio_retention(
  new_mrr: Currency<USD> per Month,
  expansion_mrr: Currency<USD> per Month,
  churned_mrr: Currency<USD> per Month,
  contraction_mrr: Currency<USD> per Month
) -> Fraction
```

**Formula:** (New + Expansion) / (Churned + Contraction)

**Example:**
```pel
var new: Currency<USD> per Month = $30000/1mo
var expansion: Currency<USD> per Month = $20000/1mo
var churned: Currency<USD> per Month = $10000/1mo
var contraction: Currency<USD> per Month = $5000/1mo
var qr = ret.quick_ratio_retention(new, expansion, churned, contraction)
// Result: 3.33
```

**Benchmarks:**
- \> 4.0: Excellent
- 2.0-4.0: Good
- 1.0-2.0: Acceptable
- < 1.0: Shrinking (negative growth)

## Retention Curve Models

### exponential_churn_curve

Model retention using exponential decay (constant churn rate).

**Signature:**
```pel
func exponential_churn_curve(
  initial_retention: Fraction,
  monthly_churn_rate: Rate per Month,
  months: Count<Month>
) -> Fraction
```

**Use Case:** Simplest model, good for short-term projections.

---

### power_law_churn_curve

Model retention using power law (decreasing churn over time).

**Signature:**
```pel
func power_law_churn_curve(
  initial_retention: Fraction,
  decay_exponent: Fraction,
  months: Count<Month>
) -> Fraction
```

**Use Case:** More realistic - older customers churn less (habit formation).

---

### weibull_churn_curve

Model retention using Weibull distribution (flexible shape).

**Signature:**
```pel
func weibull_churn_curve(
  initial_retention: Fraction,
  shape_param: Fraction,
  scale_param: Fraction,
  months: Count<Month>
) -> Fraction
```

**Use Case:** Best fit for empirical data, captures complex retention patterns.

## Lifetime Value Functions

### ltv_from_retention_curve

Calculate LTV from average customer lifetime.

**Signature:**
```pel
func ltv_from_retention_curve(
  monthly_revenue_per_customer: Currency<USD> per Month per Customer,
  average_lifetime_months: Duration<Month>
) -> Currency<USD> per Customer
```

**Example:**
```pel
var arpu: Currency<USD> per Month per Customer = $125/1mo
var lifetime: Duration<Month> = 20mo
var ltv = ret.ltv_from_retention_curve(arpu, lifetime)
// Result: $2,500 per customer
```

---

### discounted_ltv

Calculate discounted LTV (accounts for time value of money).

**Signature:**
```pel
func discounted_ltv(
  monthly_revenue_per_customer: Currency<USD> per Month per Customer,
  monthly_churn_rate: Rate per Month,
  monthly_discount_rate: Rate per Month
) -> Currency<USD> per Customer
```

**Formula:** LTV = ARPU / (churn_rate + discount_rate)

**Example:**
```pel
var arpu: Currency<USD> per Month per Customer = $125/1mo
var churn: Rate per Month = 0.05/1mo
var discount: Rate per Month = 0.01/1mo  // 12% annual discount
var ltv = ret.discounted_ltv(arpu, churn, discount)
// Result: $2,083 per customer
```

## Advanced Metrics

### retention_improvement_impact

Calculate revenue impact of improving retention.

**Signature:**
```pel
func retention_improvement_impact(
  starting_retention: Fraction,
  improved_retention: Fraction,
  monthly_revenue: Currency<USD> per Month
) -> Currency<USD> per Month
```

**Use Case:** Model ROI of retention initiatives.

---

### churn_probability_by_tenure

Model decreasing churn probability as customers age.

**Signature:**
```pel
func churn_probability_by_tenure(
  months_since_signup: Count<Month>,
  base_churn_rate: Rate per Month,
  tenure_discount_factor: Fraction
) -> Fraction
```

**Use Case:** More accurate churn forecasting by cohort age.

## Complete Example: SaaS Retention Dashboard

```pel
model saas_retention_dashboard {
  // Cohort Data
  param cohort_jan_2024_initial: Count<Customer> = 1000 {
    source: "analytics",
    method: "observed",
    confidence: 1.0
  }
  
  param cohort_jan_2024_month_6: Count<Customer> = 850 {
    source: "analytics",
    method: "observed",
    confidence: 0.95
  }
  
  var retention_6mo = ret.cohort_retention_curve(
    cohort_jan_2024_initial,
    cohort_jan_2024_month_6,
    6
  )
  
  // Churn Analysis
  var monthly_churn = ret.churn_rate_from_retention(retention_6mo)
  var half_life = ret.cohort_half_life(monthly_churn)
  
  // MRR Movement
  param starting_mrr: Currency<USD> per Month = $500000/1mo {
    source: "billing",
    method: "observed",
    confidence: 1.0
  }
  
  param new_mrr: Currency<USD> per Month = $100000/1mo {
    source: "billing",
    method: "observed",
    confidence: 1.0
  }
  
  param upsell_mrr: Currency<USD> per Month = $50000/1mo {
    source: "billing",
    method: "observed",
    confidence: 1.0
  }
  
  param cross_sell_mrr: Currency<USD> per Month = $20000/1mo {
    source: "billing",
    method: "observed",
    confidence: 1.0
  }
  
  param downgrade_mrr: Currency<USD> per Month = $10000/1mo {
    source: "billing",
    method: "observed",
    confidence: 1.0
  }
  
  param churned_mrr: Currency<USD> per Month = $30000/1mo {
    source: "billing",
    method: "observed",
    confidence: 1.0
  }
  
  var expansion = ret.expansion_mrr(upsell_mrr, cross_sell_mrr)
  var contraction = ret.contraction_mrr(downgrade_mrr, 0)
  
  // Dollar Retention
  var ndr = ret.net_dollar_retention(
    starting_mrr,
    expansion,
    contraction,
    churned_mrr
  )
  
  var gdr = ret.gross_dollar_retention(
    starting_mrr,
    contraction,
    churned_mrr
  )
  
  var quick_ratio = ret.quick_ratio_retention(
    new_mrr,
    expansion,
    churned_mrr,
    contraction
  )
  
  // LTV
  param arpu: Currency<USD> per Month per Customer = $125/1mo {
    source: "billing",
    method: "observed",
    confidence: 0.95
  }
  
  var lifetime = ret.cohort_half_life(monthly_churn) * 2  // 2x half-life
  var ltv = ret.ltv_from_retention_curve(arpu, lifetime)
  
  // Constraints
  constraint healthy_ndr: ndr >= 1.0 {
    severity: warning,
    message: "NDR below 100% - expansion not offsetting churn"
  }
  
  constraint acceptable_gdr: gdr >= 0.85 {
    severity: warning,
    message: "GDR below 85% - high revenue churn"
  }
  
  constraint strong_quick_ratio: quick_ratio >= 2.0 {
    severity: warning,
    message: "Quick ratio below 2.0 - growth efficiency concern"
  }
}
```

## Best Practices

1. **Track Cohorts, Not Averages**: Retention varies dramatically by cohort age
2. **NDR is King**: Public markets value NDR > 110% with premium multiples
3. **Expansion > Retention**: Easier to expand existing customers than reduce churn
4. **Segment Retention**: SMB, mid-market, enterprise have different patterns
5. **Leading Indicators**: Track product usage, NPS before churn happens
6. **Curve Fitting**: Use historical data to choose best retention curve model
7. **LTV Updates**: Recalculate LTV quarterly as retention patterns change

## Retention Improvement Strategies

### For Low GDR (< 85%)
- Improve onboarding (80% of churn happens in first 90 days)
- Customer success team for high-value accounts
- Product-led growth to increase stickiness
- Pricing optimization (willingness to pay vs. value delivered)

### For Low NDR (< 100%)
- Land-and-expand strategy (start small, grow over time)
- Usage-based pricing (customers grow with you)
- Multi-product cross-sell
- Enterprise features for upsell

### For Low Quick Ratio (< 2.0)
- Improve new customer acquisition (top of funnel)
- Accelerate expansion motion
- Reduce churn through product improvements
- Increase prices (if value justifies)

## Related Modules

- **unit_econ**: Calculate LTV:CAC ratio, payback period
- **cashflow**: Model cash impact of churn on runway
- **pricing**: Optimize pricing to reduce contraction

## References

- "SaaS Metrics 2.0" - David Skok
- "The Ultimate Guide to SaaS Retention" - ChartMogul
- Public SaaS company S-1 filings (NDR/GDR benchmarks)

---

**Version:** 0.1.0  
**Last Updated:** 2026-02-16  
**Maintainer:** PEL Project Contributors
