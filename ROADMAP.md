# PEL Development Roadmap

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Active Development

---

## Vision

By 2027, PEL will be the de facto standard for executable, auditable economic modeling—trusted by CFOs, adopted by analysts, and proven through public benchmarks to deliver:

- 10× fewer silent errors than spreadsheets
- 99.9%+ reproducibility rate
- Sub-60-minute time-to-first-model for common archetypes
- Multiple independent conformant runtime implementations

---

## Development Philosophy

PEL follows a **specification-first, conformance-driven** development model:

1. **Specification precedes implementation** — No code without formal semantics
2. **Conformance over features** — Portability is non-negotiable
3. **Metrics over claims** — Public benchmarks prove value
4. **Community over vendor** — Open standard, not proprietary platform

---

## Phase 0: Category Definition & Competitive Analysis ✅ COMPLETE

**Timeline:** October 2025 - December 2025  
**Status:** ✅ Complete

### Objectives
- Define PEL category vs existing standards (BPMN, DMN, AMPL, AnyLogic, Modelica)
- Document 25 canonical business archetypes
- Create competitive gap analysis

### Deliverables
✅ Category specification document  
✅ 25-archetype test suite outline  
✅ Gap analysis vs 6 major existing standards  
✅ PEL uniqueness checklist (10 criteria)

### Success Metrics
- ✅ Written proof that no existing standard satisfies all 10 PEL criteria simultaneously

---

## Phase 1: Canonical IR + Formal Semantics ✅ COMPLETE

**Timeline:** January 2026 - February 2026  
**Status:** ✅ Complete

### Objectives
- Define PEL-IR (Intermediate Representation) as canonical exchange format
- Write formal semantics for all language constructs
- Specify economic type system completely

### Deliverables
✅ `pel_ir_schema.json` — Canonical IR schema (JSON Schema v7)  
✅ `pel_formal_semantics.md` — Mathematical foundations (time, stochastic, constraint, policy)  
✅ `pel_type_system.md` — Economic types (units, scope, time-index, distributions)  
✅ IR validation rules and backward compatibility policy  
✅ Type system test cases (dimensional analysis, time legality, correlation)

### Success Metrics
- ✅ IR schema passes JSON Schema validation
- ✅ Formal semantics define evaluation order unambiguously
- ✅ Type system prevents all 15 documented silent error classes

### Key Decisions Made
- **IR format:** JSON (not protobuf/CBOR) for human readability and debugging
- **Time semantics:** Discrete time by default; events as deltas between timesteps
- **Type inference:** Bidirectional type checking with unit propagation
- **Versioning:** Semantic versioning with backward-compatible IR extensions

---

## Phase 2: Reference Runtime 🚧 IN PROGRESS

**Timeline:** February 2026 - April 2026  
**Status:** 🚧 75% Complete

### Objectives
- Implement deterministic simulator
- Implement Monte Carlo engine with correlation preservation
- Implement constraint tracing and sensitivity analysis
- Define run artifact format for reproducibility

### Deliverables
✅ Deterministic engine (`/runtime/deterministic_engine/`)  
✅ Monte Carlo engine (`/runtime/monte_carlo_engine/`)  
🚧 Sensitivity engine (tornado complete, Sobol in progress)  
✅ Constraint tracer  
✅ Correlation engine (Cholesky decomposition for multivariate sampling)  
✅ Run artifact schema (model hash + assumption hash + seed)

### Success Metrics
- ✅ Determinism test: 10,000 reruns with same seed produce bit-identical results
- ✅ Correlation preservation: Spearman ρ within 0.02 of specified correlation
- 🚧 Performance: 10,000 Monte Carlo runs on 100-variable model in <10 seconds
- ✅ Constraint tracing: Correctly identifies first binding constraint in test suite

### Current Blockers
- Sobol sensitivity engine requires integration with SALib (planned Q1-end)

---

## Phase 3: Language + Compiler ✅ COMPLETE

**Timeline:** January 2026 - February 2026  
**Status:** ✅ Complete

