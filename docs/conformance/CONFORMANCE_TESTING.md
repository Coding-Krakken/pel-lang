# PEL Conformance Testing

## Overview

The PEL Conformance Test Suite validates that the PEL compiler and runtime correctly implement the formal language specification. This suite consists of 280 systematic tests that verify lexical analysis, parsing, type checking, provenance tracking, and runtime semantics.

## Philosophy

Conformance testing differs from unit testing:

- **Unit tests** verify internal implementation correctness
- **Conformance tests** verify specification compliance

A conformance test failure indicates either:
1. The implementation doesn't match the specification
2. The specification is ambiguous or incorrect

## Test Categories

### 1. Lexical (30 tests)
**ID Range**: CONF-LEX-001 to CONF-LEX-030

Validates token recognition:
- Keywords (model, func, param, var, etc.)
- Identifiers (variable names, function names)
- Literals (numbers, strings, duration, currency, percentage)
- Operators (+, -, *, /, %, ~, |, etc.)
- Delimiters (parentheses, brackets, braces, semicolons)
- Comments (single-line, multi-line)
- Whitespace handling
- Error cases (invalid tokens, malformed literals)

### 2. Parsing (80 tests)
**ID Range**: CONF-PARSE-001 to CONF-PARSE-080

Validates AST construction:
- Model declarations
- Function declarations
- Parameter declarations (with provenance metadata)
- Variable declarations (base, expression, distribution)
- Expressions (arithmetic, logical, comparison, function calls)
- Type annotations (primitives, composites, generics)
- Control flow (if/else)
- Constraints (assert, warn, policy)
- Error cases (syntax errors, malformed declarations)

### 3. Type Checking (100 tests)
**ID Range**: CONF-TYPE-001 to CONF-TYPE-100

Validates type system:
- Primitive types (Int, Float, Currency, Duration, Percentage)
- Type inference from expressions
- Dimensional analysis (Duration * Rate, Currency operations)
- Currency type safety (mixing USD, EUR, GBP)
- Function type checking
- Distribution types (param vs var)
- TimeSeries type checking
- Type compatibility and subtyping
- Error cases (type mismatches, dimensional errors)

### 4. Provenance (20 tests)
**ID Range**: CONF-PROV-001 to CONF-PROV-020

Validates provenance tracking:
- Required metadata fields (source, date, confidence)
- Dependency tracking (variable dependencies)
- Assumption tracking
- Confidence range validation
- Correlation tracking
- Error cases (missing metadata, invalid confidence)

### 5. Runtime Semantics (50 tests)
**ID Range**: CONF-RUN-001 to CONF-RUN-050

Validates execution behavior:
- Expression evaluation (deterministic mode)
- Arithmetic operations
- Function execution
- Constraint evaluation (fatal, warn, policy)
- Policy execution
- Monte Carlo simulation (reproducibility with seeds)
- Distribution sampling
- Error cases (runtime errors, constraint violations)

## Running Tests

### Run All Conformance Tests
```bash
pytest tests/conformance/ -v
```

### Run Specific Category
```bash
pytest tests/conformance/test_lexical.py -v
pytest tests/conformance/test_parsing.py -v
pytest tests/conformance/test_typechecking.py -v
pytest tests/conformance/test_provenance.py -v
pytest tests/conformance/test_runtime.py -v
```

### Run With Coverage
```bash
pytest tests/conformance/ --cov=compiler --cov=runtime --cov-report=term-missing
```

### Validate YAML Schema
```bash
python3 tests/conformance/test_runner.py --validate-all
```

## Test Results Interpretation

### Expected Output
```
================================ test session starts =================================
collected 280 items

tests/conformance/test_lexical.py::TestLexicalConformance::test_lexical_conformance PASSED
tests/conformance/test_parsing.py::TestParsingConformance::test_parsing_conformance PASSED
tests/conformance/test_typechecking.py::TestTypeCheckingConformance::test_typechecking_conformance PASSED
tests/conformance/test_provenance.py::TestProvenanceConformance::test_provenance_conformance PASSED
tests/conformance/test_runtime.py::TestRuntimeConformance::test_runtime_conformance PASSED

================================= 280 passed in 15.2s ================================
```

### Failure Analysis

When a conformance test fails:

1. **Check the test specification** (`tests/conformance/testcases/<category>/<test-id>.yaml`)
2. **Review the spec reference** (field `spec_ref`)
3. **Determine root cause**:
   - Implementation bug (fix compiler/runtime)
   - Spec ambiguity (clarify specification)
   - Test case error (fix test case)
4. **Fix and re-run**

## Adding New Conformance Tests

### When to Add Tests

Add conformance tests when:
- Extending the language specification
- Discovering specification ambiguities
- Adding new language features
- Finding uncovered edge cases

### How to Add Tests

1. **Create YAML file** in appropriate category directory
2. **Follow naming convention**: `CONF-<CATEGORY>-<NUMBER>.yaml`
3. **Follow YAML schema** (see TEST_CASE_FORMAT.md)
4. **Link to specification**: Include `spec_ref` field
5. **Test both success and error cases**
6. **Run validation**: `python3 tests/conformance/test_runner.py --validate-all`
7. **Verify test passes**: `pytest tests/conformance/<category>/ -v`

## Coverage Goals

- **Lexical**: 100% of token types
- **Parsing**: 100% of grammar rules
- **Type Checking**: 100% of type rules
- **Provenance**: 100% of metadata requirements
- **Runtime**: 100% of semantic rules

## Immutability of Test IDs

Once assigned, test IDs are **immutable**:
- Never change a test ID
- Never reuse deleted test IDs
- Append new tests with next available ID

This ensures:
- Stable test history
- Reproducible results
- Clear test evolution tracking

## CI Integration

Conformance tests run automatically on:
- Every push to `main` branch
- Every pull request (premerge branches)

CI requirements:
- **Pass rate**: 100% (all 280 tests must pass)
- **Execution time**: < 30 seconds
- **No flakiness**: Deterministic results only

## Troubleshooting

### "YAML validation error"
- Check YAML syntax
- Verify all required fields present
- Use `--validate-all` flag

### "Token count mismatch"
- Lexer may have changed
- Verify expected tokens match lexer output
- Check for EOF token

### "AST structure mismatch"
- Parser AST structure may have changed
- Verify expected AST matches parser output
- Check AST node types

### "Type error expected but succeeded"
- Type checker may have changed
- Verify error case is still invalid
- Check expected error message

## References

- [Test Case Format](TEST_CASE_FORMAT.md)
- [PEL Language Specification](../../spec/pel_language_spec.md)
- [Contributing Guide](../../CONTRIBUTING.md)
