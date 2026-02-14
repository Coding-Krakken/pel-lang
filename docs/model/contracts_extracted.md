# PEL Contracts Extracted from Specifications

**Purpose:** Centralized reference of all formal contracts from PEL specifications  
**Date:** 2026-02-13  
**Version:** 0.1.0  
**Status:** Canonical - extracted from formal specifications  

---

## Overview

This document extracts and consolidates **formal contracts** from PEL's 11 specification documents. These contracts define:
- **Preconditions:** What MUST be true before an operation
- **Postconditions:** What MUST be true after an operation
- **Invariants:** What MUST always be true
- **Error conditions:** When and how operations fail

All contracts are **mandatory** for conformant implementations.

**Source Specifications:**
- [spec/pel_language_spec.md](../../spec/pel_language_spec.md)
- [spec/pel_formal_semantics.md](../../spec/pel_formal_semantics.md)
- [spec/pel_type_system.md](../../spec/pel_type_system.md)
- [spec/pel_uncertainty_spec.md](../../spec/pel_uncertainty_spec.md)
- [spec/pel_constraint_spec.md](../../spec/pel_constraint_spec.md)
- [spec/pel_policy_spec.md](../../spec/pel_policy_spec.md)
- [spec/pel_governance_spec.md](../../spec/pel_governance_spec.md)
- [spec/pel_security_spec.md](../../spec/pel_security_spec.md)
- [spec/pel_calibration_spec.md](../../spec/pel_calibration_spec.md)
- [spec/pel_conformance_spec.md](../../spec/pel_conformance_spec.md)

---

## 1. Type System Contracts

**Source:** [spec/pel_type_system.md](../../spec/pel_type_system.md)

### 1.1 Type Checking Contract

```yaml
contract: TYPE_CHECKING
function: TypeChecker.check(ast: Model) → Model

preconditions:
  - ast is syntactically valid (passed parser)
  - All AST nodes well-formed

postconditions_success:
  - Every expression has type annotation
  - All identifiers resolved in environment Γ
  - All type constraints satisfied
  - Dimensional correctness verified
  - Currency compatibility verified
  - No type mismatches

postconditions_error:
  - TypeError raised with code E03xx
  - Error includes source location
  - Error includes type information
  - Error includes hint (when applicable)

invariants:
  - Type environment Γ is consistent
  - Type rules from§3 applied correctly
  - Dimensional analysis rules enforced
```

### 1.2 Dimensional Analysis Contracts

#### Contract: Currency Arithmetic

```yaml
contract: CURRENCY_ADDITION
rule: Currency<X> + Currency<Y> → Currency<Z>

preconditions:
  - X and Y are valid ISO 4217 codes
  
postconditions:
  - If X = Y: Z = X (same currency)
  - If X ≠ Y: TypeError (E0301: Currency mismatch)

example_success: Currency<USD> + Currency<USD> → Currency<USD>
example_error: Currency<USD> + Currency<EUR> → TypeError
```

```yaml
contract: CURRENCY_MULTIPLICATION
rule: Currency<X> × Count<E> → Currency<X>

preconditions:
  - X is valid ISO code
  - E is entity identifier

postconditions:
  - Result has same currency as operand
  - Dimensional analysis: [Currency] × [Count] = [Currency]

example: $100 per Customer × 500 Customers → $50,000
```

```yaml
contract: CURRENCY_DIVISION
rule: Currency<X> / Count<E> → Currency<X> per Entity<E>

postconditions:
  - Result is scoped currency
  - Dimensional analysis: [Currency] / [Count] = [Currency per Entity]

example: $50,000 / 500 Customers → $100 per Customer
```

#### Contract: Rate Arithmetic

```yaml
contract: RATE_DURATION_MULTIPLICATION
rule: Rate per T × Duration<T> → Fraction

preconditions:
  - Time units MUST match
  
postconditions:
  - Result is dimensionless Fraction
  - Dimensional analysis: [1/Time] × [Time] = [1]
  
example_success: 5% per Year × 3 Years → 15%
example_error: Rate per Month × Duration<Year> → TypeError (E0302: Time unit mismatch)
```

