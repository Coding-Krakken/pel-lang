# Conformance Test Case Format

## Overview

Conformance test cases are defined in YAML files with a strict schema. This document describes the schema, provides examples for each category, and explains validation rules.

## File Naming

- **Location**: `tests/conformance/testcases/<category>/<test_id>.yaml`
- **Pattern**: `CONF-<CATEGORY>-<NNN>.yaml`
- **Example**: `tests/conformance/testcases/lexical/CONF-LEX-001.yaml`

## YAML Schema

### Required Fields

All test cases must include:

```yaml
id: string              # Unique test identifier (CONF-XXX-NNN)
category: string        # Test category (lexical, parsing, typechecking, provenance, runtime)
spec_ref: string        # Reference to specification section
description: string     # Brief description of what is being tested
input: string          # PEL source code to test
expected: object       # Category-specific expectations
```

### ID Format

- **Pattern**: `CONF-<CATEGORY>-<NUMBER>`
- **CATEGORY**: 3-5 uppercase letters
  - `LEX`: Lexical analysis
  - `PARSE`: Parsing
  - `TYPE`: Type checking
  - `PROV`: Provenance
  - `RUN`: Runtime
- **NUMBER**: 3-digit zero-padded integer (001-999)
- **Examples**: `CONF-LEX-001`, `CONF-TYPE-042`, `CONF-RUN-150`

### Category Values

Must be one of:
- `lexical`: Lexical analysis tests
- `parsing`: Parsing tests
- `typechecking`: Type checking tests
- `provenance`: Provenance metadata tests
- `runtime`: Runtime semantics tests

### Spec Reference Format

Reference to specific section in `spec/pel_language_spec.md`:

```yaml
spec_ref: spec/pel_language_spec.md#section-8.2
```

## Category-Specific Schemas

### 1. Lexical Tests

Tests tokenization of PEL source code.

**Schema**:
```yaml
id: CONF-LEX-NNN
category: lexical
spec_ref: spec/pel_language_spec.md#section-8
description: <what is being tested>
input: |
  <PEL source code>
expected:
  tokens:
    - type: TOKEN_TYPE
      value: <optional value>
    - type: TOKEN_TYPE
    # ... more tokens
```

**Example**:
```yaml
id: CONF-LEX-001
category: lexical
spec_ref: spec/pel_language_spec.md#section-8.2
description: Duration literal - hours only
input: |
  model test {
    param x: duration = 2h;
  }
expected:
  tokens:
    - type: MODEL
    - type: IDENTIFIER
      value: test
    - type: LBRACE
    - type: PARAM
    - type: IDENTIFIER
      value: x
    - type: COLON
    - type: DURATION
    - type: EQUALS
    - type: DURATION_LITERAL
      value: 2h
    - type: SEMICOLON
    - type: RBRACE
    - type: EOF
```

**Error Case Example**:
```yaml
id: CONF-LEX-999
category: lexical
spec_ref: spec/pel_language_spec.md#section-8
description: Invalid token sequence
input: |
  model test {
    param x = @@@;
  }
expected:
  error: "Unexpected character"
```

### 2. Parsing Tests

Tests AST construction from tokens.

**Schema**:
```yaml
id: CONF-PARSE-NNN
category: parsing
spec_ref: spec/pel_language_spec.md#section-12
description: <what is being tested>
input: |
  <PEL source code>
expected:
  ast:
    node_type: <AST node type>
    attributes:
      <attr_name>: <attr_value>
    children:
      - node_type: <child type>
        # ... nested structure
```

**Example**:
```yaml
id: CONF-PARSE-001
category: parsing
spec_ref: spec/pel_language_spec.md#section-12.1
description: Model declaration test
input: |
  model test {
    param x = 100;
  }
expected:
  ast:
    node_type: Model
    attributes:
      name: test
```

**Error Case Example**:
```yaml
id: CONF-PARSE-999
category: parsing
spec_ref: spec/pel_language_spec.md#section-12
description: Missing semicolon
input: |
  model test {
    param x = 100
  }
expected:
  error: "Expected semicolon"
```

### 3. Type Checking Tests

Tests type inference and dimensional analysis.

**Schema**:
```yaml
id: CONF-TYPE-NNN
category: typechecking
spec_ref: spec/pel_language_spec.md#section-13
description: <what is being tested>
input: |
  <PEL source code>
expected:
  types:
    <identifier>: <type>
```

**Success Example**:
```yaml
id: CONF-TYPE-001
category: typechecking
spec_ref: spec/pel_language_spec.md#section-13.2
description: Dimensional analysis - currency multiplication
input: |
  model test {
    param price: currency<USD> = $100;
    param quantity: number = 5;
    var total = price * quantity;
  }
expected:
  types:
    price: currency<USD>
    quantity: number
    total: currency<USD>
```

**Error Case Example**:
```yaml
id: CONF-TYPE-999
category: typechecking
spec_ref: spec/pel_language_spec.md#section-13.3
description: Currency mixing error
input: |
  model test {
    param usd: currency<USD> = $100;
    param eur: currency<EUR> = €50;
    var sum = usd + eur;
  }
expected:
  error: "Cannot add currency<USD> and currency<EUR>"
```

### 4. Provenance Tests

Tests provenance metadata tracking and validation.

**Schema**:
```yaml
id: CONF-PROV-NNN
category: provenance
spec_ref: spec/pel_language_spec.md#section-14
description: <what is being tested>
input: |
  <PEL source code>
expected:
  provenance:
    <identifier>:
      source: <source>
      date: <date>
      confidence: <confidence>
```

