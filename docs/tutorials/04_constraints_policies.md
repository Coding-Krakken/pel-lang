# Tutorial 4: Constraints & Policies

## Overview

Business models have **rules** - cash can't go negative, headcount must be integers, growth targets must be met. Spreadsheets rely on manual checking ("is this cell red?"), which is error-prone and unauditable. PEL makes business rules **executable and enforceable** through:

- **Constraints**: Conditions that must hold (or trigger warnings)
- **Policies**: Actions taken when constraints fail
- **Severity levels**: `fatal` (stops execution) vs `warning` (logged)
- **Automatic validation**: Every simulation run checks all constraints

**Time required**: 25 minutes  
**Prerequisites**: Tutorials 1-3  
**Learning outcomes**: 
- Write constraints for business rules
- Choose appropriate severity levels
- Understand policy execution
- Debug constraint failures

## Why Constraints Matter

### The Spreadsheet Problem

Consider a cash flow spreadsheet:

| Month | Revenue | Costs | Cash Balance |
|-------|---------|-------|--------------|
| Jan   | $50K    | $60K  | $140K        |
| Feb   | $45K    | $60K  | $125K        |
| ...   | ...     | ...   | ...          |
| Aug   | $30K    | $60K  | **-$15K** ❌ |

**Issues**:
- Negative cash discovered **after** model is built
- No automatic alert
- Conditional formatting requires manual setup
- No audit trail of constraint violations

### The PEL Solution

```pel
model CashFlowWithConstraints {
  var cash_balance: TimeSeries<Currency<USD>>
  
  // Constraint: Cash must never go negative
  constraint positive_cash {
    cash_balance[t] >= $0
      with severity(fatal)
      with message("Bankruptcy: cash balance is negative at t={t}")
  }
  
  // Execution stops immediately when violated
  // Clear error message with context
  // Audit log records when/why it failed
}
```

## Constraint Anatomy

Basic syntax:

```pel
constraint <name> {
  <boolean_expression>
    with severity(<fatal|warning>)
    with message("<descriptive error message>")
}
```

**Components**:
1. **Name**: Identifier for this constraint (used in error messages)
2. **Boolean expression**: Condition that must be `true`
3. **Severity**: How to handle violations
4. **Message**: Human-readable explanation (supports variable interpolation)

## Severity Levels

### `fatal`: Non-Negotiable Business Rules

Use for violations that make the model **invalid**:

```pel
model FinancialViability {
  var cash_balance: TimeSeries<Currency<USD>>
  var debt_to_equity_ratio: TimeSeries<Fraction>
  var regulatory_capital_ratio: TimeSeries<Fraction>
  
  // Fatal: Cannot operate with negative cash
  constraint solvency {
    cash_balance[t] >= $0
      with severity(fatal)
      with message("Company insolvent at month {t}: cash = {cash_balance[t]}")
  }
  
  // Fatal: Regulatory requirement (banking)
  constraint capital_adequacy {
    regulatory_capital_ratio[t] >= 0.08
      with severity(fatal)
      with message("Regulatory capital ratio {regulatory_capital_ratio[t]} below minimum 8%")
  }
  
  // Fatal: Debt covenant (loan agreement)
  constraint debt_covenant {
    debt_to_equity_ratio[t] <= 3.0
      with severity(fatal)
      with message("Debt/equity ratio {debt_to_equity_ratio[t]} exceeds covenant limit of 3.0")
  }
}
```

**When execution fails**:
```json
{
  "status": "constraint_violation",
  "constraint": "solvency",
  "time_step": 8,
  "message": "Company insolvent at month 8: cash = -$15,234",
  "severity": "fatal"
}
```

**Use fatal for**:
- Physical impossibilities (negative quantities)
- Legal/regulatory requirements
- Contractual obligations
- Data integrity checks

### `warning`: Targets and Preferences

Use for violations that are **undesirable but not impossible**:

