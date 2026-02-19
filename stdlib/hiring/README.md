# Hiring Module

Functions for workforce planning, hiring funnels, ramp time, and talent acquisition modeling.

## Key Functions

### Hiring Funnel
- `hiring_funnel()` - Multi-stage hiring conversion (applicants → offers → hires)
- `offer_acceptance_rate()` - Percentage of offers accepted
- `hiring_velocity()` - Time from application to hire
- `cost_per_hire()` - Total recruiting cost / hires

### Workforce Planning
- `required_headcount()` - Headcount needed for target capacity
- `hiring_plan()` - Hiring schedule to reach target headcount
- `attrition_replacement()` - Hires needed to offset attrition
- `growth_hiring()` - Additional hires for growth

### Ramp & Productivity
- `ramp_time()` - Time to full productivity
- `ramp_curve()` - Productivity over time (0% → 100%)
- `effective_headcount()` - Headcount adjusted for ramp
- `team_productivity()` - Total output accounting for ramp/attrition

### Capacity Planning
- `headcount_capacity()` - Output capacity per employee
- `team_capacity()` - Total team output capacity
- `capacity_per_hire()` - Incremental capacity from new hire
- `hiring_lag_impact()` - Capacity gap due to hiring delays

### Cost Modeling
- `recruiting_cost()` - Cost to fill position
- `onboarding_cost()` - Cost to train new hire
- `total_talent_cost()` - Recruiting + onboarding + comp
- `hire_roi()` - Value created vs cost of hire

## Use Cases
- Engineering team growth planning
- Sales hiring (quota capacity planning)
- Support team staffing
- Manufacturing workforce planning
- Services delivery capacity

## Production-Ready Enhancements (PR-22)

This module has been enhanced with Microsoft-production-grade quality standards:

### Robustness & Validation
- **Division-by-zero protection**: All 21 functions include guards against division by zero
- **Empty array handling**: `team_capacity()` returns 0 when passed empty arrays
- **Negative value validation**: Negative inputs (applicants, hires, costs) return safe defaults
- **Input clamping**: Conversion rates, efficiency, and progress values clamped to [0,1]
- **Ramp shape validation**: `ramp_curve()` validates shape parameter ("linear", "s-curve", "exponential") with safe fallback to "linear"
- **Already-at-target handling**: `hiring_plan()` returns 0 when current headcount equals or exceeds target

### Documentation
- **Structured @param tags**: Every parameter documented with constraints and valid ranges
- **@return tags**: Expected output ranges and units clearly specified
- **@errors tags**: Error handling behavior explicitly documented
- **Real-world examples**: Engineering hiring, sales quota planning, support staffing

### Performance & Numerical Precision
- **High-precision Euler's number**: 19-digit precision (2.71828182845904523536) for exponential ramp curves
- **O(n) complexity**: All functions have linear or better time complexity
- **Efficient array operations**: Manual loops instead of unsupported array methods

### Test Coverage
- **20 unit tests**: All core functionality validated  
- **26 edge case tests**: Division-by-zero, negative values, ramp curve shapes, boundary conditions, conversion rate validation
- **9 integration tests**: End-to-end workforce planning workflows
- **7 performance tests**: Compilation time benchmarks for large teams (100+ roles)

## Related Modules

- **[Capacity Module](../capacity/README.md)** — capacity planning functions that provide inputs to hiring decisions. Use `capacity_gap()` to determine shortfalls, then feed into `required_headcount()` and `hiring_plan()`. See integration tests for end-to-end examples.

## Example
```pel
import std.hiring.*

model EngineeringGrowth {
  param current_engineers: Count<Person> = 50 {
    source: "hr_system",
    method: "observed",
    confidence: 1.0
  }
  
  param target_engineers: Count<Person> = 100 {
    source: "growth_plan",
    method: "assumption",
    confidence: 0.8
  }
  
  param planning_horizon: Duration<Month> = 12mo {
    source: "model",
    method: "assumption",
    confidence: 1.0
  }
  
  param attrition_rate: Rate per Year = 0.15/1yr {
    source: "hr_analytics",
    method: "derived",
    confidence: 0.85
  }
  
  // Hiring funnel metrics
  param applicants_per_month: Count<Applicant> = 200 {
    source: "ats",
    method: "observed",
    confidence: 0.95
  }
  
  param screen_pass_rate: Fraction = 0.30 {
    source: "recruiting",
    method: "derived",
    confidence: 0.90
  }
  
  param interview_pass_rate: Fraction = 0.25 {
    source: "recruiting",
    method: "derived",
    confidence: 0.90
  }
  
  param offer_acceptance: Fraction = 0.70 {
    source: "recruiting",
    method: "derived",
    confidence: 0.85
  }
  
  // Calculate hiring funnel
  rate hires_per_month: Count<Person>
    = std.hiring.hiring_funnel(
        applicants_per_month,
        [screen_pass_rate, interview_pass_rate, offer_acceptance]
      )
  
  // Attrition replacement
  rate replacement_hires: Count<Person>
    = std.hiring.attrition_replacement(
        current_engineers,
        attrition_rate
      )
  
  // Growth hiring
  rate growth_hires: Count<Person>
    = std.hiring.growth_hiring(
        current_engineers,
        target_engineers,
        planning_horizon
      )
  
  rate total_hiring_need: Count<Person>
    = replacement_hires + growth_hires
  
  // Ramp time impact
  param ramp_time_months: Duration<Month> = 3mo {
    source: "hr",
    method: "assumption",
    confidence: 0.80
  }
  
  param ramped_headcount: Count<Person> = 45 {
    source: "hr",
    method: "derived",
    confidence: 0.95
  }
  
  param ramping_headcount: Count<Person> = 5 {
    source: "hr",
    method: "derived",
    confidence: 0.95
  }
  
  param avg_ramp_progress: Fraction = 0.60 {
    source: "hr",
    method: "derived",
    confidence: 0.80
  }
  
  rate effective_headcount: Count<Person>
    = std.hiring.effective_headcount(
        ramped_headcount,
        ramping_headcount,
        avg_ramp_progress
      )
  
  // Cost modeling
  param cost_per_hire: Currency<USD> per Hire = $25000 {
    source: "recruiting",
    method: "derived",
    confidence: 0.85
  }
  
  param annual_comp: Currency<USD> per Hire = $150000 {
    source: "compensation",
    method: "assumption",
    confidence: 0.90
  }
  
  rate monthly_hiring_cost: Currency<USD> per Month
    = hires_per_month * cost_per_hire / 1mo
  
  export hires_per_month, total_hiring_need, effective_headcount, monthly_hiring_cost
}
```
