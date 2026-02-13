# PEL Formal Semantics v0.1.0

**Document Status:** Stable  
**Last Updated:** February 2026  
**Authors:** PEL Core Team  
**Canonical URL:** https://spec.pel-lang.org/v0.1/formal-semantics

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Mathematical Foundations](#2-mathematical-foundations)
3. [Time Semantics](#3-time-semantics)
4. [Stochastic Semantics](#4-stochastic-semantics)
5. [Evaluation Semantics](#5-evaluation-semantics)
6. [Constraint Semantics](#6-constraint-semantics)
7. [Policy Semantics](#7-policy-semantics)
8. [Determinism and Reproducibility](#8-determinism-and-reproducibility)
9. [Operational Semantics (Small-Step)](#9-operational-semantics-small-step)
10. [Denotational Semantics](#10-denotational-semantics)
11. [Soundness and Completeness](#11-soundness-and-completeness)
12. [Formal Verification](#12-formal-verification)

---

## 1. Introduction

### 1.1 Purpose

This document provides the **formal mathematical semantics** for PEL, defining precisely:

- How time progresses in simulations
- How stochastic variables are sampled and correlated
- How expressions are evaluated
- How constraints are checked
- How policies modify model state
- What guarantees of determinism and repeatability exist

### 1.2 Notation

We use standard mathematical notation:

- **Sets:** $\mathbb{N}$ (naturals), $\mathbb{Z}$ (integers), $\mathbb{R}$ (reals), $\mathbb{B}$ (booleans)
- **Functions:** $f: A \to B$ (function from $A$ to $B$)
- **Tuples:** $(a, b, c)$
- **Sequences:** $\langle a_0, a_1, \ldots, a_n \rangle$
- **Relations:** $\to$ (reduction), $\Rightarrow$ (evaluation)
- **Judgments:** $\Gamma \vdash e : \tau$ (in context $\Gamma$, expression $e$ has type $\tau$)

### 1.3 Scope

This specification:
- Defines formal operational semantics (how programs execute step-by-step)
- Defines denotational semantics (what programs *mean*)
- Proves properties (determinism, type soundness)

This specification does **not**:
- Prescribe implementation strategies (runtimes are free to optimize)
- Define performance requirements (covered in benchmarks)

---

## 2. Mathematical Foundations

### 2.1 Value Domains

Let $\mathcal{V}$ be the domain of all values:

$$
\begin{align*}
\mathcal{V} ::= \ & \mathbb{R} \quad \text{(Fraction)} \\
| \ & \mathbb{R} \times \text{Currency} \quad \text{(Currency value)} \\
| \ & \mathbb{R} \times \text{Duration} \quad \text{(Duration value)} \\
| \ & \mathbb{R} \times \text{Rate} \times \text{TimeUnit} \quad \text{(Rate value)} \\
| \ & \mathbb{N} \times \text{Capacity} \quad \text{(Capacity value)} \\
| \ & \mathbb{N} \times \text{Count} \quad \text{(Count value)} \\
| \ & \mathbb{B} \quad \text{(Boolean)} \\
| \ & \text{Dist}(\mathcal{V}) \quad \text{(Distribution over values)} \\
| \ & \mathbb{N} \to \mathcal{V} \quad \text{(TimeSeries)} \\
| \ & (\mathbb{N} \times \mathbb{N}) \to \mathcal{V} \quad \text{(CohortSeries)}
\end{align*}
$$

### 2.2 State Space

A PEL **state** $\sigma$ is a mapping from identifiers to values:

$$\sigma: \text{Identifier} \to \mathcal{V}$$

The **initial state** $\sigma_0$ contains only parameter values.

### 2.3 Environment

An **environment** $\Gamma$ is a mapping from identifiers to types:

$$\Gamma: \text{Identifier} \to \text{Type}$$

### 2.4 Time Domain

**Simulation time** is discrete:

$$\mathcal{T} = \mathbb{N} = \{0, 1, 2, \ldots, T_{\text{max}}\}$$

Where $T_{\text{max}}$ is the simulation horizon specified by `simulate for <duration>`.

### 2.5 Random State

For stochastic simulations, we maintain a **random state** $\rho$:

$$\rho = (\text{seed}, \text{rng\_state})$$

where:
- `seed` $\in \mathbb{N}$ is the initial seed
- `rng_state` is the internal state of the PRNG (pseudo-random number generator)

**Determinism requirement:** Given the same seed, the sequence of random numbers **MUST** be identical.

---

## 3. Time Semantics

### 3.1 Discrete Time Steps

Simulation proceeds in **discrete time steps**:

$$t = 0, 1, 2, \ldots, T_{\text{max}}$$

Each timestep corresponds to a **time quantum** (default: 1 month, configurable).

### 3.2 Time-Indexed Variables

A time-indexed variable $x_t$ represents a **time series**:

$$x: \mathcal{T} \to \mathcal{V}$$

**Evaluation:** $x[t]$ retrieves the value at timestep $t$.

### 3.3 Causality Constraint

For any expression computing $x[t]$, all referenced variables **MUST** be from timesteps $\leq t$:

$$\frac{e \text{ references } y[s] \quad s > t}{x[t] = e \quad \text{is invalid}}$$

**Example (invalid):**
```pel
var revenue[t] = revenue[t+1] * 0.9  // Error: references future
```

**Example (valid):**
```pel
var revenue[t] = revenue[t-1] * (1 + growthRate)  // OK: references past
```

### 3.4 Cohort Time

A **cohort variable** $x_{c,a}$ is indexed by:
- $c \in \mathcal{T}$: cohort start time
- $a \in \mathbb{N}$: age (time since cohort start)

**Constraint:** At simulation time $t$, we can only observe cohorts where $c + a \leq t$.

### 3.5 Time Series Initialization

Time series with recurrence relations require **initial values**:

```pel
var revenue[0] = $10_000  // base case
var revenue[t] = revenue[t-1] * (1 + growthRate) for t > 0
```

**Uninitialized time series produce compile-time error.**

---

## 4. Stochastic Semantics

### 4.1 Distributions as Probability Measures

A distribution $D$ is a **probability measure** over values:

$$D: \mathcal{P}(\mathcal{V}) \to [0, 1]$$

satisfying:
- $D(\mathcal{V}) = 1$ (total probability)
- $D(A \cup B) = D(A) + D(B)$ if $A \cap B = \emptyset$ (countable additivity)

### 4.2 Supported Distributions

**Beta distribution** (bounded $[0, 1]$):
$$\text{Beta}(\alpha, \beta) \quad \alpha, \beta > 0$$
PDF: $f(x; \alpha, \beta) = \frac{x^{\alpha-1}(1-x)^{\beta-1}}{B(\alpha, \beta)}$

**Normal distribution** (unbounded):
$$\mathcal{N}(\mu, \sigma^2) \quad \mu \in \mathbb{R}, \sigma > 0$$
PDF: $f(x; \mu, \sigma) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$

**LogNormal distribution** (positive unbounded):
$$\text{LogNormal}(\mu, \sigma^2)$$
PDF: $f(x; \mu, \sigma) = \frac{1}{x\sigma\sqrt{2\pi}} \exp\left(-\frac{(\ln x - \mu)^2}{2\sigma^2}\right)$ for $x > 0$

**Uniform distribution**:
$$\mathcal{U}(a, b) \quad a < b$$

**Mixture distribution**:
$$\text{Mixture}([D_1, \ldots, D_n], [w_1, \ldots, w_n])$$
where $\sum w_i = 1$ and $w_i \geq 0$.

### 4.3 Sampling Semantics

**Deterministic mode:** Sample at **mean** (or mode for asymmetric distributions):

$$\text{sample}_{\text{det}}(\mathcal{N}(\mu, \sigma^2)) = \mu$$

**Monte Carlo mode:** Sample from distribution using PRNG:

$$\text{sample}_{\text{MC}}(D, \rho) \to (v, \rho')$$

where:
- $D$ is the distribution
- $\rho$ is current random state
- $v \sim D$ is the sampled value
- $\rho'$ is updated random state

**Determinism guarantee:**
$$\text{seed}(\rho) = \text{seed}(\rho') \implies \text{sample sequence identical}$$

### 4.4 Correlation

**Correlation matrix** $\mathbf{C}$ for $n$ variables:

$$\mathbf{C} = \begin{pmatrix}
1 & \rho_{12} & \cdots & \rho_{1n} \\
\rho_{21} & 1 & \cdots & \rho_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
\rho_{n1} & \rho_{n2} & \cdots & 1
\end{pmatrix}$$

where $\rho_{ij} \in [-1, 1]$ is the correlation between variables $i$ and $j$.

**Constraints:**
- $\rho_{ii} = 1$ (self-correlation)
- $\rho_{ij} = \rho_{ji}$ (symmetry)
- $\mathbf{C}$ **MUST** be positive semi-definite (all eigenvalues $\geq 0$)

**Sampling correlated variables:**

1. Sample independent standard normals: $\mathbf{z} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$
2. Compute Cholesky decomposition: $\mathbf{C} = \mathbf{L}\mathbf{L}^T$
3. Transform: $\mathbf{x} = \mathbf{L}\mathbf{z}$
4. Apply inverse CDF: $v_i = F_i^{-1}(\Phi(x_i))$

where $F_i$ is the CDF of variable $i$'s marginal distribution, and $\Phi$ is the standard normal CDF.

**Guarantee:** Empirical correlation of samples converges to $\mathbf{C}$ as $N \to \infty$.

---

## 5. Evaluation Semantics

### 5.1 Expression Evaluation

**Judgment:** $\sigma, \rho \vdash e \Rightarrow v, \rho'$

Reads: "In state $\sigma$ and random state $\rho$, expression $e$ evaluates to value $v$ with updated random state $\rho'$."

### 5.2 Evaluation Rules

**Literals:**
$$\frac{}{\sigma, \rho \vdash n \Rightarrow n, \rho} \quad \text{[E-Lit]}$$

**Variables:**
$$\frac{\sigma(x) = v}{\sigma, \rho \vdash x \Rightarrow v, \rho} \quad \text{[E-Var]}$$

**Addition (same dimension):**
$$\frac{\sigma, \rho \vdash e_1 \Rightarrow v_1, \rho' \quad \sigma, \rho' \vdash e_2 \Rightarrow v_2, \rho'' \quad \text{dim}(v_1) = \text{dim}(v_2)}
{\sigma, \rho \vdash e_1 + e_2 \Rightarrow v_1 + v_2, \rho''} \quad \text{[E-Add]}$$

**Multiplication (dimensional product):**
$$\frac{\sigma, \rho \vdash e_1 \Rightarrow (r_1, d_1), \rho' \quad \sigma, \rho' \vdash e_2 \Rightarrow (r_2, d_2), \rho''}
{\sigma, \rho \vdash e_1 \times e_2 \Rightarrow (r_1 \cdot r_2, d_1 \cdot d_2), \rho''} \quad \text{[E-Mul]}$$

where $(r, d)$ represents a value $r$ with dimension $d$.

**Distribution sampling (Monte Carlo):**
$$\frac{\text{sample}_{\text{MC}}(D, \rho) = (v, \rho')}
{\sigma, \rho \vdash \sim D \Rightarrow v, \rho'} \quad \text{[E-Sample-MC]}$$

**Distribution sampling (Deterministic):**
$$\frac{\text{mean}(D) = v}
{\sigma, \rho \vdash \sim D \Rightarrow v, \rho} \quad \text{[E-Sample-Det]}$$

**Time series indexing:**
$$\frac{\sigma(x) = f: \mathcal{T} \to \mathcal{V} \quad \sigma, \rho \vdash e \Rightarrow t, \rho' \quad t \in \mathcal{T}}
{\sigma, \rho \vdash x[e] \Rightarrow f(t), \rho'} \quad \text{[E-Index-TS]}$$

**Conditional:**
$$\frac{\sigma, \rho \vdash e_c \Rightarrow \text{true}, \rho' \quad \sigma, \rho' \vdash e_1 \Rightarrow v, \rho''}
{\sigma, \rho \vdash \text{if } e_c \text{ then } e_1 \text{ else } e_2 \Rightarrow v, \rho''} \quad \text{[E-If-True]}$$

$$\frac{\sigma, \rho \vdash e_c \Rightarrow \text{false}, \rho' \quad \sigma, \rho' \vdash e_2 \Rightarrow v, \rho''}
{\sigma, \rho \vdash \text{if } e_c \text{ then } e_1 \text{ else } e_2 \Rightarrow v, \rho''} \quad \text{[E-If-False]}$$

### 5.3 Statement Execution

**Variable declaration:**
$$\frac{\sigma, \rho \vdash e \Rightarrow v, \rho'}
{\sigma, \rho \vdash \text{var } x = e \leadsto \sigma[x \mapsto v], \rho'} \quad \text{[S-VarDecl]}$$

where $\sigma[x \mapsto v]$ is state $\sigma$ updated with $x := v$.

### 5.4 Simulation Loop

**Top-level simulation:**

$$
\begin{align*}
&\text{Simulate}(\text{model } M, T_{\text{max}}, \text{seed}) = \\
&\quad \text{let } \sigma_0 = \text{InitParams}(M) \\
&\quad \text{let } \rho_0 = \text{InitRNG}(\text{seed}) \\
&\quad \text{let } (\sigma_{\text{final}}, \rho_{\text{final}}) = \text{RunLoop}(\sigma_0, \rho_0, 0, T_{\text{max}}) \\
&\quad \text{return } \sigma_{\text{final}}
\end{align*}
$$

**Simulation loop (recursive definition):**

$$
\begin{align*}
&\text{RunLoop}(\sigma, \rho, t, T_{\text{max}}) = \\
&\quad \text{if } t > T_{\text{max}} \text{ then } (\sigma, \rho) \\
&\quad \text{else} \\
&\quad\quad \text{let } (\sigma', \rho') = \text{EvaluateTimeStep}(\sigma, \rho, t) \\
&\quad\quad \text{let } (\sigma'', \rho'') = \text{ApplyPolicies}(\sigma', \rho', t) \\
&\quad\quad \text{CheckConstraints}(\sigma'', t) \\
&\quad\quad \text{RunLoop}(\sigma'', \rho'', t+1, T_{\text{max}})
\end{align*}
$$

---

## 6. Constraint Semantics

### 6.1 Constraint Evaluation

A constraint $C$ has form:

$$C: e_{\text{cond}} \text{ with severity } s \text{ for scope } S$$

where:
- $e_{\text{cond}}$ is a boolean expression
- $s \in \{\text{fatal}, \text{warning}\}$
- $S$ specifies when/where constraint applies

### 6.2 Constraint Checking

At each timestep $t$, for each constraint $C_i$:

$$\text{CheckConstraint}(C_i, \sigma, t) =
\begin{cases}
\text{Pass} & \text{if } \sigma \vdash e_{\text{cond}} \Rightarrow \text{true} \\
\text{Fail}(s) & \text{if } \sigma \vdash e_{\text{cond}} \Rightarrow \text{false}
\end{cases}
$$

**Fatal constraint violation:** Simulation terminates immediately.
**Warning constraint violation:** Logged, simulation continues.

### 6.3 Slack Variables

For soft constraints with slack:

$$\text{slack}(C, \sigma, t) = \sigma \vdash e_{\text{target}} - e_{\text{actual}}$$

**Example:**
```pel
constraint target_margin: margin >= $50 { severity: warning, slack: true }
```

If `margin = $30`, then `slack = $50 - $30 = $20` (positive = violation).

### 6.4 First Binding Constraint

The **first binding constraint** at timestep $t$ is the constraint that becomes violated first:

$$t_{\text{first}} = \min\{t : \exists C_i, \text{CheckConstraint}(C_i, \sigma, t) = \text{Fail}(\text{fatal})\}$$

---

## 7. Policy Semantics

### 7.1 Policy Structure

A policy $P$ has form:

$$P: \text{when } e_{\text{trigger}} \text{ then } \text{action} \quad a$$

### 7.2 Policy Triggering

At each timestep $t$:

$$\text{Triggered}(P, \sigma, t) = \sigma \vdash e_{\text{trigger}} \Rightarrow \text{true}$$

### 7.3 Policy Execution

If $\text{Triggered}(P, \sigma, t)$, execute action $a$:

**Assignment:**
$$\frac{\sigma, \rho \vdash e \Rightarrow v, \rho'}
{\text{Execute}(x = e, \sigma, \rho) = (\sigma[x \mapsto v], \rho')} \quad \text{[P-Assign]}$$

**Multiplicative update:**
$$\frac{\sigma(x) = v_{\text{old}} \quad \sigma, \rho \vdash e \Rightarrow v_{\text{factor}}, \rho'}
{\text{Execute}(x \mathrel{{*}{=}} e, \sigma, \rho) = (\sigma[x \mapsto v_{\text{old}} \times v_{\text{factor}}], \rho')} \quad \text{[P-MulAssign]}$$

### 7.4 Policy Order

When multiple policies trigger at time $t$, they execute in **declaration order**.

**Non-commutativity warning:** If policies modify the same variable, order matters. Compiler **SHOULD** warn.

---

## 8. Determinism and Reproducibility

### 8.1 Deterministic Mode

**Theorem (Deterministic Repeatability):**

Given:
- Model $M$
- Seed $s$
- Simulation horizon $T$

Then:
$$\text{Simulate}(M, T, s) = \text{Simulate}(M, T, s)$$

bit-for-bit identically, across all runs and all conformant implementations.

**Proof sketch:**
- All operations are deterministic given fixed random state
- Random state evolution is deterministic given seed
- Evaluation order is specified (no non-determinism)

### 8.2 Monte Carlo Mode

**Theorem (Statistical Reproducibility):**

Given:
- Model $M$
- Seed $s$
- Number of runs $N$

For each run $i = 1, \ldots, N$:
$$\text{Simulate}(M, T, s_i) \quad \text{where } s_i = \text{hash}(s, i)$$

The sequence of runs is **deterministic** and **reproducible**.

**Each run is independent** (different seed $s_i$), but the **ensemble is deterministic** (given base seed $s$).

### 8.3 Model Hash

The **model hash** is computed as:

$$H(M) = \text{SHA-256}(\text{CanonicalIR}(M))$$

where $\text{CanonicalIR}(M)$ is the normalized PEL-IR representation (whitespace-invariant, key-sorted).

**Properties:**
- $M_1 = M_2 \implies H(M_1) = H(M_2)$ (semantically equivalent models have same hash)
- $H(M_1) \neq H(M_2) \implies M_1 \neq M_2$ (different hashes = different models, cryptographically)

### 8.4 Run Artifact

A **run artifact** contains:

$$\text{Artifact} = (H(M), H(A), s, V_{\text{runtime}}, \sigma_{\text{final}})$$

where:
- $H(M)$ = model hash
- $H(A)$ = assumption hash (hash of all provenance metadata)
- $s$ = seed
- $V_{\text{runtime}}$ = runtime version
- $\sigma_{\text{final}}$ = final state (all outputs)

**Reproducibility:** Given artifact, any conformant runtime **MUST** reproduce $\sigma_{\text{final}}$.

---

## 9. Operational Semantics (Small-Step)

### 9.1 Configuration

A **configuration** is a triple:

$$\langle e, \sigma, \rho \rangle$$

where:
- $e$ is expression (or statement) to evaluate
- $\sigma$ is current state
- $\rho$ is random state

### 9.2 Reduction Relation

Reduction: $\langle e, \sigma, \rho \rangle \to \langle e', \sigma', \rho' \rangle$

**Arithmetic reduction:**

$$\langle n_1 + n_2, \sigma, \rho \rangle \to \langle n_3, \sigma, \rho \rangle$$

where $n_3 = n_1 + n_2$ (numeric addition).

**Variable lookup:**

$$\langle x, \sigma, \rho \rangle \to \langle v, \sigma, \rho \rangle$$

where $\sigma(x) = v$.

**Context rule:**

$$\frac{\langle e_1, \sigma, \rho \rangle \to \langle e_1', \sigma', \rho' \rangle}
{\langle e_1 + e_2, \sigma, \rho \rangle \to \langle e_1' + e_2, \sigma', \rho' \rangle}$$

### 9.3 Progress and Preservation

**Theorem (Progress):**
If $\Gamma \vdash e : \tau$, then either:
1. $e$ is a value, or
2. $\exists e', \sigma', \rho'$ such that $\langle e, \sigma, \rho \rangle \to \langle e', \sigma', \rho' \rangle$

**Theorem (Preservation):**
If $\Gamma \vdash e : \tau$ and $\langle e, \sigma, \rho \rangle \to \langle e', \sigma', \rho' \rangle$, then $\Gamma \vdash e' : \tau$.

**Corollary (Type Safety):**
Well-typed programs do not get stuck (assuming no fatal constraint violations).

---

## 10. Denotational Semantics

### 10.1 Semantic Domains

$$
\begin{align*}
\llbracket \text{Fraction} \rrbracket &= \mathbb{R} \\
\llbracket \text{Currency} \langle X \rangle \rrbracket &= \mathbb{R} \times \{X\} \\
\llbracket \text{Boolean} \rrbracket &= \mathbb{B} \\
\llbracket \text{Distribution}\langle\tau\rangle \rrbracket &= \text{Prob}(\llbracket \tau \rrbracket)
\end{align*}
$$

where $\text{Prob}(A)$ is the space of probability measures over $A$.

### 10.2 Expression Meaning

$\llbracket e \rrbracket: \Sigma \to \mathcal{P}(\llbracket \tau \rrbracket)$

where $\Sigma$ is the state space and $\mathcal{P}$ is powerset (to accommodate non-determinism in general, though PEL is deterministic given seed).

**Literal:**
$$\llbracket n \rrbracket(\sigma) = n$$

**Variable:**
$$\llbracket x \rrbracket(\sigma) = \sigma(x)$$

**Addition:**
$$\llbracket e_1 + e_2 \rrbracket(\sigma) = \llbracket e_1 \rrbracket(\sigma) + \llbracket e_2 \rrbracket(\sigma)$$

**Distribution:**
$$\llbracket \sim D \rrbracket(\sigma) = D$$

(The meaning is the distribution itself; sampling happens at runtime, not denotational level.)

---

## 11. Soundness and Completeness

### 11.1 Type Soundness

**Theorem (Soundness):**
If $\Gamma \vdash e : \tau$ and $\langle e, \sigma, \rho \rangle \Rightarrow v, \rho'$, then $v \in \llbracket \tau \rrbracket$.

**Proof:** By structural induction on typing derivation, using Progress and Preservation lemmas.

### 11.2 Dimensional Correctness

**Theorem (Dimensional Soundness):**
If $e$ type-checks with dimension $d$, then evaluation produces value with dimension $d$.

**Informal proof:**
- Type system tracks dimensions
- Operations preserve dimensional correctness by construction (see type rules)
- Contradiction if evaluation produces wrong dimension

### 11.3 Constraint Completeness

**Theorem (Constraint Coverage):**
If model has constraints $\{C_1, \ldots, C_n\}$, runtime **MUST** check all constraints at every timestep (for scope-appropriate constraints).

**Proof:** By construction of simulation loop (see Section 5.4).

---

## 12. Formal Verification

### 12.1 Supported Verification Queries

**Reachability:**
Can state satisfying $\phi$ be reached?

$$\text{Reach}(\phi) = \exists t, \sigma_t \text{ such that } \sigma_t \models \phi$$

**Example:** "Can cash balance reach zero?"

**Invariant:**
Does property $\psi$ hold at all timesteps?

$$\text{Invariant}(\psi) = \forall t, \sigma_t \models \psi$$

**Example:** "Cash balance always non-negative."

### 12.2 Verification via Model Checking

PEL runtimes **MAY** support model checking queries via:

1. **Bounded model checking** (check up to $T_{\text{max}}$)
2. **Symbolic execution** (explore all paths with symbolic constraints)
3. **Abstract interpretation** (over-approximate reachable states)

**Not required for conformance**, but encouraged for advanced analysis.

---

## Appendix A: Proof of Determinism (Detailed)

**Theorem:** Same seed implies identical simulation.

**Proof:**

Let $M$ be a model, $s$ a seed, $T$ a horizon.

Define:
- $\sigma_0 = \text{InitParams}(M)$ (deterministic, no randomness)
- $\rho_0 = \text{InitRNG}(s)$ (deterministic initialization)

Claim: $\text{RunLoop}(\sigma_0, \rho_0, 0, T)$ is deterministic.

**Induction on timestep $t$:**

*Base case ($t = 0$):*
- $\sigma_0$ fixed (parameters)
- $\rho_0$ fixed (seed)

*Inductive case ($t \to t+1$):*
- Assume $\sigma_t, \rho_t$ deterministic
- $\text{EvaluateTimeStep}(\sigma_t, \rho_t, t)$ evaluates all expressions deterministically:
  - Arithmetic: deterministic
  - Distribution sampling: deterministic given $\rho_t$ (PRNG is deterministic)
  - Produces $\sigma_{t+1}, \rho_{t+1}$ deterministically
- $\text{ApplyPolicies}(\sigma_{t+1}, \rho_{t+1}, t)$: deterministic (ordered, no randomness in policy logic)
- Therefore $\sigma_{t+1}, \rho_{t+1}$ deterministic.

By induction, $\sigma_T, \rho_T$ deterministic. ∎

---

## Appendix B: Formal Definition of Cholesky Sampling

**Input:**
- Correlation matrix $\mathbf{C} \in \mathbb{R}^{n \times n}$ (symmetric, positive semi-definite)
- Marginal distributions $D_1, \ldots, D_n$

**Output:**
- Correlated samples $(v_1, \ldots, v_n)$ with empirical correlation $\approx \mathbf{C}$

**Algorithm:**

1. Compute Cholesky decomposition: $\mathbf{C} = \mathbf{L}\mathbf{L}^T$ where $\mathbf{L}$ lower triangular
2. Sample independent standard normals: $z_i \sim \mathcal{N}(0, 1)$ for $i = 1, \ldots, n$
3. Compute correlated normals: $\mathbf{x} = \mathbf{L}\mathbf{z}$
4. Apply inverse CDF of marginals:
   $$v_i = F_i^{-1}(\Phi(x_i))$$
   where $\Phi$ is standard normal CDF, $F_i$ is CDF of $D_i$.

**Correctness:**
- $\mathbf{x} \sim \mathcal{N}(\mathbf{0}, \mathbf{C})$ (multivariate normal with covariance $\mathbf{C}$)
- Inverse CDF transform preserves **rank correlation** (Spearman's $\rho$)
- Pearson correlation approximate (exact for Gaussian marginals)

---

## Appendix C: References

- **Pierce, B. C.** *Types and Programming Languages*. MIT Press, 2002.
- **Winskel, G.** *The Formal Semantics of Programming Languages*. MIT Press, 1993.
- **Gentle, J. E.** *Random Number Generation and Monte Carlo Methods*. Springer, 2003.
- **Modelica Association.** *Modelica Language Specification 3.5*. 2021.

---

**Document Maintainers:** PEL Core Team  
**Feedback:** [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)  
**Canonical URL:** https://spec.pel-lang.org/v0.1/formal-semantics
