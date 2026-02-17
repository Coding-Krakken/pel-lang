# Funnel Module

Functions for multi-stage conversion funnels and funnel optimization analysis.

## Key Functions

### Core Funnel Calculations
- `multi_stage_funnel()` - N-stage funnel calculation
- `funnel_step_down()` - Stage i → stage i+1 conversion
- `overall_conversion_rate()` - First → last stage conversion
- `stage_conversion_rate()` - Specific stage conversion

### Funnel Analysis
- `funnel_leakage()` - Drop-off at each stage
- `funnel_leakage_pct()` - Percentage loss at each stage
- `bottleneck_detection()` - Identifies worst-performing stage

### Funnel Velocity
- `funnel_velocity()` - Total time through funnel
- `time_in_funnel_stage()` - Average time in specific stage
- `funnel_throughput()` - Users per day throughput

### Cohort Funnels
- `cohort_funnel()` - Cohort-specific funnel
- `cohort_funnel_comparison()` - Compare two cohorts

### Pre-Built Archetypes
- `saas_signup_funnel()` - SaaS: Visit → Signup → Activation → Trial → Paid
- `ecommerce_checkout_funnel()` - E-com: View → Cart → Checkout → Purchase
- `b2b_sales_funnel()` - B2B: Lead → MQL → SQL → Opp → Closed-Won

### Optimization
- `stage_improvement_impact()` - Impact of improving one stage
- `required_conversion_rate_for_target()` - Reverse calculation

## Example Usage

```pel
import pel.stdlib.funnel as fn

model SaaS_Acquisition_Funnel {
  // Stage sizes (top of funnel)
  param website_visitors: Count<User> per Month = 10_000/1mo {
    source: "google_analytics",
    method: "observed",
    confidence: 0.95
  }
  
  // Conversion rates at each stage
  param signup_rate: Fraction = ~Beta(α=80, β=920) {
    source: "signup_data",
    method: "fitted",
    confidence: 0.85,
    notes: "~8% signup rate"
  }
  
  param activation_rate: Fraction = 0.60 {
    source: "product_analytics",
    method: "observed",
    confidence: 0.90
  }
  
  param trial_start_rate: Fraction = 0.75 {
    source: "product_analytics",
    method: "observed",
    confidence: 0.90
  }
  
  param trial_to_paid_rate: Fraction = ~Beta(α=25, β=75) {
    source: "conversion_tracking",
    method: "fitted",
    confidence: 0.80,
    notes: "~25% trial conversion"
  }
  
  // Calculate funnel
  var funnel: Array<Count<User>> = fn.saas_signup_funnel(
    website_visitors * 1mo,  // Convert to Count
    signup_rate,
    activation_rate,
    trial_start_rate,
    trial_to_paid_rate
  )
  
  // Extract key metrics
  var signups: Count<User> = funnel[1]
  var activated_users: Count<User> = funnel[2]
  var trials: Count<User> = funnel[3]
  var paid_customers: Count<User> = funnel[4]
  
  // Calculate overall conversion
  var overall_conversion: Fraction = fn.overall_conversion_rate([
    signup_rate,
    activation_rate,
    trial_start_rate,
    trial_to_paid_rate
  ])
  
  // Find bottleneck
  var bottleneck_stage: Count = fn.bottleneck_detection([
    signup_rate,
    activation_rate,
    trial_start_rate,
    trial_to_paid_rate
  ])
  
  // Monthly targets
  param target_paid_customers: Count<User> = 200 {
    source: "growth_plan",
    method: "assumption",
    confidence: 0.70
  }
  
  constraint hit_growth_target: paid_customers >= target_paid_customers {
    severity: warning,
    message: "Below monthly customer acquisition target"
  }
}
```

## Common Patterns

### Identify Where to Improve
```pel
var conversion_rates: Array<Fraction> = [0.08, 0.60, 0.75, 0.25]
var stage_names: Array<String> = ["Signup", "Activation", "Trial", "Paid"]

var bottleneck: Count = fn.bottleneck_detection(conversion_rates)
// Returns index of worst stage
// Focus optimization here for maximum impact
```

### A/B Test Impact Projection
```pel
// Current funnel
var current_activation_rate: Fraction = 0.60
var visitors: Count<User> = 10_000

// Test variant shows potential improvement
var new_activation_rate: Fraction = 0.70

var impact: Count<User> = fn.stage_improvement_impact(
  current_funnel,
  1,  // Stage index (activation)
  new_activation_rate,
  current_activation_rate
)
// Shows how many more paid customers from 10% activation lift
```

### Reverse-Engineer Required Performance
```pel
var website_traffic: Count<User> = 10_000
var target_customers: Count<User> = 200
var downstream_conversion: Fraction = 0.60 * 0.75 * 0.25  // Activation × Trial × Paid

var required_signup_rate: Fraction = fn.required_conversion_rate_for_target(
  website_traffic,
  target_customers,
  downstream_conversion
)
// Tells you what signup rate you need to hit target
```

### Time-in-Funnel Analysis
```pel
var avg_time_per_stage: Array<Duration<Day>> = [
  0d,      // Visit (instant)
  1d,      // Signup → Activation
  2d,      // Activation → Trial
  14d      // Trial → Paid (trial period)
]

var total_funnel_time: Duration<Day> = fn.funnel_velocity(avg_time_per_stage)
// = 17 days from visit to paid customer
```

## Pre-Built Archetypes

### SaaS Signup Funnel
```pel
var funnel: Array<Count<User>> = fn.saas_signup_funnel(
  visitors,
  signup_rate,
  activation_rate,
  trial_rate,
  paid_rate
)
// Returns: [Visits, Signups, Activated, Trial, Paid]
```

### E-Commerce Checkout
```pel
var checkout_funnel: Array<Count<User>> = fn.ecommerce_checkout_funnel(
  product_views,
  add_to_cart_rate,
  checkout_rate,
  purchase_rate
)
// Returns: [Views, Cart, Checkout, Purchase]
```

### B2B Sales
```pel
var sales_funnel: Array<Count<Contact>> = fn.b2b_sales_funnel(
  leads,
  mql_rate,
  sql_rate,
  opportunity_rate,
  close_rate
)
// Returns: [Leads, MQL, SQL, Opp, Closed-Won]
```

## Best Practices

1. **Model stage uncertainty**: Use distributions for conversion rates
2. **Track cohorts separately**: Acquisition funnels change over time
3. **Monitor velocity**: Faster funnels = faster growth
4. **Fix bottlenecks first**: Biggest ROI from worst-performing stage

## Typical Conversion Benchmarks

### SaaS
- Visit → Signup: 5-10%
- Signup → Activation: 40-60%
- Activation → Trial: 70-90%
- Trial → Paid: 20-40%
- **Overall**: 0.5-2% visit → paid

### E-Commerce
- View → Add to Cart: 5-15%
- Cart → Checkout: 50-70%
- Checkout → Purchase: 60-80%
- **Overall**: 2-8% view → purchase

### B2B SaaS
- Lead → MQL: 20-40%
- MQL → SQL: 30-50%
- SQL → Opportunity: 40-60%
- Opportunity → Closed-Won: 20-30%
- **Overall**: 1-5% lead → customer

## Related Modules

- `demand` - For top-of-funnel lead generation
- `unit_econ` - For CAC calculation from funnel + spend
- `retention` - For what happens after funnel (churn)