```yaml
contract: RATE_ADDITION
rule: Rate per T + Rate per T → Rate per T

preconditions:
  - Time units MUST match
  
postconditions:
  - Result has same time unit
  
example_success: 5% per Month + 3% per Month → 8% per Month
example_error: Rate per Month + Rate per Year → TypeError
```

### 1.3 Type Inference Contract

```yaml
contract: TYPE_INFERENCE
function: infer_type(expr: Expression, Γ: Environment) → Type

algorithm: Bidirectional type checking

preconditions:
  - expr is valid AST node
  - Γ contains all identifiers in scope

postconditions:
  - Returns unique type for expr
  - Type is most specific (no unnecessary generalization)
  - Preserves dimensional correctness

rules:
  literals:
    - $100 → Currency<USD>
    - 5% → Fraction
    - 30d → Duration<Day>
  
  variables:
    - Look up identifier in Γ
    - If not found → TypeError (E0303: Undefined variable)
  
  binary_operations:
    - Infer types of left and right operands
    - Apply dimensional analysis rules
    - Return result type or error
  
  function_calls:
    - Look up function signature
    - Check argument types match parameters
    - Return declared return type
```

---

## 2. Formal Semantics Contracts

**Source:** [spec/pel_formal_semantics.md](../../spec/pel_formal_semantics.md)

### 2.1 Evaluation Contract

```yaml
contract: EXPRESSION_EVALUATION
function: eval(e: Expression, σ: State, t: Timestep) → Value

preconditions:
  - e is well-typed
  - σ contains all free variables in e
  - t ∈ [0, T] where T = time_horizon

postconditions:
  - Returns value of appropriate type
  - Evaluation is deterministic (same e, σ, t → same value)
  - Side-effect free (σ unchanged)

invariants:
  - Causality: Only references variables at timesteps ≤ t
  - Type preservation: type(result) = type(e)
```

### 2.2 Time Semantics Contract

```yaml
contract: CAUSALITY
property: No future references in TimeSeries

enforcement: Compile-time check

rule: |
  For expression computing variable x[t]:
    All referenced variables y[s] MUST have s ≤ t

preconditions:
  - Dependency graph analyzed
  - Temporal relationships identified

violations:
  - TimeSeries[t] references TimeSeries[t+1] → TypeError (E0304)
  - Example: revenue[t] = revenue[t+1] × 1.05 → ERROR

valid_references:
  - Same timestep: revenue[t] = price[t] × quantity[t] ✓
  - Past: revenue[t] = revenue[t-1] × 1.05 ✓
  - Initial: revenue[0] = initial_value ✓
```

### 2.3 Constraint Evaluation Contract

```yaml
contract: CONSTRAINT_CHECKING
function: check_constraint(c: Constraint, σ: State, t: Timestep) → (bool, message)

preconditions:
  - c.condition is well-typed (returns bool)
  - σ contains all variables referenced in c.condition
  
postconditions:
  - Returns (true, _) if constraint satisfied
  - Returns (false, message) if violated
  - Evaluation is deterministic

behavior:
  fatal_violation:
    - Stop simulation immediately
    - Return partial results
    - Log: (t, constraint_name, message, values)
  
  warning_violation:
    - Log violation
    - Continue simulation
    - Include warnings in final results

example:
  constraint: cash[t] >= 0 (fatal)
  violation_at_t: 18
  action: Stop, return results[0:18]
```

### 2.4 Policy Execution Contract

```yaml
contract: POLICY_EXECUTION
function: execute_policy(p: Policy, σ: State, t: Timestep) → State

preconditions:
  - p.trigger is well-typed (returns bool)
  - p.action is well-formed
  - σ contains all variables referenced

postconditions:
  - If trigger evaluates to true: σ' = apply(action, σ)
  - If trigger evaluates to false: σ' = σ (unchanged)
  - Execution is deterministic

ordering:
  - Policies executed in declaration order
  - Same (σ, t) → same policy sequence
  
actions:
  set: σ'[var] = value
  multiply: σ'[var] = σ[var] × factor
  add: σ'[var] = σ[var] + increment

example:
  policy: |
    if t % 12 == 0:
      monthlyPrice *= 1.05
  
  effect: Every 12 timesteps, increase price by 5%
```

---

## 3. Provenance Contracts

**Source:** [spec/pel_governance_spec.md](../../spec/pel_governance_spec.md)

