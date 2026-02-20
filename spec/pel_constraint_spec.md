# PEL Constraint Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Authors:** PEL Core Team  
**Canonical URL:** https://spec.pel-lang.org/v0.1/constraints

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Constraint Syntax and Semantics](#2-constraint-syntax-and-semantics)
3. [Severity Levels](#3-severity-levels)
4. [Scope Specifications](#4-scope-specifications)
5. [Temporal Constraints](#5-temporal-constraints)
6. [Soft Constraints and Slack](#6-soft-constraints-and-slack)
7. [Constraint Checking](#7-constraint-checking)
8. [First Binding Constraint Detection](#8-first-binding-constraint-detection)
9. [Multi-Domain Constraints](#9-multi-domain-constraints)
10. [Constraint Hierarchies](#10-constraint-hierarchies)

---

## 1. Introduction

### 1.1 Purpose

PEL elevates **constraints** from afterthoughts to **first-class language constructs**. Constraints enforce:

- **Financial feasibility:** Cash ≥ 0, debt covenants
- **Operational limits:** Capacity, lead times, utilization
- **Compliance requirements:** Regulations, contractual obligations
- **Business rules:** Pricing policies, service levels

### 1.2 Design Philosophy

**Principles:**

1. **Constraint-first modeling:** Limits are real; models must respect them
2. **Fatal vs soft:** Distinguish between hard limits (bankruptcy) and targets (aspirational margin)
3. **Explicit slack:** Quantify how far from constraint violation
4. **First binding constraint:** Identify which limit binds first (bottleneck analysis)
5. **Cross-domain:** Finance + Operations + Compliance in one model

### 1.3 Non-Goals

- PEL constraints are **NOT** optimization objectives (use AMPL/GAMS for that)
- PEL constraints do **NOT** automatically adjust variables (no solver; use policies for adaptation)

---

## 2. Constraint Syntax and Semantics

### 2.1 Basic Syntax

```pel
constraint constraint_name: boolean_expression {
  severity: fatal | warning,
  message: "Human-readable explanation",
  for: scope_specification
}
```

**Components:**

- `constraint_name`: Identifier for this constraint
- `boolean_expression`: Condition that **MUST** be true
- `severity`: `fatal` (simulation stops if violated) or `warning` (log and continue)
- `message`: Explanation shown when violated
- `for`: When/where constraint applies (optional; default: all times/entities)

### 2.2 Simple Example

```pel
constraint cash_positive: cashBalance >= $0 {
  severity: fatal,
  message: "Company insolvent - cash balance negative"
}
```

**Semantics:**
- Checked every timestep
- If `cashBalance < $0`, simulation terminates immediately with error
- Outputs: "Constraint violated: cash_positive at t=14"

### 2.3 Constraint Evaluation

**Judgment:** $\text{Check}(C, \sigma, t) \to \text{Pass} | \text{Fail}$

$$\text{Check}(C, \sigma, t) = \begin{cases}
\text{Pass} & \text{if } \sigma, t \vdash e_{\text{cond}} \Rightarrow \text{true} \\
\text{Fail}(s, m) & \text{if } \sigma, t \vdash e_{\text{cond}} \Rightarrow \text{false}
\end{cases}$$

where:
- $C$ is the constraint
- $\sigma$ is simulation state
- $t$ is current timestep
- $e_{\text{cond}}$ is the boolean expression
- $s$ is severity (`fatal` or `warning`)
- $m$ is the message

---

## 3. Severity Levels

### 3.1 Fatal Constraints

**Semantics:** Simulation **MUST** terminate immediately if violated.

**Use cases:**
- Physical impossibilities (negative inventory)
- Legal boundaries (cash < 0 = bankruptcy)
- Contractual hard limits (debt covenants)

**Example:**
```pel
constraint debt_covenant_limit: debtToEquityRatio <= 3.0 {
  severity: fatal,
  message: "Debt covenant breached - triggers default"
}
```

**Runtime behavior:**
- Checked after every timestep
- If violated: simulation stops, outputs partial results + violation info
- Exit code: non-zero

### 3.2 Warning Constraints

**Semantics:** Violation logged, simulation continues.

**Use cases:**
- Target metrics (desired but not required)
- Best practices (utilization < 80%)
- Early warning indicators

**Example:**
```pel
constraint target_margin: unitMargin >= $50 {
  severity: warning,
  message: "Unit economics below target"
}
```

**Runtime behavior:**
- Checked after every timestep
- If violated: log warning with timestep, continue simulation
- Warning count included in summary report

### 3.3 Severity Selection Guidelines

| Condition | Severity |
|-----------|----------|
| Business continues if violated | `warning` |
| Business fails if violated | `fatal` |
| Legal/contractual hard limit | `fatal` |
| Aspirational goal/target | `warning` |
| Operational impossibility | `fatal` |
| Strategic preference | `warning` |

---

## 4. Scope Specifications

### 4.1 Temporal Scope

**All timesteps (default):**
```pel
constraint cash_positive: cashBalance >= $0 {
  severity: fatal
}
```

Checked at every $t \in [0, T_{\text{max}}]$.

**Specific time range:**
```pel
constraint runway_12mo: cashBalance[t] >= $100_000 for all t in [0..12] {
  severity: fatal,
  message: "Must survive first year with minimum cash"
}
```

Checked only for $t \in [0, 12]$.

**Specific timestep:**
```pel
constraint year_end_profitability: revenue[12] > costs[12] {
  severity: warning,
  message: "Not profitable by month 12"
}
```

Checked only at $t = 12$.

### 4.2 Entity Scope

**All entities:**
```pel
constraint employee_utilization: utilization[employee] <= 1.0 for all employee {
  severity: warning,
  message: "Employee overutilized"
}
```

**Specific entities:**
```pel
constraint location_capacity: demandVolume[location] <= capacity[location] 
for all location in [SF, NYC, London] {
  severity: fatal,
  message: "Demand exceeds location capacity"
}
```

### 4.3 Conditional Scope

**Constraint applies only if condition met:**
```pel
constraint price_floor_premium_plan: 
  if plan == Premium then monthlyPrice >= $99 {
  severity: fatal,
  message: "Premium plan price below $99"
}
```

---

## 5. Temporal Constraints

### 5.1 Intertemporal Inequalities

**Monotonicity:**
```pel
constraint revenue_nondecreasing: revenue[t] >= revenue[t-1] for all t > 0 {
  severity: warning,
  message: "Revenue declined from previous month"
}
```

**Bounded growth:**
```pel
constraint growth_rate_limit: revenue[t] <= revenue[t-1] * 1.50 for all t > 0 {
  severity: fatal,
  message: "Revenue growth >50% per month is implausible"
}
```

### 5.2 Cumulative Constraints

**Total spend limit:**
```pel
constraint total_marketing_budget: sum(marketingSpend[t] for t in [0..36]) <= $1_000_000 {
  severity: fatal,
  message: "Total marketing budget exceeded"
}
```

**Runway (cash depletion):**
```pel
constraint positive_runway: min(cashBalance[t] for t in [0..24]) >= $0 {
  severity: fatal,
  message: "Cash runs out within 24 months"
}
```

### 5.3 Lead/Lag Constraints

**Payment terms (30-day lag):**
```pel
constraint payment_lag: cashCollected[t] == revenue[t-1] for all t >= 1 {
  severity: fatal,
  message: "Payment lag must be 1 month"
}
```

---

## 6. Soft Constraints and Slack

### 6.1 Slack Variables

**Syntax:**
```pel
constraint target_margin: unitMargin >= $50 {
  severity: warning,
  slack: true
}
```

**Semantics:**
If constraint violated, compute **slack**:

$$\text{slack} = \text{target} - \text{actual}$$

**Example:**
If `unitMargin = $30` and target is `$50`:

$$\text{slack} = \$50 - \$30 = \$20$$

(Positive slack = violation magnitude)

### 6.2 Slack Tracking

**Runtime outputs:**
```json
{
  "constraint": "target_margin",
  "type": "warning",
  "slack_over_time": [
    {"t": 0, "slack": 20},
    {"t": 1, "slack": 15},
    {"t": 2, "slack": 10},
    {"t": 3, "slack": 0}   // Constraint met at t=3
  ],
  "first_satisfied": 3
}
```

### 6.3 Slack Minimization (Future Extension)

**Not in v0.1**, but planned:

Integration with optimization solvers to find parameter values minimizing total slack.

---

## 7. Constraint Checking

### 7.1 Checking Algorithm

**For each timestep $t$:**

```
CheckAllConstraints(σ, t):
  for each constraint C in model:
    if C.scope.applies_at(t):
      result = Check(C, σ, t)
      if result == Fail(fatal, msg):
        TerminateSimulation(msg, t)
        return FAIL
      else if result == Fail(warning, msg):
        LogWarning(C, msg, t)
  return PASS
```

### 7.2 Evaluation Order

Constraints checked in **declaration order**.

**Important:** If multiple fatal constraints violated at same timestep, **first** in declaration order terminates simulation.

**Best practice:** Declare most critical constraints first.

### 7.3 Short-Circuit Evaluation

**Fatal constraints:**
- Stop checking further constraints after first fatal violation
- Enables fast-fail

**Warning constraints:**
- All warnings must be checked and logged

### 7.4 Performance Optimization

**Compiler MAY:**
- Precompute constraint applicability (static analysis of `for` scopes)
- Skip constraints provably satisfied (invariant analysis)
- Parallelize independent constraint checks

**Runtime MUST:**
- Produce semantically equivalent results
- Maintain declaration order for fatal constraint precedence

---

## 8. First Binding Constraint Detection

### 8.1 Definition

**First binding constraint** = constraint that becomes violated first (earliest timestep).

$$t_{\text{first}} = \min\{t : \exists C, \text{Check}(C, \sigma, t) = \text{Fail}(\text{fatal}, \_)\}$$

**Constraint that binds:**

$$C_{\text{binding}} = \text{argmin}_{C} \{ t : \text{Check}(C, \sigma, t) = \text{Fail}(\text{fatal}, \_) \}$$

### 8.2 Use Cases

**Bottleneck analysis:**
- Which constraint limits growth?
- Is it cash, capacity, hiring, compliance?

**Scenario planning:**
- If we relax constraint X, does another constraint bind instead?

**Capital allocation:**
- Which limit should we invest to relieve?

### 8.3 Runtime Reporting

```bash
pel run model.pel --report first-binding-constraint
```

**Output:**
```
First Binding Constraint Report:
  Constraint: cash_positive
  Time: t=18 months
  Value at violation: $-5,000
  Slack at t=17: $12,000
  Slack at t=18: $-5,000
  
Recommendation: Business model fails at month 18 due to cash depletion.
  Consider: (1) reduce burn rate, (2) increase revenue, (3) raise capital.
```

### 8.4 Multi-Run Analysis

**Monte Carlo:**
- Identify first-binding constraint frequency across runs

**Example output:**
```
First Binding Constraint (N=10,000 runs):
  cash_positive: 6,200 runs (62%)
  hiring_capacity: 2,800 runs (28%)
  inventory_limit: 1,000 runs (10%)
  
Interpretation: Cash is primary bottleneck in 62% of scenarios.
```

---

## 9. Multi-Domain Constraints

### 9.1 Finance + Operations

**Example: Cash and headcount coupled**
```pel
constraint cash_constrained_hiring: 
  headcount * avgSalary * 6mo <= cashBalance {
  severity: fatal,
  message: "Insufficient cash for 6-month runway given headcount"
}
```

**Semantics:**
- Can't hire if it violates cash runway
- Enforces coordination between finance and operations

### 9.2 Compliance + Finance

**Example: Debt-to-equity ratio (regulatory)**
```pel
constraint regulatory_leverage: totalDebt / equity <= 5.0 {
  severity: fatal,
  message: "Regulatory leverage limit exceeded"
}
```

### 9.3 Service Level + Capacity

**Example: Utilization and SLA**
```pel
constraint sla_utilization_tradeoff: 
  if utilization > 0.85 then slaBreachRate <= 0.05 {
  severity: warning,
  message: "High utilization causing SLA breaches"
}
```

---

## 10. Constraint Hierarchies

### 10.1 Constraint Dependencies

PEL **MAY** specify constraint dependencies (planned future extension):

```pel
constraint cash_positive: cashBalance >= $0 {
  severity: fatal
}

constraint growth_target: revenue_growth_rate >= 0.10 {
  severity: warning,
  subordinate_to: cash_positive  // Only care about growth if cash survives
}
```

**Semantics:**
- If `cash_positive` violated, don't report `growth_target` violations
- Avoids noise in constraint reports

### 10.2 Constraint Priority

**Future extension:** Assign numeric priorities for soft constraints.

Not in v0.1, but planned for optimization integration.

---

## Appendix A: Common Constraint Patterns

### A.1 Financial Constraints

**Cash non-negativity:**
```pel
constraint cash_positive: cashBalance[t] >= $0 for all t
```

**Minimum runway:**
```pel
constraint min_runway: cashBalance[t] >= burnRate * 6mo for all t
```

**Debt covenant (leverage ratio):**
```pel
constraint debt_covenant: totalDebt / ebitda <= 3.0
```

**Working capital:**
```pel
constraint working_capital: currentAssets >= currentLiabilities * 1.5
```

### A.2 Operational Constraints

**Capacity limit:**
```pel
constraint capacity: demandServed <= maxCapacity
```

**Utilization bound:**
```pel
constraint utilization_limit: utilization <= 0.90
```

**Lead time:**
```pel
constraint lead_time: orderFulfillmentTime <= 7d
```

**Inventory bounds:**
```pel
constraint inventory_range: minInventory <= inventory <= maxInventory
```

### A.3 Compliance Constraints

**Regulatory capital:**
```pel
constraint capital_adequacy: capitalRatio >= 0.08  // 8% Basel requirement
```

**Data retention:**
```pel
constraint gdpr_retention: customerDataAge <= 2y
```

**Labor laws:**
```pel
constraint max_hours: weeklyHours[employee] <= 60h for all employee
```

---

## Appendix B: Error Codes

### E0500-E0599: Constraint Errors

- **E0500:** Constraint always false (trivially unsatisfiable)
- **E0501:** Constraint condition not Boolean
- **E0502:** Constraint scope invalid (time range exceeds T_max)
- **E0503:** Constraint references undefined variable
- **E0504:** Constraint severity invalid (must be `fatal` or `warning`)
- **E0505:** Fatal constraint violated at runtime
- **E0506:** Slack tracking requested for fatal constraint (not allowed)

---

## Appendix C: References

- **Dantzig, G.** *Linear Programming and Extensions*. Princeton, 1963.
- **Boyd, S. & Vandenberghe, L.** *Convex Optimization*. Cambridge, 2004.
- **Constraint programming literature:** Rossi, van Beek, Walsh (eds.), *Handbook of Constraint Programming*, 2006.

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)  
**Canonical URL:** https://spec.pel-lang.org/v0.1/constraints
