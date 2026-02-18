# PEL — Programmable Economic Language

[![CI Pipeline](https://github.com/Coding-Krakken/pel-lang/actions/workflows/ci.yml/badge.svg)](https://github.com/Coding-Krakken/pel-lang/actions/workflows/ci.yml)

**Version:** 0.1.0  
**Status:** Production-ready specification and reference implementation  
**License:** AGPL-3.0-or-later OR Commercial (Dual Licensed)

---

## What is PEL?

**PEL (Programmable Economic Language)** is the first complete, formally specified, programmable language purpose-built for economic and business modeling.

PEL is **not**:
- A spreadsheet wrapper
- A JSON configuration schema
- A business rules engine
- A diagramming notation
- A simulation platform UI

PEL **is**:
> The first language that makes economic models executable, auditable, reproducible, type-safe, and uncertainty-native by design.

---

## The PEL Promise

### 1. **Economically Typed**
Every variable has units (USD, USD/month, customers/day), scope (per-customer, per-location), and time semantics (scalar vs time-series vs cohort-indexed). Dimensional errors are **compile-time failures**.

### 2. **Uncertainty-Native**
Distributions, correlations, and fat-tail shocks are first-class syntax, not afterthoughts. Every uncertain parameter must be explicit.

### 3. **Constraint-First**
Cash limits, capacity constraints, hiring ramps, compliance rules—all enforced across finance and operations simultaneously.

### 4. **Policy-Executable**
Strategic decisions become executable policies that adapt the model over time, simulated stochastically with auditability.

### 5. **Multi-Paradigm Runtime**
Single unified model supports agent-based modeling (ABM), discrete-event simulation (DES), system dynamics, and cash-precision accounting.

### 6. **Audit & Provenance Native**
Every assumption requires source, method, confidence, and freshness metadata. Models generate assumption registers automatically.

### 7. **Calibratable (Digital Twin)**
Models ingest real data, fit distributions, detect drift, and recommend what to measure next based on sensitivity analysis.

### 8. **Portable & Reproducible**
Standard IR (Intermediate Representation) with conformance tests guarantees identical results across compliant runtimes. Model hash + seed = deterministic output.

### 9. **Language-Grade Tooling**
LSP server, formatter, linter, test runner, package manager, dependency visualizer—treat business models like production code.

### 10. **Benchmarked & Proven**
Public benchmark suites measure expressiveness, correctness, auditability, tail-risk accuracy, and developer experience.

---

## Why PEL Exists

### The Problem

Today's business modeling stack is fragmented and broken:

- **BPMN**: Process diagrams, not executable economics
- **DMN**: Decision rules, not full simulation
- **SBVR**: Vocabulary/logic, not runtime semantics
- **AMPL/GAMS**: Optimization, not time-evolving business dynamics
- **AnyLogic/SimPy**: Simulation platforms without standardized economic type systems
- **Modelica**: Physical systems, not business/economic semantics
- **Spreadsheets**: Everything is implicit, nothing is enforceable

**Result:** Silent errors, fake certainty, non-reproducible models, political artifacts instead of engineering truth.

### The Solution

PEL provides what no existing standard or tool delivers:

1. **No silent errors**: Units/time/scope checked at compile-time
2. **No fake certainty**: Uncertainty must be explicit
3. **No hidden assumptions**: Provenance metadata required
4. **No gaming**: Anti-gaming enforcement (must show fragility and caveats)
5. **No vendor lock-in**: Open IR with conformance suite
6. **No "vibes"**: Causal mechanisms enforced (compiler rejects prose claims)

---

## Quick Example

```pel
// PEL enforces economic types, uncertainty, and provenance

model SaaSUnitEconomics {
  // Types include units, scope, and time semantics
  param monthlyPrice: Currency<USD> per Customer = $99 {
    source: "pricing_page_2026-01",
    confidence: 0.95,
    method: "observed"
  }
  
  param churnRate: Rate per Month ~ Beta(α=2, β=18) {
    source: "cohort_analysis_2025-Q4",
    confidence: 0.70,
    method: "fitted",
    freshness: "3_months"
  }
  
  param cac: Currency<USD> per Customer ~ LogNormal(μ=500, σ=150) {
    source: "marketing_dashboard",
    confidence: 0.60,
    method: "trailing_90d_average",
    correlated_with: [conversionRate, -0.4]  // CAC and conversion often anti-correlate
  }
  
  // Constraints are first-class
  constraint cashflow_survival: 
    cashBalance[t] >= $50_000 for all t in [0..36] {
      severity: fatal,
      message: "Company insolvent"
    }
  
  // Policies are executable decision logic
  policy pricing_elasticity_response {
    when: monthlyPrice changes
    then: demandVolume *= (1 - priceElasticity * percentChange(monthlyPrice))
  }
  
  // Equations use dimensional analysis
  var ltv: Currency<USD> per Customer = 
    monthlyPrice / churnRate  // Compiler verifies: USD * Month = USD ✓
  
  var unitMargin: Currency<USD> per Customer = ltv - cac
  
  // Illegal example (caught at compile time):
  // var broken = cac + churnRate  // ERROR: Cannot add Currency to Rate
}
```

Compiling this model:
1. Type-checks all units and dimensions
2. Validates time-index legality
3. Generates an **Assumption Register** with all provenance
4. Produces a **model hash** for reproducibility
5. Outputs **PEL-IR** (portable intermediate representation)

Running this model:
- Deterministic mode: same seed → same results
- Monte Carlo mode: 10,000 runs with correlation preservation
- Sensitivity analysis: tornado charts and Sobol indices
- Constraint tracing: "first binding constraint at month 14: cashflow_survival"

---

## Repository Structure

```
/pel
  /spec                     # Complete formal specifications
    pel_language_spec.md    # Syntax, grammar, semantics
    pel_formal_semantics.md # Mathematical foundations
    pel_type_system.md      # Economic type theory
    pel_uncertainty_spec.md # Distributions, correlation, shocks
    pel_constraint_spec.md  # Constraint semantics
    pel_policy_spec.md      # Policy language and execution
    pel_calibration_spec.md # Digital twin / data ingestion
    pel_governance_spec.md  # Provenance, audit, reproducibility
    pel_security_spec.md    # Sandboxing, package signing
    pel_benchmark_suite.md  # Evaluation methodology
    pel_conformance_spec.md # Runtime certification requirements

  /ir                       # Intermediate Representation
    pel_ir_schema.json      # Canonical IR format
    ir_validation_rules.md  # Validation and versioning

  /compiler                 # PEL compiler implementation
    parser/                 # Lexer + parser
    ast/                    # Abstract syntax tree
    typechecker/            # Unit/scope/time checker
    constraint_checker/     # Constraint validation
    mechanism_validator/    # Anti-"vibes" enforcement
    provenance_enforcer/    # Assumption completeness
    compiler_tests/         # Negative + positive tests

  /runtime                  # Reference runtime engines
    deterministic_engine/   # Seed-based repeatability
    monte_carlo_engine/     # N-run stochastic simulation
    sensitivity_engine/     # Tornado, Sobol, etc.
    constraint_tracer/      # First binding constraint detection
    correlation_engine/     # Correlation preservation
    runtime_tests/          # Determinism + property tests

  /stdlib                   # Standard library (PEL-STD)
    demand_module/          # Acquisition, leads, funnel
    funnel_module/          # Conversion stages
    pricing_module/         # Elasticity, response curves
    unit_econ_module/       # LTV, CAC, margins
    cashflow_module/        # AR, AP, payroll timing
    retention_module/       # Cohort, churn, retention curves
    capacity_module/        # Queueing, utilization
    hiring_module/          # Ramp curves, attrition
    shock_library/          # Recession, platform shocks

  /tooling                  # Language tooling
    lsp_server/             # Language Server Protocol
    formatter/              # `pel fmt`
    linter/                 # `pel lint`
    cli/                    # `pel compile`, `pel run`, `pel test`
    visualizer/             # Dependency graphs, risk maps

  /tests                    # Conformance + benchmark suites
    pel_100_expressiveness/ # 100 business archetype models
    pel_safe_correctness/   # Silent error prevention tests
    pel_trust_auditability/ # Provenance completeness tests
    pel_risk_tail/          # Tail risk accuracy tests
    golden_models/          # Reference results

  README.md                 # This file
  ROADMAP.md                # Development phases
  CONTRIBUTING.md           # Contribution guidelines
  LICENSE                   # AGPL-3.0
  COMMERCIAL_LICENSE        # Commercial license terms
  COMMERCIAL-LICENSE.md     # Commercial license guide
  CLA.md                    # Contributor License Agreement
  NOTICE                    # Copyright and attribution
```

---

## Getting Started

### Installation

```bash
# Install PEL compiler and runtime
pip install pel-lang

# Or build from source
git clone https://github.com/pel-lang/pel.git
cd pel
make install
```

### Your First Model

Create `hello_economics.pel`:

```pel
model HelloEconomics {
  param revenue: Currency<USD> per Month = $10_000 {
    source: "example",
    confidence: 1.0,
    method: "hardcoded"
  }
  
  param growthRate: Rate per Month = 0.05 {
    source: "assumption",
    confidence: 0.5,
    method: "guess"
  }
  
  var revenue_t: TimeSeries<Currency<USD>> = 
    revenue * (1 + growthRate) ^ t
  
  simulate for 12 months
}
```

Compile and run:

```bash
pel compile hello_economics.pel -o hello.pel-ir
pel run hello.pel-ir --deterministic --seed 42
pel run hello.pel-ir --monte-carlo --runs 1000
pel report hello.pel-ir --assumptions
pel report hello.pel-ir --sensitivity
```

Output includes:
- Assumption register (all parameters with provenance)
- Time series results (with confidence intervals if Monte Carlo)
- Sensitivity ranking (which parameters matter most)
- Model hash and reproducibility artifacts

### Code Quality

```bash
pel format hello_economics.pel --check
pel lint hello_economics.pel
```

See the style guide at [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md).

---

## Design Philosophy

### 1. **Explicit Over Implicit**
If it's implicit, it's wrong. Uncertainty, units, assumptions, constraints—everything must be declared.

### 2. **Compile-Time Rigor**
Catch semantic errors before runtime. Economic nonsense (adding hours to dollars) fails compilation.

### 3. **Provenance is Mandatory**
Every parameter must have source, method, confidence, freshness. No assumption register = no compilation.

### 4. **Anti-Gaming by Design**
Models must expose fragility, sensitivity, and caveats. Cannot hide dependencies or overstate certainty.

### 5. **Reproducibility is Non-Negotiable**
Model hash + assumption hash + seed → deterministic results. Third parties can reproduce any run from artifacts.

### 6. **Standard Library Beats Reinvention**
Common patterns (funnels, cohorts, retention) are stdlib modules, not copy-paste.

### 7. **Portable Semantics**
Same model runs identically on any conformant runtime. IR + conformance suite enforce this.

### 8. **Tailored for Economics, Not Adapted**
PEL is not physics simulation + business logic bolted on. Economics and business are first-class domains.

---

## Success Metrics

PEL measures itself against objective benchmarks:

### Correctness Metrics
- **Silent error prevention rate**: % of unit/time/scope bugs caught at compile-time (target: >99%)
- **Determinism rate**: % of reruns producing identical results given same hash+seed (target: 100%)

### Usability Metrics
- **Time-to-first-runnable-model**: Minutes to implement canonical archetypes (target: <60 min)
- **LOC per archetype**: Lines of code vs equivalent spreadsheet/code (target: 10× smaller)

### Trust Metrics
- **Assumption completeness**: % of parameters with full provenance (target: >95% for published models)
- **Reproducibility score**: % of third-party artifact reruns succeeding (target: >99.9%)

### Risk Metrics
- **Tail coverage**: Accuracy of probability-of-ruin under synthetic ground truth (target: calibrated)
- **Sensitivity transparency**: Fraction of critical parameters correctly identified (target: >90%)

### Adoption Metrics
- **Conformant runtimes**: Number of independent implementations passing conformance (target: ≥2)
- **Model exchange**: Number of public PEL models (target: >100 in first year)

---

## Comparison to Existing Standards

| Feature | Spreadsheets | BPMN/DMN | AMPL/GAMS | AnyLogic | Modelica | **PEL** |
|---------|--------------|----------|-----------|----------|----------|---------|
| Economic type system | ❌ | ❌ | Partial | ❌ | ❌ (physical) | ✅ |
| Compile-time unit checking | ❌ | ❌ | ✅ | ❌ | ✅ (physical) | ✅ |
| Uncertainty-native | ❌ | ❌ | Via extensions | ✅ | Via extensions | ✅ |
| Correlation modeling | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Provenance required | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Constraint-first | ❌ | Partial | ✅ | Partial | ✅ | ✅ |
| Policy executable | ❌ | ✅ (DMN) | ❌ | ✅ | ❌ | ✅ |
| Multi-paradigm (ABM/DES/SD) | ❌ | ❌ | ❌ | ✅ | Partial | ✅ |
| Deterministic by design | ❌ | N/A | Varies | Varies | ✅ | ✅ |
| Portable IR | ❌ | ✅ (XML) | Varies | ❌ | ✅ (FMI) | ✅ |
| Conformance suite | ❌ | Partial | ❌ | ❌ | ✅ (FMI) | ✅ |
| Anti-gaming enforcement | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Calibration from real data | Manual | ❌ | ❌ | ✅ | ✅ | ✅ |
| Language-grade tooling | ❌ | Partial | Partial | ✅ (IDE) | ✅ | ✅ |
| Public benchmark suite | ❌ | ❌ | ❌ | ❌ | Partial | ✅ |

**Conclusion:** PEL is the only standard that combines economic type safety, uncertainty-native syntax, mandatory provenance, multi-paradigm runtime, and conformance-tested portability.

---

## Status & Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development phases.

**Current Status (v0.1.0):**
- ✅ Complete formal specifications
- ✅ PEL-IR schema and validation rules
- ✅ Reference compiler implementation
- ✅ Deterministic and Monte Carlo runtimes
- ✅ Core standard library modules
- ✅ LSP server and basic tooling
- ✅ Conformance test harness
- ✅ PEL-100 expressiveness benchmark suite
- 🚧 Calibration loop (planned Q2 2026)
- 🚧 Advanced sensitivity (Sobol) (planned Q3 2026)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Specification change process (PEL Enhancement Proposals - PEPs)
- Test requirements
- Conformance requirements for runtime implementers

---

## Community & Support

- **Website:** [pel-lang.org](https://pel-lang.org)
- **Documentation:** [docs.pel-lang.org](https://docs.pel-lang.org)
- **GitHub:** [github.com/pel-lang/pel](https://github.com/pel-lang/pel)
- **Discord:** [discord.gg/pel-lang](https://discord.gg/pel-lang)
- **Mailing List:** [groups.google.com/g/pel-lang](https://groups.google.com/g/pel-lang)

---

## Citation

If you use PEL in academic work, please cite:

```bibtex
@software{pel2026,
  title = {PEL: Programmable Economic Language},
  author = {PEL Project Contributors},
  year = {2026},
  version = {0.1.0},
  url = {https://github.com/pel-lang/pel}
}
```

---

## License

PEL is **dual-licensed**:

### Open Source (AGPL-3.0-or-later)

For open source use, PEL is licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**.

This means:
- ✅ Free to use for open source projects
- ✅ Free for research and academic use
- ✅ Free for internal company use
- ⚠️ **Must share source code** if you offer PEL as a network service
- ⚠️ **Must open-source derivative works** under AGPL-3.0

See the [LICENSE](LICENSE) file for full AGPL-3.0 terms.

### Commercial License

For proprietary and commercial use without source code disclosure requirements, a **Commercial License** is available.

**You need a Commercial License if you:**
- Build proprietary software using PEL
- Offer PEL-based SaaS or API services
- Embed PEL in a commercial product
- Want to keep your modifications private

**Benefits:**
- ✅ No source code disclosure obligations
- ✅ Use in proprietary/closed-source applications
- ✅ Offer as SaaS without open-sourcing your platform
- ✅ Keep modifications private
- ✅ Optional professional support and maintenance

**Get a Commercial License:**
- 📧 Contact: davidtraversmailbox@gmail.com
- 📄 Details: See [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)
- 💼 Custom pricing based on your use case

### Why Dual Licensing?

Dual licensing allows us to:
1. Keep PEL freely available for the open source community
2. Allow businesses to use PEL in proprietary products
3. Sustain long-term development and maintenance
4. Provide professional support for commercial users

This model is used successfully by many projects including MariaDB, GitLab, and MongoDB.

### Contributing

Contributions are welcome! By contributing to PEL, you agree to the [Contributor License Agreement (CLA)](CLA.md), which allows us to maintain dual licensing. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Copyright 2026 PEL Project Contributors**

---

## Acknowledgments

PEL stands on the shoulders of giants:

- **BPMN/DMN**: Process and decision modeling standards
- **Modelica/FMI**: Equation-based modeling and model exchange
- **GAMS/AMPL**: Optimization modeling languages
- **Units libraries**: Pint (Python), uom (Rust), F# Units of Measure
- **Simulation frameworks**: AnyLogic, SimPy, Mesa
- **Probabilistic programming**: Stan, PyMC, Turing.jl

PEL synthesizes lessons from all of these while creating something new: a purpose-built economic modeling language with formal semantics, portable execution, and audit-grade rigor.

---

**PEL: Making economic models executable, auditable, and real.**