### 3.1 Provenance Completeness Contract

```yaml
contract: PROVENANCE_VALIDATION
function: validate_provenance(param: ParamDecl) → (bool, score, errors)

preconditions:
  - param is well-formed parameter declaration

postconditions:
  - Returns validation result
  - Calculates completeness score
  - Lists missing/invalid fields

required_fields:
  - source: str (non-empty)
  - method: str ∈ {observed, fitted, derived, expert_estimate, external_research, assumption}
  - confidence: float ∈ [0.0, 1.0]

recommended_fields:
  - freshness: ISO 8601 duration (e.g., "P30D")
  - owner: str (responsible party)

optional_fields:
  - correlated_with: List[Tuple[str, float]]
  - notes: str

completeness_score:
  formula: fields_present / (3 required + 2 recommended)
  range: [0.0, 1.0]
  target: ≥ 0.80

errors:
  - E0401: Missing required field {field}
  - E0402: confidence out of range [0.0, 1.0]
  - E0403: Invalid method value
```

### 3.2 Model Fingerprinting Contract

```yaml
contract: MODEL_HASHING
function: compute_fingerprint(ir: IR) → Fingerprint

components:
  model_hash: SHA-256(canonical_json(ir.model))
  assumption_hash: SHA-256(canonical_json(all_provenance))
  runtime_version: "pel-0.1.0"

preconditions:
  - IR is valid JSON
  - All provenance data present

postconditions:
  - model_hash is 64-char hex string
  - assumption_hash is 64-char hex string
  - Deterministic (same IR → same hashes)

reproducibility_guarantee: |
  Given:
    - model_hash H_m
    - assumption_hash H_a
    - runtime_version V
    - seed S
  
  Then:
    ANY conformant runtime version V MUST produce
    bit-identical results from the model

canonical_json_rules:
  - Keys sorted alphabetically
  - No whitespace
  - Floats formatted consistently (6 decimal places)
  - Arrays/objects compact
```

---

## 4. Uncertainty Contracts

**Source:** [spec/pel_uncertainty_spec.md](../../spec/pel_uncertainty_spec.md)

### 4.1 Distribution Validation Contract

```yaml
contract: DISTRIBUTION_VALIDATION
function: validate_distribution(dist: Distribution) → (bool, error)

distribution_types:
  
  Beta:
    parameters: [alpha: float > 0, beta: float > 0]
    support: [0, 1]
    validation:
      - alpha > 0 else E0501
      - beta > 0 else E0501
  
  Normal:
    parameters: [μ: float, σ: float > 0]
    support: (-∞, +∞)
    validation:
      - σ > 0 else E0502
  
  LogNormal:
    parameters: [μ: float, σ: float > 0]
    support: (0, +∞)
    validation:
      - σ > 0 else E0503
  
  Uniform:
    parameters: [low: float, high: float]
    support: [low, high]
    validation:
      - low < high else E0504
  
  Triangular:
    parameters: [low: float, mode: float, high: float]
    support: [low, high]
    validation:
      - low ≤ mode ≤ high else E0505
  
  Pareto:
    parameters: [x_min: float > 0, alpha: float > 0]
    support: [x_min, +∞)
    validation:
      - x_min > 0 else E0506
      - alpha > 0 else E0506

postconditions:
  - Returns (true, _) if all parameters valid
  - Returns (false, error_code) if invalid
```

### 4.2 Correlation Contract

```yaml
contract: CORRELATION_VALIDATION
function: validate_correlation(matrix: Matrix) → (bool, error)

preconditions:
  - matrix is square (n × n)
  - Variables listed in row/column order

validation_rules:
  - All diagonal elements = 1.0
  - All off-diagonal elements ∈ [-1.0, 1.0] (E0507 if violated)
  - Matrix is symmetric (m[i,j] = m[j,i])
  - Matrix is positive semi-definite (all eigenvalues ≥ 0) (E0508 if violated)

postconditions:
  - Returns (true, _) if valid correlation matrix
  - Returns (false, error_code) if invalid

sampling_contract:
  method: Cholesky decomposition
  precondition: Matrix is positive semi-definite
  postcondition: Sampled variables have empirical correlation ≈ specified correlation
```

