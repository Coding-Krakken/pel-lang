# PEL Conformance Testing

## Overview

The PEL Conformance Test Suite validates that the PEL compiler and runtime correctly implement the formal language specification defined in `spec/pel_language_spec.md`. This ensures:

- **Specification Compliance**: Implementation matches formal semantics
- **Regression Detection**: Prevents drift from specifications during refactoring
- **Third-Party Certification**: Enables validation of alternative implementations
- **Production Readiness**: Systematic verification before "production-ready" claims

## Philosophy

Conformance tests differ from unit tests:

| Unit Tests | Conformance Tests |
|------------|------------------|
| Test implementation details | Test specification compliance |
| White-box testing | Black-box testing |
| Fast, isolated | Comprehensive, integrated |
| Code coverage focus | Behavior verification focus |

## Test Categories

The PEL-SAFE conformance suite includes **280 tests** across 5 categories:

### 1. Lexical Analysis (30 tests)
**Scope**: Tokenization of PEL source code

- Duration literals: `2h`, `30m`, `2h30m`, `1y2mo3d`
- Currency literals: `$100`, `€50`, `£75`
- Percentage literals: `50%`, `12.5%`
- Comments: single-line (`//`), block (`/* */`)
- Operators: `+`, `-`, `*`, `/`, `~`, `|`

**Example Test**: `CONF-LEX-001` validates `2h` duration literal tokenization.

### 2. Parsing (80 tests)
**Scope**: Syntax tree construction from tokens

- Model declarations: `model MyModel { ... }`
- Parameter declarations: `param x: number = 100 @{ ... };`
- Variable declarations: `var y = x * 2;`
- Expression parsing: arithmetic, logical, comparisons
- Distribution syntax: `uniform(10, 20)`, `normal(100, 15)`

**Example Test**: `CONF-PARSE-001` validates model declaration parsing.

### 3. Type Checking (100 tests)
**Scope**: Type inference and dimensional analysis

- Dimensional analysis: `USD * months`, `customers / month`
- Currency typing: USD, EUR, GBP mixing rules
- Type inference: expression type derivation
- Distribution types: param vs var constraints
- Error cases: type mismatches, dimension conflicts

**Example Test**: `CONF-TYPE-001` validates dimensional analysis for currency operations.

### 4. Provenance (20 tests)
**Scope**: Metadata tracking and validation

- Required fields: `source`, `date`, `confidence`
- Confidence range validation: `0.0 <= confidence <= 1.0`
- Correlation tracking: `correlated_with: ["x", "y"]`

**Example Test**: `CONF-PROV-001` validates required provenance fields.

### 5. Runtime Semantics (50 tests)
**Scope**: Execution behavior and correctness

- Expression evaluation: deterministic mode
- Constraint checking: `fatal`, `warn`, `policy` levels
- Policy execution: business rule application
- Reproducibility: seed determinism

**Example Test**: `CONF-RUN-001` validates deterministic expression evaluation.

## Running Conformance Tests

### Run All Tests
```bash
pytest tests/conformance/ -v
# Expected: 280 passed in < 30s
```

### Run by Category
```bash
# Lexical tests only
pytest tests/conformance/ -v -k lexical

# Type checking tests only
pytest tests/conformance/ -v -k typechecking
```

### Validate Test Cases
```bash
# Validate YAML schema
python3 tests/conformance/test_runner.py --validate-all
# Expected: ✅ All 280 test cases valid

# Check for duplicate IDs
find tests/conformance/testcases/ -name "*.yaml" -exec grep "^id:" {} \; | sort | uniq -d
# Expected: (no output = all unique)
```

## Test Case Format

Test cases are defined in YAML files following this schema:

```yaml
id: CONF-XXX-NNN
category: <lexical|parsing|typechecking|provenance|runtime>
spec_ref: spec/pel_language_spec.md#section-N
description: Brief description of what is being tested
input: |
  model test {
    # PEL source code
  }
expected:
  # Category-specific expectations
  # For lexical: tokens
  # For parsing: ast
  # For typechecking: types or error
  # For provenance: provenance or error
  # For runtime: values
```

