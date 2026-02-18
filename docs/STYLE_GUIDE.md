# PEL Style Guide

This guide defines the official formatting and naming conventions for PEL (Programmable Economic Language). These rules are enforced by `pel format` (formatter) and `pel lint` (linter).

**Table of Contents:**
- [Philosophy](#philosophy)
- [Formatting Rules](#formatting-rules)
- [Naming Conventions](#naming-conventions)
- [Code Organization](#code-organization)
- [Comments and Documentation](#comments-and-documentation)
- [Best Practices](#best-practices)
- [Anti-Patterns](#anti-patterns)

---

## Philosophy

The PEL style guide is designed around these principles:

1. **Readability First**: Code is read more often than written
2. **Consistency**: Uniform style reduces cognitive load
3. **Semantic Clarity**: Names and structure should reveal intent
4. **Domain Appropriateness**: Economic modeling conventions matter
5. **Tool-Friendly**: Code should be easy to format and lint automatically

**Why These Rules?**
- **4 spaces**: Balances readability and horizontal space
- **100 character lines**: Fits most screens, allows side-by-side diffs
- **snake_case for parameters**: Matches mathematical notation conventions
- **PascalCase for models**: Distinguishes models as "types" or "classes"

---

## Formatting Rules

### Indentation

**Rule**: Use **4 spaces** per indentation level (never tabs).

```pel
// ✅ Good
model SaaSGrowth {
    param initial_mrr: Currency<USD> = $10_000
    var revenue: TimeSeries<Currency<USD>>
}

// ❌ Bad (2 spaces)
model SaaSGrowth {
  param initial_mrr: Currency<USD> = $10_000
}

// ❌ Bad (tabs)
model SaaSGrowth {
	param initial_mrr: Currency<USD> = $10_000
}
```

**Rationale**: 4 spaces provides clear visual hierarchy without excessive horizontal space usage. Tabs cause inconsistent rendering across editors.

### Line Length

**Rule**: Limit lines to **100 characters** (soft limit).

```pel
// ✅ Good
param annual_recurring_revenue: Currency<USD> = monthly_revenue * 12

// ⚠️ Acceptable (slightly over for readability)
param customer_acquisition_cost_with_marketing: Currency<USD> = total_marketing_spend / new_customers

// ❌ Bad (excessive length)
param this_is_an_extremely_long_parameter_name_that_makes_the_line_unreadable_and_should_be_broken_up_or_renamed: Currency<USD> = some_calculation
```

**Rationale**: 100 characters fits comfortably on modern displays while allowing side-by-side code comparison. Longer lines hinder readability.

### Spacing

**Operators**: Add spaces around binary operators.

```pel
// ✅ Good
var profit = revenue - costs
var growth = previous * (1 + growth_rate)
var ratio = numerator / denominator

// ❌ Bad
var profit=revenue-costs
var growth=previous*(1+growth_rate)
```

**Commas**: Space after commas, not before.

```pel
// ✅ Good
var values = [100, 200, 300, 400]

// ❌ Bad
var values = [100,200,300,400]
var values = [100 ,200 ,300]
```

**Colons**: Space after colons in type annotations.

```pel
// ✅ Good
param initial_revenue: Currency<USD> = $10_000

// ❌ Bad
param initial_revenue:Currency<USD> = $10_000
param initial_revenue : Currency<USD> = $10_000
```

**Parentheses/Brackets**: No spaces inside.

```pel
// ✅ Good
var result = calculate(a, b, c)
var arr = [1, 2, 3]

// ❌ Bad
var result = calculate( a, b, c )
var arr = [ 1, 2, 3 ]
```

**Braces**: Space before opening brace, newline after.

```pel
// ✅ Good
model Test {
    param x: Int = 10
}

// ❌ Bad
model Test{
    param x: Int = 10
}

model Test 
{
    param x: Int = 10
}
```

### Blank Lines

**Rule**: Use blank lines to separate logical sections.

- **2 blank lines** between top-level model definitions (if multiple in one file)
- **1 blank line** between parameter/variable groups
- **0 blank lines** within tightly related declarations

```pel
// ✅ Good
model Revenue {
    // Initial conditions
    param initial_mrr: Currency<USD> = $10_000
    param growth_rate: Rate per Month = 0.10 / 1mo
    
    // Calculated metrics
    var mrr: TimeSeries<Currency<USD>>
    var arr = mrr * 12
}

// ❌ Bad (no logical grouping)
model Revenue {
    param initial_mrr: Currency<USD> = $10_000

    param growth_rate: Rate per Month = 0.10 / 1mo

    var mrr: TimeSeries<Currency<USD>>

    var arr = mrr * 12
}
```

**Maximum consecutive blank lines**: 2 (enforced by formatter).

### Final Newline

**Rule**: All files must end with a single newline character.

**Rationale**: POSIX standard, prevents "no newline at end of file" warnings in version control.

---

## Naming Conventions

### Models: PascalCase

**Rule**: Model names use **PascalCase** (uppercase first letter, camelCase thereafter).

```pel
// ✅ Good
model SaaSGrowth { }
model CustomerRetention { }
model ThreeYearForecast { }

// ❌ Bad
model saas_growth { }        // snake_case
model saasGrowth { }         // camelCase
model SAASGROWTH { }         // ALL_CAPS
```

**Rationale**: Models act as "types" in PEL, similar to classes in OOP. PascalCase clearly distinguishes them from variables.

### Parameters and Variables: snake_case

**Rule**: Parameters and variables use **snake_case** (lowercase with underscores).

```pel
// ✅ Good
param initial_revenue: Currency<USD> = $10_000
param monthly_growth_rate: Rate per Month = 0.10 / 1mo
var customer_lifetime_value: Currency<USD>

// ❌ Bad
param InitialRevenue: Currency<USD> = $10_000        // PascalCase
param monthlyGrowthRate: Rate per Month = 0.10 / 1mo // camelCase
param INITIAL_REVENUE: Currency<USD> = $10_000       // ALL_CAPS
```

**Rationale**: snake_case aligns with mathematical notation conventions (e.g., `r_0`, `growth_rate`). It's also easier to read for long names common in economic modeling.

### Constants: UPPER_SNAKE_CASE

**Rule**: Constants (immutable, non-configurable values) use **UPPER_SNAKE_CASE**.

```pel
// ✅ Good
const PI: Int = 3.14159
const DAYS_PER_YEAR: Int = 365
const MAX_ITERATIONS: Int = 1000

// ❌ Bad
const pi: Int = 3.14159           // lowercase
const DaysPerYear: Int = 365      // PascalCase
```

**Rationale**: ALL_CAPS clearly signals "this value never changes" to readers.

### Functions: snake_case

**Rule**: Function names use **snake_case**.

```pel
// ✅ Good
func calculate_npv(cashflows: Array<Currency>, discount_rate: Rate) -> Currency {
    // ...
}

// ❌ Bad
func calculateNPV(...) { }    // camelCase
func CalculateNPV(...) { }    // PascalCase
```

### Prefixes for Special Cases

**Unused Variables**: Prefix with underscore `_` to silence linter.

```pel
// ✅ Good (intentionally unused)
param _reserved_capacity: Int = 1000

// ❌ Bad (triggers PEL001/PEL002 violations)
param reserved_capacity: Int = 1000  // Never used
```

**Private/Internal**: Use single underscore prefix (convention, not enforced).

```pel
// ✅ Convention for internal implementation details
var _intermediate_calculation = step1 + step2
var _cache: TimeSeries<Int>
```

---

## Code Organization

### Model Structure

**Recommended order** within a model:

1. Model declaration and metadata
2. Parameters (sorted by: required → optional → derived)
3. Constants
4. Variables (sorted by: declaration → timeseries → derived)
5. Functions
6. Constraints
7. Policies
8. Statements/logic

```pel
// ✅ Good - Clear organization
model RevenueModel {
    // === Parameters ===
    param initial_mrr: Currency<USD> = $10_000
    param growth_rate: Rate per Month = 0.10 / 1mo
    
    // === Constants ===
    const MONTHS_PER_YEAR: Int = 12
    
    // === Variables ===
    var mrr: TimeSeries<Currency<USD>>
    var arr: Currency<USD>
    
    // === Logic ===
    mrr[0] = initial_mrr
    mrr[t+1] = mrr[t] * (1 + growth_rate)
    arr = mrr * MONTHS_PER_YEAR
}

// ❌ Bad - Random order
model RevenueModel {
    var arr: Currency<USD>
    const MONTHS_PER_YEAR: Int = 12
    mrr[0] = initial_mrr
    param growth_rate: Rate per Month = 0.10 / 1mo
    var mrr: TimeSeries<Currency<USD>>
    param initial_mrr: Currency<USD> = $10_000
}
```

### Grouping Related Items

Use blank lines and comments to group related declarations.

```pel
// ✅ Good
model SaaSMetrics {
    // Revenue parameters
    param initial_mrr: Currency<USD> = $10_000
    param expansion_rate: Rate per Month = 0.05 / 1mo
    param contraction_rate: Rate per Month = 0.02 / 1mo
    
    // Cost parameters
    param cogs_percent: Percent = 30%
    param opex_fixed: Currency<USD> = $50_000
    
    // Calculated metrics
    var net_mrr: TimeSeries<Currency<USD>>
    var gross_margin: Percent
}
```

---

## Comments and Documentation

### Line Comments

**Rule**: Use `//` for line comments. Place on own line or at end of statement.

```pel
// ✅ Good
// This parameter represents the initial monthly recurring revenue
param initial_mrr: Currency<USD> = $10_000

param growth_rate: Rate per Month = 0.10 / 1mo  // Conservative estimate

// ❌ Bad (overly verbose)
// This is the initial monthly recurring revenue parameter that we use
// to seed the model with a starting value for the MRR calculation
param initial_mrr: Currency<USD> = $10_000
```

### Documentation Requirements

**Models** (public): Should have a comment explaining purpose.

```pel
// ✅ Good
// SaaS growth model forecasting MRR and ARR over 36 months.
// Includes expansion and contraction effects.
model SaaSGrowth {
    // ...
}
```

**Complex Logic**: Add comments for non-obvious calculations.

```pel
// ✅ Good
// CAC Payback Period = Cost to acquire / Monthly revenue per customer
// Assumes linear recovery (no compounding)
var payback_months = customer_acquisition_cost / (arr / customer_count / 12)

// ❌ Bad (no explanation for complex formula)
var magic_number = (a * b) / (c + d) - sqrt(e)
```

### Comment Style

- **Sentence case**: Start with capital letter, end with period for complete sentences
- **Keep concise**: Comments should clarify, not repeat code
- **Update with code**: Outdated comments are worse than no comments

---

## Best Practices

### 1. Use Meaningful Names

```pel
// ✅ Good
param customer_acquisition_cost: Currency<USD> = $500
param monthly_churn_rate: Rate per Month = 0.05 / 1mo

// ❌ Bad
param cac: Currency<USD> = $500           // Unclear abbreviation
param r: Rate per Month = 0.05 / 1mo      // Single letter
param thing: Currency<USD> = $500         // Generic name
```

### 2. Prefer Explicit Types

```pel
// ✅ Good
param initial_revenue: Currency<USD> = $10_000
var count: Int = 100

// ⚠️ Acceptable but less clear
param initial_revenue = $10_000  // Type inferred
var count = 100
```

### 3. Use Provenance Annotations

```pel
// ✅ Good
param conversion_rate: Percent = 2.5% {
    source: "Q4_2025_metrics",
    method: "observed",
    confidence: 0.95
}

// ❌ Bad (no provenance for important parameter)
param conversion_rate: Percent = 2.5%
```

### 4. Avoid Magic Numbers

```pel
// ✅ Good
const MONTHS_PER_YEAR: Int = 12
const AVERAGE_DAYS_PER_MONTH: Int = 30.44

var annual_revenue = monthly_revenue * MONTHS_PER_YEAR

// ❌ Bad
var annual_revenue = monthly_revenue * 12  // What is 12?
```

### 5. Break Down Complex Expressions

```pel
// ✅ Good
var gross_margin = (revenue - cogs) / revenue
var operating_margin = (revenue - cogs - opex) / revenue
var net_margin = (revenue - cogs - opex - taxes) / revenue

// ❌ Bad
var net_margin = (revenue - cogs - opex - taxes) / revenue  // Do gross/operating separately
```

---

## Anti-Patterns

### ❌ Avoid: Deeply Nested Expressions

```pel
// ❌ Bad
var result = ((a + b) * (c - d)) / ((e * f) + (g / h))

// ✅ Good
var numerator = (a + b) * (c - d)
var denominator = (e * f) + (g / h)
var result = numerator / denominator
```

### ❌ Avoid: Circular Dependencies

```pel
// ❌ Bad
var a = b + 1
var b = a * 2  // Circular!

// ✅ Good
var a = 10
var b = a * 2
var c = b + 1
```

### ❌ Avoid: Unused Parameters

```pel
// ❌ Bad
param unused_value: Int = 100  // Never referenced

// ✅ Good (if intentionally unused)
param _reserved_capacity: Int = 100  // Prefix with _
```

### ❌ Avoid: Inconsistent Naming

```pel
// ❌ Bad
model revenue_calculator {           // snake_case model
    param MonthlyRevenue: Currency   // PascalCase param
    var ANNUAL_REV: Currency         // ALL_CAPS var
}

// ✅ Good
model RevenueCalculator {
    param monthly_revenue: Currency<USD>
    var annual_revenue: Currency<USD>
}
```

---

## Tools

### Automatic Formatting

```bash
# Format a single file
pel format model.pel

# Format all .pel files in a directory
pel format src/

# Check formatting without modifying (CI-friendly)
pel format . --check

# Show diff of changes
pel format model.pel --diff
```

### Linting

```bash
# Lint a file
pel lint model.pel

# Lint with JSON output (for CI)
pel lint model.pel --json

# Only show errors (suppress warnings)
pel lint model.pel --severity error

# Lint specific rules only
pel lint model.pel --rule PEL001 --rule PEL010
```

### Configuration

Create `.pelformat.toml` to customize formatting:

```toml
[format]
line_length = 120      # Override default 100
indent_size = 2        # Override default 4
max_blank_lines = 1    # Override default 2
```

Create `.pellint.toml` to customize linting:

```toml
[linter]
enabled_rules = ["PEL001", "PEL002", "PEL008", "PEL010"]
line_length = 120

[rules.PEL010]
severity = "warning"   # Upgrade from info to warning
```

---

## Summary

**Key Takeaways:**
- ✅ Use `pel format` to auto-format code
- ✅ Models: PascalCase, Parameters/Variables: snake_case
- ✅ 4 spaces indentation, 100 character lines
- ✅ Group related declarations, add explanatory comments
- ✅ Avoid magic numbers, circular dependencies, unused parameters
- ✅ Enable pre-commit hooks for automatic enforcement

**Questions or Suggestions?**  
See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to propose style guide changes.