### 4.3 Monte Carlo Sampling Contract

```yaml
contract: MONTE_CARLO_SAMPLING
function: sample(dist: Distribution, n: int, seed: int) → List[float]

preconditions:
  - dist is valid distribution
  - n ≥ 1
  - seed is fixed integer

postconditions:
  - Returns list of length n
  - All samples within distribution support
  - Empirical distribution approximates theoretical distribution (as n → ∞)
  - Deterministic (same seed → same samples)

reproducibility:
  - Set PRNG seed before sampling
  - Use single PRNG instance per simulation
  - Sample in declaration order

example:
  dist: ~Normal(μ=0.05, σ=0.02)
  n: 1000
  seed: 42
  result: [0.0531, 0.0672, 0.0421, ...] (1000 values, same every run)
```

---

## 5. Constraint Contracts

**Source:** [spec/pel_constraint_spec.md](../../spec/pel_constraint_spec.md)

### 5.1 Constraint Declaration Contract

```yaml
contract: CONSTRAINT_SYNTAX
declaration: |
  constraint <name> {
    condition: <boolean_expression>
    severity: fatal | warning
    message: "<error_message>"
  }

validation:
  - name is valid identifier
  - condition has type bool
  - severity ∈ {fatal, warning}
  - message is non-empty string

example:
  constraint cash_positive {
    condition: cash[t] >= 0
    severity: fatal
    message: "Company ran out of cash"
  }
```

### 5.2 Constraint Checking Contract

```yaml
contract: CONSTRAINT_EVALUATION
function: check_constraint(c: Constraint, state: State, t: int) → Result

preconditions:
  - c.condition is well-typed (bool)
  - state contains all variables in condition
  - 0 ≤ t ≤ T

evaluation:
  - Substitute state values into condition
  - Evaluate to boolean
  - Handle per severity

fatal_severity:
  - If condition = false: STOP simulation
  - Log: (t, constraint_name, message, variable_values)
  - Return: RuntimeError with partial results

warning_severity:
  - If condition = false: CONTINUE simulation
  - Log: (t, constraint_name, message, variable_values)
  - Include warning in final results

postconditions:
  - Evaluation is deterministic
  - All constraints checked every timestep
```

---

## 6. Policy Contracts

**Source:** [spec/pel_policy_spec.md](../../spec/pel_policy_spec.md)

### 6.1 Policy Declaration Contract

```yaml
contract: POLICY_SYNTAX
declaration: |
  policy <name> {
    trigger: <condition>
    action: <action_spec>
  }

trigger_types:
  - time: Boolean expression (e.g., t % 12 == 0)
  - threshold: Boolean expression (e.g., mrr[t] > 1000000)
  - event: External event (future)

action_types:
  - set: variable = value
  - multiply: variable *= factor
  - add: variable += increment

validation:
  - name is valid identifier
  - trigger has type bool
  - action references valid variable
  - action preserves variable type

example:
  policy annual_price_increase {
    trigger: t % 12 == 0
    action: monthlyPrice *= 1.05
  }
```

### 6.2 Policy Execution Contract

```yaml
contract: POLICY_EXECUTION_ORDER
function: execute_policies(policies: List[Policy], state: State, t: int) → State

preconditions:
  - All policies are valid
  - state is consistent

execution_algorithm: |
  state' = state
  for policy in policies (in declaration order):
    if eval(policy.trigger, state', t):
      state' = apply(policy.action, state')
  return state'

postconditions:
  - Deterministic (same state, policies, t → same result)
  - Declaration order preserved
  - State modified only if trigger true

composability:
  - Multiple policies can execute in same timestep
  - Later policies see effects of earlier policies
  - Order matters (not commutative)
```

---

## 7. Security Contracts

**Source:** [spec/pel_security_spec.md](../../spec/pel_security_spec.md)

### 7.1 Sandbox Contract

