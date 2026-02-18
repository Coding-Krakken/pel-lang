# Migration Guide: Adding Semantic Contract Documentation

This guide explains how to add semantic contract documentation to existing PEL models to take advantage of enhanced error messages and contract analysis tooling.

## Overview

The semantic type system introduces 7 built-in contracts that justify common type conversions in business models:

1. **RevenuePerUnit_to_Price**: `Quotient<Currency, Count>` → `Currency`
2. **RateNormalization**: `Quotient<Currency, Duration>` → `Currency`
3. **FractionFromRatio**: `Quotient<Count, Count>` → `Fraction`
4. **FractionToRate**: `Product<Fraction, Rate>` → `Rate`
5. **DurationFromCount**: `Count<TimeUnit>` → `Duration<TimeUnit>`
6. **CountFromDuration**: `Duration<TimeUnit>` → `Count<TimeUnit>`
7. **TemporalAggregation**: `Sum(values over time)` → `aggregate value`

## Step 1: Analyze Your Model

Run the contract analysis tool on your existing model:

```bash
python compiler/compiler.py --contract-report examples/your_model.pel
```

This generates a report showing:
- All type conversions in your model
- Which conversions are justified by semantic contracts
- Suggested contract documentation for unjustified conversions

Example output:

```markdown
# Semantic Contract Analysis Report

## Model: saas_metrics

### Variables with Justified Conversions

1. **monthly_recurring_revenue** (line 12)
   - Type: Currency<USD>
   - Expression: `annual_contract_value / 12`
   - Conversion: Quotient<Currency, Currency> → Currency
   - Contract: RateNormalization
   - Justification: Time-normalized revenue calculation

### Variables with Unjustified Conversions

1. **average_price** (line 25)
   - Type: Currency<USD>
   - Expression: `total_revenue / customer_count`
   - Suggested contract: RevenuePerUnit_to_Price
   - Suggested documentation:
     ```
     # @contract RevenuePerUnit_to_Price
     # Justification: Average revenue per customer represents unit pricing
     ```

## Summary
- Total variables: 15
- Justified conversions: 8 (53%)
- Unjustified conversions: 7 (47%)
```

## Step 2: Add Contract Documentation

For each unjustified conversion, add inline documentation using the suggested format.

### Before (No Contract Documentation):

```pel
model SaaS_Metrics {
    param total_revenue: Currency<USD> = $100000
    param customer_count: Count<Customer> = 100
    
    var average_revenue_per_customer: Currency<USD> = 
        total_revenue / customer_count
}
```

**Problem**: Division creates `Quotient<Currency, Count>`, not `Currency`. This causes a type error.

### After (With Contract Documentation):

```pel
model SaaS_Metrics {
    param total_revenue: Currency<USD> = $100000
    param customer_count: Count<Customer> = 100
    
    # @contract RevenuePerUnit_to_Price
    # Justification: Average revenue per customer represents unit economics
    var average_revenue_per_customer: Currency<USD> = 
        total_revenue / customer_count
}
```

**Result**: Contract documentation justifies the conversion. Type checker accepts it.

## Step 3: Common Migration Patterns

### Pattern 1: MRR Calculations (RateNormalization)

**Before:**
```pel
var monthly_revenue: Currency<USD> = annual_revenue / 12
# Type error: Quotient<Currency, Number> → Currency
```

**After:**
```pel
# @contract RateNormalization
# Justification: Annual revenue normalized to monthly recurring revenue
var monthly_revenue: Currency<USD> = annual_revenue / 12
```

### Pattern 2: Conversion Rates (FractionFromRatio)

**Before:**
```pel
var conversion_rate: Fraction = paid_customers / trial_users
# Type error: Quotient<Count, Count> → Fraction
```

**After:**
```pel
# @contract FractionFromRatio
# Justification: Trial-to-paid conversion rate (business percentage)
var conversion_rate: Fraction = paid_customers / trial_users
```

