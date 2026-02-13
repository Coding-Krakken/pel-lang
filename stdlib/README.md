# PEL Standard Library (PEL-STD)

The PEL Standard Library provides battle-tested, reusable economic modeling components.

## Philosophy

- **Correct by default**: All functions are dimensionally sound and type-safe
- **Well-documented**: Each function includes provenance and usage examples  
- **Auditable**: All assumptions are explicit
- **Composable**: Modules work together seamlessly

## Modules

### 1. `demand/` - Demand Forecasting
- Lead generation models
- Seasonality handling
- Bass diffusion curves
- Market saturation

### 2. `funnel/` - Conversion Funnels
- Multi-stage conversion
- Drop-off analysis
- Cohort tracking
- A/B test impact

### 3. `pricing/` - Pricing Models
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

### 5. `cashflow/` - Cash Flow Waterfall
- Accounts receivable timing
- Accounts payable timing
- Payroll schedules
- Tax calculations

### 6. `retention/` - Retention & Churn
- Survival curves
- Cohort retention
- Expansion/contraction revenue
- Net dollar retention

### 7. `capacity/` - Capacity Planning
- Queueing models
- Utilization optimization
- WIP limits
- Bottleneck analysis

### 8. `hiring/` - Hiring & Headcount
- Ramp curves
- Attrition models
- Span of control
- Cost per employee by level

### 9. `shocks/` - Scenario Library
- Recession scenarios
- Supply disruptions
- Demand spikes
- Platform risk events

## Usage

### Import a module

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
import stdlib.unit_econ as ue
import stdlib.cashflow as cf

var payback = ue.payback_period(cac, monthly_margin)
var cash_impact = cf.ar_timing(revenue, payment_terms)
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
