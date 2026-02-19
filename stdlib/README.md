# PEL Standard Library (PEL-STD)

The PEL Standard Library provides battle-tested, reusable economic modeling components.

## Philosophy

- **Correct by default**: All functions are dimensionally sound and type-safe
- **Well-documented**: Each function includes provenance and usage examples  
- **Auditable**: All assumptions are explicit
- **Composable**: Modules work together seamlessly

## Modules

### 1. `demand/` - Demand Forecasting 🔜
- Lead generation models
- Seasonality handling
- Bass diffusion curves
- Market saturation

### 2. `funnel/` - Conversion Funnels ✅ **IMPLEMENTED**
- Multi-stage conversion
- Drop-off analysis  
- Cohort tracking
- A/B test impact
- Pre-built archetypes (SaaS, e-commerce, B2B sales)

### 3. `pricing/` - Pricing Models 🔜
- Elasticity curves
- Willingness-to-pay distributions
- Dynamic pricing
- Tiered pricing logic

### 4. `unit_econ/` - Unit Economics ✅ **IMPLEMENTED**
- LTV calculations (simple, discounted, cohort-based)
- Payback period
- LTV:CAC ratio
- Contribution margin
- SaaS magic number, burn multiple, rule of 40
- Usage-based revenue

### 5. `cashflow/` - Cash Flow Waterfall ✅ **IMPLEMENTED**
- Accounts receivable timing (DSO, AR balance)
- Accounts payable timing (DPO, AP balance)
- Payroll schedules (semi-monthly, monthly)
- Burn rate and runway calculations
- Cash conversion cycle
- Free cash flow

### 6. `retention/` - Retention & Churn ✅ **IMPLEMENTED**
- Survival curves (exponential, power law)
- Cohort retention
- Expansion/contraction revenue
- Net dollar retention (NDR)
- Gross dollar retention (GDR)
- Quick ratio

### 7. `capacity/` - Capacity Planning ✅ **IMPLEMENTED (PR-22)**
- Utilization calculations
- Capacity gap analysis
- Resource allocation (priority-weighted, proportional)
- Scaling and expansion planning
- Bottleneck detection
- Utilization metrics (peak, average, variability - using Welford's algorithm)
- Overutilization penalties
- **Enhancements:**
  - Comprehensive input validation (division-by-zero guards, empty array protection)
  - High-performance Welford's algorithm for variance calculation
  - @param/@return/@errors documentation

### 8. `hiring/` - Hiring & Headcount ✅ **IMPLEMENTED (PR-22)**
- Hiring funnel modeling (multi-stage conversion)
- Ramp curves (linear, s-curve, exponential)
- Attrition models and replacement planning
- Workforce capacity planning
- Talent acquisition cost modeling
- Growth hiring calculations
- Effective headcount (ramp-adjusted)
- Team capacity aggregation
- **Enhancements:**
  - High-precision mathematical constants (19-digit Euler's number: 2.71828182845904523536)
  - Comprehensive edge case handling
  - Ramp curve shape validation
  - @param/@return/@errors documentation

### 9. `shocks/` - Scenario Library 🔜
- Recession scenarios
- Supply disruptions
- Demand spikes
- Platform risk events

**Implementation Status:** 6 of 9 modules complete (67%)

## Usage

### Import a module

Import syntax is not yet implemented in the parser and is shown here as aspirational/future syntax.

```pel
import stdlib.unit_econ as ue

model MyModel {
  param arpu: Currency<USD> per Month = $125/1mo {
    source: "billing_system",
    method: "observed",
    confidence: 0.95
  }
  
  param churn: Rate per Month = 0.05/1mo {
    source: "analytics",
    method: "fitted",
    confidence: 0.80
  }
  
  param cac: Currency<USD> = $450 {
    source: "marketing",
    method: "derived",
    confidence: 0.70
  }
  
  // Use stdlib functions
  var ltv = ue.ltv_simple(arpu, churn)  // $2,500
  var ltv_cac = ue.ltv_to_cac_ratio(ltv, cac)  // 5.56
}
```

### Compose functions

```pel
// Use direct function calls for now.

var payback = payback_period(cac, monthly_margin)
var ar_balance = accounts_receivable(revenue, 45d, payment_terms)
```

## Governance

All stdlib modules:
- **MUST** be type-safe and pass conformance tests
- **MUST** include comprehensive test coverage
- **MUST** document all assumptions explicitly
- **SHOULD** include real-world validation data where possible

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- How to propose new stdlib modules
- Testing requirements
- Documentation standards
- Peer review process

## Versioning

Stdlib follows semantic versioning:
- **Major**: Breaking changes to function signatures
- **Minor**: New functions (backward compatible)
- **Patch**: Bug fixes, documentation improvements

Current version: **0.1.0**

## License

AGPL-3.0-or-later OR Commercial - Same as PEL core

See [LICENSE](../LICENSE) and [COMMERCIAL-LICENSE.md](../COMMERCIAL-LICENSE.md) for details.

---

**Status Legend:**
- ✅ Implemented
- 🚧 In Progress
- 🔜 Planned
