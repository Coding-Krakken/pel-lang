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

## Advanced Constraint Patterns

### Multi-Condition Constraints

Check compound conditions using logical operators:

```pel
model SaaSOpsAdvanced {
  var revenue: TimeSeries<Currency<USD>>
  var costs: TimeSeries<Currency<USD>>
  var gross_margin: TimeSeries<Fraction>
  
  gross_margin[t] = (revenue[t] - costs[t]) / revenue[t]
  
  // Constraint: Margin between 30% and 80% (outside this is suspicious)
  constraint reasonable_margin {
    (gross_margin[t] >= 0.30) and (gross_margin[t] <= 0.80)
      with severity(warning)
      with message("Gross margin {gross_margin[t]} at t={t} is outside 30-80% range")
  }
  
  // Constraint: Revenue growth year-over-year must be positive
  constraint yoy_growth {
    (t >= 12) implies (revenue[t] > revenue[t-12])
      with severity(warning)
      with message("YoY revenue declined: {revenue[t]} vs {revenue[t-12]}")
  }
  
  // Constraint: No single month can drop more than 20%
  constraint month_over_month_stability {
    (t >= 1) implies (revenue[t] >= 0.80 * revenue[t-1])
      with severity(fatal)
      with message("Revenue dropped {(revenue[t-1] - revenue[t])/revenue[t-1]} from t={t-1} to t={t}")
  }
}
```

### Aggregation Constraints

Check properties of entire time series:

```pel
model AggregateChecks {
  var headcount: TimeSeries<Fraction>
  var revenue_per_employee: TimeSeries<Currency<USD>>
  
  revenue_per_employee[t] = revenue[t] / headcount[t]
  
  // Constraint: Average revenue per employee over 36 months must exceed $150K
 constraint productivity_target {
    sum(revenue[t] for t in 0..35) / sum(headcount[t] for t in 0..35) >= $150_000
      with severity(warning)
      with message("Average RPE over 36 months is below target")
  }
  
  // Constraint: Maximum headcount never exceeds 500
  constraint headcount_cap {
    max(headcount[t] for t in 0..120) <= 500.0
      with severity(fatal)
      with message("Headcount cap exceeded")
  }
  
  // Constraint: Minimum cash balance across all periods > $100K
  constraint cash_reserve {
    min(cash_balance[t] for t in 0..60) >= $100_000
      with severity(fatal)
      with message("Cash reserve breached: min was {min(cash_balance[t] for t in 0..60)}")
  }
}
```

**Note**: `sum()`, `max()`, `min()` are hypothetical stdlib functions. Current PEL may require explicit loops or manual checks.

### Threshold Constraints with Soft Boundaries

Use warnings for "yellow zone" and fatal for "red zone":

```pel
model RiskZones {
  var debt_to_equity: TimeSeries<Fraction>
  
  // Yellow zone: D/E ratio above 1.5 (warning)
  constraint leverage_warning {
    debt_to_equity[t] <= 1.5
      with severity(warning)
      with message("Leverage ratio {debt_to_equity[t]} exceeds 1.5 (caution zone)")
  }
  
  // Red zone: D/E ratio above 3.0 (fatal)
  constraint leverage_fatal {
    debt_to_equity[t] <= 3.0
      with severity(fatal)
      with message("Leverage ratio {debt_to_equity[t]} exceeds 3.0 (critical zone)")
  }
}
```

### Conditional Constraints

Apply constraints only when certain conditions hold:

```pel
model ConditionalValidation {
  param is_profitable: Bool = true
  var net_income: TimeSeries<Currency<USD>>
  var marketing_spend: TimeSeries<Currency<USD>>
  
  // Only enforce marketing cap if we're profitable
  constraint marketing_cap {
    is_profitable implies (marketing_spend[t] <= 0.30 * revenue[t])
      with severity(warning)
      with message("Marketing spend exceeds 30% of revenue while profitable")
  }
  
  // Different constraint if not profitable: stricter cap
  constraint burn_control {
    (not is_profitable) implies (marketing_spend[t] <= 0.15 * revenue[t])
      with severity(fatal)
      with message("Marketing spend exceeds 15% of revenue while unprofitable")
  }
}
```

### Rate-of-Change Constraints

Limit how fast variables can change:

```pel
model GrowthLimits {
  var customers: TimeSeries<Fraction>
  
  // Maximum 50% month-over-month growth (prevents unrealistic scaling)
  constraint realistic_growth_cap {
    (t >= 1) implies (customers[t] <= 1.50 * customers[t-1])
      with severity(warning)
      with message("Customer growth exceeds 50% MoM at t={t}")
  }
  
  // Minimum 95% retention (max 5% MoM decline)
  constraint minimum_retention {
    (t >= 1) implies (customers[t] >= 0.95 * customers[t-1])
      with severity(fatal)
      with message("Customer decline exceeds 5% at t={t}")
  }
}
```

### Cross-Variable Ratio Constraints

Enforce relationships between multiple variables:

```pel
model UnitEconomics {
  var ltv: TimeSeries<Currency<USD>>
  var cac: TimeSeries<Currency<USD>>
  
  // LTV:CAC ratio must be at least 3:1 for healthy SaaS
  constraint ltv_cac_ratio {
    ltv[t] >= 3.0 * cac[t]
      with severity(warning)
      with message("LTV:CAC ratio is {ltv[t]/cac[t]} at t={t}, below 3:1 target")
  }
  
  // Payback period must be under 18 months
  var payback_months: TimeSeries<Fraction>
  payback_months[t] = cac[t] / (revenue_per_customer[t] / 12.0)
  
  constraint payback_period {
    payback_months[t] <= 18.0
      with severity(warning)
      with message("Payback period is {payback_months[t]} months at t={t}")
  }
}
```

## Debugging Constraint Failures

### Step-by-Step Debugging Process

When a constraint fails:

```bash
$ pel run model.ir.json --mode deterministic

ERROR: Constraint 'positive_cash' violated
  At time step: t=14
  Condition: cash_balance[14] >= $0
  Actual: cash_balance[14] = -$23,450
  Message: Bankruptcy: cash balance is negative at t=14
```

**Debugging workflow**:

#### 1. Identify the Time of Failure

```
t=14 → Month 14 (February of Year 2)
```

#### 2. Inspect Variable Values at That Time

```bash
pel run model.ir.json --mode deterministic --trace cash_balance,revenue,costs
```

Output:
```
t=0:  cash_balance=$500K, revenue=$100K, costs=$80K
t=1:  cash_balance=$520K, revenue=$105K, costs=$82K
...
t=13: cash_balance=$15K, revenue=$120K, costs=$125K  ← Warning: costs > revenue
t=14: cash_balance=-$23.5K, revenue=$115K, costs=$153.5K  ← Failure
```

#### 3. Trace Dependencies

"Why are costs so high at t=14?"

```pel
var costs[t] = fixed_costs + variable_costs[t] + marketing_spend[t]

// Inspect components at t=14:
// fixed_costs = $50K (param)
// variable_costs[14] = ???
// marketing_spend[14] = ???
```

```bash
pel run model.ir.json --mode deterministic --trace fixed_costs,variable_costs,marketing_spend
```

Output:
```
t=14: 
  fixed_costs = $50K
  variable_costs[14] = $45K
  marketing_spend[14] = $58.5K  ← Suspicious spike!
```

#### 4. Investigate Root Cause

```pel
var marketing_spend[t] = revenue[t] * marketing_spend_pct

// Why did marketing_spend_pct spike?
param marketing_spend_pct: Fraction = 0.50  ← HERE: 50% is too high!
```

**Fix**: Adjust parameter to reasonable level (e.g., 0.20).

### Using Assertions for Intermediate Validation

```pel
model DebugFriendly {
  var revenue: TimeSeries<Currency<USD>>
  var costs: TimeSeries<Currency<USD>>
  var cash_balance: TimeSeries<Currency<USD>>
  
  // Intermediate assertion: revenue should never be zero
  constraint revenue_nonzero {
    revenue[t] > $0
      with severity(fatal)
      with message("Revenue is zero at t={t} (data error?)")
  }
  
  // Intermediate assertion: costs should be less than 2× revenue
  constraint costs_sanity {
    costs[t] <= 2.0 * revenue[t]
      with severity(warning)
      with message("Costs ({costs[t]}) > 2× revenue ({revenue[t]}) at t={t}")
  }
  
  // Main constraint: cash must be positive
  cash_balance[0] = initial_cash
  cash_balance[t+1] = cash_balance[t] + revenue[t] - costs[t]
  
  constraint positive_cash {
    cash_balance[t] >= $0
      with severity(fatal)
      with message("Cash negative at t={t}: {cash_balance[t]}")
  }
}
```

**Benefit**: Earlier failure with more specific message (easier to debug).

### Constraint Violation Reports

After a failed run, PEL outputs detailed reports:

```json
{
  "status": "constraint_violated",
  "constraint": "positive_cash",
  "severity": "fatal",
  "time_step": 14,
  "message": "Cash negative at t=14: $-23,450",
  "context": {
    "cash_balance[14]": -23450,
    "revenue[14]": 115000,
    "costs[14]": 153500,
    "marketing_spend[14]": 58500,
    "marketing_spend_pct": 0.50
  }
}
```

**Use for**:
- Automated testing (CI/CD)
- Audit trails (compliance)
- Debugging logs (copy-paste into issues)

## Monte Carlo Risk Analysis

### Constraint Violation Rates

In Monte Carlo mode, constraints are checked across all samples:

```bash
pel run model.ir.json --mode monte_carlo --samples 5000 -o results.json
```

Output:
```json
{
  "constraints": {
    "positive_cash": {
      "violations": 1250,
      "total_samples": 5000,
      "violation_rate": 0.25,
      "severity": "fatal",
      "first_violation_time": {
        "min_t": 8,
        "max_t": 24,
        "mean_t": 14.3
      }
    },
    "ltv_cac_ratio": {
      "violations": 3200,
      "total_samples": 5000,
      "violation_rate": 0.64,
      "severity": "warning"
    }
  }
}
```

**Interpretation**:
- **positive_cash**: 25% of scenarios lead to bankruptcy (high risk!)
- **Failure occurs between t=8 and t=24** (average t=14.3)
- **ltv_cac_ratio**: 64% of scenarios have poor unit economics (warning)

### Adjusting Parameters to Reduce Risk

**Goal**: Reduce bankruptcy risk to < 5%.

**Approach 1**: Increase initial cash

```pel
// Before
param initial_cash: Currency<USD> = $500_000

// After
param initial_cash: Currency<USD> = $800_000  // +60% buffer
```

Re-run:
```json
{
  "positive_cash": {
    "violation_rate": 0.04  // ← Now 4% (below 5% target)
  }
}
```

**Approach 2**: Reduce costs

```pel
// Before
param fixed_costs: Currency<USD> = $50_000 / 1mo

// After
param fixed_costs: Currency<USD> = $40_000 / 1mo  // -20% costs
```

**Approach 3**: Add risk mitigation constraint

```pel
model RiskMitigation {
  var cash_balance: TimeSeries<Currency<USD>>
  var emergency_funding: Currency<USD> = $200_000
  
  // Trigger emergency funding if cash falls below $100K
  var cash_with_backup[t] = 
    if cash_balance[t] < $100_000
      then cash_balance[t] + emergency_funding
      else cash_balance[t]
  
  constraint positive_cash {
    cash_with_backup[t] >= $0
      with severity(fatal)
  }
}
```

### Sensitivity Analysis with Constraints

Identify which parameters most impact constraint violations:

```bash
# Test parameter ranges
pel run model.ir.json --mode monte_carlo --samples 2000 \
  --set revenue_growth=Normal(μ=0.10/1mo,σ=0.02/1mo) \
  -o results_low_growth.json

pel run model.ir.json --mode monte_carlo --samples 2000 \
  --set revenue_growth=Normal(μ=0.15/1mo,σ=0.02/1mo) \
  -o results_med_growth.json

pel run model.ir.json --mode monte_carlo --samples 2000 \
  --set revenue_growth=Normal(μ=0.20/1mo,σ=0.02/1mo) \
  -o results_high_growth.json

# Compare violation rates
python3 << EOF
import json

files = ['results_low_growth.json', 'results_med_growth.json', 'results_high_growth.json']
for f in files:
    with open(f) as fp:
        data = json.load(fp)
    vr = data['constraints']['positive_cash']['violation_rate']
    print(f"{f}: {vr*100:.1f}% bankruptcy risk")
EOF
```

Output:
```
results_low_growth.json: 45.2% bankruptcy risk
results_med_growth.json: 18.3% bankruptcy risk
results_high_growth.json: 3.1% bankruptcy risk
```

**Conclusion**: Revenue growth is the most sensitive parameter.

## Real-World Constraint Examples

### Example 1: Regulatory Compliance (Financial Services)

