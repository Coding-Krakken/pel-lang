# PEL Language Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Authors:** PEL Core Team  
**Canonical URL:** https://spec.pel-lang.org/v0.1/language

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Lexical Structure](#2-lexical-structure)
3. [Types and Type System](#3-types-and-type-system)
4. [Expressions](#4-expressions)
5. [Statements and Declarations](#5-statements-and-declarations)
6. [Models and Modules](#6-models-and-modules)
7. [Provenance and Metadata](#7-provenance-and-metadata)
8. [Constraints](#8-constraints)
9. [Policies](#9-policies)
10. [Simulation Directives](#10-simulation-directives)
11. [Error Handling](#11-error-handling)
12. [Formal Grammar (EBNF)](#12-formal-grammar-ebnf)
13. [Reserved Keywords](#13-reserved-keywords)
14. [Operator Precedence](#14-operator-precedence)
15. [Semantic Rules](#15-semantic-rules)
16. [Compilation Phases](#16-compilation-phases)
17. [Error Codes](#17-error-codes)
18. [Examples](#18-examples)
19. [Design Rationale](#19-design-rationale)
20. [Non-Goals](#20-non-goals)
21. [Future Extensions](#21-future-extensions)

---

## 1. Introduction

### 1.1 Purpose

This document defines the **Programmable Economic Language (PEL)**, a domain-specific language for specifying, simulating, and auditing economic and business models with:

- **Economic type safety** (units, scope, time semantics)
- **Uncertainty as first-class construct** (distributions, correlations)
- **Mandatory provenance** (source, method, confidence, freshness)
- **Constraint enforcement** (cash, capacity, compliance)
- **Policy execution** (strategic decisions as code)
- **Reproducibility** (deterministic + auditable)

### 1.2 Scope

This specification covers:

- Lexical syntax (tokens, identifiers, literals)
- Type system (primitive and composite economic types)
- Expression and statement semantics
- Model structure and module composition
- Provenance metadata requirements
- Constraint and policy semantics
- Compilation and validation rules
- Error codes and diagnostic requirements

This specification does **not** cover:

- Runtime implementation details (see `pel_runtime_spec.md`)
- Standard library APIs (see `pel_stdlib_spec.md`)
- IR binary encoding (see `pel_ir_schema.json`)
- Tooling protocols (LSP, package management)

### 1.3 Conformance

A PEL implementation **conforms** to this specification if:

1. It accepts all valid PEL programs defined herein
2. It rejects all invalid programs with appropriate error codes
3. It produces semantically equivalent PEL-IR for identical source
4. It enforces all mandatory semantic rules

**Conformance levels:**
- **PEL Core:** Types, basic simulation, deterministic execution
- **PEL Extended:** Monte Carlo, sensitivity, full stdlib
- **PEL Calibration:** Data ingestion, fitting, drift detection

### 1.4 Notation

This document uses:

- **EBNF** grammar notation (see Section 12)
- **`monospace`** for code
- **MUST/SHALL** for mandatory requirements
- **SHOULD** for strong recommendations
- **MAY** for optional features

---

## 2. Lexical Structure

### 2.1 Source Encoding

PEL source files:
- **MUST** be UTF-8 encoded
- **SHOULD** use Unix line endings (`\n`)
- **MAY** use UTF-8 BOM (ignored by lexer)
- **MUST** have `.pel` extension

### 2.2 Comments

```pel
// Single-line comment

/*
 * Multi-line comment
 * Nested /* comments */ are allowed
 */
```

**Rules:**
- Comments are treated as whitespace
- Nested block comments **MUST** be balanced
- Comments **MAY** appear anywhere whitespace is allowed

### 2.3 Identifiers

```ebnf
identifier = letter { letter | digit | "_" }
letter = "A".."Z" | "a".."z"
digit = "0".."9"
```

**Rules:**
- Identifiers **MUST NOT** start with digit or underscore
- Identifiers **MUST NOT** match reserved keywords (case-sensitive)
- Identifiers **SHOULD** use `snake_case` (convention, not enforced)

**Examples:**
```pel
revenue        // ✓ valid
customer_count // ✓ valid
R2             // ✓ valid
_private       // ✗ invalid (starts with underscore)
2nd_quarter    // ✗ invalid (starts with digit)
model          // ✗ invalid (reserved keyword)
```

### 2.4 Keywords

See Section 13 for complete list.

```pel
model param var func constraint policy when then simulate
Currency Rate Duration Capacity Distribution TimeSeries
per from to as import public private
```

### 2.5 Literals

#### 2.5.1 Numeric Literals

```ebnf
integer = [ "-" | "+" ] digit+ [ "_" digit+ ]*
decimal = integer "." digit+ [ exponent ]
exponent = ("e" | "E") [ "-" | "+" ] digit+
```

**Examples:**
```pel
42
-17
3.14159
1.602e-19
1_000_000    // underscores for readability (ignored)
```

**Rules:**
- Underscores **MAY** be used as separators (e.g., `1_000`)
- Scientific notation **MUST** use `e` or `E`
- Leading zeros **ARE** allowed (unlike Python)

#### 2.5.2 Currency Literals

```pel
$100         // USD (default)
€50          // EUR
£30          // GBP
¥1000        // JPY/CNY (context-dependent)
$1_250.50    // with decimal and separator
```

**Rules:**
- Currency symbol **MUST** precede numeric value
- Infers type `Currency<USD>`, `Currency<EUR>`, etc.
- Ambiguous symbols (¥) require explicit type annotation

#### 2.5.3 Percentage Literals

```pel
5%           // 0.05 as dimensionless fraction
25.5%        // 0.255
```

**Rules:**
- Percentage **MUST** immediately follow number (no space)
- Represents fraction (5% = 0.05)
- Type: `Fraction` (dimensionless)

#### 2.5.4 Duration Literals

```pel
30d          // 30 days
12mo         // 12 months
2y           // 2 years
1.5h         // 1.5 hours
```

**Supported units:**
- `s` (seconds), `m` (minutes), `h` (hours)
- `d` (days), `w` (weeks), `mo` (months), `y` (years)

**Rules:**
- Unit **MUST** immediately follow number
- Months assumed 30 days, years 365 days (configurable via runtime)

#### 2.5.5 String Literals

```pel
"Hello, world!"
"Line 1\nLine 2"       // escape sequences
"Cost is $100"         // $ not interpreted as currency
"""
Multi-line string
with preserved newlines
"""
```

**Escape sequences:**
- `\n` (newline), `\t` (tab), `\\` (backslash), `\"` (quote)
- `\u{XXXX}` (Unicode code point)

#### 2.5.6 Boolean Literals

```pel
true
false
```

### 2.6 Operators and Punctuation

```
+  -  *  /  %  ^      // arithmetic
== != <  >  <= >=     // comparison
&& || !               // logical
=  :=                 // assignment
~                     // distribution
::                    // scope resolution
|                     // alternation
,  ;  :               // separators
( ) [ ] { }           // grouping
.                     // member access
->                    // function return type
```

---

## 3. Types and Type System

**See `pel_type_system.md` for complete formal specification.**

### 3.1 Type Categories

PEL has **four** type categories:

1. **Primitive economic types** (Currency, Rate, Duration, Capacity, Count, Fraction)
2. **Composite types** (TimeSeries, Distribution, Scoped, CohortSeries)
3. **Structural types** (Record, Enum, Array)
4. **Function types** (param types → return type)

### 3.2 Primitive Types

#### 3.2.1 Currency<ISO>

```pel
var price: Currency<USD> = $100
var cost: Currency<EUR> = €50
```

**Properties:**
- Parameterized by ISO 4217 currency code
- Nominal typing: `Currency<USD>` ≠ `Currency<EUR>`
- Dimensional: `Currency * Count = Currency`, `Currency / Duration = Currency / Duration`

**Operations:**
- Addition/subtraction within same currency: `Currency<X> + Currency<X> = Currency<X>`
- Multiplication by dimensionless: `Currency<X> * Fraction = Currency<X>`
- Division: `Currency<X> / Currency<X> = Fraction`, `Currency<X> / Count = Currency<X>`

#### 3.2.2 Rate

```pel
var churnRate: Rate per Month = 0.05 / 1mo
var growthRate: Rate per Year = 0.20 / 1y
```

**Properties:**
- Represents change per unit time
- Dimensional: `Rate * Duration = Fraction`
- **MUST** specify time unit (`per Month`, `per Day`, etc.)

**Operations:**
- Addition/subtraction within same time unit: `Rate per X + Rate per X = Rate per X`
- Multiplication by duration: `Rate per X * Duration<X> = Fraction`

#### 3.2.3 Duration

```pel
var cycle: Duration = 30d
var payback: Duration = 18mo
```

**Properties:**
- Represents time intervals
- Convertible between units (with potential loss of precision)

**Operations:**
- Addition/subtraction: `Duration + Duration = Duration`
- Multiplication by dimensionless: `Duration * Fraction = Duration`
- Division: `Duration / Duration = Fraction`

#### 3.2.4 Capacity

```pel
var headcount: Capacity<Employees> = 50
var seats: Capacity<Seats> = 100
```

**Properties:**
- Represents resource limits
- Parameterized by resource type (nominal)
- Prevents mixing incompatible capacities

**Operations:**
- Addition/subtraction within type: `Capacity<X> + Capacity<X> = Capacity<X>`
- Comparison: `<`, `>`, `<=`, `>=`

#### 3.2.5 Count

```pel
var customers: Count<Customers> = 1000
var orders: Count<Orders> = 2500
```

**Properties:**
- Represents countable entities
- Parameterized by entity type
- Distinguishes `Count<Customers>` from `Count<Orders>`

**Operations:**
- Addition/subtraction within type: `Count<X> + Count<X> = Count<X>`
- Division: `Count<X> / Count<Y> = Fraction`, `Count<X> / Count<X> = Fraction`

#### 3.2.6 Fraction (dimensionless)

```pel
var margin: Fraction = 0.25
var elasticity: Fraction = -1.5
```

**Properties:**
- Dimensionless real number
- Used for ratios, percentages, coefficients

**Operations:**
- All arithmetic operations (`+`, `-`, `*`, `/`, `^`)

### 3.3 Composite Types

#### 3.3.1 TimeSeries<T>

```pel
var revenue_t: TimeSeries<Currency<USD>>
```

**Properties:**
- Indexed by time: `revenue_t[t]` where `t` is simulation timestep
- Immutable once computed (unless explicitly redefined with policies)

**Operations:**
- Indexing: `series[t]` returns `T` at timestep `t`
- Slicing: `series[t1..t2]` returns `TimeSeries<T>` for range

#### 3.3.2 Distribution<T>

```pel
var cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150)
var conversionRate: Fraction ~ Beta(α=10, β=40)
```

**Supported distributions:**
- `Beta(α, β)` — (0, 1) bounded
- `Normal(μ, σ)` — unbounded
- `LogNormal(μ, σ)` — positive unbounded
- `Uniform(low, high)` — bounded
- `Triangular(low, mode, high)` — bounded
- `Mixture([dist1, dist2, ...], [w1, w2, ...])` — weighted mixture

**Properties:**
- `~` operator indicates distributional variable
- Deterministic mode samples at mean/mode
- Monte Carlo mode samples from distribution

#### 3.3.3 Scoped<T, S>

```pel
var revenuePerCustomer: Scoped<Currency<USD>, Customer>
```

**Properties:**
- Represents "per-entity" quantities
- Type safety: prevents summing per-customer values incorrectly

**Operations:**
- Multiplication by count: `Scoped<Currency, Customer> * Count<Customers> = Currency`

#### 3.3.4 CohortSeries<T>

```pel
var cohort_revenue: CohortSeries<Currency<USD>>
```

**Properties:**
- Indexed by `[cohort_time, age]`
- `cohort_revenue[t=10, age=3]` = revenue from cohort starting at time 10, at age 3

**Operations:**
- Cohort indexing: `series[t, age]`
- Total at time: `sum(series[where age + t = T])`

### 3.4 Structural Types

#### 3.4.1 Records

```pel
record Customer {
  id: Count<Customers>
  ltv: Currency<USD>
  acquisitionCost: Currency<USD>
}
```

**Properties:**
- Named fields with types
- Structural typing (not nominal)

#### 3.4.2 Enums

```pel
enum Plan {
  Free,
  Starter,
  Professional,
  Enterprise
}
```

**Properties:**
- Closed set of named values
- Can be used as discriminators in policies

#### 3.4.3 Arrays

```pel
var prices: Array<Currency<USD>> = [$10, $20, $30]
```

**Properties:**
- Homogeneous element types
- Fixed or dynamic length (depends on runtime)

### 3.5 Type Annotations and Inference

```pel
// Explicit annotation
var price: Currency<USD> = $100

// Inferred from literal
var cost = $50  // inferred: Currency<USD>

// Inferred from expression
var margin = (price - cost) / price  // inferred: Fraction
```

**Rules:**
- Parameters **MUST** have explicit type annotations
- Variables **MAY** omit type if unambiguous
- Compiler **MUST** reject ambiguous inferences

### 3.6 Type Compatibility and Conversion

**Strict rules:**
- No implicit conversions between currencies
- No implicit conversions between time units (unless lossless)
- No implicit conversions between capacity/count types

**Explicit conversions:**
```pel
var usd: Currency<USD> = $100
var eur: Currency<EUR> = usd as Currency<EUR> with exchangeRate(1.08)
```

**Dimensional conversions (automatic):**
```pel
var months: Duration = 3mo
var days: Duration = months  // automatically converted to ~90d
```

---

## 4. Expressions

### 4.1 Literals

See Section 2.5.

### 4.2 Identifiers and Paths

```pel
revenue               // simple identifier
Customer.ltv          // member access
stdlib.pricing.elasticity  // module path
```

### 4.3 Arithmetic Expressions

```pel
a + b    // addition
a - b    // subtraction
a * b    // multiplication
a / b    // division
a % b    // modulo (Fraction only)
a ^ b    // exponentiation
```

**Type rules:**
- Addition/subtraction: operands **MUST** have same dimension
- Multiplication: dimensions combine (e.g., `Currency * Count = Currency`)
- Division: dimensions cancel (e.g., `Currency / Currency = Fraction`)
- Exponentiation: exponent **MUST** be `Fraction`, base **MAY** be any numeric type

### 4.4 Comparison Expressions

```pel
a == b   // equality
a != b   // inequality
a < b    // less than
a > b    // greater than
a <= b   // less or equal
a >= b   // greater or equal
```

**Type rules:**
- Operands **MUST** have compatible types (same dimension or comparable)
- Result type: `Boolean`

### 4.5 Logical Expressions

```pel
a && b   // logical AND
a || b   // logical OR
!a       // logical NOT
```

**Type rules:**
- Operands **MUST** be `Boolean`
- Result type: `Boolean`

### 4.6 Conditional Expressions

```pel
if condition then expr1 else expr2
```

**Type rules:**
- `condition` **MUST** be `Boolean`
- `expr1` and `expr2` **MUST** have same type

### 4.7 Function Calls

```pel
sqrt(value)
pow(base, exponent)
sum(array)
```

**Type rules:**
- Argument types **MUST** match parameter types
- Result type determined by function signature

### 4.8 Distribution Expressions

```pel
~ Beta(α=2, β=8)
~ Normal(μ=100, σ=15)
~ LogNormal(μ=$500, σ=$100)
```

**Type rules:**
- Distribution parameters **MUST** match expected types
- Result type: `Distribution<T>` where `T` is inferred from parameters

### 4.9 Array Literals and Indexing

```pel
[1, 2, 3, 4, 5]           // array literal
prices[0]                 // index (0-based)
revenue_t[t]              // time series index
cohort[t=10, age=3]       // cohort index
```

### 4.10 Lambda Expressions

```pel
(x: Fraction) -> x ^ 2
(price: Currency<USD>, quantity: Count<Items>) -> price * quantity
```

---

## 5. Statements and Declarations

### 5.1 Parameter Declarations

```pel
param name: Type = value {
  source: "...",
  method: "...",
  confidence: 0.0..1.0,
  freshness: "PnM"
}
```

**Rules:**
- **MUST** include provenance block (source, method, confidence)
- `freshness` **SHOULD** be included (ISO 8601 duration format)
- Parameters are **immutable** (cannot be reassigned)

**Example:**
```pel
param churnRate: Rate per Month = 0.05 / 1mo {
  source: "cohort_analysis_2025Q4",
  method: "fitted",
  confidence: 0.75,
  freshness: "P3M",
  correlated_with: [conversionRate, -0.3]
}
```

### 5.2 Variable Declarations

```pel
var name: Type = expression
var name = expression  // type inferred
```

**Rules:**
- Variables are **immutable by default** (use `var mut` for mutable)
- Type **MAY** be inferred if unambiguous

**Example:**
```pel
var ltv = monthlyPrice / churnRate
var mut cashBalance: Currency<USD> = $100_000  // mutable
```

### 5.3 Function Declarations

```pel
func name(param1: Type1, param2: Type2) -> ReturnType {
  // body
  return expression
}
```

**Example:**
```pel
func payback_period(cac: Currency<USD>, margin: Currency<USD> per Month) -> Duration {
  return cac / margin  // returns Duration (months)
}
```

### 5.4 Record Declarations

```pel
record Name {
  field1: Type1,
  field2: Type2
}
```

### 5.5 Enum Declarations

```pel
enum Name {
  Variant1,
  Variant2,
  Variant3
}
```

---

## 6. Models and Modules

### 6.1 Model Declaration

```pel
model ModelName {
  // parameters, variables, constraints, policies
}
```

**Rules:**
- Every PEL file **MUST** contain exactly one top-level `model` declaration
- Model name **SHOULD** be PascalCase

**Example:**
```pel
model SaaSUnitEconomics {
  param monthlyPrice: Currency<USD> per Customer = $99 { /* provenance */ }
  param churnRate: Rate per Month = 0.05 / 1mo { /* provenance */ }
  
  var ltv = monthlyPrice / churnRate
  var margin = ltv - cac
  
  constraint positive_margin: margin > $0 {
    severity: warning
  }
  
  simulate for 36mo
}
```

### 6.2 Import Declarations

```pel
import stdlib.pricing
import stdlib.demand as demand_module
import custom.models.{Funnel, Cohort}
```

**Rules:**
- Imports **MUST** appear before model declaration
- Imported modules accessed via namespace or alias

### 6.3 Module System

- **stdlib**: Standard library (bundled)
- **Custom modules**: User-defined, installed via `pel pkg`

**Module structure:**
```
my_module/
  pel_module.json    // metadata (name, version, dependencies)
  main.pel           // entry point
  utils.pel          // additional files
```

---

## 7. Provenance and Metadata

### 7.1 Provenance Block

**Mandatory fields:**
- `source`: String describing data origin
- `method`: Enumeration or string describing derivation method
- `confidence`: Numeric value in [0.0, 1.0]

**Optional fields:**
- `freshness`: ISO 8601 duration (e.g., "P3M" = 3 months)
- `owner`: String (email or team name)
- `correlated_with`: Array of `[variable_name, correlation_coefficient]`
- `notes`: String (free-form explanation)

**Method types:**
- `observed`: Direct measurement
- `fitted`: Statistical fitting from data
- `derived`: Calculated from other parameters
- `expert_estimate`: Subject matter expert input
- `external_research`: Third-party study
- `assumption`: Pure assumption (requires justification in notes)

**Example:**
```pel
param cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150) {
  source: "marketing_dashboard_2025",
  method: "fitted",
  confidence: 0.60,
  freshness: "P1M",
  owner: "marketing@company.com",
  correlated_with: [conversionRate, -0.4],
  notes: "Historical 90-day trailing average; strong seasonality in Q4"
}
```

### 7.2 Assumption Register

**Generated automatically by compiler.**

Output format (JSON):
```json
{
  "model_hash": "sha256:abcd1234...",
  "assumptions": [
    {
      "name": "cac",
      "type": "Currency<USD> per Customer",
      "value": "LogNormal(μ=$500, σ=$150)",
      "source": "marketing_dashboard_2025",
      "method": "fitted",
      "confidence": 0.60,
      "freshness": "P1M",
      "sensitivity_rank": 3
    }
  ]
}
```

---

## 8. Constraints

### 8.1 Constraint Declaration

```pel
constraint name: condition {
  severity: fatal | warning,
  message: "...",
  for: time_range | entity_scope
}
```

### 8.2 Severity Levels

- **`fatal`**: Simulation stops if violated
- **`warning`**: Violation logged but simulation continues

### 8.3 Time-Scoped Constraints

```pel
constraint cash_positive: cashBalance[t] >= $0 for all t in [0..36] {
  severity: fatal,
  message: "Company insolvent"
}
```

### 8.4 Entity-Scoped Constraints

```pel
constraint utilization_limit: utilization[employee] <= 1.0 for all employee {
  severity: warning,
  message: "Employee overutilized"
}
```

### 8.5 Soft Constraints (Slack Variables)

```pel
constraint target_margin: margin >= $50 {
  severity: warning,
  slack: true  // allow violation, track slack
}
```

**Slack computed as:**
- If `margin = $30`, slack = $20 (negative = violation magnitude)

---

## 9. Policies

### 9.1 Policy Declaration

```pel
policy name {
  when: trigger_condition,
  then: action
}
```

### 9.2 Trigger Conditions

```pel
when: t == 12                     // at specific time
when: cashBalance < $50_000       // when condition met
when: monthlyPrice changes        // when variable updated
```

### 9.3 Actions

```pel
then: variable = expression       // update variable
then: variable *= factor          // multiplicative update
then: variable += delta           // additive update
then: emit event("...")           // log event
```

### 9.4 Example

```pel
policy price_increase {
  when: t % 12 == 0,  // every 12 months
  then: monthlyPrice *= 1.05
}

policy emergency_cash_preservation {
  when: cashBalance < $50_000,
  then: headcount_growth_rate = 0.0
}
```

---

## 10. Simulation Directives

### 10.1 Simulation Time Horizon

```pel
simulate for 36mo
simulate for 5y
simulate for 1000d
```

### 10.2 Simulation Mode

```pel
simulate deterministic with seed 42
simulate monte_carlo with runs 10_000
```

### 10.3 Output Specification

```pel
output [revenue_t, margin_t, cashBalance]
```

---

## 11. Error Handling

### 11.1 Compile-Time Errors

All semantic errors **MUST** be caught at compile time:
- Type mismatches
- Dimensional errors (adding incompatible units)
- Time index errors (referencing future in non-causal context)
- Missing provenance metadata
- Undefined identifiers
- Constraint contradictions

### 11.2 Runtime Errors

Runtime errors **SHOULD** be minimized by compile-time checks:
- Division by zero (if not statically provable)
- Constraint violations (fatal constraints)
- Numerical overflow/underflow

### 11.3 Error Messages

Error messages **MUST** include:
- Error code (e.g., `E0301`)
- Location (file, line, column)
- Explanation of problem
- Suggestion for fix (when possible)

**Example:**
```
error[E0301]: Cannot add Currency<USD> and Rate per Month
  --> model.pel:15:20
   |
15 |   var total = revenue + growthRate
   |                         ^^^^^^^^^^ type mismatch
   |
   = note: left operand has type `Currency<USD>`
   = note: right operand has type `Rate per Month`
   = help: did you mean to multiply? `revenue * (1 + growthRate * duration)`
```

---

## 12. Formal Grammar (EBNF)

```ebnf
(* Top-level structure *)
program = { import_decl } model_decl ;

import_decl = "import" module_path [ "as" identifier ] ;

model_decl = "model" identifier "{" { model_item } "}" ;

model_item = param_decl
           | var_decl
           | func_decl
           | record_decl
           | enum_decl
           | constraint_decl
           | policy_decl
           | simulate_decl
           ;

(* Parameters *)
param_decl = "param" identifier ":" type "=" expr provenance_block ;

provenance_block = "{" 
  "source" ":" string ","
  "method" ":" string ","
  "confidence" ":" number
  [ "," "freshness" ":" string ]
  [ "," "owner" ":" string ]
  [ "," "correlated_with" ":" correlation_list ]
  [ "," "notes" ":" string ]
"}" ;

(* Variables *)
var_decl = "var" [ "mut" ] identifier [ ":" type ] "=" expr ;

(* Functions *)
func_decl = "func" identifier "(" param_list ")" "->" type block ;

param_list = [ param ":" type { "," param ":" type } ] ;

(* Types *)
type = primitive_type
     | composite_type
     | identifier  (* user-defined types *)
     ;

primitive_type = "Currency" "<" currency_code ">"
               | "Rate" "per" time_unit
               | "Duration"
               | "Capacity" "<" identifier ">"
               | "Count" "<" identifier ">"
               | "Fraction"
               | "Boolean"
               ;

composite_type = "TimeSeries" "<" type ">"
               | "Distribution" "<" type ">"
               | "Scoped" "<" type "," identifier ">"
               | "CohortSeries" "<" type ">"
               | "Array" "<" type ">"
               ;

(* Expressions *)
expr = literal
     | identifier
     | expr binop expr
     | unop expr
     | expr "[" expr "]"  (* indexing *)
     | func_call
     | if_expr
     | lambda_expr
     | "(" expr ")"
     ;

binop = "+" | "-" | "*" | "/" | "%" | "^"
      | "==" | "!=" | "<" | ">" | "<=" | ">="
      | "&&" | "||"
      ;

unop = "-" | "!" ;

func_call = identifier "(" [ expr { "," expr } ] ")" ;

if_expr = "if" expr "then" expr "else" expr ;

lambda_expr = "(" param_list ")" "->" expr ;

(* Literals *)
literal = number | currency | percentage | duration | string | boolean | array_literal ;

array_literal = "[" [ expr { "," expr } ] "]" ;

(* Constraints *)
constraint_decl = "constraint" identifier ":" expr constraint_block ;

constraint_block = "{"
  "severity" ":" ("fatal" | "warning")
  [ "," "message" ":" string ]
  [ "," "for" ":" scope_spec ]
"}" ;

scope_spec = "all" identifier "in" range
           | "all" identifier
           ;

(* Policies *)
policy_decl = "policy" identifier "{"
  "when" ":" expr ","
  "then" ":" action
"}" ;

action = identifier "=" expr
       | identifier "*=" expr
       | identifier "+=" expr
       | "emit" "event" "(" string ")"
       ;

(* Simulation *)
simulate_decl = "simulate" "for" duration
              | "simulate" mode "for" duration
              ;

mode = "deterministic" "with" "seed" integer
     | "monte_carlo" "with" "runs" integer
     ;
```

---

## 13. Reserved Keywords

```
and         as          async       await       
bool        break       constraint  continue    
Currency    Capacity    Count       CohortSeries
deterministic Distribution Duration  else        
emit        enum        event       false       
Fraction    for         from        func        
if          import      in          let         
loop        match       model       module      
monte_carlo mut         not         or          
param       per         policy      private     
public      Rate        record      return      
Scoped      simulate    struct      then        
TimeSeries  true        type        var         
when        where       while       with        
yield
```

---

## 14. Operator Precedence

(Highest to lowest)

1. Member access: `.`, `::`
2. Indexing: `[]`
3. Function call: `()`
4. Unary: `-`, `!`
5. Exponentiation: `^` (right-associative)
6. Multiplicative: `*`, `/`, `%`
7. Additive: `+`, `-`
8. Comparison: `<`, `>`, `<=`, `>=`
9. Equality: `==`, `!=`
10. Logical AND: `&&`
11. Logical OR: `||`
12. Conditional: `if-then-else`
13. Assignment: `=`

---

## 15. Semantic Rules

### 15.1 Time Causality

Variables **MUST NOT** reference future values non-causally:

```pel
// ✗ Invalid: future reference
var revenue[t] = revenue[t+1] * 0.9

// ✓ Valid: past reference
var revenue[t] = revenue[t-1] * (1 + growthRate)
```

### 15.2 Dimensional Consistency

All arithmetic operations **MUST** preserve dimensional correctness:

```pel
// ✗ Invalid: incompatible dimensions
var total = $100 + 0.05 / 1mo

// ✓ Valid: dimensions match
var totalCost: Currency<USD> = fixedCost + variableCost
```

### 15.3 Provenance Completeness

All `param` declarations **MUST** include valid provenance metadata.

### 15.4 Constraint Feasibility

Compiler **SHOULD** warn if constraints are trivially unsatisfiable:

```pel
// Warning: constraints contradict
constraint a: x > 10 { severity: fatal }
constraint b: x < 5 { severity: fatal }
```

---

## 16. Compilation Phases

1. **Lexical Analysis**: Source → Tokens
2. **Parsing**: Tokens → AST
3. **Semantic Analysis**:
   - Type checking
   - Dimensional analysis
   - Time causality checking
   - Provenance validation
   - Constraint feasibility analysis
4. **IR Generation**: AST → PEL-IR (JSON)
5. **Optimization** (optional): IR transformations
6. **Validation**: IR schema conformance

---

## 17. Error Codes

### E0xxx: Lexical/Syntax Errors

- **E0001**: Invalid character in source
- **E0002**: Unterminated string literal
- **E0003**: Unterminated block comment
- **E0004**: Invalid numeric literal

### E01xx: Type Errors

- **E0100**: Type mismatch
- **E0101**: Undefined type
- **E0102**: Cannot infer type (ambiguous)
- **E0103**: Recursive type definition

### E02xx: Dimensional Errors

- **E0200**: Incompatible dimensions in arithmetic
- **E0201**: Incompatible currency types
- **E0202**: Cannot convert between dimensions

### E03xx: Time Errors

- **E0300**: Non-causal time reference (future dependency)
- **E0301**: Time index out of bounds
- **E0302**: Cohort index mismatch

### E04xx: Provenance Errors

- **E0400**: Missing provenance metadata
- **E0401**: Invalid provenance field
- **E0402**: Confidence out of range [0, 1]

### E05xx: Constraint Errors

- **E0500**: Constraint always false (trivially unsatisfiable)
- **E0501**: Constraint condition not Boolean

### E06xx: Scope Errors

- **E0600**: Undefined identifier
- **E0601**: Identifier already defined
- **E0602**: Cannot access private member

**See `/spec/error_codes.md` for complete list.**

---

## 18. Examples

### 18.1 Minimal Model

```pel
model MinimalExample {
  param revenue: Currency<USD> per Month = $10_000 {
    source: "example",
    method: "assumption",
    confidence: 1.0
  }
  
  simulate for 12mo
}
```

### 18.2 SaaS Unit Economics

```pel
model SaaSUnitEconomics {
  param monthlyPrice: Currency<USD> per Customer = $99 {
    source: "pricing_page_2026-01",
    method: "observed",
    confidence: 0.95
  }
  
  param churnRate: Rate per Month ~ Beta(α=2, β=18) {
    source: "cohort_analysis_2025Q4",
    method: "fitted",
    confidence: 0.70,
    freshness: "P3M"
  }
  
  param cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150) {
    source: "marketing_dashboard",
    method: "fitted",
    confidence: 0.60,
    correlated_with: [conversionRate, -0.4]
  }
  
  var ltv = monthlyPrice / churnRate
  var margin = ltv - cac
  
  constraint positive_unit_economics: margin > $0 {
    severity: fatal,
    message: "Unit economics are negative"
  }
  
  simulate monte_carlo with runs 10_000 for 36mo
  output [ltv, margin]
}
```

---

## 19. Design Rationale

### 19.1 Why Economic Types?

**Problem:** Spreadsheets allow `=A1+B1` where A1 is dollars and B1 is hours. Nonsense.

**Solution:** PEL enforces dimensional correctness at compile time, preventing entire classes of silent errors.

### 19.2 Why Mandatory Provenance?

**Problem:** Models become political artifacts. Assumptions are hidden, undocumented, or forgotten.

**Solution:** PEL requires source, method, and confidence for all parameters. Generates assumption register automatically.

### 19.3 Why Distributions as Syntax?

**Problem:** Uncertainty is bolted on (sensitivity tables, scenario dropdowns). Correlation ignored.

**Solution:** `~` operator makes uncertainty first-class. Correlation specified inline. Monte Carlo is built-in, not optional.

### 19.4 Why Constraints?

**Problem:** Models assume infinite cash, instant hiring, unlimited capacity. Reality crashes these models.

**Solution:** Constraints make limits explicit. Fatal constraints stop simulation (no impossible paths).

---

## 20. Non-Goals

PEL is **not**:

1. **A general-purpose programming language**: No pointers, no manual memory management, no I/O (except via runtime).
2. **Turing-complete**: Intentionally restricted to ensure termination and analyzability.
3. **A database query language**: No joins, no transactions.
4. **A machine learning framework**: No training loops (though can consume ML outputs).

---

## 21. Future Extensions

Potential future additions (not in v0.1):

- **Causal inference operators**: `do(intervention)` for counterfactuals
- **Multi-agent game theory**: Nash equilibria, mechanism design
- **Stochastic differential equations**: Continuous-time extensions
- **Formal verification**: Reachability analysis, invariant checking

---

## Appendix A: Comparison to Related Languages

| Feature | PEL | Python | Modelica | AMPL | AnyLogic |
|---------|-----|--------|----------|------|----------|
| Economic types | ✓ Native | ✗ Manual | ✗ Physical | ✗ Abstract | ✗ Manual |
| Compile-time unit checking | ✓ | ✗ | ✓ (physical) | ✓ | ✗ |
| Uncertainty-native | ✓ | Libraries | Libraries | Extensions | ✓ Platform |
| Mandatory provenance | ✓ | ✗ | ✗ | ✗ | ✗ |
| Portable IR | ✓ | ✗ | ✓ (FMI) | ✗ | ✗ |

---

## Appendix B: Version History

- **v0.1.0** (Feb 2026): Initial stable specification

---

## Appendix C: References

- Modelica Language Specification: https://specification.modelica.org
- AMPL Modeling Language: https://ampl.com/resources/the-ampl-book/
- F# Units of Measure: https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/units-of-measure
- Rust Type System: https://doc.rust-lang.org/reference/types.html

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)  
**Canonical URL:** https://spec.pel-lang.org/v0.1/language