See `TEST_CASE_FORMAT.md` for detailed schema documentation.

## Adding New Conformance Tests

### When to Add
- When implementing a new language feature
- When fixing a specification ambiguity
- When discovering a missing edge case
- **NOT** for implementation-specific optimizations

### Steps
1. Choose appropriate category and next available ID
2. Create YAML file: `tests/conformance/testcases/<category>/CONF-XXX-NNN.yaml`
3. Follow schema in `TEST_CASE_FORMAT.md`
4. Reference specific spec section in `spec_ref`
5. Validate: `python3 tests/conformance/test_runner.py --validate-all`
6. Run: `pytest tests/conformance/testcases/<category>/CONF-XXX-NNN.yaml -v`
7. Commit with message: `Add conformance test CONF-XXX-NNN: <description>`

### Naming Convention
- **Format**: `CONF-<CATEGORY>-<NUMBER>`
- **Categories**: `LEX` (lexical), `PARSE` (parsing), `TYPE` (typechecking), `PROV` (provenance), `RUN` (runtime)
- **Numbers**: Zero-padded 3-digit sequence (001-999)
- **Examples**: `CONF-LEX-001`, `CONF-TYPE-042`, `CONF-RUN-017`

## Guardrails

### Immutability
- **Test IDs are immutable**: Once assigned, never change
- Renumber only when absolutely necessary (e.g., major refactor)
- Update all references when renumbering

### No False Positives
- Tests must accurately reflect specification
- Review test expectations carefully
- Cross-reference spec sections

### Determinism
- All tests must be deterministic (no flakiness)
- Use fixed seeds for stochastic tests
- No network dependencies, no timing dependencies

### Performance
- Full suite must complete in < 30 seconds
- Individual tests < 1 second
- Use simple examples, not production-scale models

## CI Integration

Conformance tests run automatically on:
- Every PR to `main`
- Every push to `premerge/*` branches
- Nightly builds

### Requirements
- 100% pass rate (280/280)
- No skipped tests
- No test failures tolerated

### Artifacts
- Conformance report (HTML)
- Test execution logs
- Coverage data (separate from unit tests)

## Specification References

Each test case links to a specific section in the specification:

- **Section 8**: Lexical Structure
- **Section 12**: Grammar and Parsing
- **Section 13**: Type System and Dimensional Analysis
- **Section 14**: Provenance Metadata
- **Section 15**: Runtime Semantics

## Conformance Levels

PEL defines three conformance levels:

### Core (280 tests) ✅ Implemented
- Lexical, parsing, type checking, provenance, runtime basics
- Required for all implementations

### Extended (future)
- Monte Carlo simulation
- Correlation analysis
- Advanced constraints

### Calibration (future)
- Model calibration
- Parameter estimation
- Statistical tests

This document describes the **Core** conformance level.

## FAQ

### Q: Why separate from unit tests?
**A**: Unit tests verify implementation details (coverage-driven). Conformance tests verify specification compliance (behavior-driven).

### Q: Can I skip failing conformance tests?
**A**: No. All conformance tests must pass. If a test fails, either fix the implementation or update the specification (with justification).

### Q: How do I debug a failing conformance test?
**A**: 
1. Run test individually: `pytest tests/conformance/testcases/<category>/CONF-XXX-NNN.yaml -vv`
2. Check test case YAML for expected vs actual
3. Review referenced spec section
4. Add `print()` statements in test_runner.py execution functions

### Q: Can I modify existing test cases?
**A**: Only to fix errors in the test case itself (not to make failing tests pass). Document any changes in commit message.

## See Also

- `TEST_CASE_FORMAT.md`: YAML schema and examples
- `CONTRIBUTING.md`: How to contribute conformance tests
- `spec/pel_language_spec.md`: Formal language specification
- `tests/README.md`: Testing strategy overview
