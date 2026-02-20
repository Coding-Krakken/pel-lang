# PEL-IR Validation Rules v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Canonical URL:** https://spec.pel-lang.org/v0.1/ir/validation

---

## 1. Introduction

The PEL-IR JSON Schema defines **structural validity**. This document defines **semantic validity** rules that cannot be expressed in JSON Schema.

---

## 2. Validation Rules

### V001: Dependency Acyclicity

**Rule:** Node dependency graph MUST be acyclic.

**Check:**
```python
def validate_dependency_graph(nodes):
    graph = {n.node_id: n.dependencies for n in nodes}
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False
    
    for node_id in graph:
        if node_id not in visited:
            if has_cycle(node_id):
                raise ValidationError(f"V001: Cyclic dependency involving {node_id}")
```

---

### V002: Dependency Resolution

**Rule:** All dependency node_ids MUST exist.

**Check:**
```python
def validate_dependencies_exist(nodes):
    all_ids = {n.node_id for n in nodes}
    for node in nodes:
        for dep_id in node.dependencies:
            if dep_id not in all_ids:
                raise ValidationError(f"V002: Unknown dependency '{dep_id}' in node '{node.node_id}'")
```

---

### V003: Provenance Requirement

**Rule:** All `param` nodes MUST have provenance block.

**Check:**
```python
def validate_provenance(nodes):
    for node in nodes:
        if node.node_type == "param" and node.provenance is None:
            raise ValidationError(f"V003: Parameter '{node.name}' missing provenance")
```

---

### V004: Correlation Matrix Positive Semi-Definite

**Rule:** Correlation matrix formed by `correlated_with` declarations MUST be positive semi-definite.

**Check:**
```python
import numpy as np

def validate_correlation_matrix(nodes):
    # Extract correlations
    corr_matrix = build_correlation_matrix(nodes)
    
    # Compute eigenvalues
    eigenvalues = np.linalg.eigvalsh(corr_matrix)
    
    # Check all eigenvalues >= 0 (allowing small numerical errors)
    if np.any(eigenvalues < -1e-8):
        raise ValidationError(f"V004: Correlation matrix not positive semi-definite (min eigenvalue: {eigenvalues.min()})")
```

---

### V005: Correlation Coefficients in [-1, 1]

**Rule:** All correlation coefficients MUST be in range [-1, 1].

**Check:**
```python
def validate_correlation_coefficients(nodes):
    for node in nodes:
        if node.provenance and node.provenance.correlated_with:
            for corr in node.provenance.correlated_with:
                if not -1.0 <= corr.coefficient <= 1.0:
                    raise ValidationError(f"V005: Invalid correlation coefficient {corr.coefficient} for '{node.name}' (must be in [-1, 1])")
```

---

### V006: TimeSeries Causality

**Rule:** TimeSeries indexing MUST NOT reference future timesteps.

**Check:**
```python
def validate_timeseries_causality(expression, current_time_var="t"):
    if expression.expr_type == "Indexing":
        if is_timeseries_variable(expression.base):
            index_expr = expression.index
            # Check if index contains t+k where k > 0
            if contains_future_reference(index_expr, current_time_var):
                raise ValidationError(f"V006: Future reference in TimeSeries indexing")
    # Recurse into subexpressions...
```

---

### V007: Distribution Parameter Validity

**Rule:** Distribution parameters MUST satisfy domain constraints.

**Constraints:**
- **Beta:** alpha > 0, beta > 0
- **Normal:** sigma > 0
- **LogNormal:** sigma > 0
- **Uniform:** low < high
- **Triangular:** low ≤ mode ≤ high
- **Pareto:** alpha > 0, x_min > 0

**Check:**
```python
def validate_distribution_parameters(dist):
    if dist.distribution_type == "Beta":
        alpha = dist.parameters.get("alpha")
        beta = dist.parameters.get("beta")
        if alpha <= 0 or beta <= 0:
            raise ValidationError(f"V007: Beta distribution requires alpha > 0, beta > 0")
    elif dist.distribution_type == "Normal":
        sigma = dist.parameters.get("sigma")
        if sigma <= 0:
            raise ValidationError(f"V007: Normal distribution requires sigma > 0")
    # ... other distributions
```

---

### V008: Type Consistency

**Rule:** Expression types MUST match declared type annotations.

**Check:**
```python
def validate_type_consistency(node):
    declared_type = node.type_annotation
    inferred_type = infer_expression_type(node.value)
    
    if not types_compatible(declared_type, inferred_type):
        raise ValidationError(f"V008: Type mismatch for '{node.name}': declared {declared_type}, inferred {inferred_type}")
```

---

### V009: Dimensional Correctness

**Rule:** Arithmetic operations MUST respect dimensional analysis.

**Check:**
```python
def validate_dimensional_correctness(expr):
    if expr.expr_type == "BinaryOp":
        left_dim = get_dimension(expr.left)
        right_dim = get_dimension(expr.right)
        
        if expr.operator in ["+", "-"]:
            if left_dim != right_dim:
                raise ValidationError(f"V009: Cannot {expr.operator} incompatible dimensions: {left_dim} vs {right_dim}")
        elif expr.operator == "*":
            result_dim = multiply_dimensions(left_dim, right_dim)
        elif expr.operator == "/":
            result_dim = divide_dimensions(left_dim, right_dim)
```

---

### V010: Scope Validity

**Rule:** Scoped expressions MUST reference valid entities.

