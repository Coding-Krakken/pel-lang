# PEL Policy Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Authors:** PEL Core Team  
**Canonical URL:** https://spec.pel-lang.org/v0.1/policies

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Policy Syntax and Semantics](#2-policy-syntax-and-semantics)
3. [Trigger Conditions](#3-trigger-conditions)
4. [Policy Actions](#4-policy-actions)
5. [Evaluation Order](#5-evaluation-order)
6. [Policy Composition](#6-policy-composition)
7. [Policy Testing](#7-policy-testing)
8. [Policy Auditability](#8-policy-auditability)

---

## 1. Introduction

### 1.1 Purpose

PEL **policies** make strategic decisions executable. Unlike static models, policies allow the model to **adapt** over time based on conditions, creating realistic simulations of:

- Pricing adjustments (dynamic pricing, annual increases)
- Resource allocation (hiring freezes, budget cuts)
- Strategic pivots (change product mix, exit markets)
- Emergency responses (cash preservation, restructuring)

### 1.2 Design Philosophy

**Principles:**

1. **Strategy as code:** Business logic becomes versioned, testable, auditable
2. **Trigger-action semantics:** Clear "when X happens, do Y" structure
3. **Deterministic execution:** Same state → same policy decisions
4. **Auditability:** Every policy execution logged with rationale
5. **Testability:** Policies can be unit-tested independently

### 1.3 Distinction from Constraints

| | **Constraints** | **Policies** |
|---|---|---|
| **Purpose** | Enforce limits | Adapt behavior |
| **Checked** | Passively (every timestep) | Actively (when triggered) |
| **Effect** | Stop/warn if violated | Modify variables |
| **Example** | `cash >= $0` | `if cash < $50k then freeze_hiring` |

---

## 2. Policy Syntax and Semantics

### 2.1 Basic Syntax

```pel
policy policy_name {
  when: trigger_expression,
  then: action
}
```

**Components:**

- `policy_name`: Identifier
- `trigger_expression`: Boolean condition determining when policy activates
- `action`: What to do when triggered (variable assignment, event emission)

### 2.2 Simple Example

```pel
policy annual_price_increase {
  when: t % 12 == 0 && t > 0,  // Every 12 months after start
  then: monthlyPrice *= 1.05    // 5% price increase
}
```

**Execution trace:**
```
t=0:  monthlyPrice = $99
t=12: Policy 'annual_price_increase' triggered → monthlyPrice = $103.95
t=24: Policy 'annual_price_increase' triggered → monthlyPrice = $109.15
```

### 2.3 Formal Semantics

**Policy evaluation:**

$$\text{EvalPolicy}(P, \sigma, t) = \begin{cases}
\sigma' & \text{if } \sigma, t \vdash e_{\text{trigger}} \Rightarrow \text{true} \text{ and } \sigma' = \text{Execute}(a, \sigma) \\
\sigma & \text{otherwise (not triggered)}
\end{cases}$$

where:
- $P$ is the policy
- $\sigma$ is current state
- $t$ is timestep
- $e_{\text{trigger}}$ is trigger expression
- $a$ is action
- $\sigma'$ is updated state

---

## 3. Trigger Conditions

### 3.1 Time-Based Triggers

**Specific timestep:**
```pel
policy launch_professional_plan {
  when: t == 6,  // After 6 months
  then: {
    planAvailability.Professional = true,
    monthlyPrice.Professional = $199
  }
}
```

**Periodic (modulo arithmetic):**
```pel
policy quarterly_review {
  when: t % 3 == 0 && t > 0,  // Every 3 months
  then: emit event("quarterly_review")
}
```

**Time range:**
```pel
policy expansion_phase {
  when: t >= 12 && t <= 24,
  then: marketingBudgetMultiplier = 1.5
}
```

### 3.2 Threshold-Based Triggers

**Simple threshold:**
```pel
policy cash_preservation {
  when: cashBalance < $100_000,
  then: {
    hiring_frozen = true,
    discretionary_spend = $0
  }
}
```

**Statistical trigger:**
```pel
policy churn_spike_response {
  when: churnRate > historicalAvgChurn * 1.5,
  then: customer_support_capacity *= 1.3
}
```

**Ratio-based:**
```pel
policy margin_squeeze_response {
  when: unitMargin / revenue < 0.20,  // Margin below 20%
  then: reduce_cac_target *= 0.85
}
```

### 3.3 Event-Based Triggers

**Variable change:**
```pel
policy price_change_elasticity {
  when: monthlyPrice changes,  // Any change to monthlyPrice
  then: demandVolume *= (1 - priceElasticity * percentChange(monthlyPrice))
}
```

**State transition:**
```pel
policy profitability_reached {
  when: netIncome[t] > 0 && netIncome[t-1] <= 0,  // First profitable month
  then: emit event("profitability_milestone")
}
```

### 3.4 Composite Triggers

**Conjunction (AND):**
```pel
policy aggressive_expansion {
  when: cashBalance > $500_000 && unitMargin > $100 && t >= 12,
  then: expansionMode = true
}
```

**Disjunction (OR):**
```pel
policy emergency_mode {
  when: cashBalance < $50_000 || debtToEquityRatio > 4.0 || churnRate > 0.20,
  then: emit event("emergency_mode_activated")
}
```

---

## 4. Policy Actions

### 4.1 Variable Assignment

**Direct assignment:**
```pel
then: headcount_growth_rate = 0.0  // Freeze hiring
```

**Type checking:** RHS must match variable type.

### 4.2 Multiplicative Updates

**Increase by percentage:**
```pel
then: monthlyPrice *= 1.10  // 10% increase
```

**Decrease by percentage:**
```pel
then: cac_target *= 0.90  // 10% reduction in target CAC
```

### 4.3 Additive Updates

**Increment:**
```pel
then: headcount += 5  // Hire 5 people
```

**Decrement:**
```pel
then: cashBalance -= emergencyExpense
```

### 4.4 Block Actions (Multiple Statements)

```pel
policy pivot_to_enterprise {
  when: t == 18,
  then: {
    targetSegment = Enterprise,
    avgDealSize *= 5.0,
    salesCycleLength *= 2.0,
    cac *= 3.0,
    churnRate *= 0.5
  }
}
```

### 4.5 Conditional Actions

```pel
policy dynamic_pricing {
  when: t % 6 == 0,  // Every 6 months
  then: {
    if demandUtilization > 0.90 then monthlyPrice *= 1.08
    else if demandUtilization < 0.60 then monthlyPrice *= 0.95
  }
}
```

### 4.6 Event Emission

**For logging/tracking:**
```pel
then: emit event("milestone_profitability_reached")
```

**Runtime behavior:**
- Logged to event stream
- Available for post-simulation analysis
- **Does NOT** affect model state

---

## 5. Evaluation Order

### 5.1 Execution Order

**Policies execute in declaration order** within each timestep.

**Example:**
```pel
policy A { when: t == 10, then: x *= 2 }
policy B { when: t == 10, then: x += 5 }
```

**At t=10, if x=10:**
1. Policy A triggers: `x = 10 * 2 = 20`
2. Policy B triggers: `x = 20 + 5 = 25`

**Final value:** `x = 25`

**If declaration order reversed:**
1. Policy B triggers: `x = 10 + 5 = 15`
2. Policy A triggers: `x = 15 * 2 = 30`

**Final value:** `x = 30` (different!)

### 5.2 Non-Commutativity Warning

**Compiler SHOULD warn** if multiple policies modify the same variable and trigger simultaneously:

```
warning[W0700]: Non-commutative policy interaction
  --> model.pel:45:3
   |
45 |   policy B { when: t == 10, then: x += 5 }
   |   ^^^^^^^^ Policy B modifies variable 'x'
   |
   = note: Policy A (line 42) also modifies 'x' at t=10
   = note: Execution order: A, then B (declaration order)
   = help: Consider combining into single policy or using explicit precedence
```

### 5.3 Phase Separation (Advanced)

**Future extension:** Policy phases for deterministic multi-stage updates.

Not in v0.1, but planned.

---

## 6. Policy Composition

### 6.1 Reusable Policy Logic (Functions)

**Define policy helper:**
```pel
func adjust_price_by_demand(utilization: Fraction) -> Fraction {
  if utilization > 0.90 then return 1.08
  else if utilization < 0.60 then return 0.95
  else return 1.0
}

policy dynamic_pricing {
  when: t % 6 == 0,
  then: monthlyPrice *= adjust_price_by_demand(demand_utilization)
}
```

### 6.2 Policy Hierarchies

**Conditional policies:**
```pel
policy expansion_strategy {
  when: t >= 12 && cashBalance > $300_000,
  then: expansionMode = true
}

policy expansion_hiring {
  when: expansionMode == true,
  then: hiring_rate *= 1.5
}
```

**Note:** `expansion_hiring` **indirectly depends** on `expansion_strategy`.

### 6.3 Policy Disabling

**Temporary disable:**
```pel
var hiring_enabled: Boolean = true

policy conditionally_disable_hiring {
  when: cashBalance < $100_000,
  then: hiring_enabled = false
}

policy hire_if_enabled {
  when: hiring_enabled && headcount < target_headcount,
  then: headcount += 1
}
```

---

## 7. Policy Testing

### 7.1 Unit Testing Policies

**Test framework (conceptual):**
```pel
test "annual_price_increase applies 5% increase" {
  given: {
    monthlyPrice = $100,
    t = 12
  }
  when: policy annual_price_increase triggers
  then: {
    assert monthlyPrice == $105
  }
}
```

### 7.2 Policy Scenarios

**Scenario-based testing:**
```pel
scenario "high_churn_response" {
  initial_conditions: {
    churnRate = 0.25,  // Elevated
    cashBalance = $200_000
  }
  expected_policies_triggered: [
    "churn_spike_response",
    "customer_support_increase"
  ]
  expected_outcomes: {
    customer_support_capacity >= 1.3 * baseline
  }
}
```

### 7.3 Policy Coverage Metrics

**Compiler SHOULD track:**
- Which policies never trigger (dead code)
- Which policies trigger every run (always-on)
- Which policies trigger conditionally (useful policies)

**Example output:**
```
Policy Coverage Report:
  annual_price_increase: 3 times (t=12, 24, 36)
  cash_preservation: 0 times (never triggered)
  expansion_strategy: 1 time (t=18)
  
Warning: Policy 'cash_preservation' never triggered (dead code?)
```

---

## 8. Policy Auditability

### 8.1 Policy Execution Log

**Runtime MUST log:**
- Which policies triggered
- At what timestep
- What variables changed
- Before/after values

**Example log (JSON):**
```json
{
  "policy_execution_log": [
    {
      "timestep": 12,
      "policy": "annual_price_increase",
      "triggered": true,
      "actions": [
        {
          "variable": "monthlyPrice",
          "before": "$99.00",
          "after": "$103.95",
          "operation": "multiply",
          "factor": 1.05
        }
      ]
    },
    {
      "timestep": 18,
      "policy": "cash_preservation",
      "triggered": true,
      "actions": [
        {
          "variable": "hiring_frozen",
          "before": false,
          "after": true,
          "operation": "assign"
        },
        {
          "event": "cash_preservation_activated"
        }
      ]
    }
  ]
}
```

### 8.2 Policy Provenance

**Policies SHOULD include metadata:**
```pel
policy annual_price_increase {
  when: t % 12 == 0 && t > 0,
  then: monthlyPrice *= 1.05,
  metadata: {
    rationale: "Industry standard is 5% annual increase",
    owner: "pricing_team@company.com",
    approved_date: "2025-12-01",
    review_frequency: "annual"
  }
}
```

### 8.3 Scenario Comparison

**Compare policy effects across scenarios:**
```bash
pel run model.pel --scenario baseline > baseline.json
pel run model.pel --scenario aggressive_pricing > aggressive.json
pel diff --policy-effects baseline.json aggressive.json
```

**Output:**
```
Policy Effect Comparison:
  Policy: annual_price_increase
    Scenario: baseline
      Executed at: t=12,24,36
      Final price: $115.76
    Scenario: aggressive_pricing
      Executed at: t=6,12,18,24,30,36
      Final price: $132.78
  
  Impact: Aggressive pricing increases final price by 14.7%
```

---

## Appendix A: Common Policy Patterns

### A.1 Pricing Policies

**Annual increase:**
```pel
policy annual_price_increase {
  when: t % 12 == 0 && t > 0,
  then: monthlyPrice *= 1.05
}
```

**Dynamic pricing (demand-responsive):**
```pel
policy demand_based_pricing {
  when: t % 3 == 0,
  then: {
    if demand_utilization > 0.90 then monthlyPrice *= 1.10
    else if demand_utilization < 0.50 then monthlyPrice *= 0.90
  }
}
```

**A/B test pricing:**
```pel
policy ab_test_pricing {
  when: t == 6,
  then: {
    if cohort_id % 2 == 0 then monthlyPrice = $99
    else monthlyPrice = $129
  }
}
```

### A.2 Resource Allocation Policies

**Growth hiring:**
```pel
policy growth_hiring {
  when: revenue[t] > revenue[t-1] * 1.20 && cashBalance > $500_000,
  then: headcount_growth_rate = 0.15
}
```

**Hiring freeze:**
```pel
policy hiring_freeze_cash_constraint {
  when: cashBalance < burnRate * 9mo,
  then: headcount_growth_rate = 0.0
}
```

**Budget reallocation:**
```pel
policy shift_to_retention_spend {
  when: churnRate > 0.15,
  then: {
    acquisitionBudget *= 0.80,
    retentionBudget *= 1.40
  }
}
```

### A.3 Emergency Response Policies

**Cash preservation:**
```pel
policy emergency_cash_preservation {
  when: cashBalance < $50_000,
  then: {
    discretionary_spend = $0,
    headcount_growth_rate = 0.0,
    marketing_budget *= 0.50,
    emit event("emergency_mode")
  }
}
```

**Restructuring:**
```pel
policy restructuring {
  when: consecutive_loss_months >= 6,
  then: {
    headcount *= 0.70,  // 30% reduction
    fixed_costs *= 0.60,
    emit event("restructuring_initiated")
  }
}
```

### A.4 Strategic Pivot Policies

**Segment pivot:**
```pel
policy pivot_to_enterprise {
  when: t == 24 && smb_ltv < $500,
  then: {
    target_segment = Enterprise,
    avgDealSize *= 10.0,
    salesCycleLength *= 3.0,
    cac *= 5.0,
    churnRate *= 0.40
  }
}
```

---

## Appendix B: Error Codes

### E0700-E0799: Policy Errors

- **E0700:** Policy trigger condition not Boolean
- **E0701:** Policy action assigns incompatible type
- **E0702:** Policy modifies immutable parameter
- **E0703:** Policy references undefined variable
- **E0704:** Circular policy dependency detected
- **E0705:** Policy execution failed at runtime

---

## Appendix C: Policy Formal Semantics

### Operational Semantics

**Small-step policy reduction:**

$$\frac{\sigma, t \vdash e_{\text{trigger}} \Rightarrow \text{true} \quad \sigma, \rho \vdash a \leadsto \sigma', \rho'}
{\langle \text{policy } P, \sigma, \rho, t \rangle \to \langle \bullet, \sigma', \rho', t \rangle}$$

$$\frac{\sigma, t \vdash e_{\text{trigger}} \Rightarrow \text{false}}
{\langle \text{policy } P, \sigma, \rho, t \rangle \to \langle \bullet, \sigma, \rho, t \rangle}$$

where $\bullet$ represents completed policy execution.

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)  
**Canonical URL:** https://spec.pel-lang.org/v0.1/policies
