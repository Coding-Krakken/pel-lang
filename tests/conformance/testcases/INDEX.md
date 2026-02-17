# PEL Conformance Test Index

## Quick Reference

| Category | ID Range | Count | Location |
|----------|----------|-------|----------|
| Lexical | CONF-LEX-001 to CONF-LEX-030 | 30 | `testcases/lexical/` |
| Parsing | CONF-PARSE-001 to CONF-PARSE-080 | 80 | `testcases/parsing/` |
| Type Checking | CONF-TYPE-001 to CONF-TYPE-100 | 100 | `testcases/typechecking/` |
| Provenance | CONF-PROV-001 to CONF-PROV-020 | 20 | `testcases/provenance/` |
| Runtime | CONF-RUN-001 to CONF-RUN-050 | 50 | `testcases/runtime/` |
| **Total** | | **280** | |

## Lexical Tests (30)

Core tokenization tests for PEL lexical grammar.

**Key Tests:**
- CONF-LEX-001 to 004: Duration literals (d, mo, yr)
- CONF-LEX-005 to 007: Currency literals ($100, $50_000, $99.99)
- CONF-LEX-008 to 009: Percentage literals (5%, 2.5%)
- CONF-LEX-010: All keywords
- CONF-LEX-011 to 012: Identifiers
- CONF-LEX-013 to 016: Number literals (integers, decimals, suffixes)
- CONF-LEX-017 to 018: String literals
- CONF-LEX-019: Boolean literals
- CONF-LEX-020 to 023: Operators and delimiters
- CONF-LEX-024: Comments
- CONF-LEX-025: Distribution syntax (~)
- CONF-LEX-026: Type annotations
- CONF-LEX-027 to 029: Error cases
- CONF-LEX-030: Large currency values

## Parsing Tests (80)

AST construction tests for PEL grammar productions.

**Key Tests:**
- CONF-PARSE-001: Empty model
- CONF-PARSE-002 to 005: Parameter declarations
- CONF-PARSE-006 to 008: Variable declarations
- CONF-PARSE-009 to 020: Binary expressions and operators
- CONF-PARSE-021 to 040: Logical operators, function calls, arrays
- CONF-PARSE-041 to 045: Constraints, policies, functions
- CONF-PARSE-046 to 070: Complex scenarios (distributions, control flow)
- CONF-PARSE-071 to 080: Error cases

## Type Checking Tests (100)

Type inference and validation tests.

**Key Tests:**
- CONF-TYPE-001 to 010: Basic type inference
- CONF-TYPE-011 to 030: Arithmetic type rules
- CONF-TYPE-031 to 050: Comparison and logical operators
- CONF-TYPE-051 to 070: Function types and TimeSeries
- CONF-TYPE-071 to 100: Complex type scenarios

## Provenance Tests (20)

Metadata tracking and uncertainty propagation tests.

**Key Tests:**
- CONF-PROV-001 to 004: Basic provenance metadata
- CONF-PROV-005 to 007: Dependency tracking
- CONF-PROV-008 to 009: Uncertainty propagation
- CONF-PROV-010 to 020: Advanced provenance scenarios

## Runtime Tests (50)

Execution and evaluation tests.

**Key Tests:**
- CONF-RUN-001 to 020: Expression evaluation
- CONF-RUN-021 to 030: Control flow and functions
- CONF-RUN-031 to 040: Advanced features (Monte Carlo, policies)
- CONF-RUN-041 to 050: Error handling and analysis modes

## Usage

```bash
# Validate all tests
python3 tests/conformance/test_runner.py --validate-all

# Run all tests
pytest tests/conformance/

# Run specific category
pytest tests/conformance/test_lexical.py
pytest tests/conformance/test_parsing.py

# Run specific test
pytest tests/conformance/ -k CONF-LEX-001
```

## File Naming Convention

All test files follow the pattern: `CONF-{CATEGORY}-{NUMBER}.yaml`

Where:
- CATEGORY: LEX, PARSE, TYPE, PROV, RUN
- NUMBER: 001-030 (LEX), 001-080 (PARSE), 001-100 (TYPE), 001-020 (PROV), 001-050 (RUN)

## Test Structure

Each YAML file contains:
- `id`: Unique test identifier
- `category`: Test category
- `spec_ref`: Reference to language spec section
- `description`: Human-readable test description
- `input`: PEL source code to test
- `expected`: Expected outcome (success with results or error)