```pel
model GrowthTargets {
  var monthly_revenue: TimeSeries<Currency<USD>>
  var customer_count: TimeSeries<Fraction>
  var team_size: TimeSeries<Fraction>
  
  param revenue_target: Currency<USD> = $1_000_000 {
    source: "board_okrs",
    method: "assumption",
    confidence: 0.80
  }
  
  // Warning: Performance target (aspirational)
  constraint hit_revenue_target {
    monthly_revenue[12] >= revenue_target
      with severity(warning)
      with message("Revenue {monthly_revenue[12]} below annual target {revenue_target}")
  }
  
  // Warning: Efficiency metric (guideline, not hard rule)
  constraint revenue_per_employee {
    (monthly_revenue[t] * 12.0) / team_size[t] >= $200_000
      with severity(warning)
      with message("Revenue per employee below $200K/year at t={t}")
  }
  
  // Warning: Growth rate preference
  constraint maintain_growth {
    customer_count[t+1] >= customer_count[t] * 1.05
      with severity(warning)
      with message("Monthly customer growth below 5% at t={t}")
  }
}
```

**When warning triggered** (execution continues):
```json
{
  "status": "success",
  "warnings": [
    {
      "constraint": "hit_revenue_target",
      "time_step": 12,
      "message": "Revenue $850,000 below annual target $1,000,000",
      "severity": "warning"
    }
  ],
  "results": { ... }
}
```

**Use warnings for**:
- Aspirational targets (OKRs, stretch goals)
- Best practices (efficiency metrics)
- Sanity checks (unexpected ranges)
- Stakeholder preferences

## Time-Indexed Constraints

Constraints can check **every time step** or **specific points**:

### Check All Time Steps

```pel
constraint cash_always_positive {
  cash_balance[t] >= $0
    with severity(fatal)
    with message("Cash negative at t={t}")
}
// Checked for t=0, t=1, t=2, ... until simulation end
```

### Check Specific Time Steps

```pel
constraint launch_readiness {
  team_size[6] >= 10.0
    with severity(warning)
    with message("Team size {team_size[6]} below 10 at launch (month 6)")
}
// Only checked at t=6
```

### Check Final State

```pel
constraint profitability_achieved {
  monthly_profit[t_max] > $0
    with severity(warning)
    with message("Not profitable by end of planning horizon")
}
// t_max = last time step in simulation
```

### Range Checks

```pel
constraint growth_phase_complete {
  // By month 12, revenue should be 2x initial
  monthly_revenue[12] >= monthly_revenue[0] * 2.0
    with severity(warning)
    with message("Revenue growth below 2x in first year")
}
```

## Constraint Composition

Combine multiple conditions:

### AND Conditions

```pel
constraint healthy_growth {
  // Both conditions must be true
  (customer_count[t+1] > customer_count[t]) &&
  (churn_rate[t] < 0.10)
    with severity(warning)
    with message("Unhealthy growth: high churn or negative growth at t={t}")
}
```

### OR Conditions

```pel
constraint funding_or_profitability {
  // At least one must be true
  (cash_balance[t] >= $500_000) ||
  (monthly_profit[t] > $0)
    with severity(fatal)
    with message("Must be profitable OR well-funded at t={t}")
}
```

### Complex Logic

```pel
constraint sustainable_burn_rate {
  // If not profitable, burn must be sustainable
  (monthly_profit[t] >= $0) ||
  (cash_balance[t] / (-monthly_profit[t]) >= 6.0)
    with severity(warning)
    with message("Less than 6 months runway at t={t}")
}
// Translation: "Either profitable, OR have 6+ months of runway"
```

## Policies: Actions on Constraint Violations

**Note**: Policy execution is a **planned feature** (v0.2.0). Current version logs violations but does not execute corrective actions.

Future syntax (illustrative):

```pel
policy maintain_liquidity {
  on_violation(constraint: "minimum_cash") {
    // Automatic actions when cash drops below threshold
    reduce_opex_by(0.20)  // 20% cost cut
    notify_stakeholder("CFO")
    trigger_fundraising_process()
  }
}
```

## Practical Example: SaaS Financial Model with Constraints

