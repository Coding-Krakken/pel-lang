# PEL Semantic Type System - User Guide

## Introduction

The PEL semantic type system provides a foundation for writing economically sound models with explicit documentation of type conversions. This guide helps you understand when and how to use semantic contracts in your models.

## Core Concept: Three-Layer Type Safety

PEL's type system has three layers:

```
Layer 1: Dimensional Types (strict)
         ↓
        Currency<USD>, Count<Customer>, Rate per Month
         ↓
         ↓
Layer 2: Semantic Contracts (documented)
         ↓
        Why conversions are valid for your domain
         ↓
         ↓
Layer 3: Business Rules (your domain logic)
         ↓
        Custom validation for your specific use case
```

### Layer 1: Dimensional Types
Ensures physical correctness using dimensional analysis, like how engineers check if physical equations are dimensionally consistent.

**Examples**:
- `Currency<USD>`: Money in US dollars
- `Count<Customer>`: Number of customers
- `Rate per Month`: Value per month (MRR, churn rate, etc.)
- `Fraction`: Dimensionless ratio (0.0-1.0 or any multiplier)

### Layer 2: Semantic Contracts
Explains **why** type conversions are mathematically valid despite dimensional differences.

**Examples**:
- **RevenuePerUnit_to_Price**: Revenue / Customers = Price per Customer (Currency)
- **RateNormalization**: Annual Revenue / 12 = Monthly Revenue (Currency)
- **FractionFromRatio**: Success Count / Total Count = Success Rate (Fraction)

### Layer 3: Business Rules
Your custom validation rules for your specific domain (future feature).

## Semantic Contracts: When to Use Them

### Scenario 1: Revenue Per Unit (RevenuePerUnit_to_Price)

**Problem**: You have total revenue and customer count, and want revenue per customer.

```pel
model SaaS {
    param annual_revenue: Currency<USD> = $1200000
    param customer_count: Count<Customer> = 1000
    
    // This is a Quotient type: Currency / Count
    var revenue_per_customer = annual_revenue / customer_count
    
    // You want to treat this as a Price (Currency)
    // Semantic contract: RevenuePerUnit_to_Price
    var avg_customer_value: Currency<USD> = revenue_per_customer {
        // Future: explicit contract documentation
        // semantic_contract: RevenuePerUnit_to_Price
    }
}
```

**When to use**: When dividing revenue or costs by quantity to get unit economics (price, cost per item, etc.).

**Contract**: `RevenuePerUnit_to_Price`
- From: `Quotient<Currency, Count>`
- To: `Currency`
- Reason: Revenue per unit yields an effective price

### Scenario 2: MRR and Time-Normalized Revenue (RateNormalization)

**Problem**: You have annual revenue but need monthly revenue (MRR).

```pel
model SaaS {
    param annual_revenue: Currency<USD> = $1200000
    
    // This creates: Quotient<Currency, Duration>
    // But semantically it's MRR (Currency per month)
    var monthly_revenue: Currency<USD> = annual_revenue / 12 {
        // Future: 
        // semantic_contract: RateNormalization,
        // meaning: "Converting annual to monthly for recurring revenue"
    }
}
```

**When to use**: When dividing revenue by a time period to get revenue per unit time (especially 1/12 for monthly from annual).

**Contract**: `RateNormalization`
- From: `Quotient<Currency, Duration>`
- To: `Currency`
- Reason: Time-normalized revenue is Currency-like

**Common subcases**:
- Annual → Monthly: divide by 12
- Annual → Daily: divide by 365
- Quarterly → Monthly: divide by 3

### Scenario 3: Count Ratios (FractionFromRatio)

**Problem**: You have successful transactions and total transactions, want success rate.

```pel
model Conversion {
    param total_users: Count<User> = 10000
    param activated_users: Count<User> = 3000
    
    // This is Quotient<Count, Count>
    // Semantically it's a fraction/percentage
    var activation_rate: Fraction = activated_users / total_users {
        // Future:
        // semantic_contract: FractionFromRatio,
        // meaning: "Ratio of successful outcomes to total outcomes"
    }
}
```

**When to use**: When dividing one count by another to get a ratio, percentage, or probability.

**Contract**: `FractionFromRatio`
- From: `Quotient<Count, Count>`
- To: `Fraction`
- Reason: Count ratios are naturally dimensionless