### Objectives
- Define PEL concrete syntax (grammar)
- Implement parser → AST → IR compiler
- Implement all compilation passes (type checking, provenance, mechanism validation)
- Generate comprehensive error codes

### Deliverables
✅ `pel_language_spec.md` — Complete syntax and grammar (EBNF)  
✅ Parser (ANTLR4 grammar + Python implementation)  
✅ AST representation (`/compiler/ast/`)  
✅ Type checker (`/compiler/typechecker/`) — units, scope, time-index validation  
✅ Constraint checker (`/compiler/constraint_checker/`)  
✅ Mechanism validator (`/compiler/mechanism_validator/`) — anti-"vibes" enforcement  
✅ Provenance enforcer (`/compiler/provenance_enforcer/`) — assumption completeness  
✅ 287 documented compiler error codes with fix suggestions

### Success Metrics
- ✅ Negative compilation test suite: 150+ expected failures caught correctly
- ✅ Mechanism coverage: 100% rejection rate for prose claims without variable mappings
- ✅ Provenance completeness: All parameters require source+method+confidence or compilation fails

### Key Design Decisions
- **Syntax style:** Rust-inspired (clear sigils, explicit types, blocks)
- **Type system:** Nominative for economic types (Currency<USD> ≠ Currency<EUR>)
- **Error messages:** Rust-quality (explain what's wrong, why, and suggest fix)
- **Provenance syntax:** Inline metadata blocks (not sidecar files)

---

## Phase 4: Standard Library (PEL-STD) 🚧 IN PROGRESS

**Timeline:** December 2025 - March 2026  
**Status:** 🚧 67% Complete

### Objectives
- Implement standard library modules for common economic patterns
- Each module includes golden tests and reference results
- Conformance: modules behave identically across runtimes

### Deliverables
🔜 Demand module (`demand_module/`) — lead generation, seasonality  
✅ Funnel module (`funnel_module/`) — multi-stage conversion  
🔜 Pricing module (`pricing_module/`) — elasticity, response curves  
✅ Unit economics module (`unit_econ_module/`) — LTV, CAC, payback  
✅ Cashflow module (`cashflow_module/`) — AR/AP timing, payroll  
✅ Retention module (`retention_module/`) — cohort analysis, churn curves  
✅ Capacity module (`capacity_module/`) — queueing, utilization  
✅ Hiring module (`hiring_module/`) — ramp curves, attrition  
🔜 Shock library (`shock_library/`) — recession, platform changes, supply shocks

### Success Metrics
- ✅ 6 of 9 core modules complete with golden tests
- 🚧 All modules pass conformance tests on reference runtime (90% complete)
- 🚧 Documentation includes examples, edge cases, and failure modes for each module

### Planned Modules (Q2 2026)
- Inventory module (stock levels, reorder points, lead times)
- Tax module (jurisdiction-aware payroll, sales, corporate tax)
- Debt module (amortization, covenants, refinancing)
- Foreign exchange module (multi-currency, hedging)

---

## Phase 5: Tooling Ecosystem 🚧 IN PROGRESS

**Timeline:** January 2026 - March 2026  
**Status:** 🚧 30% Complete

### Objectives
- Provide language-grade developer experience
- CLI tooling for compilation and execution
- Visualizer and package manager

### Deliverables
⏸️ LSP server — deferred to future release (prototype removed to reduce maintenance surface)  
⏸️ Formatter (`pel fmt`) — deferred to future release (prototype removed to reduce maintenance surface)  
⏸️ Linter (`pel lint`) — deferred to future release (prototype removed to reduce maintenance surface)  
✅ CLI (`pel compile`, `pel run`, `pel test`)  
🚧 Visualizer (`pel graph`) — dependency graph, risk hotspot map (40% complete)  
🚧 Package manager (`pel pkg`) — semantic versioning, signing (30% complete)

### Success Metrics
- ⏸️ LSP — deferred; will be re-evaluated after stdlib stabilises
- ⏸️ Formatter — deferred; will be re-evaluated after stdlib stabilises
- 🚧 Visualizer generates interactive dependency graphs from IR

### Current Focus
- Visualizer interactive graph generation
- Package manager cryptographic signing implementation

---

## Phase 6: Assumption Governance + Provenance 🚧 IN PROGRESS

**Timeline:** February 2026 - March 2026  
**Status:** 🚧 40% Complete

### Objectives
- Enforce assumption metadata as first-class requirement
- Auto-generate assumption register
- Enable "economic git" (model diffing)
- Produce board-grade reproducibility artifacts

### Deliverables
✅ Provenance schema (source, method, confidence, freshness, owner)  
🚧 Assumption Register auto-generation (70% complete)  
🚧 Model diff system (`pel diff`) — economic change summaries (50% complete)  
🚧 Run audit trail format — JSON artifact with full reproducibility data (80% complete)  
🚧 Dashboard for assumption completeness scoring (30% complete)

### Success Metrics
- 🚧 Assumption completeness score implemented (algorithm defined, UI pending)
- ✅ Reproducibility artifacts include model hash + assumption hash + seed + runtime version
- 🚧 Model diff correctly identifies economic changes vs syntactic changes

### Key Design Decisions
- **Freshness encoding:** ISO 8601 durations (e.g., "P3M" = 3 months)
- **Confidence scale:** 0.0-1.0 (not percentages or qualitative labels)
- **Source types:** Observed, fitted, derived, expert_estimate, external_research, assumption
- **Model hash:** SHA-256 of normalized IR (whitespace-invariant)

---

## Phase 7: Calibration Loop (Digital Twin) 🔜 PLANNED Q2 2026

**Timeline:** April 2026 - June 2026  
**Status:** 🔜 Specification phase

### Objectives
- Connect PEL models to real accounting/CRM/ops data
- Fit distributions from historical data
- Detect drift (model vs reality divergence)
- Recommend "what to measure next" based on sensitivity

### Planned Deliverables
- Data connectors (QuickBooks, Salesforce, Stripe, generic CSV/SQL)
- Parameter estimation module (MLE, Bayesian fitting)
- Drift detection alerts (Kolmogorov-Smirnov, sequential testing)
- Sensitivity-driven measurement prioritization

### Success Metrics (Target)
- Forecast error improvement (MAPE reduction >20% after calibration)
- Drift detection precision/recall >80%
- Time-to-detect cash crunch reduced by >50% vs manual monitoring

### Risks
- Integration complexity with heterogeneous data sources
- Privacy/security concerns for production data access
- Requires mature sensitivity engine (dependency on Phase 2)

---

## Phase 8: Public Benchmark Suites ✅ PARTIALLY COMPLETE

**Timeline:** January 2026 - Ongoing  
**Status:** 🚧 PEL-100 complete, others in progress

### Objectives
- Prove PEL superiority with objective metrics
- Public scoreboard for continuous improvement
- Enable third-party runtime comparison

### Deliverables
✅ **PEL-100 Expressiveness Suite** — 100 business archetypes (SaaS, marketplace, manufacturing, etc.)  
  - Metrics: Model coverage, median LOC, time-to-first-simulation  
  - Status: ✅ Complete

🚧 **PEL-SAFE Correctness Suite** (70% complete)  
  - Metrics: Silent error prevention rate, determinism rate  
  - Status: 15 error classes documented, 180+ test cases

🚧 **PEL-TRUST Auditability Suite** (50% complete)  
  - Metrics: Assumption completeness, provenance coverage, reproducibility  
  - Status: Scoring rubric defined, 50 test models

🔜 **PEL-RISK Tail Robustness Suite** (planned Q2)  
  - Metrics: Probability-of-ruin accuracy, tail coverage under correlated shocks  
  - Requires: Synthetic ground truth models with known risk profiles

🔜 **PEL-UX Human Study Suite** (planned Q3)  
  - Metrics: Time-to-implement, error rate, comprehension score, trust score  
  - Requires: IRB approval, participant recruitment

### Success Metrics
- ✅ PEL-100: All 100 archetypes implemented in <200 LOC each
- 🚧 PEL-SAFE: >99% silent error prevention vs spreadsheet baseline
- 🚧 PEL-TRUST: >95% assumption completeness on published models
- 🔜 PEL-RISK: Calibrated probability-of-ruin (Brier score <0.2)
- 🔜 PEL-UX: >70% prefer PEL over spreadsheets (statistically significant)

---

## Phase 9: Conformance & Standardization 🚧 IN PROGRESS

**Timeline:** February 2026 - May 2026  
**Status:** 🚧 85% Complete

### Objectives
- Define conformance requirements for third-party runtimes
- Create certification process
- Establish governance model for spec evolution
- Enable multi-vendor ecosystem

### Deliverables
✅ `pel_conformance_spec.md` — Conformance levels (Core, Extended, Calibration)  
✅ Conformance test harness (100% complete) — 280 automated tests across 5 categories  
  - ✅ Lexical conformance (30 tests)
  - ✅ Parsing conformance (80 tests)
  - ✅ Type checking conformance (100 tests)
  - ✅ Provenance conformance (20 tests)
  - ✅ Runtime conformance (50 tests)
🚧 Certification process documentation (40% complete)  
🚧 PEL Enhancement Proposal (PEP) process (specification complete, tooling 20%)  
🚧 IR backward compatibility guarantee (policy defined, tests 50%)

### Success Metrics
- ✅ Conformance test harness covers 100% of Core specification (280 tests)
- 🔜 At least 1 third-party runtime implementation in progress (target: Q2 2026)
- 🔜 First PEP submitted and ratified through governance process

### Conformance Levels
1. **PEL Core** — Deterministic simulation, type checking, basic stdlib
2. **PEL Extended** — Monte Carlo, sensitivity analysis, full stdlib
3. **PEL Calibration** — Data ingestion, fitting, drift detection

---

## Phase 10: Community & Adoption 🚧 IN PROGRESS

**Timeline:** Ongoing  
**Status:** 🚧 Early stage

### Objectives
- Build community of practitioners and contributors
- Create learning resources
- Demonstrate value with case studies
- Achieve network effects for model exchange

### Deliverables
✅ Documentation site (docs.pel-lang.org) — hosted Sphinx docs  
🚧 Tutorial series (3 of 10 complete)  
  - ✅ Intro: "Your First PEL Model"
  - ✅ Types: "Understanding Economic Types"
  - ✅ Uncertainty: "Distributions and Correlation"
  - 🔜 Constraints, Policies, Calibration, Advanced (Q2)
🚧 Example model gallery (20 models published)  
🔜 Case studies (target: 5 by Q3 2026)  
🔜 Academic paper submission (planned for Q2 2026 submission)

### Success Metrics (12-Month Targets)
- 🎯 100+ public PEL models in model gallery
- 🎯 500+ community members (Discord, mailing list)
- 🎯 10+ external code contributors
- 🎯 2+ conference presentations or academic citations
- 🎯 1+ enterprise pilot adoption

### Community Engagement Strategy
- Monthly community calls
- Quarterly "PEL Model of the Month" showcase
- Annual PELCon conference (planned 2027)
- University partnerships for coursework integration

---

## Long-Term Vision (2027-2028)

### Year 2 Goals (2027)

**Technical Maturity**
- PEL 1.0 specification stable and versioned
- 3+ conformant runtime implementations
- All 5 benchmark suites complete with public scoreboards
- Calibration loop production-ready

**Ecosystem Growth**
- 1,000+ public PEL models
- 10+ organizational adopters
- Standard library expanded to 20+ modules
- IDE plugins for major editors (VS Code, IntelliJ, Jupyter)

**Mindshare**
- Academic papers published in top-tier venues
- Referenced in textbooks/courses
- CFO/finance community awareness >10%
- "PEL-certified model" becomes trust signal

### Year 3+ Goals (2028+)

**Standardization**
- Submit to standards body (ISO, OMG, or independent foundation)
- Multi-vendor support and competition on runtime performance/UX
- PEL-as-a-Service cloud offerings
- Regulatory acceptance (e.g., for financial reporting, compliance)

**Killer Use Cases**
- Real-time strategic dashboards (CFO "mission control")
- Automated scenario planning for boards
- Regulatory stress testing (e.g., Basel-like frameworks for non-banks)
- M&A due diligence (target model validation)

**Research Directions**
- Causal inference integration (do-calculus, intervention modeling)
- AI-assisted model generation from narrative descriptions
- Formal verification of economic properties (reachability, invariants)
- Multi-agent game theory extensions

---

## Risk Management

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance bottlenecks in Monte Carlo | Medium | High | Profile early, optimize hot paths, parallel sampling |
| IR bloat over time | Medium | Medium | Strict backward compatibility policy, deprecation process |
| Type system complexity ceiling | Low | High | Simplicity-first design, avoid Turing-complete type system |
| Third-party runtime divergence | Medium | High | Comprehensive conformance suite, mandatory certification |

### Adoption Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| "Too complex for spreadsheet users" | High | High | Gentle learning curve, stdlib hides complexity, great docs |
| "Not invented here" from enterprises | High | Medium | Case studies, ROI proof, interop with existing tools |
| Network effects failure (no models shared) | Medium | High | Model gallery, showcase best models, community incentives |
| Tooling fragmentation | Low | Medium | LSP standard ensures editor portability |

### Ecosystem Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Competing standard emerges | Low | High | First-mover advantage, public benchmarks prove superiority |
| Open-source sustainability | Medium | Medium | Dual licensing (AGPL-3.0 + Commercial), sponsorships, support contracts |
| Academic credibility gap | Medium | Medium | Publish papers, partner with universities, formal verification work |

---

## Resource Allocation (2026)

### Core Team (Estimated FTE)
- Specification & design: 1.0 FTE
- Compiler development: 1.5 FTE
- Runtime development: 1.5 FTE
- Standard library: 1.0 FTE
- Tooling: 1.0 FTE
- Documentation & community: 0.5 FTE

**Total: 6.5 FTE** (mix of full-time and part-time contributors)

### Priorities (Next 6 Months)
1. **Complete Phase 2** (runtime) — unblocks external validation
2. **Complete Phase 4** (stdlib) — enables real-world models
3. **Complete Phase 5** (tooling) — improves developer experience
4. **Advance Phase 8** (benchmarks) — proves value objectively
5. **Grow Phase 10** (community) — network effects and adoption

---

## Version History

### v0.1.0 (February 2026) — "Foundation Release"
- Complete formal specifications
- Reference compiler and runtime
- Core standard library
- Basic tooling (LSP, formatter, CLI)
- PEL-100 expressiveness benchmark

### v0.2.0 (Planned April 2026) — "Ecosystem Release"
- Complete standard library
- Advanced sensitivity analysis (Sobol)
- Linter with 50+ rules
- Model diff and governance tools
- PEL-SAFE and PEL-TRUST benchmark suites

### v0.3.0 (Planned June 2026) — "Calibration Release"
- Data connectors and fitting
- Drift detection
- PEL-RISK benchmark suite
- First third-party runtime (in beta)

### v1.0.0 (Planned December 2026) — "Stability Release"
- Specification frozen for backward compatibility
- Conformance certification live
- All benchmark suites complete
- Production-ready tooling
- Multi-runtime ecosystem

---

## How to Contribute to the Roadmap

The roadmap is a living document. To propose changes:

1. **Open an issue** on GitHub with tag `roadmap-feedback`
2. **Attend monthly community calls** to discuss priorities
3. **Submit a PEP** (PEL Enhancement Proposal) for major features
4. **Vote in quarterly priority surveys** (community + core team)

The core team reviews roadmap quarterly and adjusts based on:
- Technical blockers/dependencies
- Community feedback and adoption signals
- Resource availability
- Competitive landscape changes

---

## Conclusion

PEL's roadmap is designed for **credibility through measurability**. Every phase has concrete deliverables, success metrics, and public artifacts.

By the end of 2026, PEL will have:
- Proven technical superiority through benchmark suites
- Demonstrated portability through conformant runtimes
- Enabled real-world adoption through tooling and examples
- Established governance for long-term standardization

**The goal is not to be "interesting." The goal is to be indispensable.**

---

**Next Review:** April 2026  
**Roadmap Owner:** PEL Core Team  
**Community Feedback:** [github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)