```pel
model SaasFinancialConstraints {
  // --- Parameters ---
  param initial_cash: Currency<USD> = $500_000 {
    source: "bank_account",
    method: "observed",
    confidence: 0.99
  }
  
  param monthly_revenue: Currency<USD> = $50_000 {
    source: "billing_system",
    method: "observed",
    confidence: 0.95
  }
  
  param revenue_growth_rate: Rate per Month = 0.15 / 1mo {
    source: "growth_forecast",
    method: "assumption",
    confidence: 0.60
  }
  
  param monthly_opex: Currency<USD> = $60_000 {
    source: "budget_2026",
    method: "assumption",
    confidence: 0.80
  }
  
  param headcount: Fraction = 8.0 {
    source: "hr_system",
    method: "observed",
    confidence: 1.0
  }
  
  // --- Time Series ---
  var revenue: TimeSeries<Currency<USD>>
  revenue[0] = monthly_revenue
  revenue[t+1] = revenue[t] * (1 + revenue_growth_rate)
  
  var profit: TimeSeries<Currency<USD>>
  profit[t] = revenue[t] - monthly_opex
  
  var cash: TimeSeries<Currency<USD>>
  cash[0] = initial_cash
  cash[t+1] = cash[t] + profit[t]
  
  // --- Constraints: Financial Viability ---
  
  // FATAL: Must maintain positive cash (solvency)
  constraint solvency {
    cash[t] >= $0
      with severity(fatal)
      with message("Bankrupt at month {t}: cash = {cash[t]}")
  }
  
  // WARNING: Should have 6+ months runway
  constraint runway {
    (profit[t] >= $0) || (cash[t] / (-profit[t]) >= 6.0)
      with severity(warning)
      with message("Runway below 6 months at t={t}")
  }
  
  // --- Constraints: Growth Targets ---
  
  // WARNING: Board target - 3x revenue in 12 months
  constraint board_target {
    revenue[12] >= revenue[0] * 3.0
      with severity(warning)
      with message("Revenue growth below 3x target: {revenue[12]} vs {revenue[0]}")
  }
  
  // WARNING: Should reach profitability by month 18
  constraint profitability_timeline {
    profit[18] > $0
      with severity(warning)
      with message("Not profitable by month 18: profit = {profit[18]}")
  }
  
  // --- Constraints: Operational Efficiency ---
  
  // WARNING: Revenue per employee should exceed $100K/year
  constraint revenue_per_employee {
    (revenue[t] * 12.0) / headcount >= $100_000
      with severity(warning)
      with message("Revenue per employee below $100K/year at t={t}")
  }
  
  // FATAL: Minimum viable team size
  constraint minimum_team {
    headcount >= 5.0
      with severity(fatal)
      with message("Team size below minimum viable (5)")
  }
  
  // --- Constraints: Data Integrity ---
  
  // FATAL: Sanity check on growth rate
  constraint reasonable_growth {
    revenue_growth_rate >= -0.50 / 1mo && revenue_growth_rate <= 0.50 / 1mo
      with severity(fatal)
      with message("Growth rate {revenue_growth_rate} outside reasonable bounds [-50%, +50%]")
  }
  
  // FATAL: OpEx must be realistic for team size
  constraint opex_sanity {
    monthly_opex >= headcount * $5_000 && monthly_opex <= headcount * $30_000
      with severity(fatal)
      with message("OpEx per employee outside realistic range [$5K-$30K]")
  }
}
```

## Running Constrained Models

### Deterministic Execution

```bash
pel compile saas_constraints.pel
pel run saas_constraints.ir.json --mode deterministic -o results.json
```

**Output (constraint violations)**:
```json
{
  "status": "constraint_violation",
  "constraint": "runway",
  "time_step": 5,
  "severity": "warning",
  "message": "Runway below 6 months at t=5",
  "details": {
    "cash_balance": "$180,000",
    "monthly_burn": "$10,000",
    "months_runway": 18.0
  }
}
```

### Monte Carlo Execution

With uncertainty, constraints are checked **per sample**:

```bash
pel run saas_constraints.ir.json --mode monte_carlo --samples 10000 -o mc_results.json
```

**Output (aggregated violations)**:
```json
{
  "status": "success",
  "samples": 10000,
  "constraint_violations": {
    "solvency": {
      "count": 342,
      "rate": 0.0342,
      "message": "3.42% of scenarios result in bankruptcy"
    },
    "board_target": {
      "count": 6521,
      "rate": 0.6521,
      "message": "65.21% of scenarios miss revenue target"
    }
  },
  "results": { ... }
}
```

**Interpretation**: In 3.4% of scenarios, the company goes bankrupt (fatal). In 65% of scenarios, it misses the board revenue target (warning).

## Debugging Constraint Failures

### Step 1: Identify the Violated Constraint

Error message:
```
Constraint violation: 'solvency'
Time step: 8
Message: Bankrupt at month 8: cash = -$15,234
```

### Step 2: Inspect Time Series Leading to Failure

```bash
pel run model.ir.json --mode deterministic --debug -o debug.json
```