```pel
model BankCapitalRequirements {
  var tier1_capital: TimeSeries<Currency<USD>>
  var risk_weighted_assets: TimeSeries<Currency<USD>>
  var tier1_ratio: TimeSeries<Fraction>
  
  tier1_ratio[t] = tier1_capital[t] / risk_weighted_assets[t]
  
  // Basel III: Tier 1 capital ratio must be ≥ 6%
  constraint basel_iii_tier1 {
    tier1_ratio[t] >= 0.06
      with severity(fatal)
      with message("Tier 1 capital ratio {tier1_ratio[t]} violates Basel III minimum at t={t}")
  }
  
  // Internal policy: maintain 8% buffer (above regulatory minimum)
  constraint internal_capital_policy {
    tier1_ratio[t] >= 0.08
      with severity(warning)
      with message("Tier 1 ratio {tier1_ratio[t]} below internal policy at t={t}")
  }
}
```

### Example 2: SaaS Board Targets

```pel
model SaaSBoardMetrics {
  var arr: TimeSeries<Currency<USD>>  // Annual Recurring Revenue
  var revenue_retention: TimeSeries<Fraction>  // Net Revenue Retention
  var rule_of_40: TimeSeries<Fraction>
  
  // Rule of 40: growth% + profit_margin% >= 40%
  rule_of_40[t] = ((arr[t] - arr[t-12]) / arr[t-12]) + profit_margin[t]
  
  constraint rule_of_40_compliance {
    (t >= 12) implies (rule_of_40[t] >= 0.40)
      with severity(warning)
      with message("Rule of 40 is {rule_of_40[t]*100}% at t={t}, below 40%")
  }
  
  // Net Revenue Retention (NRR) >= 100% (no net churn)
  constraint nrr_target {
    revenue_retention[t] >= 1.00
      with severity(warning)
      with message("NRR is {revenue_retention[t]*100}% at t={t}, below 100%")
  }
  
  // Annual growth rate >= 100% (T2D3 path: triple-triple-double-double-double)
  constraint t2d3_growth {
    (t == 12) implies (arr[t] >= 3.0 * arr[0])  // Year 1: Triple
      with severity(warning)
    
    (t == 24) implies (arr[t] >= 9.0 * arr[0])  // Year 2: Triple again (3×3=9×)
      with severity(warning)
    
    (t == 36) implies (arr[t] >= 18.0 * arr[0])  // Year 3: Double (9×2=18×)
      with severity(warning)
  }
}
```

### Example 3: E-commerce Inventory Management

```pel
model InventoryConstraints {
  var inventory_units: TimeSeries<Fraction>
  var days_of_inventory: TimeSeries<Duration>
  var stockout_risk: TimeSeries<Fraction>
  
  days_of_inventory[t] = inventory_units[t] / daily_sales_rate[t]
  
  // Minimum inventory: 14 days of stock
  constraint min_inventory {
    days_of_inventory[t] >= 14day
      with severity(warning)
      with message("Inventory is only {days_of_inventory[t]} at t={t}, risk of stockout")
  }
  
  // Maximum inventory: 90 days (avoid overstock)
  constraint max_inventory {
    days_of_inventory[t] <= 90day
      with severity(warning)
      with message("Inventory is {days_of_inventory[t]} at t={t}, risk of obsolescence")
  }
  
  // Stockout risk must be < 5%
  constraint stockout_risk_limit {
    stockout_risk[t] <= 0.05
      with severity(fatal)
      with message("Stockout risk {stockout_risk[t]} exceeds 5% at t={t}")
  }
}
```

## Constraint Testing Strategies

### 1. Boundary Testing

Test edge cases:

```pel
model BoundaryTests {
  var ltv: Currency<USD> = $1000
  var cac: Currency<USD> = $333.33
  
  constraint ltv_cac {
    ltv >= 3.0 * cac
      with severity(fatal)
  }
  
  // Test cases:
  // ltv=$1000, cac=$333.33 → ratio=3.00 → PASS (boundary)
  // ltv=$1000, cac=$333.34 → ratio=2.999 → FAIL
  // ltv=$1000, cac=$333.32 → ratio=3.001 → PASS
}
```

### 2. Regression Testing

Add constraints as tests:

```pel
// tests/regression/cash_flow_regression.pel
model CashFlowRegression {
  // Known-good scenario from 2025-Q4
  param initial_cash: Currency<USD> = $500_000
  param monthly_revenue: Currency<USD> = $100_000 / 1mo
  param monthly_costs: Currency<USD> = $80_000 / 1mo
  
  var cash[0] = initial_cash
  var cash[t+1] = cash[t] + monthly_revenue - monthly_costs
  
  // Regression: Cash at t=12 should be $740K (verified in previous model)
  constraint regression_cash_t12 {
    cash[12] == $740_000
      with severity(fatal)
      with message("Regression failed: expected $740K, got {cash[12]}")
  }
}
```