```yaml
contract: SANDBOX_ISOLATION
enforcement: Runtime validation + AST inspection

prohibited_operations:
  - File I/O: open, read, write, delete
  - Network I/O: socket, http requests
  - Process: subprocess, fork, exec
  - Dynamic code: eval, exec, compile, __import__
  - Introspection (unrestricted): vars, dir, globals

preconditions:
  - PEL code submitted for execution

validation_steps:
  1. AST inspection: Check for Import nodes, file operations
  2. Disable builtins: Remove dangerous functions from namespace
  3. Capability check: Verify declared capabilities match usage

postconditions:
  - Code cannot access file system (unless capability granted)
  - Code cannot access network (unless capability granted)
  - Code cannot spawn processes
  - Code cannot execute arbitrary Python

violation:
  - Raise SecurityError
  - Terminate execution
  - Log attempted violation
```

### 7.2 Resource Limit Contract

```yaml
contract: RESOURCE_LIMITS
enforcement: OS-level (setrlimit, signal)

limits:
  memory:
    default: 2GB
    enforcement: resource.setrlimit(RLIMIT_AS, 2GB)
    violation: MemoryError
  
  execution_time:
    default: 60 seconds
    enforcement: signal.alarm(60)
    violation: TimeoutError
  
  iterations:
    default: 1M per loop
    enforcement: Compile-time analysis
    violation: CompilationError

handling:
  - Graceful termination
  - Partial results if available
  - Logged resource usage
```

### 7.3 Input Validation Contract

```yaml
contract: INPUT_VALIDATION
function: validate_input(data: Any, schema: Schema) → Result

validation_types:
  
  csv_injection:
    pattern: "^[=+\\-@]"
    action: Strip leading character or reject
    rationale: Prevent formula injection
  
  type_validation:
    check: Runtime type matches declared type
    action: Reject if mismatch
  
  range_validation:
    check: Values within expected ranges
    examples:
      - confidence ∈ [0.0, 1.0]
      - time_horizon ≥ 0
    action: Reject if out of range

postconditions:
  - All inputs validated before use
  - Invalid inputs rejected with clear error
  - No injection attacks possible
```

---

## 8. IR Validation Contracts

**Source:** `ir/ir_validation_rules.md`

### 8.1 Structural Validation Contracts

```yaml
contract: V001_DEPENDENCY_ACYCLICITY
rule: Dependency graph MUST be acyclic

algorithm: Topological sort
validation:
  - Build dependency graph from variable definitions
  - Attempt topological sort
  - If cycle detected → ValidationError

error: "Circular dependency detected: {cycle_path}"

example_valid:
  x = 10
  y = x + 5  # y depends on x ✓
  z = y * 2  # z depends on y ✓

example_invalid:
  x = y + 1
  y = x + 1  # ERROR: x depends on y, y depends on x
```

```yaml
contract: V002_DEPENDENCIES_EXIST
rule: All referenced variables MUST be declared

validation:
  - For each variable reference in expressions
  - Check if variable declared in model
  - If not found → ValidationError

error: "Undefined variable '{var}' referenced in '{context}'"

example_valid:
  param x: Fraction = 0.05
  var y: Fraction = x * 2  # x declared ✓

example_invalid:
  var y: Fraction = x * 2  # ERROR: x not declared
```

```yaml
contract: V003_PROVENANCE_REQUIRED
rule: All params MUST have provenance metadata

validation:
  - For each param node in IR
  - Check provenance object present
  - Check required fields: source, method, confidence
  - If missing → ValidationError

error: "Parameter '{name}' missing provenance metadata"
```

### 8.2 Semantic Validation Contracts

```yaml
contract: V006_TEMPORAL_CAUSALITY
rule: TimeSeries[t] MUST NOT reference TimeSeries[> t]

validation:
  - Analyze all TimeSeries indexing expressions
  - Check index ≤ current timestep
  - If future reference → ValidationError

error: "Causality violation: {var}[{t}] references future value"

example_valid:
  revenue[t] = revenue[t-1] * 1.05  # Past reference ✓
  revenue[t] = price[t] * quantity[t]  # Same timestep ✓

example_invalid:
  revenue[t] = revenue[t+1] * 0.95  # ERROR: Future reference
```

```yaml
contract: V007_DISTRIBUTION_PARAMETERS
rule: Distribution parameters MUST be valid

validation:
  - For each distribution in IR
  - Validate parameters per distribution type contract (§4.1)
  - If invalid → ValidationError

error: "Invalid distribution parameters: {dist_type} {params}"

example_valid:
  ~Beta(α=2, β=38)  # α > 0, β > 0 ✓
  ~Normal(μ=0.05, σ=0.02)  # σ > 0 ✓

example_invalid:
  ~Beta(α=-1, β=38)  # ERROR: α must be > 0
  ~Normal(μ=0.05, σ=-0.02)  # ERROR: σ must be > 0
```

