# PEL Conformance Test Case Format

## Overview

PEL conformance tests are defined in YAML files following a strict schema. Each test case validates a specific aspect of the language specification.

## YAML Schema

### Required Fields

All conformance test cases must include these fields:

```yaml
id: CONF-<CATEGORY>-<NUMBER>
category: lexical|parsing|typechecking|provenance|runtime
spec_ref: spec/pel_language_spec.md#section-reference
description: Brief description of what this test validates
input: |
  # PEL source code to test
expected:
  type: success|error
  # Category-specific expectations
```

### Field Descriptions

#### `id` (string, required)
Unique test identifier following pattern:
- `CONF-LEX-NNN`: Lexical tests (001-030)
- `CONF-PARSE-NNN`: Parsing tests (001-080)
- `CONF-TYPE-NNN`: Type checking tests (001-100)
- `CONF-PROV-NNN`: Provenance tests (001-020)
- `CONF-RUN-NNN`: Runtime tests (001-050)

**Rules:**
- IDs are immutable once assigned
- Never reuse deleted IDs
- Use zero-padded numbers (001, not 1)

#### `category` (string, required)
Test category, must match ID prefix:
- `lexical`: Token recognition tests
- `parsing`: AST construction tests
- `typechecking`: Type system tests
- `provenance`: Provenance tracking tests
- `runtime`: Runtime semantics tests

#### `spec_ref` (string, required)
Reference to language specification section being tested.

Format: `spec/pel_language_spec.md#section-anchor`

Example: `spec/pel_language_spec.md#duration-literals`

#### `description` (string, required)
One-sentence description of what this test validates.

**Good examples:**
- "Duration literal - hours and minutes"
- "Type error when adding Currency and Duration"
- "Provenance tracking for derived variables"

**Bad examples:**
- "Test duration" (too vague)
- "This test checks if the parser correctly handles..." (too verbose)

#### `input` (string, required)
PEL source code to test, using YAML multiline string syntax.

**Important:**
- Include complete, valid PEL code
- Use realistic examples
- Keep test focused (small code snippets preferred)
- Format with proper indentation

#### `expected` (object, required)
Expected test outcome with type-specific fields.

## Expected Outcomes by Category

### Lexical Tests

For successful tokenization:

```yaml
expected:
  type: success
  tokens:
    - type: TOKEN_TYPE_NAME
      value: "token_value"  # optional
    - type: TOKEN_TYPE_NAME
    # ... more tokens
    - type: EOF  # always include EOF token
```

For lexical errors:

```yaml
expected:
  type: error
  error_message: "partial error text"
```

**Example:**
```yaml
id: CONF-LEX-001
category: lexical
spec_ref: spec/pel_language_spec.md#keywords
description: Model keyword recognition
input: |
  model test {
  }
expected:
  type: success
  tokens:
    - type: MODEL
      value: model
    - type: IDENTIFIER
      value: test
    - type: LBRACE
    - type: RBRACE
    - type: EOF
```

### Parsing Tests

For successful parsing:

```yaml
expected:
  type: success
  ast:
    node_type: ASTNodeTypeName
    attributes:
      attr_name: expected_value
```

For parse errors:

```yaml
expected:
  type: error
  error_message: "partial error text"
```

**Example:**
```yaml
id: CONF-PARSE-001
category: parsing
spec_ref: spec/pel_language_spec.md#model-declarations
description: Simple model declaration
input: |
  model revenue_model {
  }
expected:
  type: success
  ast:
    node_type: Program
```

### Type Checking Tests

For successful type checking:

```yaml
expected:
  type: success
  type_map:
    variable_name: ExpectedType
```

For type errors:

```yaml
expected:
  type: error
  error_message: "partial error text"
```

**Example:**
```yaml
id: CONF-TYPE-001
category: typechecking
spec_ref: spec/pel_language_spec.md#type-inference
description: Integer arithmetic type inference
input: |
  model test {
    var x: Int = 10 + 20;
  }
expected:
  type: success
  type_map:
    x: Int
```

### Provenance Tests

For successful provenance tracking:

```yaml
expected:
  type: success
  provenance:
    variable_name: [dependency1, dependency2]
```

For provenance errors:

```yaml
expected:
  type: error
  error_message: "partial error text"
```

**Example:**
```yaml
id: CONF-PROV-001
category: provenance
spec_ref: spec/pel_language_spec.md#provenance-metadata
description: Basic dependency tracking
input: |
  model test {
    param x: Int = 10;
    var y: Int = x * 2;
  }
expected:
  type: success
  provenance:
    y: [x]
```

### Runtime Tests

For successful execution:

```yaml
expected:
  type: success
  runtime_values:
    variable_name: expected_value
```

For runtime errors:

```yaml
expected:
  type: error
  error_message: "partial error text"
```

**Example:**
```yaml
id: CONF-RUN-001
category: runtime
spec_ref: spec/pel_language_spec.md#arithmetic-operations
description: Integer addition evaluation
input: |
  model test {
    var result: Int = 10 + 20;
  }
expected:
  type: success
  runtime_values:
    result: 30
```

## Test Naming Conventions

### File Names
- Format: `CONF-<CATEGORY>-<NUMBER>.yaml`
- Category codes: LEX, PARSE, TYPE, PROV, RUN
- Numbers: Zero-padded 3 digits (001-999)

### Test IDs
- Must match file name (without .yaml extension)
- Immutable once assigned
- Sequential within category

### Descriptions
- Start with capital letter
- End without period
- Be specific and concise
- Avoid "Test that..." prefix

**Good:**
- "Currency literal with decimal places"
- "Type error when dividing Duration by Currency"

**Bad:**
- "test currency"
- "Test that currency literals work correctly with decimal places and proper formatting"

## Best Practices

### 1. Focus on One Thing
Each test should validate exactly one aspect of the specification.

**Bad** (tests multiple things):
```yaml
input: |
  model test {
    param x: Int = 10;
    param y: Float = 3.14;
    var z: Currency = $100;
  }
```

**Good** (focused test):
```yaml
input: |
  model test {
    var z: Currency = $100;
  }
```

### 2. Use Realistic Code
Write code that resembles actual PEL programs, not contrived examples.

### 3. Test Both Success and Error
For every feature, test:
- Valid usage (success case)
- Invalid usage (error case)

### 4. Include Edge Cases
Test boundary conditions:
- Empty inputs
- Maximum values
- Special characters
- Whitespace variations

### 5. Link to Specification
Every test must reference a specific section in the language specification.

### 6. Keep Tests Deterministic
- No random values
- No time-dependent behavior
- No external dependencies
- Reproducible results

## Validation

### Manual Validation
```bash
# Validate single file
python3 -c "import yaml; yaml.safe_load(open('tests/conformance/testcases/lexical/CONF-LEX-001.yaml'))"

# Validate all files
python3 tests/conformance/test_runner.py --validate-all
```

### Automated Validation
Validation checks:
- Valid YAML syntax
- All required fields present
- ID matches file name
- Category matches ID prefix
- Spec reference format correct
- Expected type is 'success' or 'error'

## Examples

See existing test cases in:
- `tests/conformance/testcases/lexical/`
- `tests/conformance/testcases/parsing/`
- `tests/conformance/testcases/typechecking/`
- `tests/conformance/testcases/provenance/`
- `tests/conformance/testcases/runtime/`

## References

- [Conformance Testing Guide](CONFORMANCE_TESTING.md)
- [PEL Language Specification](../../spec/pel_language_spec.md)
- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
