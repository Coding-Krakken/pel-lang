# Retention Module

Functions for customer retention curves, churn analysis, and cohort dynamics.

## Key Functions

### Retention Curves
- `exponential_retention_curve()` - Standard decay model (common for SaaS)
- `power_law_retention_curve()` - Long-tail retention (network effects)
- `cohort_retention_table()` - Period-by-period cohort tracking

### Churn Metrics
- `simple_churn_rate()` - Monthly churn %
- `cohort_churn_rate()` - Cohort-specific churn
- `customer_lifetime_months()` - Expected lifetime

### Dollar-Based Metrics
- `net_dollar_retention()` - NDR (includes expansion)
- `gross_dollar_retention()` - GDR (excludes expansion)
- `quick_ratio_retention()` - Growth efficiency

### Helpers
- `retention_rate_from_churn()` - Convert churn → retention
- `churn_rate_from_retention()` - Convert retention → churn
- `retention_hazard()` - Conditional churn probability

## Example Usage

```pel
import pel.stdlib.retention as ret

model SaaS_Retention {
  param monthly_churn: Rate per Month = ~Beta(α=2, β=38) {
    source: "cohort_analysis",
    method: "fitted",
    confidence: 0.75
  }
  
  param initial_customers: Count<Customer> = 1000 {
    source: "current_base",
    method: "observed",
    confidence: 1.0
  }
  
  // Generate 36-month retention curve
  var retention_curve: Array<Fraction> = 
    ret.exponential_retention_curve(monthly_churn, 36)
  
  // Calculate cohort sizes over time
  var cohort_sizes: Array<Count<Customer>> = 
    ret.cohort_retention_table(initial_customers, retention_curve)
  
  // Calculate average customer lifetime
  var avg_lifetime: Duration<Month> = 
    ret.customer_lifetime_months(1.0 - monthly_churn * 1mo)
  
  // NDR calculation
  var ndr: Fraction = ret.net_dollar_retention(
    $100_000,  // Starting MRR
    $20_000,   // Expansion
    $8_000,    // Churn
    $3_000     // Contraction
  )
  
  // Health check
  constraint healthy_ndr: ndr >= 1.0 {
    severity: warning,
    message: "NDR below 100% - losing existing customers faster than expanding"
  }
}
```

## Choosing a Retention Model

### When to use Exponential
- ✅ SaaS subscriptions with constant churn rate
- ✅ Simple models, easy to reason about
- ✅ Most common use case

### When to use Power Law
- ✅ Products with network effects (social, marketplace)
- ✅ High engagement / habit-forming products
- ✅ Long-tail retention patterns observed in data

### Example Comparison
```pel
// For a product with 5% monthly churn:
var exp_curve: Array<Fraction> = ret.exponential_retention_curve(0.05/1mo, 24)
// Month 12: ~54% retained
// Month 24: ~29% retained

// Power law might show:
var power_curve: Array<Fraction> = ret.power_law_retention_curve(0.9, 0.15, 24)
// Month 12: ~65% retained (better long-tail)
// Month 24: ~55% retained
```

## Common Patterns

### Cohort Comparison
```pel
var cohort_2023_curve: Array<Fraction> = ret.exponential_retention_curve(0.06/1mo, 12)
var cohort_2024_curve: Array<Fraction> = ret.exponential_retention_curve(0.04/1mo, 12)

var improvement: Fraction = 
  cohort_2024_curve[12] - cohort_2023_curve[12]
// Shows retention improvement over time
```

### NDR Decomposition
```pel
var starting_mrr: Currency<USD> = $1_000_000
var churned_mrr: Currency<USD> = $50_000
var expansion_mrr: Currency<USD> = $150_000

var gdr: Fraction = ret.gross_dollar_retention(starting_mrr, churned_mrr, $0)
// GDR = 95% (retained 95% of base)

var ndr: Fraction = ret.net_dollar_retention(starting_mrr, expansion_mrr, churned_mrr, $0)
// NDR = 110% (10% net growth from existing customers)
```

## Best Practices

1. **Model uncertainty in churn**: Use distributions (`~Beta(α, β)`)
2. **Track cohorts separately**: Different vintages have different behavior
3. **Monitor NDR > GDR gap**: Expansion revenue is compounding growth
4. **Target NDR > 100%**: Means you grow without new customer acquisition

## Related Modules

- `unit_econ` - For LTV calculation (uses retention)
- `funnel` - For acquisition (complements retention)
