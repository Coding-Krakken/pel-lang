# PEL Semantic Type System Implementation

## Overview

This document describes the implementation of PEL's semantic type system, a three-layer architecture for type checking that combines dimensional correctness with domain-specific semantics.

## Architecture: Three-Layer Type System

### Layer 1: Dimensional Types (Foundation)
Ensures dimensional correctness using physical unit analysis.

**Status**: ✅ Implemented (existing)
- `Currency<Code>`: Monetary values with currency codes (e.g., USD, EUR)
- `Count<Entity>`: Discrete quantities (e.g., customers, transactions)
- `Rate per TimeUnit`: Time-normalized values (e.g., $/month)
- `Duration`: Time intervals
- `Fraction`: Dimensionless ratios
- `Quotient`: Result of division operations maintaining dimensional info
- `Product`: Result of multiplication

### Layer 2: Semantic Contracts (Current Implementation)
Explicitly documents when and why type conversions are semantically valid beyond dimension correctness.

**Status**: 🔄 In Progress (Phase 1)

#### What Are Semantic Contracts?

A semantic contract specifies:
1. **Source Type Pattern**: What types can be converted FROM
2. **Target Type**: What type they convert TO  
3. **Reasoning**: WHY the conversion is domain-valid
4. **Constraints**: CONDITIONS under which the conversion applies
5. **Documentation**: EXAMPLES and references

#### Built-in Contracts

| Contract | Source | Target | Reason | Use Case |
|----------|--------|--------|--------|----------|
| `RevenuePerUnit_to_Price` | `Quotient<Currency, Count>` | `Currency` | Revenue divided by units yields price per unit | Pricing, unit economics |
| `RateNormalization` | `Quotient<Currency, Duration>` | `Currency` | Time-normalized revenue (MRR) is Currency-like | SaaS metrics, recurring revenue |
| `FractionFromRatio` | `Quotient<Count, Count>` | `Fraction` | Count ratios are naturally fractions | Success rates, churn, activation |
| `AverageFromTotal` | `Quotient<Currency, Count>` | `Fraction` | Revenue per unit as ratio | Cost modeling, profit margins |
| `CountAggregation` | `Quotient<Count, Duration>` | `Count` | Rates of counts aggregate to counts | Annual/quarterly rollups |
| `QuotientNormalization` | `Quotient<*>` | `Fraction` | Any division normalized to dimensionless | Advanced analytics |
| `IdentityWithScalars` | `Count` | `Fraction` | Counts can be dimensionless ratios | Ratio semantics |

### Layer 3: Model Validation (Future)
User-defined business rule validation and custom contract definitions.

**Status**: ❌ Not Yet Implemented (Phase 3)

## Implementation Phases

### Phase 1: Semantic Contract Foundation ✅ Completed
**Objective**: Establish the semantic contract system and integrate into type checker

**Deliverables**:
- ✅ `compiler/semantic_contracts.py`: Core contract system
  - `SemanticContract` class: Individual contract definition
  - `SemanticContracts` registry: Global contract management
  - Built-in contracts: 7 pre-defined domain-specific conversions
  - Contract validation framework
  
- ✅ `compiler/typechecker.py` integration:
  - `find_applicable_contracts()`: Discover applicable contracts
  - `document_conversion_justification()`: Generate user guidance
  - `validate_conversion_with_contract()`: Contract-based validation

- 📝 Documentation:
  - `docs/SEMANTIC_TYPE_SYSTEM_IMPLEMENTATION.md` (this file)
  - `spec/semantic_contracts_guide.md` (implementation guide)
  - `spec/model_style_guide.md` (user guide)

**Key Design Decisions**:
- Contracts are declarative, not imperative
- Contracts document business logic, not just type rules
- Starting with built-in contracts; custom contracts in Phase 3
- Backward compatible: doesn't break existing models

### Phase 2: Enhanced Error Messages 🔄 In Progress
**Objective**: Guide users toward semantic contracts when conversions fail

**Work Items**:
- [ ] Update type error messages to suggest applicable contracts
- [ ] Add conversion guidance in compiler warnings
- [ ] Create recovery suggestions for common mismatches
- [ ] Add `--explain` flag to show contract details

**Example**:
```
Error: Cannot assign Currency to Count
  Suggestion: If you're computing cost per unit, use:
    var cost_per_unit: Currency = total_cost / unit_count
  Applicable contract: RevenuePerUnit_to_Price
  See: docs/examples/cost_modeling.pel
```

### Phase 3: Model Validation Layer ❌ Not Started
**Objective**: Enable user-defined validation rules and custom contracts

**Work Items**:
- [ ] Custom contract syntax in PEL
- [ ] Business rule validation layer
- [ ] Contract extension mechanism
- [ ] Validation report generation

**Example Syntax** (proposed):
```pel
contract MyCustomContract {
    from: Quotient<Currency, Count>
    to: Currency
    reason: "Revenue per entity for my domain"
    constraints: {
        "numerator_is_revenue": true,
        "entity_is_customer": true
    }
    examples: [
        "subscription_fee / seats = price_per_seat"
    ]
}

model SaaS {
    var mrr: Currency<USD> = total_revenue / 12 {
        semantic_contract: MyCustomContract
    }
}
```