**Check:**
```python
def validate_scope_references(model):
    declared_entities = extract_entity_declarations(model)
    
    for node in model.nodes:
        if node.type_annotation.type_kind == "Scoped":
            scope_entity = node.type_annotation.scope_entity
            if scope_entity not in declared_entities:
                raise ValidationError(f"V010: Unknown entity scope '{scope_entity}' for '{node.name}'")
```

---

### V011: Constraint Scope Valid

**Rule:** Constraint temporal/entity scopes MUST be valid.

**Check:**
```python
def validate_constraint_scopes(constraint, model):
    if constraint.scope and constraint.scope.temporal:
        t_scope = constraint.scope.temporal
        if t_scope.type == "specific" and t_scope.timestep < 0:
            raise ValidationError(f"V011: Negative timestep in constraint '{constraint.name}'")
        if t_scope.type == "range" and t_scope.start > t_scope.end:
            raise ValidationError(f"V011: Invalid range [{t_scope.start}..{t_scope.end}] in constraint '{constraint.name}'")
```

---

### V012: Model Hash Correctness

**Rule:** `model_hash` MUST match SHA-256 of normalized IR.

**Check:**
```python
import hashlib
import json

def validate_model_hash(ir_document):
    # Normalize IR (sort keys, remove metadata)
    normalized = normalize_ir(ir_document)
    canonical_json = json.dumps(normalized, sort_keys=True)
    
    computed_hash = hashlib.sha256(canonical_json.encode()).hexdigest()
    declared_hash = ir_document["metadata"]["model_hash"]
    
    if f"sha256:{computed_hash}" != declared_hash:
        raise ValidationError(f"V012: Model hash mismatch (computed: {computed_hash}, declared: {declared_hash})")
```

---

### V013: Assumption Hash Correctness

**Rule:** `assumption_hash` MUST match SHA-256 of all provenance blocks.

**Check:**
```python
def validate_assumption_hash(ir_document):
    provenance_data = extract_all_provenance(ir_document)
    canonical_json = json.dumps(provenance_data, sort_keys=True)
    
    computed_hash = hashlib.sha256(canonical_json.encode()).hexdigest()
    declared_hash = ir_document["metadata"]["assumption_hash"]
    
    if f"sha256:{computed_hash}" != declared_hash:
        raise ValidationError(f"V013: Assumption hash mismatch")
```

---

### V014: Time Horizon Consistency

**Rule:** If `time_horizon` specified, no TimeSeries indexing may exceed it.

**Check:**
```python
def validate_time_horizon(model):
    if model.time_horizon is not None:
        for node in model.nodes:
            max_index = find_max_timeseries_index(node.value)
            if max_index and max_index >= model.time_horizon:
                raise ValidationError(f"V014: TimeSeries index {max_index} exceeds time_horizon {model.time_horizon} in '{node.name}'")
```

---

### V015: Policy Execution Order

**Rule:** Policies with overlapping triggers MUST have deterministic order (declaration order preserved).

**Check:**
```python
def validate_policy_order(policies):
    # Check that policy_id ordering matches declaration order
    for i, policy in enumerate(policies):
        expected_id = f"policy_{i}"
        if policy.policy_id != expected_id:
            raise ValidationError(f"V015: Policy ordering inconsistent (expected '{expected_id}', got '{policy.policy_id}')")
```

---

## 3. Validation Levels

### Level 1: Structural (JSON Schema)

**Validates:**
- JSON syntax
- Required fields present
- Types match schema
- Enums in valid range

**Tool:** `jsonschema` library

### Level 2: Semantic (This Document)

**Validates:**
- Rules V001-V015
- Mathematical constraints
- Graph properties

**Tool:** Custom validator (part of PEL compiler/runtime)

### Level 3: Logical (Optional)

**Validates:**
- Constraint satisfiability (SAT solver)
- Dead code detection
- Unreachable constraints

**Tool:** Advanced static analysis (future extension)

---

## 4. Validation Workflow

```python
# Example usage
from pel_ir_validator import IRValidator
import json

# Load IR
with open("model.ir.json") as f:
    ir_doc = json.load(f)

# Validate
validator = IRValidator()
try:
    validator.validate(ir_doc)
    print("✓ IR is valid")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

---

## 5. Error Reporting

**Validation errors use format:**

```
error[V003]: Parameter 'churnRate' missing provenance
  --> model.ir.json:45:12
   |
45 |   "node_type": "param",
46 |   "name": "churnRate",
47 |   "provenance": null
   |                 ^^^^ provenance required for all parameters
   |
   = help: Add provenance block with source, method, confidence
```

---

## 6. Conformance Requirement

**All conformant runtimes MUST:**
- Validate JSON Schema (Level 1)
- Validate rules V001-V015 (Level 2)
- Reject invalid IR before execution

**Runtimes MAY:**
- Implement Level 3 validation
- Add warning-level checks (non-fatal)

---

## 7. Test Suite

**Repository:** `github.com/Coding-Krakken/pel-conformance/ir-validation-tests`

**Structure:**
```
/ir-validation-tests/
  /valid/       # 50 valid IR documents (should pass)
  /invalid/     # 150 invalid IR documents (should fail with specific error)
    /v001/      # Tests for rule V001
    /v002/      # Tests for rule V002
    ...
```

**Each test:**
```json
{
  "test_id": "v001-cyclic-dependency",
  "description": "Detect cyclic dependency A -> B -> A",
  "ir": { ... },
  "expected_result": "error",
  "expected_error_code": "V001"
}
```

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/Coding-Krakken/pel-lang/discussions](https://github.com/Coding-Krakken/pel-lang/discussions)
