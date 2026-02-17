# Retention Module Guide

## Overview

The `retention` module provides functions for customer retention analysis, churn modeling, and lifetime value calculations. It enables data-driven analysis of customer behavior, expansion revenue, and cohort dynamics.

## Key Concepts

### Retention vs. Churn

- **Retention Rate**: Percentage of customers remaining (e.g., 95%)
- **Churn Rate**: Percentage of customers lost (e.g., 5%)
- **Relationship**: Churn = 1 - Retention

### Cohort Analysis

A **cohort** is a group of customers who started in the same time period. Analyzing cohorts reveals:

- How retention changes over customer lifetime
- Whether product improvements reduce churn
- Impact of customer segments on retention

### Net Dollar Retention (NDR)

**NDR** measures revenue retention including expansion and contraction:

```
NDR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
```

- **NDR > 100%**: Net expansion (excellent!)
- **NDR = 100%**: Flat retention
- **NDR < 100%**: Net contraction

**Benchmarks:**
- **Best-in-class SaaS**: 120%+
- **Good SaaS**: 100-120%
- **Acceptable**: 90-100%
- **Concerning**: < 90%

## Module Functions

### Cohort Functions

#### `cohort_survival_rate(retained_customers, initial_customers)`

Calculate what percentage of a cohort remains.

**Example:**
```pel
// Started with 1000 customers, 950 remain after 1 month
var survival = cohort_survival_rate(950, 1000)
// Result: 0.95 (95%)
```

#### `cohort_half_life(monthly_churn_rate)`

Calculate time for cohort to shrink to 50%.

**Example:**
```pel
// 5% monthly churn
var half_life = cohort_half_life(0.05)
// Result: ~14 months
```

### Churn Metrics

#### `customer_churn_rate(churned_customers, starting_customers)`

**Example:**
```pel
// 2000 starting, 100 churned
var churn = customer_churn_rate(100, 2000)
// Result: 0.05 (5%)
```

#### `revenue_churn_rate(churned_mrr, starting_mrr)`

**Example:**
```pel
// $100k starting MRR, $3k churned
var rev_churn = revenue_churn_rate($3_000/1mo, $100_000/1mo)
// Result: 0.03 (3%)
```

### NDR Functions

#### `net_dollar_retention(starting_cohort_mrr, expansion_mrr, contraction_mrr, churned_mrr)`

**Example:**
```pel
// $100k starting, $20k expansion, $5k contraction, $10k churn
var ndr = net_dollar_retention($100_000/1mo, $20_000/1mo, $5_000/1mo, $10_000/1mo)
// Result: 1.05 (105% NDR)
```

#### `quick_ratio(new_mrr, expansion_mrr, churned_mrr, contraction_mrr)`

Measures growth efficiency.

**Example:**
```pel
// $50k new, $20k expansion, $15k churn, $5k contraction
var qr = quick_ratio($50_000/1mo, $20_000/1mo, $15_000/1mo, $5_000/1mo)
// Result: 3.5
```

**Benchmarks:**
- **> 4.0**: Excellent growth efficiency
- **2.0-4.0**: Good
- **< 2.0**: Growth challenged

### LTV Functions

#### `ltv_from_retention_curve(monthly_arpu, avg_retention_rate)`

**Example:**
```pel
// $100 ARPU, 95% retention (5% churn)
var ltv = ltv_from_retention_curve($100/1mo, 0.95)
// Result: $2000
```

**Formula:**
```
LTV = ARPU / Churn Rate
```

#### `discounted_ltv(monthly_arpu, avg_retention_rate, monthly_discount_rate)`

Accounts for time value of money.

**Example:**
```pel
// $100 ARPU, 95% retention, 1% discount rate
var discounted = discounted_ltv($100/1mo, 0.95, 0.01)
// Result: $1667 (lower than simple LTV)
```

## Complete Example: Cohort Analysis

```pel
model cohort_analysis {
  // Starting cohort
  param initial_customers: Count<Customer> = 1000
  param starting_mrr: Currency<USD> per Month = $100_000/1mo
  param arpu: Currency<USD> per Month per Customer = $100/1mo
  
  // Retention metrics
  param monthly_churn_rate: Fraction = 0.05
  param expansion_rate: Fraction = 0.03
  param contraction_rate: Fraction = 0.01
  
  // Calculate retention
  var retention_rate = 1.0 - monthly_churn_rate
  var retained = initial_customers * retention_rate
  var survival = cohort_survival_rate(retained, initial_customers)
  
  // Calculate churn
  var churned_count = customer_churn_rate(
    initial_customers * monthly_churn_rate,
    initial_customers
  )
  var churned_mrr = starting_mrr * monthly_churn_rate
  
  // Calculate expansion/contraction
  var expansion = starting_mrr * expansion_rate
  var contraction = starting_mrr * contraction_rate
  
  // Calculate NDR
  var ndr = net_dollar_retention(
    starting_mrr,
    expansion,
    contraction,
    churned_mrr
  )
  
  // Calculate LTV
  var ltv = ltv_from_retention_curve(arpu, retention_rate)
  
  // Results:
  // - Survival: 95% after 1 month
  // - Churn: 5% (50 customers)
  // - NDR: 103% (net expansion!)
  // - LTV: $2000 per customer
}
```

## Best Practices

### 1. Track NDR by Cohort

```pel
constraint ndr_healthy {
  severity: "info"
  condition: ndr >= 1.0
  message: "Cohort achieving net expansion"
}

constraint ndr_warning {
  severity: "warning"
  condition: ndr < 0.90
  message: "Cohort NDR below 90% - investigate churn drivers"
}
```

### 2. Monitor Quick Ratio

```pel
constraint growth_efficiency {
  severity: "warning"
  condition: quick_ratio < 2.0
  message: "Quick ratio below 2.0 - growth challenged"
}
```

### 3. Segment Cohorts

Different customer segments have different retention:

- **Enterprise**: Lower churn (< 2%), higher expansion
- **SMB**: Higher churn (5-10%), lower expansion
- **Self-serve**: Highest churn (10-20%), moderate expansion

### 4. Use Retention Curves

Different churn patterns over time:

- **Exponential**: Constant churn rate (most common)
- **Power Law**: Decreasing churn (improving retention)
- **Weibull**: Flexible shape (early churn then stable)

## Integration with Other Modules

### With `unit_econ`:

```pel
import stdlib.unit_econ as ue
import stdlib.retention as ret

// LTV/CAC ratio using retention-based LTV
var ltv = ret.ltv_from_retention_curve(arpu, retention_rate)
var ltv_cac = ue.ltv_to_cac_ratio(ltv, cac)
```

### With `cashflow`:

```pel
import stdlib.cashflow as cf
import stdlib.retention as ret

// Churn affects revenue and cash
var churn_rate = ret.customer_churn_rate(churned, starting)
var churned_revenue = revenue * churn_rate
var reduced_cash = cf.cash_balance_projection(
  starting_cash,
  revenue - churned_revenue - expenses,
  12mo
)
```

---

**Module:** `stdlib/retention/retention.pel`  
**Version:** 0.1.0  
**Status:** Complete (18 functions)  
**Dependencies:** None