**Common subcases**:
- Success rate: activated / total
- Churn rate: churned / initial
- Conversion rate: converted / visitors
- Take rate: fees / revenue

### Scenario 4: Cost Ratios (AverageFromTotal)

**Problem**: You want cost as a percentage of revenue.

```pel
model Margins {
    param revenue: Currency<USD> = 100000
    param cogs: Currency<USD> = 30000
    
    // This is Quotient<Currency, Count> if treating it as cost per unit
    // Or Quotient<Currency, Currency> if treating as ratio
    // Either way, as a fraction: COGS / Revenue
    var cogs_ratio: Fraction = cogs / revenue {
        // Future:
        // semantic_contract: AverageFromTotal,
        // meaning: "Cost as ratio of revenue"
    }
}
```

**When to use**: When expressing one monetary value as a ratio of another (margins, cost ratios, fee percentages).

**Contract**: `AverageFromTotal`
- From: `Quotient<Currency, Count>` (or similar)
- To: `Fraction`
- Reason: Revenue ratios are dimensionless

## When NOT to Use Conversions

If a conversion doesn't fit any semantic contract, reconsider your model:

### Red Flag 1: Currency → Count (Direct, no divide)
❌ **Wrong**:
```pel
var customers: Count<Customer> = $100000  // Makes no sense!
```

✅ **Correct**: If you need to infer count from cost, divide by unit cost:
```pel
var unit_cost: Currency<USD> = $100
var customers: Count<Customer> = budget / unit_cost
```

### Red Flag 2: Unexplained Quotient Conversions
❌ **Unclear**:
```pel
var mystery: Currency<USD> = something / some_number  // Why is this Currency?
```

✅ **Clear**:
```pel
var price_per_customer: Currency<USD> = total_revenue / customer_count {
    // semantic_contract: RevenuePerUnit_to_Price
}
```

### Red Flag 3: Breaking Unit Economics
❌ **Wrong**:
```pel
var mrr: Currency<USD> = churn_rate / customer_count  // Nonsensical!
```

✅ **Correct**:
```pel
var mrr: Currency<USD> = annual_revenue / 12  // Time normalization
var churn_rate: Fraction = churned_customers / total_customers  // Ratio
```

## Best Practices

### 1. Name Variables Descriptively

Use names that indicate the semantic contract:

```pel
// Good - name indicates it's a per-unit value
var revenue_per_customer: Currency<USD> = total_revenue / customers

// Unclear - name doesn't match meaning
var temp: Currency<USD> = total_revenue / customers
```

### 2. Use Type Annotations Explicitly

Always annotate derived variables:

```pel
// Good - explicit type documents intent
var monthly_revenue: Currency<USD> = annual_revenue / 12

// Bad - could be inferred as Quotient type
var monthly_revenue = annual_revenue / 12
```

### 3. Document Complex Conversions

For non-obvious calculations, add comments:

```pel
// Conversion contract: RateNormalization
// We divide by 12 because revenue data is annual and our model operates in monthly terms
var monthly_revenue: Currency<USD> = annual_revenue / 12
```

### 4. Group Related Variables

Organize variables by conversion type:

```pel
// Unit economics (RevenuePerUnit_to_Price contracts)
var revenue_per_customer: Currency<USD> = annual_revenue / customer_count
var cost_per_customer: Currency<USD> = total_costs / customer_count
var profit_per_customer: Currency<USD> = revenue_per_customer - cost_per_customer

// Ratios (FractionFromRatio contracts)
var gross_margin: Fraction = profit / revenue
var customer_acquisition_cost: Currency<USD> = marketing_spend / new_customers
```

### 5. Validate Your Conversions

Ask yourself: "Which semantic contract justifies this conversion?"

If you can't answer clearly, the conversion is suspect.

## Common Patterns by Domain

### SaaS / Subscription Revenue

```pel
// Monthly recurring revenue (RateNormalization)
var mrr: Currency<USD> = annual_revenue / 12

// Customer economics (RevenuePerUnit_to_Price)
var arpu: Currency<USD> = monthly_revenue / active_subscribers
var cac: Currency<USD> = marketing_spend / new_customers
var payback_period: Duration = cac / (arpu - cogs_per_customer)

// Ratios (FractionFromRatio)
var churn_rate: Fraction = churned_customers / start_customers
var growth_rate: Fraction = (end_customers - start_customers) / start_customers
var magic_number: Fraction = (end_mrr - start_mrr) / marketing_spend
```