### Pattern 3: Unit Pricing (RevenuePerUnit_to_Price)

**Before:**
```pel
var price_per_unit: Currency<USD> = total_revenue / units_sold
# Type error: Quotient<Currency, Count> → Currency
```

**After:**
```pel
# @contract RevenuePerUnit_to_Price
# Justification: Average selling price per unit
var price_per_unit: Currency<USD> = total_revenue / units_sold
```

### Pattern 4: Efficiency Multipliers (FractionToRate)

**Before:**
```pel
var effective_rate: Rate<Customer, Day> = signup_rate * conversion_rate
# Type error: Product<Rate, Fraction> → Rate
```

**After:**
```pel
# @contract FractionToRate
# Justification: Conversion efficiency scales signup rate to customer rate
var effective_rate: Rate<Customer, Day> = signup_rate * conversion_rate
```

### Pattern 5: Time Period Conversions (DurationFromCount)

**Before:**
```pel
var trial_period: Duration<Day> = trial_days
# Type error: Count<Day> → Duration<Day>
```

**After:**
```pel
# @contract DurationFromCount
# Justification: Trial configuration (14 days) represents time period duration
var trial_period: Duration<Day> = trial_days
```

### Pattern 6: Period Counting (CountFromDuration)

**Before:**
```pel
var lifetime_revenue: Currency<USD> = mrr * customer_lifetime
# Type error: Currency * Duration → Currency (needs count)
```

**After:**
```pel
# @contract CountFromDuration
# Justification: Lifetime duration converted to month count for revenue calculation
var lifetime_months: Count<Month> = customer_lifetime
var lifetime_revenue: Currency<USD> = mrr * lifetime_months
```

### Pattern 7: Temporal Aggregation (TemporalAggregation)

**Before:**
```pel
var quarterly_revenue: Currency<USD> = jan_revenue + feb_revenue + mar_revenue
# Implicit temporal aggregation
```

**After:**
```pel
# @contract TemporalAggregation
# Justification: Sum monthly revenues to quarterly total
var quarterly_revenue: Currency<USD> = jan_revenue + feb_revenue + mar_revenue
```

## Step 4: Validate Changes

After adding contract documentation, validate your model:

```bash
# Run the compiler
python compiler/compiler.py examples/your_model.pel

# Run the contract analyzer again
python compiler/compiler.py --contract-report examples/your_model.pel
```

Expected result: All conversions should now be justified, and the report should show 100% justified conversions.

## Step 5: Update Tests (If Any)

If your model has associated tests, ensure they still pass:

```bash
pytest tests/test_your_model.py -v
```

## Best Practices

### 1. Be Specific in Justifications

**Bad:**
```pel
# @contract RevenuePerUnit_to_Price
# Justification: Unit pricing
```

**Good:**
```pel
# @contract RevenuePerUnit_to_Price
# Justification: Average selling price per widget, used for margin analysis
```

### 2. Document Business Logic

**Bad:**
```pel
# @contract RateNormalization
var mrr: Currency<USD> = arr / 12
```

**Good:**
```pel
# @contract RateNormalization
# Justification: Annual recurring revenue normalized to monthly for cash flow analysis
# Used in cohort retention and revenue forecasting
var mrr: Currency<USD> = arr / 12
```

### 3. Group Related Contracts

```pel
# Customer acquisition funnel analysis
# @contract FractionToRate
var trial_signups: Rate<User, Day> = visitor_rate * trial_conversion_rate

# @contract FractionToRate
var paid_customers: Rate<Customer, Day> = trial_signups * paid_conversion_rate

# @contract RevenuePerUnit_to_Price
var customer_acquisition_cost: Currency<USD> = marketing_spend / paid_customers
```

### 4. Use Contract Analysis for Code Review

Include contract analysis in your development workflow:

```bash
# Before committing changes
python compiler/compiler.py --contract-report examples/model.pel > contract_analysis.txt
git add contract_analysis.txt
git commit -m "Add semantic contract documentation"
```

