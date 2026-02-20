# Demand Module

Functions for demand forecasting, seasonality, market dynamics, and growth modeling.

## Key Functions

### Core Demand Forecasting
- `seasonal_multiplier()` - Calculate seasonal demand variations
- `lead_generation()` - Generate leads from marketing spend
- `funnel_demand()` - Demand flowing through conversion stages
- `elasticity_demand()` - Price elasticity impact on demand
- `market_saturation()` - Market penetration and saturation effects
- `competitor_impact()` - Competitive pressure on demand
- `event_driven_spike()` - Event-driven demand spikes
- `churn_demand_feedback()` - Churn feedback loop impact

### Advanced Demand Models
- `bass_diffusion()` - Bass diffusion model for new product adoption
- `aggregate_demand()` - Total demand across multiple channels
- `demand_decay()` - Time decay for promotions/events
- `viral_coefficient()` - Viral growth k-factor
- `constrained_demand()` - Capacity-constrained demand with backlog
- `addressable_segment()` - Addressable market calculation (TAM/SAM)
- `network_demand()` - Network effects on demand
- `demand_forecast()` - Trend-based demand forecasting
- `weighted_demand()` - Weighted average across scenarios

## Use Cases
- SaaS demand forecasting and lead generation
- Seasonal business planning (retail, hospitality, e-commerce)
- New product launch modeling (Bass diffusion)
- Viral growth analysis (social networks, marketplaces)
- Competitive strategy and market share analysis
- Event-driven demand modeling (Black Friday, product launches)
- Capacity planning with demand constraints

## Production-Ready Standards

This module follows Microsoft-production-grade quality standards:

### Robustness & Validation
- **Input validation**: All 18 functions include guards against invalid inputs
- **Boundary clamping**: Fraction parameters clamped to valid ranges (0.0-1.0)
- **Negative value handling**: Negative demands/counts return safe defaults (0)
- **Array safety**: Empty array checks with safe default returns
- **Overflow prevention**: Exponential functions capped (max 100 periods)

### Documentation
- **Structured @param tags**: Every parameter documented with constraints
- **@return tags**: Expected output ranges and units clearly specified
- **@errors tags**: Error handling behavior explicitly documented
- **Example usage**: Real-world examples with realistic values
- **Contract annotations**: @Monotonic, @Bounded annotations for formal verification

### Mathematical Correctness
- **High-precision constants**: Euler's number (e) with 19-digit precision
- **Numerical stability**: Proper handling of exponential decay, bounds checking
- **Dimensionally sound**: All Rate per Month, Currency, Duration types correctly used
- **Formula documentation**: Each function documents underlying formula

### Test Coverage
- **17 unit tests**: All core functionality validated
- **Edge cases**: Zero values, boundary conditions, empty arrays
- **Integration ready**: Functions compose cleanly with other stdlib modules

## Related Modules

- **[Pricing Module](../pricing/README.md)** — pricing elasticity, willingness-to-pay. Use `elasticity_demand()` with pricing functions for revenue optimization.
- **[Funnel Module](../funnel/README.md)** — conversion funnel modeling. Use `funnel_demand()` to model stage-by-stage conversion.
- **[Retention Module](../retention/README.md)** — churn and retention. Use `churn_demand_feedback()` to model demand impact of churn.

## Example

```pel
import std.demand.*

model SaaSDemandForecast {
  // Seasonal parameters
  param current_month: Int = 12 {
    source: "calendar",
    method: "observed",
    confidence: 1.0
  }
  
  param seasonality_strength: Fraction = 0.25 {
    source: "historical_sales_data",
    method: "derived",
    confidence: 0.9
  }
  
  param peak_month: Int = 11 {  // November (Black Friday)
    source: "business_planning",
    method: "assumption",
    confidence: 1.0
  }
  
  // Marketing spend
  param monthly_marketing_budget: Currency<USD> = $50000 {
    source: "marketing_plan",
    method: "assumption",
    confidence: 1.0
  }
  
  param cost_per_lead: Currency<USD> = $75 {
    source: "ad_platform_metrics",
    method: "observed",
    confidence: 0.95
  }
  
  param marketing_efficiency: Fraction = 0.85 {
    source: "campaign_performance",
    method: "derived",
    confidence: 0.9
  }
  
  // Competitive environment
  param baseline_demand: Rate per Month = 500 / 1mo {
    source: "sales_pipeline",
    method: "observed",
    confidence: 0.95
  }
  
  param competitor_market_share: Fraction = 0.35 {
    source: "market_research",
    method: "estimate",
    confidence: 0.75
  }
  
  param competitive_intensity: Fraction = 0.7 {
    source: "competitive_analysis",
    method: "judgment",
    confidence: 0.7
  }
  
  // Calculated metrics
  var seasonal_adj: Fraction = seasonal_multiplier(current_month, seasonality_strength, peak_month)
  
  var leads_generated: Count = lead_generation(monthly_marketing_budget, cost_per_lead, marketing_efficiency)
  
  var competitive_demand: Rate per Month = competitor_impact(baseline_demand, competitor_market_share, competitive_intensity)
  
  rate total_demand: Rate per Month
    = competitive_demand * seasonal_adj
  
  // Forecast 6 months ahead with 5% monthly growth
  var forecast_6mo: Rate per Month = demand_forecast(total_demand, 0.05, 6)
}
```