### Phase 4: Documentation & Examples 🔜 Planned
**Objective**: Comprehensive user guide on semantic contracts

**Work Items**:
- [ ] Update `pel_type_system.md` with contract section
- [ ] Create `semantic_type_style_guide.md`
- [ ] 10 annotated example models showing contracts
- [ ] FAQ: "When do I need to use a contract?"
- [ ] Video tutorial (optional)

## Integration with Existing Code

### Backward Compatibility
The implementation maintains full backward compatibility:

1. **Type checking**: Existing `types_compatible()` method unchanged
2. **Models**: All 100 PEL-100 models continue to work
3. **Pragmatic coercions**: Still allowed for now
4. **Errors**: No new failures introduced in Phase 1

### Future Strictness
In Phase 2+, we plan:
- Optional "strict mode" requiring explicit contract documentation
- Lint rules encouraging contract usage
- Migration path for existing models

## Key Methods in `TypeChecker`

### Finding Contracts
```python
# Discover which contracts justify a conversion
contracts = type_checker.find_applicable_contracts(
    source_type=Quotient(Currency, Count),
    target_type=Currency
)
# Returns: [REVENUE_PER_UNIT_TO_PRICE, ...]
```

### Documenting Conversions
```python
# Generate user-friendly explanation
explanation = type_checker.document_conversion_justification(
    source_type=Quotient(Currency, Count),
    target_type=Currency
)
# Returns: "Valid conversion from Quotient<Currency, Count> to Currency:
#          1. RevenuePerUnit_to_Price
#             Reason: normalization
#             When revenue (Currency) is divided by unit count..."
```

### Validating with Contracts
```python
# Check if conversion is valid and satisfies constraints
is_valid, error = type_checker.validate_conversion_with_contract(
    source_type=Quotient(Currency, Count),
    target_type=Currency,
    context={"numerator_dimension": "Currency", "denominator_type": "Count"}
)
# Returns: (True, None) or (False, "error message")
```

## Benefits of Semantic Contracts

1. **Explicit Intent**: Conversion logic is documented in code
2. **Domain Knowledge**: Captures why conversions are valid, not just that they are
3. **User Guidance**: Helps users understand valid patterns
4. **Extensibility**: Custom contracts can be added by users in Phase 3
5. **Validation**: Enforces constraints on conversions
6. **Discovery**: Users can see all valid conversions for a target type
7. **Migration Path**: Enables gradual strictness increase

## Testing

Semantic contracts are tested via:

1. **Unit Tests** (`tests/unit/test_semantic_contracts.py`):
   - Contract registration and lookup
   - Pattern matching and validation
   - Constraint checking
   - Documentation generation

2. **Integration Tests** (`tests/unit/test_typechecker_semantic.py`):
   - Contract usage in type checking
   - Error message generation with contract guidance
   - Multiple contract applicability

3. **Benchmark Validation**:
   - All 100 PEL-100 models validate correctly
   - Coverage of contract types across model suite

## Next Steps

### Immediate (Phase 1 Completion)
- [ ] Extract error patterns from existing models
- [ ] Verify all 7 contracts cover pattern coverage
- [ ] Add comprehensive tests
- [ ] Create style guide

### Short-term (Phase 2)  
- [ ] Enhanced error messages with contract guidance
- [ ] Compiler flag `--contract-report` for contract analysis
- [ ] Migration guide for existing models

### Medium-term (Phase 3)
- [ ] Custom contract support in language
- [ ] User-defined validation rules
- [ ] Contract-aware refactoring tools

## References

- [`compiler/semantic_contracts.py`](../compiler/semantic_contracts.py): Core implementation
- [`compiler/typechecker.py`](../compiler/typechecker.py): Integration point
- [`spec/pel_type_system.md`](../spec/pel_type_system.md): Type system spec
- [`spec/model_style_guide.md`](../spec/model_style_guide.md): User guide (planned)

## Glossary

- **Semantic Contract**: Explicit rule documenting domain logic for type conversions
- **Dimensional Type**: Type based on physical unit analysis (Currency, Count, etc.)
- **Coercion**: Implicit type conversion allowed by type system
- **Constraint**: Condition that must be true for conversion to be valid
- **Contract Reason**: Category of justification (e.g., NORMALIZATION, COUNTING)
- **Pragmatic Coercion**: Type conversion allowed for backward compatibility but not best practice

## Questions for Users

1. **Should contracts be required or optional?**
   - Current: Optional for 100% backward compatibility
   - Proposed Phase 2: Optional but encouraged via lints
   - Proposed Phase 3+: Could become mandatory in strict mode

2. **Should syntax support explicit contract references?**
   - Example: `var mrr: Currency = revenue / 12 { uses_contract: RateNormalization }`
   - Decision deferred to Phase 3

3. **How do we handle multi-contract scenarios?**
   - Some conversions could be valid under multiple contracts
   - Current: Return all applicable contracts; user chooses intent
   - Alternative: Require explicit selection

4. **Custom contracts - built-in or language feature?**
   - Current: Built-in only (Phase 1)
   - Phase 3: Language feature or external registry?
   - Need community feedback
