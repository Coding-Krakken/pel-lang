# Pricing Module

Functions for pricing strategy, elasticity analysis, revenue optimization, and dynamic pricing.

## Key Functions

### Core Pricing Calculations
- `elasticity_curve()` - Demand at different price points (elasticity curve)
- `competitive_pricing()` - Competitive pricing response
- `dynamic_pricing()` - Dynamic pricing based on utilization
- `discount_impact()` - Revenue impact of discounts
- `price_point_optimization()` - Find optimal price for max revenue
- `tiered_pricing_revenue()` - Revenue from tiered/graduated pricing
- `bundle_pricing()` - Bundle pricing calculation
- `freemium_conversion()` - Freemium-to-paid conversion revenue
- `willingness_to_pay()` - WTP distribution quantiles

### Advanced Pricing Models
- `reservation_price()` - Maximum WTP before customer walks
- `value_based_pricing()` - Price based on value delivered
- `penetration_pricing()` - Market share impact of penetration pricing
- `price_skimming()` - Price skimming decay over time
- `psychological_anchor()` - Psychological anchoring effect
- `usage_based_pricing()` - Usage-based (metered) pricing revenue
- `price_discrimination()` - Revenue from price discrimination (versioning)
- `cost_plus_pricing()` - Cost-plus pricing with target margin

## Use Cases
- SaaS pricing strategy and optimization
- E-commerce dynamic pricing and discounting
- Marketplace pricing and fee structures
- Subscription tier optimization
- Freemium conversion modeling
- Competitive pricing analysis
- Revenue management and yield optimization
- Value-based pricing and willingness-to-pay analysis

## Production-Ready Standards

This module follows Microsoft-production-grade quality standards:

### Robustness & Validation
- **Price validation**: All 18 functions guard against negative/zero prices
- **Boundary clamping**: Fractions clamped to valid ranges (0.0-1.0)
- **Division-by-zero protection**: Guards in all division operations
- **Margin safety**: Cost-plus pricing caps margins at 99% to prevent division issues
- **Array safety**: Empty array checks with safe defaults

### Documentation
- **Structured @param tags**: Every parameter documented with constraints
- **@return tags**: Expected output ranges and units clearly specified
- **@errors tags**: Error handling behavior explicitly documented
- **Example usage**: Real-world examples with realistic pricing scenarios
- **Contract annotations**: @Monotonic, @Bounded annotations for formal verification

### Economic Correctness
- **Standard formulas**: Implements textbook pricing models (elasticity, WTP, anchoring)
- **Dimensionally sound**: All Currency, Rate, Fraction types correctly applied
- **Industry benchmarks**: Functions use realistic default values (elasticity coefficients, conversion rates)

### Test Coverage
- **17 unit tests**: All core functionality validated
- **Edge cases**: Zero prices, boundary conditions, optimization edge cases
- **Integration ready**: Functions compose with demand and revenue modules

## Related Modules

- **[Demand Module](../demand/README.md)** — demand forecasting and elasticity. Use `elasticity_curve()` with demand functions for revenue optimization.
- **[Unit Economics Module](../unit_econ/README.md)** — LTV, CAC, margins. Use pricing functions to model unit economics impact.
- **[Cashflow Module](../cashflow/README.md)** — payment timing and collections. Use pricing with payment terms for cash modeling.

## Example

