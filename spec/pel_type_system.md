# PEL Type System Specification v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Authors:** PEL Core Team  
**Canonical URL:** https://spec.pel-lang.org/v0.1/type-system

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Type Categories](#2-type-categories)
3. [Primitive Economic Types](#3-primitive-economic-types)
4. [Dimensional Analysis](#4-dimensional-analysis)
5. [Composite Types](#5-composite-types)
6. [Structural Types](#6-structural-types)
7. [Type Inference](#7-type-inference)
8. [Subtyping and Compatibility](#8-subtyping-and-compatibility)
9. [Type Checking Rules](#9-type-checking-rules)
10. [Error Detection](#10-error-detection)
11. [Type System Properties](#11-type-system-properties)

---

## 1. Introduction

### 1.1 Purpose

The PEL type system provides **compile-time guarantees** for economic correctness:

- **Unit safety:** Cannot add dollars to days
- **Scope safety:** Cannot sum per-customer values without multiplying by customer count
- **Time safety:** Cannot reference future values non-causally
- **Currency safety:** USD ≠ EUR (nominal typing)
- **Distribution safety:** Cannot mix point estimates and distributions unsafely

### 1.2 Design Principles

1. **Economic first:** Types model economic reality, not programming convenience
2. **Explicit over implicit:** No silent conversions
3. **Fail fast:** Errors caught at compile time, not runtime
4. **Expressiveness:** Common patterns easy, nonsense hard
5. **Tool-friendly:** Types enable IDE autocomplete, refactoring, analysis

---

## 2. Type Categories

PEL has four type categories:

| Category | Examples | Purpose |
|----------|----------|---------|
| **Primitive** | `Currency<USD>`, `Rate`, `Duration` | Economic quantities with units |
| **Composite** | `TimeSeries<T>`, `Distribution<T>` | Time-indexed or stochastic values |
| **Structural** | `record`, `enum`, `Array<T>` | Data organization |
| **Function** | `(T1, T2) -> T3` | Computations |

---

## 3. Primitive Economic Types

### 3.1 Currency<ISO>

**Syntax:**
```pel
Currency<USD>
Currency<EUR>
Currency<GBP>
```

**Semantics:**
- Parameterized by ISO 4217 currency code
- **Nominal typing:** `Currency<USD>` ≠ `Currency<EUR>` (even if values equal)
- Represents monetary amounts

**Dimensional behavior:**
```
Currency<X> + Currency<X> → Currency<X>
Currency<X> - Currency<X> → Currency<X>
Currency<X> * Fraction → Currency<X>
Currency<X> / Fraction → Currency<X>
Currency<X> / Currency<X> → Fraction
Currency<X> * Count<Y> → Currency<X>  (totaling)
```

**Literals:**
```pel
$100         // Currency<USD>
€50          // Currency<EUR>
£25.50       // Currency<GBP>
```

**Type-checking rule:**
$$\frac{\Gamma \vdash e_1 : \text{Currency}\langle X \rangle \quad \Gamma \vdash e_2 : \text{Currency}\langle X \rangle}
{\Gamma \vdash e_1 + e_2 : \text{Currency}\langle X \rangle}$$

**Error example:**
```pel
var total = $100 + €50  // Error E0201: Cannot add Currency<USD> and Currency<EUR>
```

### 3.2 Rate

**Syntax:**
```pel
Rate per Month
Rate per Day
Rate per Year
```

**Semantics:**
- Represents change rate per time unit
- Dimensional: `Rate * Duration → Fraction`

**Dimensional behavior:**
```
Rate per X + Rate per X → Rate per X
Rate per X * Duration<X> → Fraction
Rate per X * Count<Y> → Rate per X
```

**Literals:**
```pel
0.05 / 1mo      // Rate per Month
2.5% / 1d       // Rate per Day
```

**Type-checking rule:**
$$\frac{\Gamma \vdash e_1 : \text{Rate per } U \quad \Gamma \vdash e_2 : \text{Duration}\langle U \rangle}
{\Gamma \vdash e_1 \times e_2 : \text{Fraction}}$$

**Example:**
```pel
param churnRate: Rate per Month = 0.05 / 1mo
param lifetime: Duration<Month> = 20mo
var expectedChurns: Fraction = churnRate * lifetime  // 1.0 (100%)
```

### 3.3 Duration

**Syntax:**
```pel
Duration
Duration<Month>  // with explicit time unit
```

**Semantics:**
- Represents time intervals
- Implicit unit unless specified
- Convertible between units (may lose precision)

**Dimensional behavior:**
```
Duration + Duration → Duration
Duration - Duration → Duration
Duration * Fraction → Duration
Duration / Duration → Fraction
```

**Literals:**
```pel
30d        // 30 days
18mo       // 18 months
2.5y       // 2.5 years
```

**Conversion rules:**
- 1 month = 30 days (configurable)
- 1 year = 365 days (configurable)
- Implicit conversions allowed if lossless

**Example:**
```pel
var payback: Duration = cac / monthlyMargin  // Result in months
```

### 3.4 Capacity<R>

**Syntax:**
```pel
Capacity<Employees>
Capacity<Seats>
Capacity<Servers>
```

**Semantics:**
- Represents resource limits/availability
- **Nominal typing:** different capacity types cannot mix
- Used for constraint modeling

**Dimensional behavior:**
```
Capacity<R> + Capacity<R> → Capacity<R>
Capacity<R> - Capacity<R> → Capacity<R>
Capacity<R> * Fraction → Capacity<R>
Capacity<R> / Capacity<R> → Fraction
```

**Example:**
```pel
param maxHeadcount: Capacity<Employees> = 100
var currentHeadcount: Capacity<Employees> = 75
constraint hiring_limit: currentHeadcount <= maxHeadcount
```

### 3.5 Count<E>

**Syntax:**
```pel
Count<Customers>
Count<Orders>
Count<Units>
```

**Semantics:**
- Represents countable entities
- **Nominal typing:** prevents mixing incompatible counts
- Distinguishes populations (customers vs orders vs units)

**Dimensional behavior:**
```
Count<E> + Count<E> → Count<E>
Count<E> - Count<E> → Count<E>
Count<E> * Fraction → Count<E>
Count<E> / Count<E> → Fraction
Count<E> / Duration → Count<E> per Duration  (flow rate)
```

**Example:**
```pel
var newCustomers: Count<Customers> = 100
var orders: Count<Orders> = 250
// var invalid = newCustomers + orders  // Error: incompatible count types
```

### 3.6 Fraction (dimensionless)

**Syntax:**
```pel
Fraction
```

**Semantics:**
- Dimensionless real number
- Used for ratios, percentages, elasticities, coefficients

**Dimensional behavior:**
```
Fraction + Fraction → Fraction
Fraction * Fraction → Fraction
Fraction * T → T  (for any dimensional type T)
```

**Literals:**
```pel
0.25
25%        // 0.25
-1.5       // elasticity coefficient
```

---

## 4. Dimensional Analysis

### 4.1 Dimension Algebra

Every type has an associated **dimension**:

$$\text{dim}: \text{Type} \to \text{Dimension}$$

**Base dimensions:**
- `[Currency<X>]`: monetary dimension (per currency)
- `[Duration]`: time dimension
- `[Count<E>]`: entity count dimension (per entity type)
- `[Capacity<R>]`: resource capacity dimension (per resource)
- `[Fraction]`: dimensionless (identity)

**Dimension operations:**

$$
\begin{align*}
\text{dim}(T_1 + T_2) &= \text{dim}(T_1) \quad \text{[requires dim}(T_1) = \text{dim}(T_2)] \\
\text{dim}(T_1 \times T_2) &= \text{dim}(T_1) \cdot \text{dim}(T_2) \\
\text{dim}(T_1 / T_2) &= \text{dim}(T_1) / \text{dim}(T_2) \\
\end{align*}
$$

**Example:**
```pel
Currency<USD> / Duration  → [Currency<USD>] / [Duration]  = [Currency<USD> / Duration]
Currency<USD> * Count<Customers>  → [Currency<USD>] * [Count<Customers>]  = [Currency<USD>]
```

### 4.2 Type Inference from Dimensions

**Rule:**
$$\frac{\Gamma \vdash e_1 : \tau_1 \quad \Gamma \vdash e_2 : \tau_2 \quad \text{dim}(\tau_1) \cdot \text{dim}(\tau_2) = d}
{\Gamma \vdash e_1 \times e_2 : \text{typeOf}(d)}$$

where `typeOf(d)` constructs the type with dimension `d`.

**Example:**
```pel
var price: Currency<USD> per Customer = $99  // Scoped<Currency<USD>, Customer>
var customers: Count<Customers> = 100
var revenue = price * customers  // Inferred: Currency<USD>
```

### 4.3 Dimensional Error Detection

**Invalid operations caught at compile time:**

```pel
// Error E0200: Cannot add Currency and Duration
var invalid1 = $100 + 30d

// Error E0201: Cannot add different currencies
var invalid2 = $100 + €50

// Error E0202: Cannot multiply two currencies (dimension [Currency]^2 not representable)
var invalid3 = $100 * $50
```

---

## 5. Composite Types

### 5.1 TimeSeries<T>

**Syntax:**
```pel
TimeSeries<Currency<USD>>
TimeSeries<Count<Customers>>
```

**Semantics:**
- Indexed by time: `series[t]` where `t ∈ ℕ`
- Immutable (unless policy updates)

**Operations:**
```
series[t: Nat] → T
series[t1..t2] → TimeSeries<T>  (slicing)
```

**Type-checking rule:**
$$\frac{\Gamma \vdash s : \text{TimeSeries}\langle T \rangle \quad \Gamma \vdash t : \mathbb{N}}
{\Gamma \vdash s[t] : T}$$

**Example:**
```pel
var revenue_t: TimeSeries<Currency<USD>>
var revenue_at_12 = revenue_t[12]  // Type: Currency<USD>
```

### 5.2 Distribution<T>

**Syntax:**
```pel
Distribution<Currency<USD>>
Distribution<Fraction>
```

**Semantics:**
- Represents uncertain variable
- Specifies probability distribution over type `T`

**Constructors:**
```pel
~ Beta(α, β)                  // Distribution<Fraction>
~ Normal(μ, σ)                // Distribution<Fraction> (or typed parameter)
~ LogNormal(μ: $500, σ: $150) // Distribution<Currency<USD>>
~ Uniform(low, high)
~ Mixture([D1, D2], [w1, w2])
```

**Type-checking rule:**
$$\frac{\Gamma \vdash \mu : T \quad \Gamma \vdash \sigma : T}
{\Gamma \vdash \sim \text{Normal}(\mu, \sigma) : \text{Distribution}\langle T \rangle}$$

**Example:**
```pel
param cac: Currency<USD> per Customer ~ LogNormal(μ=$500, σ=$150)
// Type: Distribution<Scoped<Currency<USD>, Customer>>
```

### 5.3 Scoped<T, S>

**Syntax:**
```pel
Scoped<Currency<USD>, Customer>
Scoped<Duration, Order>
```

**Semantics:**
- Represents "per-entity" quantities
- Prevents naive summing of per-entity values

**Type-checking rule (totaling):**
$$\frac{\Gamma \vdash e_1 : \text{Scoped}\langle T, E \rangle \quad \Gamma \vdash e_2 : \text{Count}\langle E \rangle}
{\Gamma \vdash e_1 \times e_2 : T}$$

**Example:**
```pel
var ltv: Currency<USD> per Customer = $1200  // Scoped<Currency<USD>, Customer>
var customers: Count<Customers> = 500
var totalLTV = ltv * customers  // Type: Currency<USD>
```

**Error detection:**
```pel
var ltv_per_customer: Currency<USD> per Customer = $1200
var ltv_per_order: Currency<USD> per Order = $80
// var invalid = ltv_per_customer + ltv_per_order  // Error: different scopes
```

### 5.4 CohortSeries<T>

**Syntax:**
```pel
CohortSeries<Currency<USD>>
```

**Semantics:**
- Indexed by `[cohort_start_time, age]`
- Used for cohort analysis (retention, LTV curves)

**Operations:**
```
cohort[c: Nat, a: Nat] → T
```

**Type-checking rule:**
$$\frac{\Gamma \vdash c : \mathbb{N} \quad \Gamma \vdash a : \mathbb{N} \quad c + a \leq t_{\text{current}}}
{\Gamma \vdash \text{cohort}[c, a] : T}$$

(Causality: can only access cohorts where `c + a ≤ current_time`)

**Example:**
```pel
var cohort_revenue: CohortSeries<Currency<USD>>
var month_10_age_3_revenue = cohort_revenue[10, 3]
```

---

## 6. Structural Types

### 6.1 Records

**Syntax:**
```pel
record Customer {
  id: Count<Customers>,
  ltv: Currency<USD>,
  cac: Currency<USD>,
  acquired_at: Duration
}
```

**Semantics:**
- Named fields with types
- Structural typing (duck typing)

**Type-checking rule:**
$$\frac{\Gamma \vdash r : \text{record} \{f_1: T_1, \ldots, f_n: T_n\}}
{\Gamma \vdash r.f_i : T_i}$$

### 6.2 Enums

**Syntax:**
```pel
enum Plan {
  Free,
  Starter,
  Professional,
  Enterprise
}
```

**Semantics:**
- Closed set of values
- Used for discriminating policies/logic

### 6.3 Arrays

**Syntax:**
```pel
Array<Currency<USD>>
Array<Count<Customers>>
```

**Semantics:**
- Homogeneous elements
- Fixed or dynamic length

**Operations:**
```
array[i: Nat] → T
length(array) → Nat
```

---

## 7. Type Inference

### 7.1 Bidirectional Type Checking

PEL uses **bidirectional type checking**:

- **Checking mode:** Given type, verify expression conforms
- **Synthesis mode:** Derive type from expression

**Synthesis (↑):**
$$\Gamma \vdash e \Uparrow \tau$$
"In context Γ, expression e synthesizes type τ"

**Checking (↓):**
$$\Gamma \vdash e \Downarrow \tau$$
"In context Γ, expression e checks against type τ"

### 7.2 Inference Rules

**Literal (synthesize):**
$$\frac{}{\Gamma \vdash \$100 \Uparrow \text{Currency}\langle\text{USD}\rangle}$$

**Variable (synthesize):**
$$\frac{\Gamma(x) = \tau}{\Gamma \vdash x \Uparrow \tau}$$

**Addition (synthesize):**
$$\frac{\Gamma \vdash e_1 \Uparrow \tau \quad \Gamma \vdash e_2 \Downarrow \tau}
{\Gamma \vdash e_1 + e_2 \Uparrow \tau}$$

**Multiplication (synthesize with dimensional inference):**
$$\frac{\Gamma \vdash e_1 \Uparrow \tau_1 \quad \Gamma \vdash e_2 \Uparrow \tau_2 \quad \tau_3 = \text{dimProduct}(\tau_1, \tau_2)}
{\Gamma \vdash e_1 \times e_2 \Uparrow \tau_3}$$

### 7.3 Ambiguity Resolution

When type cannot be inferred, **compiler requires annotation**:

```pel
// Ambiguous: is this Currency<USD> or Currency<EUR>?
// var price = 100  // Error E0102: Cannot infer currency type

// Unambiguous: literal specifies currency
var price = $100  // Inferred: Currency<USD>

// Unambiguous: annotation specifies type
var price: Currency<EUR> = 100  // Type: Currency<EUR>
```

---

## 8. Subtyping and Compatibility

### 8.1 No Implicit Subtyping

PEL has **no subtype hierarchy** for primitive types:

- `Currency<USD>` is NOT a subtype of `Currency<EUR>`
- `Count<Customers>` is NOT a subtype of `Count<Orders>`

**Rationale:** Economic types are nominal; implicit conversions cause silent errors.

### 8.2 Explicit Conversions

**Currency conversion:**
```pel
var usd: Currency<USD> = $100
var eur: Currency<EUR> = usd as Currency<EUR> with exchangeRate(1.08)
```

**Time unit conversion (automatic if lossless):**
```pel
var months: Duration = 3mo
var days: Duration = months  // Automatic: 3mo → 90d
```

### 8.3 Compatibility Rules

Two types are **compatible** for operation `op` if:

1. **Identical types:** `T op T` (for `+`, `-`)
2. **Dimensional compatibility:** `dim(T1 op T2)` is valid
3. **Explicit conversion:** One type is explicitly converted

---

## 9. Type Checking Rules

### 9.1 Expression Typing

**Literals:**
$$\frac{}{\Gamma \vdash n : \text{Fraction}} \quad \text{[T-Num]}$$

$$\frac{}{\Gamma \vdash \$n : \text{Currency}\langle\text{USD}\rangle} \quad \text{[T-Currency]}$$

**Variables:**
$$\frac{x : \tau \in \Gamma}{\Gamma \vdash x : \tau} \quad \text{[T-Var]}$$

**Addition (same dimension):**
$$\frac{\Gamma \vdash e_1 : \tau \quad \Gamma \vdash e_2 : \tau}
{\Gamma \vdash e_1 + e_2 : \tau} \quad \text{[T-Add]}$$

**Multiplication (dimensional):**
$$\frac{\Gamma \vdash e_1 : \tau_1 \quad \Gamma \vdash e_2 : \tau_2 \quad \tau_3 = \tau_1 \otimes \tau_2}
{\Gamma \vdash e_1 \times e_2 : \tau_3} \quad \text{[T-Mul]}$$

where $\otimes$ is dimensional product operator.

**Division (dimensional):**
$$\frac{\Gamma \vdash e_1 : \tau_1 \quad \Gamma \vdash e_2 : \tau_2 \quad \tau_3 = \tau_1 \oslash \tau_2}
{\Gamma \vdash e_1 / e_2 : \tau_3} \quad \text{[T-Div]}$$

**Time series indexing:**
$$\frac{\Gamma \vdash s : \text{TimeSeries}\langle\tau\rangle \quad \Gamma \vdash t : \mathbb{N}}
{\Gamma \vdash s[t] : \tau} \quad \text{[T-Index-TS]}$$

**Distribution:**
$$\frac{\Gamma \vdash \mu : \tau \quad \Gamma \vdash \sigma : \tau}
{\Gamma \vdash \sim \text{Normal}(\mu, \sigma) : \text{Distribution}\langle\tau\rangle} \quad \text{[T-Dist-Normal]}$$

### 9.2 Statement Typing

**Variable declaration:**
$$\frac{\Gamma \vdash e : \tau}
{\Gamma \vdash \text{var } x = e : \Gamma, x:\tau} \quad \text{[T-VarDecl]}$$

**Parameter declaration (requires provenance):**
$$\frac{\Gamma \vdash e : \tau \quad \text{valid\_provenance}(P)}
{\Gamma \vdash \text{param } x : \tau = e\ P : \Gamma, x:\tau} \quad \text{[T-ParamDecl]}$$

**Constraint:**
$$\frac{\Gamma \vdash e : \mathbb{B}}
{\Gamma \vdash \text{constraint } c: e\ \{...\} : \Gamma} \quad \text{[T-Constraint]}$$

---

## 10. Error Detection

### 10.1 Type Errors

**E0100: Type mismatch**
```pel
var x: Currency<USD> = 0.25  // Error: expected Currency<USD>, got Fraction
```

**E0101: Undefined type**
```pel
var x: UnknownType = 10  // Error: UnknownType not defined
```

**E0102: Cannot infer type (ambiguous)**
```pel
var x = [1, 2, 3]  // Error: is this Array<Fraction>? Array<Count<...>>?
```

### 10.2 Dimensional Errors

**E0200: Incompatible dimensions**
```pel
var total = $100 + 30d  // Error: Cannot add Currency and Duration
```

**E0201: Incompatible currency types**
```pel
var total = $100 + €50  // Error: Cannot add Currency<USD> and Currency<EUR>
```

**E0202: Invalid dimensional operation**
```pel
var invalid = $100 * $50  // Error: Currency^2 not representable
```

### 10.3 Time Errors

**E0300: Non-causal time reference**
```pel
var revenue[t] = revenue[t+1] * 0.9  // Error: Cannot reference future
```

**E0301: Time index out of bounds**
```pel
var x = revenue_t[100]  // Error if T_max < 100
```

---

## 11. Type System Properties

### 11.1 Soundness

**Theorem (Type Safety):**
If $\Gamma \vdash e : \tau$ and $e \Rightarrow v$, then $v : \tau$.

**Informally:** Well-typed programs produce values of the expected type.

### 11.2 Progress

**Theorem (Progress):**
If $\Gamma \vdash e : \tau$, then either:
1. $e$ is a value, or
2. $e \to e'$ for some $e'$

**Informally:** Well-typed programs don't get stuck.

### 11.3 Preservation

**Theorem (Preservation):**
If $\Gamma \vdash e : \tau$ and $e \to e'$, then $\Gamma \vdash e' : \tau$.

**Informally:** Types are preserved during evaluation.

### 11.4 Dimensional Soundness

**Theorem:**
If $\Gamma \vdash e : \tau$ and $\text{dim}(\tau) = d$, then evaluation produces value with dimension $d$.

**Proof sketch:** By induction on typing derivation, using dimensional operator rules.

---

## Appendix A: Full Typing Rules (Formal)

[Complete formal typing rules in sequent calculus style...]

---

## Appendix B: Dimensional Operator Table

| Operation | Type 1 | Type 2 | Result Type |
|-----------|--------|--------|-------------|
| `+` | `Currency<X>` | `Currency<X>` | `Currency<X>` |
| `+` | `Duration` | `Duration` | `Duration` |
| `+` | `Rate per U` | `Rate per U` | `Rate per U` |
| `*` | `Currency<X>` | `Fraction` | `Currency<X>` |
| `*` | `Currency<X>` | `Count<E>` | `Currency<X>` |
| `*` | `Scoped<T, E>` | `Count<E>` | `T` |
| `*` | `Rate per U` | `Duration<U>` | `Fraction` |
| `/` | `Currency<X>` | `Currency<X>` | `Fraction` |
| `/` | `Currency<X>` | `Rate per U` | `Currency<X> * Duration<U>` |
| `/` | `Currency<X>` | `Duration` | `Currency<X> per Duration` |
| `/` | `Count<E>` | `Duration` | `Count<E> per Duration` |

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)  
**Canonical URL:** https://spec.pel-lang.org/v0.1/type-system