Run in CI/CD:
```bash
pel compile tests/regression/*.pel -o regression.ir.json
pel run regression.ir.json --mode deterministic || exit 1
```

### 3. Fuzz Testing

Generate random parameters, check constraints hold:

```bash
# Generate 100 random parameter sets
python3 generate_fuzz_params.py --count 100 --output fuzz_params.json

# Run model with each parameter set
for params in $(cat fuzz_params.json | jq -c '.[]'); do
  pel run model.ir.json --mode deterministic --params "$params" || echo "FAIL: $params"
done
```

## Constraint Performance Considerations

### Constraint Evaluation Cost

```pel
// ❌ Expensive: Checks t² conditions
constraint expensive {
  for all t1 in 0..120:
    for all t2 in 0..120:
      revenue[t1] != revenue[t2]  // All revenues are unique (slow!)
  with severity(warning)
}

// ✅ Cheap: Checks t conditions
constraint cheap {
  revenue[t] > $0
    with severity(fatal)
}
```

**Rule of thumb**: Constraints with nested loops over time steps are expensive.

### Lazy Evaluation

PEL evaluates constraints lazily in some mode:

```pel
model LazyConstraints {
  constraint early_fail {
    cash[t] >= $0
      with severity(fatal)
  }
  
  constraint late_check {
    ltv[t] >= 3.0 * cac[t]
      with severity(warning)
  }
}
```

If `early_fail` triggers at t=10, `late_check` may not be evaluated for t>10 (execution stopped).

## Practice Exercises

### Exercise 1: Write a Profitability Constraint

Ensure gross profit margin stays above 40%:

```pel
model Exercise1 {
  var revenue: TimeSeries<Currency<USD>>
  var cogs: TimeSeries<Currency<USD>>
  var gross_margin: TimeSeries<Fraction>
  
  gross_margin[t] = (revenue[t] - cogs[t]) / revenue[t]
  
  // TODO: Write constraint
  constraint ??? {
    ???
      with severity(???)
      with message("???")
  }
}
```

<details>
<summary>Solution</summary>

```pel
constraint min_gross_margin {
  gross_margin[t] >= 0.40
    with severity(warning)
    with message("Gross margin {gross_margin[t]} below 40% target at t={t}")
}
```
</details>

### Exercise 2: Debug a Constraint Failure

Given error message:
```
ERROR: Constraint 'headcount_cap' violated
  At time step: t=28
  Actual: headcount[28] = 523
  Expected: headcount[t] <= 500
```

**Task**: Which parameter(s) would you investigate?

<details>
<summary>Solution</summary>

1. Check hiring rate: `param monthly_hires` or `param hiring_rate`
2. Check initial headcount: `headcount[0]`
3. Check attrition: `param monthly_attrition_rate`
4. Check growth formula: `headcount[t+1] = headcount[t] * (1 + hiring_rate - attrition_rate)`

Likely cause: `hiring_rate` too high or `attrition_rate` too low.
</details>

### Exercise 3: Model a Debt Covenant

Senior lenders require:
- Debt Service Coverage Ratio (DSCR) ≥ 1.25
- Total debt < 3× EBITDA

```pel
model DebtCovenant {
  var ebitda: TimeSeries<Currency<USD>>
  var debt_principal: TimeSeries<Currency<USD>>
  var debt_interest: TimeSeries<Currency<USD>>
  var dscr: TimeSeries<Fraction>
  
  dscr[t] = ebitda[t] / (debt_principal[t] + debt_interest[t])
  
  // TODO: Write two constraints for the covenants above
}
```

<details>
<summary>Solution</summary>

```pel
constraint dscr_covenant {
  dscr[t] >= 1.25
    with severity(fatal)
    with message("DSCR {dscr[t]} violates covenant (min 1.25) at t={t}")
}

constraint leverage_covenant {
  debt_principal[t] <= 3.0 * ebitda[t]
    with severity(fatal)
    with message("Debt {debt_principal[t]} exceeds 3× EBITDA {ebitda[t]} at t={t}")
}
```
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
- **Reference**: See `spec/pel_constraint_spec.md` for complete constraint syntax

## Additional Resources

- [Constraint Specification](../../spec/pel_constraint_spec.md)
- [Policy Specification](../../spec/pel_policy_spec.md)
- [Examples with Constraints](../../examples/)

---

**Feedback**: Found an error or want to suggest an improvement? [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new).