## Troubleshooting

### "No applicable contract found"

**Symptom**: Compiler error says "No applicable contract found for conversion"

**Solution**: Check that you're using the right contract name. Available contracts:
- `RevenuePerUnit_to_Price`
- `RateNormalization`
- `FractionFromRatio`
- `FractionToRate`
- `DurationFromCount`
- `CountFromDuration`
- `TemporalAggregation`

### "Contract doesn't match conversion types"

**Symptom**: Contract documentation doesn't resolve type error

**Solution**: Verify the conversion matches the contract signature:

```pel
# RevenuePerUnit_to_Price: Quotient<Currency, Count> → Currency
var price: Currency<USD> = revenue / count  # ✓ Correct

var price: Currency<USD> = revenue / duration  # ✗ Wrong (need RateNormalization)
```

### "Enhanced error message not showing"

**Symptom**: Type errors don't include contract suggestions

**Solution**: Ensure you're using the latest compiler version with Phase 2 error enhancements. Rebuild if necessary:

```bash
pip install -e .
```

## Complete Migration Example

### Original Model (Type Errors):

```pel
model Unit_Economics {
    param annual_revenue: Currency<USD> = $1200000
    param customer_count: Count<Customer> = 100
    param trial_signups: Count<User> = 500
    
    var monthly_revenue: Currency<USD> = annual_revenue / 12
    var revenue_per_customer: Currency<USD> = annual_revenue / customer_count
    var conversion_rate: Fraction = customer_count / trial_signups
}
```

**Compiler output:**
```
Error: Type mismatch in variable 'monthly_revenue'
  Expected: Currency<USD>
  Got: Quotient<Currency<USD>, Number>

Error: Type mismatch in variable 'revenue_per_customer'
  Expected: Currency<USD>
  Got: Quotient<Currency<USD>, Count<Customer>>

Error: Type mismatch in variable 'conversion_rate'
  Expected: Fraction
  Got: Quotient<Count<Customer>, Count<User>>
```

### Migrated Model (Fully Documented):

```pel
model Unit_Economics {
    param annual_revenue: Currency<USD> = $1200000
    param customer_count: Count<Customer> = 100
    param trial_signups: Count<User> = 500
    
    # @contract RateNormalization
    # Justification: Annual revenue normalized to monthly recurring revenue
    var monthly_revenue: Currency<USD> = annual_revenue / 12
    
    # @contract RevenuePerUnit_to_Price
    # Justification: Average annual revenue per customer (unit economics)
    var revenue_per_customer: Currency<USD> = annual_revenue / customer_count
    
    # @contract FractionFromRatio
    # Justification: Trial-to-paid conversion rate (success metric)
    var conversion_rate: Fraction = customer_count / trial_signups
}
```

**Compiler output:**
```
✓ Compilation successful
✓ All semantic contracts validated
```

**Contract analysis output:**
```
# Semantic Contract Analysis Report

## Model: Unit_Economics

### Summary
- Total variables: 3
- Justified conversions: 3 (100%)
- Unjustified conversions: 0 (0%)

✓ All conversions are semantically justified
```

## Additional Resources

- **Contract Reference**: See `docs/semantic_contracts.md` for detailed contract specifications
- **Examples**: Check `examples/semantic_contracts/` for real-world usage patterns
- **Type System**: Read `spec/pel_type_system.md` for comprehensive type information
- **API Documentation**: See `contracts/compiler_api.yaml` for programmatic access

## Summary

Migration steps:
1. ✅ Run `--contract-report` on existing models
2. ✅ Review unjustified conversions
3. ✅ Add contract documentation with justifications
4. ✅ Validate with compiler and analyzer
5. ✅ Update tests and documentation

The semantic type system enhances PEL models with:
- **Type safety**: Catch modeling errors at compile time
- **Self-documentation**: Business logic encoded in contracts
- **Analysis tooling**: Automated contract validation
- **Better errors**: Helpful suggestions when types don't match