```yaml
contract: V012_MODEL_HASH_VALID
rule: model_hash MUST match SHA-256 of canonical IR

validation:
  - Compute SHA-256(canonical_json(ir.model))
  - Compare with ir.metadata.model_hash
  - If mismatch → ValidationError

error: "Model hash mismatch: expected {computed}, got {provided}"

purpose: Detect tampering or corruption
```

---

## 9. Conformance Contracts

**Source:** [spec/pel_conformance_spec.md](../../spec/pel_conformance_spec.md)

### 9.1 Core Conformance Contract

```yaml
contract: CORE_CONFORMANCE
level: Core
requirement: MUST pass for v1.0 conformance

test_categories:
  compiler:
    - Lexer: 50 tests (tokenization, error handling)
    - Parser: 100 tests (grammar coverage, error recovery)
    - TypeChecker: 150 tests (type inference, dimensional analysis)
    - ProvenanceChecker: 40 tests (validation, completeness)
    - IRGenerator: 40 tests (JSON generation, hashing)
  
  runtime:
    - Deterministic: 80 tests (evaluation, constraints, policies)
    - Reproducibility: 20 tests (same seed → same results)
  
  total_tests: 480

pass_criteria:
  - All tests pass
  - No undefined behavior
  - Error messages clear and actionable
```

### 9.2 Extended Conformance Contract

```yaml
contract: EXTENDED_CONFORMANCE
level: Extended
requirement: Optional for v1.0, target for v1.1

test_categories:
  - Monte Carlo: 50 tests (sampling, aggregation)
  - Correlation: 40 tests (Cholesky, correlation validation)
  - Sensitivity: 30 tests (Tornado charts, Sobol indices)
  
total_tests: 120

pass_criteria:
  - All Core tests pass
  - All Extended tests pass
  - Statistical accuracy within bounds
```

---

## 10. Summary of Critical Contracts

### Top 10 Most Critical Contracts

1. **COMPILATION_DETERMINISM:** Same source → same IR (always)
2. **RUNTIME_REPRODUCIBILITY:** Same IR + seed → identical results (always)
3. **TYPE_SAFETY:** Well-typed programs don't crash (always)
4. **CAUSALITY:** No future references in TimeSeries (always)
5. **PROVENANCE_COMPLETENESS:** All params have metadata (required for governance)
6. **SANDBOX_ISOLATION:** No unauthorized I/O (security requirement)
7. **RESOURCE_LIMITS:** Bounded memory and time (security requirement)
8. **DEPENDENCY_ACYCLICITY:** No circular dependencies (V001)
9. **CONSTRAINT_SEMANTICS:** Fatal → stop, warning → continue (behavioral contract)
10. **MODEL_HASHING:** Correct cryptographic fingerprints (reproducibility requirement)

### Contract Enforcement Summary

| Contract | Enforcement Point | Validation Method |
|----------|------------------|-------------------|
| Type contracts | Compile-time | Type checker |
| Provenance contracts | Compile-time | Provenance checker |
| Causality | Compile-time | Dependency analysis |
| IR validation (V001-V015) | Post-compilation | JSON Schema + semantic rules |
| Constraint semantics | Runtime | Constraint evaluator |
| Policy semantics | Runtime | Policy executor |
| Reproducibility | Runtime | Determinism tests |
| Security contracts | Runtime | Sandbox + resource limits |

---

## 11. Contract Validation Checklist

For each implementation change, verify:

- [ ] All preconditions checked
- [ ] All postconditions satisfied
- [ ] Invariants preserved
- [ ] Error conditions handled
- [ ] Determinism maintained
- [ ] Tests updated to verify contracts
- [ ] Documentation updated if contracts change

**Next Steps:**
1. Implement runtime contract checking (instrumentation)
2. Generate property-based tests from contracts
3. Add contract assertions to implementation
4. Create contract violation reporting

---

**End of Contract Extraction**  
**All contracts are MANDATORY for conformant implementations.**