```pel
import std.pricing.*

model SaaSPricingStrategy {
  // Current pricing
  param current_price: Currency<USD> = $99 {
    source: "pricing_page",
    method: "observed",
    confidence: 1.0
  }
  
  param current_demand: Rate per Month = 500 / 1mo {
    source: "sales_data",
    method: "observed",
    confidence: 0.95
  }
  
  param price_elasticity: Fraction = -1.2 {
    source: "pricing_experiments",
    method: "derived",
    confidence: 0.85
  }
  
  // Competitive landscape
  param competitor_price: Currency<USD> = $89 {
    source: "competitive_intelligence",
    method: "observed",
    confidence: 0.9
  }
  
  param price_sensitivity: Fraction = 0.55 {
    source: "customer_surveys",
    method: "derived",
    confidence: 0.75
  }
  
  // Willingness to pay analysis
  param wtp_median: Currency<USD> = $120 {
    source: "van_westendorp_analysis",
    method: "derived",
    confidence: 0.8
  }
  
  param wtp_spread: Currency<USD> = $35 {
    source: "van_westendorp_analysis",
    method: "derived",
    confidence: 0.75
  }
  
  // Test price points
  param test_price_low: Currency<USD> = $79 {
    source: "pricing_options",
    method: "assumption",
    confidence: 1.0
  }
  
  param test_price_mid: Currency<USD> = $99 {
    source: "pricing_options",
    method: "assumption",
    confidence: 1.0
  }
  
  param test_price_high: Currency<USD> = $129 {
    source: "pricing_options",
    method: "assumption",
    confidence: 1.0
  }
  
  // Calculated metrics
  var wtp_90th_percentile: Currency<USD> = willingness_to_pay(wtp_median, wtp_spread, 0.9)
  
  var competitive_demand: Rate per Month = competitive_pricing(
    current_price,
    competitor_price,
    current_demand,
    price_sensitivity
  )
  
  var optimal_price_idx: Int = price_point_optimization(
    [test_price_low, test_price_mid, test_price_high],
    current_price,
    current_demand,
    price_elasticity
  )
  
  // Revenue scenarios
  rate current_revenue: Currency<USD> per Month
    = current_price * competitive_demand
  
  var demand_at_low: Rate per Month = elasticity_curve(
    current_price, test_price_low, current_demand, price_elasticity
  )
  
  rate revenue_at_low: Currency<USD> per Month
    = test_price_low * demand_at_low
}
```

## Function Reference

### `elasticity_curve(baseline_price, new_price, baseline_demand, price_elasticity) -> Rate per Month`

Calculate demand at different price points using price elasticity.

**Parameters:**
- `baseline_price`: Reference price point
- `new_price`: New price to evaluate
- `baseline_demand`: Demand at baseline price
- `price_elasticity`: Elasticity coefficient (typically -0.5 to -3.0 for normal goods)

**Returns:** Demand at new price point

**Formula:** `demand_new = demand_base * (price_new/price_base)^elasticity`

**Example:**
```pel
// 20% price increase with -1.5 elasticity → ~27% demand drop
var new_demand: Rate per Month = elasticity_curve($100, $120, 1000/1mo, -1.5)
// Result: ~729/1mo
```

### `tiered_pricing_revenue(usage, tier_limits, tier_prices) -> Currency<USD>`

Calculate revenue from tiered/graduated pricing (like AWS, utilities).

**Parameters:**
- `usage`: Customer usage level
- `tier_limits`: Array of tier boundaries (sorted ascending)
- `tier_prices`: Price per unit in each tier (length = tier_limits.length + 1)

**Returns:** Total revenue for usage

**Example:**
```pel
// $1/unit for 0-100, $0.80 for 100-200, $0.60 for 200+
var revenue: Currency<USD> = tiered_pricing_revenue(
  150.0,
  [0.0, 100.0, 200.0],
  [$1, $0.80, $0.60, $0.50]
)
// Result: (100*$1) + (50*$0.80) = $140
```

### `freemium_conversion(free_users, conversion_rate, paid_price) -> Currency<USD> per Month`

Model freemium-to-paid conversion revenue.

**Parameters:**
- `free_users`: Number of free tier users
- `conversion_rate`: Free-to-paid conversion (0.0-1.0)
- `paid_price`: Paid tier monthly price

**Returns:** Monthly recurring revenue from conversions

**Example:**
```pel
// 10,000 free users, 3% convert to $29/mo → $8,700 MRR
var mrr: Currency<USD> per Month = freemium_conversion(10000, 0.03, $29)
```

### `willingness_to_pay(wtp_median, wtp_spread, quantile) -> Currency<USD>`

Calculate willingness-to-pay at different quantiles (e.g., 90th percentile).

**Parameters:**
- `wtp_median`: Median WTP (50th percentile)
- `wtp_spread`: Spread/standard deviation in WTP
- `quantile`: Quantile to calculate (0.0-1.0)

**Returns:** WTP at given quantile

**Uses normal distribution approximation with piecewise z-scores**