### Marketplaces

```pel
var take_rate: Fraction = platform_revenue / gross_volume  // Ratio
var commission_per_transaction: Currency<USD> = total_commissions / transactions  // Unit
var marketplace_value: Currency<USD> = total_gvp / total_customers  // Unit (fragile!)
```

### E-commerce

```pel
var revenue_per_transaction: Currency<USD> = total_revenue / transaction_count
var customer_lifetime_value: Currency<USD> = total_revenue / unique_customers
var cost_of_goods_sold_ratio: Fraction = cogs / revenue
var shipping_cost_per_order: Currency<USD> = total_shipping / order_count
```

### Network Effects

```pel
var engagement_rate: Fraction = active_users / registered_users  // FractionFromRatio
var virality_coefficient: Fraction = new_users_from_invites / invites_sent  // FractionFromRatio
var revenue_per_engaged_user: Currency<USD> = total_revenue / engaged_users  // RevenuePerUnit
```

## Understanding Error Messages

When the type checker detects an invalid conversion, it will guide you toward applicable contracts:

### Example Error
```
Type Error: Cannot assign Quotient<Currency, Count> to Count
What went wrong: You're dividing Currency by Count but expecting a Count result

Suggestion: If you're computing revenue per unit, use RevenuePerUnit_to_Price contract:
  var price_per_unit: Currency = total_revenue / unit_count

See: spec/semantic_contracts_guide.md#revenue-per-unit
```

## Checking if Your Model Uses Contracts Correctly

Run the contract analyzer:

```bash
$ pel compile --contract-report model.pel
```

This generates a report showing:
- All type conversions in your model
- Which semantic contract justifies each
- Whether all conversions have clear justification

Example output:
```
Contract Analysis Report: model.pel

Variable: revenue_per_customer
  Conversion: Quotient<Currency, Count> → Currency
  Contract: RevenuePerUnit_to_Price ✓
  Status: JUSTIFIED

Variable: monthly_revenue
  Conversion: Quotient<Currency, Duration> → Currency
  Contract: RateNormalization ✓
  Status: JUSTIFIED

Variable: magic_metric
  Conversion: Currency → Count
  Contract: ???
  Status: NO CONTRACT FOUND
  Recommendation: This conversion lacks justification. Reconsider your model logic.
```

## FAQ

### Q: Do I need to explicitly list contracts in my code?
**A**: Not in Phase 1. Contracts are discovered automatically by the type checker. In Phase 3+, you'll be able to explicitly reference contracts for clarity.

### Q: What if my conversion doesn't match any contract?
**A**: This signals that your conversion may be logically unsound. Double-check:
1. Are the dimensions physically correct? (Layer 1)
2. Does the conversion make economic sense? (Layer 2)
3. Is there an undocumented domain rule? (Layer 3 - propose as new contract)

### Q: Can I create custom contracts?
**A**: In Phase 1: No, only built-in contracts are available.
In Phase 3+: Yes, you'll be able to define custom contracts for your domain.

### Q: Is this stricter than before?
**A**: In Phase 1: No, all existing models continue to work. The system **documents** conversions but doesn't enforce them.
In Phase 2+: We'll add optional strict mode that requires contract justification.

### Q: How is this different from just adding comments?
**A**: Great question!
- **Comments**: Human-readable but not machine-checked
- **Contracts**: Both machine-checkable AND human-readable
- **Future**: Contracts enable automated validation, migration, and refactoring

## Next Steps

1. **Understand your conversions**: Identify all type conversions in your model
2. **Map to contracts**: For each conversion, identify which contract justifies it
3. **Annotate variables**: Use clear type annotations (already required!)
4. **Test thoroughly**: Ensure your model produces economically sensible results
5. **Share patterns**: Report patterns that don't fit existing contracts

## References

- [Semantic Contracts API](../compiler/semantic_contracts.py)
- [Type System Specification](../spec/pel_type_system.md)
- [Implementation Guide](../docs/SEMANTIC_TYPE_SYSTEM_IMPLEMENTATION.md)
- Examples: See `benchmarks/pel_100/` directory for 100 real models

## Getting Help

If a conversion seems justified but isn't covered by a contract:
1. Open an issue with: "Contract request: [domain] - [conversion]"
2. Describe the domain logic that justifies it
3. Provide an example model
4. Propose a name and description for the contract

Your contributions help build a more comprehensive semantic type system!