## Function Reference

### `seasonal_multiplier(month, seasonality_amplitude, peak_month) -> Fraction`

Calculate seasonal demand multiplier using sinusoidal curve.

**Parameters:**
- `month`: Month number (1-12, auto-clamped)
- `seasonality_amplitude`: Strength of seasonality 0.0-1.0
- `peak_month`: Month of peak demand (1-12)

**Returns:** Multiplier in range `[1-amplitude, 1+amplitude]`

**Example:**
```pel
var dec_multiplier: Fraction = seasonal_multiplier(12, 0.3, 12)  // ~1.3 (30% boost)
var jun_multiplier: Fraction = seasonal_multiplier(6, 0.3, 12)   // ~0.7 (30% drop)
```

### `bass_diffusion(innovation_rate, imitation_rate, market_potential, current_adopters) -> Count`

Classic Bass diffusion model for new product adoption (Rogers' innovation curve).

**Parameters:**
- `innovation_rate`: Coefficient of innovation (p) — adopters from advertising
- `imitation_rate`: Coefficient of imitation (q) — adopters from word-of-mouth
- `market_potential`: Total addressable market
- `current_adopters`: Cumulative adopters to date

**Returns:** New adopters in next period

**Formula:** `dN/dt = (p + q*N/M) * (M - N)`

**Example:**
```pel
// Typical SaaS product: low innovation, high imitation
var new_users: Count = bass_diffusion(0.03, 0.38, 100000, 15000)
```

### `viral_coefficient(invites_per_user, invite_conversion) -> Fraction`

Calculate viral k-factor for viral growth loops.

**Parameters:**
- `invites_per_user`: Average invites sent per user
- `invite_conversion`: Invite-to-signup conversion rate

**Returns:** Viral coefficient (k > 1 = viral growth, k < 1 = sub-viral)

**Example:**
```pel
var k_factor: Fraction = viral_coefficient(5.0, 0.25)  // k=1.25 (viral!)
```

## Best Practices

1. **Seasonality modeling**: Use `seasonal_multiplier()` with historical peak months, calibrate amplitude to data
2. **Lead gen planning**: Combine `lead_generation()` with funnel conversion rates for pipeline forecasting
3. **New product launches**: Use `bass_diffusion()` for S-curve adoption, tune p/q coefficients to category
4. **Viral products**: Monitor `viral_coefficient()` — need k>1 for sustainable viral growth
5. **Market saturation**: Track with `market_saturation()` to model growth headroom
6. **Competitive dynamics**: Use `competitor_impact()` for scenario planning and war gaming
7. **Event planning**: Model spikes with `event_driven_spike()` for Black Friday, product launches, etc.

## Common Patterns

**Multi-channel demand aggregation:**
```pel
var direct_demand: Rate per Month = lead_generation(direct_budget, direct_cpl, direct_efficiency)
var partner_demand: Rate per Month = lead_generation(partner_budget, partner_cpl, partner_efficiency)
var online_demand: Rate per Month = lead_generation(online_budget, online_cpl, online_efficiency)

var total_pipeline: Rate per Month = aggregate_demand([direct_demand, partner_demand, online_demand])
```

**Scenario-weighted forecasting:**
```pel
var pessimistic: Rate per Month = demand_forecast(baseline, -0.05, 12)  // -5% decline
var base_case: Rate per Month = demand_forecast(baseline, 0.03, 12)     // 3% growth
var optimistic: Rate per Month = demand_forecast(baseline, 0.15, 12)    // 15% growth

var expected_demand: Rate per Month = weighted_demand(
  [pessimistic, base_case, optimistic],
  [0.2, 0.5, 0.3]  // Probabilities
)
```

**Capacity-constrained demand:**
```pel
var raw_demand: Rate per Month = lead_generation(budget, cpl, efficiency)
var serviceable_demand: Rate per Month = constrained_demand(
  raw_demand,
  capacity_limit,
  backlog_conversion_rate
)
```