Examine `debug.json`:
```json
{
  "cash": [
    {"t": 0, "value": 500000},
    {"t": 1, "value": 490000},
    ...
    {"t": 7, "value": 12000},
    {"t": 8, "value": -15234}  // ❌ Violation
  ]
}
```

### Step 3: Trace Root Cause

Check dependent variables:
```json
{
  "profit": [
    {"t": 7, "value": -27234},  // Large loss
    ...
  ],
  "revenue": [
    {"t": 7, "value": 32000}  // Low revenue
  ],
  "opex": [
    {"t": 7, "value": 60000}  // High costs
  ]
}
```

**Diagnosis**: OpEx ($60K) exceeds revenue ($32K), causing cash drain.

### Step 4: Adjust Parameters or Constraints

Fix options:
1. **Increase revenue**: Adjust `revenue_growth_rate` upward
2. **Reduce costs**: Lower `monthly_opex`
3. **Add capital**: Increase `initial_cash` or model fundraising
4. **Change constraint**: If bankruptcy is realistic, change to `warning`

## Common Constraint Patterns

### Pattern 1: Non-Negativity

```pel
constraint positive_quantity {
  variable[t] >= 0.0
    with severity(fatal)
    with message("{variable} cannot be negative")
}
```

### Pattern 2: Bounded Range

```pel
constraint valid_percentage {
  variable[t] >= 0.0 && variable[t] <= 1.0
    with severity(fatal)
    with message("{variable} must be in [0, 1]")
}
```

### Pattern 3: Monotonic Increase

```pel
constraint non_decreasing {
  variable[t+1] >= variable[t]
    with severity(warning)
    with message("Unexpected decrease in {variable} at t={t}")
}
```

### Pattern 4: Ratio Constraints

```pel
constraint debt_to_equity_limit {
  debt[t] / equity[t] <= 2.5
    with severity(fatal)
    with message("Debt/equity ratio exceeds 2.5x")
}
```

### Pattern 5: Conditional Constraints

```pel
constraint conditional_check {
  // If revenue > $1M, must have COO
  (revenue[t] < $1_000_000) || (has_coo == true)
    with severity(warning)
    with message("Revenue exceeds $1M but no COO hired")
}
```

## Quiz: Test Your Understanding

1. **When should you use `fatal` vs `warning` severity?**
   <details>
   <summary>Answer</summary>
   
   - **Fatal**: Physical impossibilities, legal requirements, data integrity violations
   - **Warning**: Targets, preferences, efficiency metrics, sanity checks
   </details>

2. **What's wrong with this constraint?**
   ```pel
   constraint profit_target {
     profit[t] >= $100_000
       with message("Profit below target")
   }
   ```
   <details>
   <summary>Answer</summary>
   Missing `with severity(...)`. Must specify either `fatal` or `warning`.
   </details>

3. **How do you check if cash never goes negative?**
   <details>
   <summary>Answer</summary>
   
   ```pel
   constraint solvency {
     cash[t] >= $0
       with severity(fatal)
       with message("Cash is negative at t={t}")
   }
   ```
   The `[t]` means it checks all time steps.
   </details>

4. **In Monte Carlo mode, what does "30% constraint violation rate" mean?**
   <details>
   <summary>Answer</summary>
   In 30% of the simulated scenarios (e.g., 3,000 out of 10,000 samples), the constraint was violated. Indicates significant risk.
   </details>

## Key Takeaways

1. **Constraints encode business rules**: Make assumptions explicit and enforceable
2. **Fatal vs. warning**: Fatal stops execution, warning logs but continues
3. **Time-indexed constraints**: Use `[t]` to check all steps, `[k]` for specific step
4. **Monte Carlo reveals risk**: Constraint violation rates quantify scenario probability
5. **Debug systematically**: Trace from violation → dependent vars → root cause

## Next Steps

- **Tutorial 5**: Provenance & Assumption Governance - track where numbers come from
- **Tutorial 6**: Time-Series Modeling - advanced patterns for recurrence relations
- **Reference**: See `/docs/model/constraints.md` for complete constraint syntax

## Additional Resources

- [Constraint Syntax Reference](/docs/model/constraints.md)
- [Policy Execution (Planned)](/docs/roadmap/policies.md)
- [Debugging Guide](/docs/troubleshooting/constraint_failures.md)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