**Example:**
```pel
var wtp_p50: Currency<USD> = willingness_to_pay($100, $30, 0.5)   // $100 (median)
var wtp_p90: Currency<USD> = willingness_to_pay($100, $30, 0.9)   // ~$138
var wtp_p10: Currency<USD> = willingness_to_pay($100, $30, 0.1)   // ~$62
```

### `value_based_pricing(cost_to_serve, value_delivered, value_capture_rate) -> Currency<USD>`

Price based on value delivered to customer.

**Parameters:**
- `cost_to_serve`: Cost to deliver product/service
- `value_delivered`: Value created for customer
- `value_capture_rate`: Fraction of value surplus to capture (0.0-1.0)

**Returns:** Value-based price

**Formula:** `price = cost + (value - cost) * capture_rate`

**Example:**
```pel
// Cost $40, deliver $200 value, capture 40% of surplus
var price: Currency<USD> = value_based_pricing($40, $200, 0.4)
// Result: $40 + ($160 * 0.4) = $104
```

## Best Practices

1. **Elasticity modeling**: Use `elasticity_curve()` with elasticity between -0.5 (inelastic) and -3.0 (highly elastic)
2. **Competitive positioning**: Use `competitive_pricing()` for relative pricing strategies
3. **Dynamic pricing**: Use `dynamic_pricing()` for yield management during peak demand
4. **Freemium optimization**: Target 2-5% conversion rates for sustainable freemium models
5. **WTP research**: Calibrate `willingness_to_pay()` with Van Westendorp or Gabor-Granger studies
6. **Tiered pricing**: Use `tiered_pricing_revenue()` for usage-based revenue modeling
7. **Price testing**: Use `price_point_optimization()` to find revenue-maximizing price

## Common Patterns

**Revenue optimization across price points:**
```pel
var prices: Array<Currency<USD>> = [$79, $99, $119, $149]
var best_idx: Int = price_point_optimization(
  prices,
  current_price,
  current_demand,
  elasticity
)
// Use best_idx to select optimal price from array
```

**Freemium revenue modeling:**
```pel
var free_users: Count = 50000
var conversion_rates: Array<Fraction> = [0.02, 0.03, 0.05]  // Scenarios

var conservative_mrr: Currency<USD> per Month = freemium_conversion(free_users, 0.02, $29)
var base_mrr: Currency<USD> per Month = freemium_conversion(free_users, 0.03, $29)
var optimistic_mrr: Currency<USD> per Month = freemium_conversion(free_users, 0.05, $29)
```

**Value-based pricing strategy:**
```pel
var cost: Currency<USD> = $50
var value: Currency<USD> = $500
var conservative_price: Currency<USD> = value_based_pricing(cost, value, 0.2)  // $140
var aggressive_price: Currency<USD> = value_based_pricing(cost, value, 0.5)    // $275
```

**Psychological pricing with anchoring:**
```pel
var reference_price: Currency<USD> = $199  // "Was $199"
var sale_price: Currency<USD> = $99        // "Now $99"
var anchor_multiplier: Fraction = psychological_anchor($199, $99, 0.6)
// Perceived value boost from anchoring effect
```

## Pricing Strategy Frameworks

### Good-Better-Best (3-Tier SaaS)
```pel
var basic_revenue: Currency<USD> per Month = price_discrimination(5000, 0, $29, $0)
var pro_revenue: Currency<USD> per Month = price_discrimination(0, 2000, $99, $0)
var enterprise_revenue: Currency<USD> per Month = price_discrimination(0, 200, $499, $0)

rate total_mrr: Currency<USD> per Month = basic_revenue + pro_revenue + enterprise_revenue
```

### Usage-Based Pricing
```pel
var monthly_revenue: Currency<USD> per Month = usage_based_pricing(
  $50,      // Base platform fee
  125000,   // API calls
  $0.0001   // $0.0001 per call
)
// Result: $50 + $12.50 = $62.50/mo
```

### Penetration Pricing Strategy
```pel
var market_price: Currency<USD> = $100
var our_discount: Fraction = 0.25  // 25% below market
var share_sensitivity: Fraction = 0.6  // 0.6% share per 1% discount

var share_gain: Fraction = penetration_pricing(market_price, our_discount, share_sensitivity)
// Result: 15% market share gained (25% * 0.6)
```