**Success Example**:
```yaml
id: CONF-PROV-001
category: provenance
spec_ref: spec/pel_language_spec.md#section-14.1
description: Required provenance fields
input: |
  model test {
    param x: number = 100 @{
      source: "Market Research 2026",
      date: "2026-01-15",
      confidence: 0.95
    };
  }
expected:
  provenance:
    x:
      source: "Market Research 2026"
      date: "2026-01-15"
      confidence: 0.95
```

**Error Case Example**:
```yaml
id: CONF-PROV-999
category: provenance
spec_ref: spec/pel_language_spec.md#section-14.2
description: Missing required field
input: |
  model test {
    param x: number = 100 @{
      source: "Test"
    };
  }
expected:
  error: "Missing required provenance field: date"
```

### 5. Runtime Tests

Tests runtime evaluation and semantics.

**Schema**:
```yaml
id: CONF-RUN-NNN
category: runtime
spec_ref: spec/pel_language_spec.md#section-15
description: <what is being tested>
input: |
  <PEL source code>
expected:
  values:
    <identifier>: <expected_value>
```

**Example**:
```yaml
id: CONF-RUN-001
category: runtime
spec_ref: spec/pel_language_spec.md#section-15.1
description: Expression evaluation - arithmetic
input: |
  model test {
    param x = 100;
    param y = 50;
    var sum = x + y;
    var product = x * y;
  }
expected:
  values:
    sum: 150
    product: 5000
```

**Determinism Example**:
```yaml
id: CONF-RUN-050
category: runtime
spec_ref: spec/pel_language_spec.md#section-15.5
description: Reproducibility with seed
input: |
  model test {
    seed = 42;
    var x = uniform(0, 100);
  }
expected:
  values:
    x: 49.6714153011451  # Deterministic with seed=42
```

## Validation Rules

### Schema Validation

All test cases are validated against the schema:

```bash
python3 tests/conformance/test_runner.py --validate-all
```

**Checks**:
1. Required fields present
2. ID format correct (CONF-XXX-NNN)
3. Category is valid
4. Expected structure matches category
5. YAML is well-formed

### ID Uniqueness

All test IDs must be unique:

```bash
find tests/conformance/testcases/ -name "*.yaml" -exec grep "^id:" {} \; | sort | uniq -d
```

Expected output: *empty* (no duplicates)

### Spec Reference Validity

Spec references should point to existing sections in `spec/pel_language_spec.md`. While not automatically validated, reviewers should check references during PR review.

## Best Practices

### 1. Keep Tests Simple

Use minimal code to test the specific feature:

❌ **Bad** (too complex):
```yaml
input: |
  model complex {
    param x = 1;
    param y = 2;
    param z = 3;
    var a = x + y;
    var b = y + z;
    var c = a + b;
    constraint c > 0;
  }
```

✅ **Good** (focused):
```yaml
input: |
  model test {
    param x = 1;
    param y = 2;
    var sum = x + y;
  }
```

### 2. Use Descriptive IDs

Match ID to feature being tested:
- `CONF-LEX-001`: First lexical test (duration literals)
- `CONF-TYPE-042`: Type checking test 42 (dimensional analysis)
- `CONF-RUN-017`: Runtime test 17 (constraint checking)

### 3. Reference Specific Spec Sections

Be precise with spec references:
- ❌ `spec/pel_language_spec.md`
- ✅ `spec/pel_language_spec.md#section-13.2`

### 4. Test One Thing

Each test should validate one specific behavior:
- ❌ Test parsing AND type checking
- ✅ Test parsing only (separate test for type checking)

### 5. Include Edge Cases

Test boundaries and edge cases:
- `CONF-LEX-010`: Fractional duration (`1.5h`)
- `CONF-TYPE-100`: Type error case
- `CONF-PROV-015`: Confidence boundary (0.0, 1.0)

## Schema Evolution

As PEL evolves, the schema may be extended:

### Adding Optional Fields

New optional fields can be added without breaking existing tests:

```yaml
expected:
  tokens: [...]
  # New optional field
  metadata:
    line_numbers: true
```

### Adding New Categories

New categories can be added for extended conformance levels:

```yaml
category: montecarlo  # New category for Extended level
```

### Deprecation Process

1. Mark field as deprecated in documentation
2. Add migration guide
3. Provide automated migration script
4. Remove after one release cycle

## Tools

### Validation Script

Located at `tests/conformance/test_runner.py`:

```bash
# Validate all test cases
python3 tests/conformance/test_runner.py --validate-all

# Outputs:
# ✅ All 280 test cases valid
# or
# ❌ Validation failed: N invalid test cases
```

### Test Template Generator

Use this template for new tests:

```bash
cat > tests/conformance/testcases/<category>/CONF-<XXX>-<NNN>.yaml << 'EOF'
id: CONF-<XXX>-<NNN>
category: <category>
spec_ref: spec/pel_language_spec.md#section-<N>
description: <description>
input: |
  model test {
    # Your test code here
  }
expected:
  # Category-specific expectations
EOF
```

## See Also

- `CONFORMANCE_TESTING.md`: Overview of conformance testing
- `spec/pel_language_spec.md`: Language specification
- `tests/conformance/test_runner.py`: Test execution engine
- `tests/conformance/assertions.py`: Assertion helpers
