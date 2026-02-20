# PEL Tutorial Learning Path

Welcome to the **PEL Tutorial Suite** - your guide from "Hello World" to production deployment. These tutorials enable independent learning and provide a structured path to mastering economic modeling with PEL.

## 🎯 Learning Path Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    START HERE                                │
│  Tutorial 1: Your First Model in 15 Minutes                 │
│  Build, run, analyze a simple growth model                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼─────────┐
│ Tutorial 2     │  │ Tutorial 3      │
│ Economic Types │  │ Uncertainty &   │
│                │  │ Distributions   │
└───────┬────────┘  └───────┬─────────┘
        │                   │
        └─────────┬─────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼─────────┐
│ Tutorial 4     │  │ Tutorial 5      │
│ Constraints &  │  │ Provenance &    │
│ Policies       │  │ Governance      │
└───────┬────────┘  └───────┬─────────┘
        │                   │
        └─────────┬─────────┘
                  │
┌─────────────────▼───────────────────┐
│ Tutorial 6: Time-Series Modeling    │
│ Master dynamic values over time     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ Tutorial 7: Stdlib Functions        │
│ Use pre-built components            │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ Tutorial 8: Calibration Basics      │
│ Fit models to real data             │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼─────────┐
│ Tutorial 9     │  │ Tutorial 10     │
│ Migration from │  │ Production      │
│ Spreadsheets   │  │ Deployment      │
└────────────────┘  └─────────────────┘
```

## 📚 Tutorial Catalog

### Core Foundations (Start Here)

#### 1. [Your First Model in 15 Minutes](your_first_model_15min.md)
**Time**: 15 minutes | **Difficulty**: Beginner | **Prerequisites**: None

Build, compile, and run a simple SaaS growth model. Learn basic PEL syntax, parameters, variables, and execution modes.

**You'll learn**:
- Write a PEL model
- Compile models to IR
- Run deterministic and Monte Carlo simulations
- Generate reports

**Next steps**: → Tutorial 2 (Types) or Tutorial 3 (Uncertainty)

---

#### 2. [Understanding Economic Types](02_economic_types.md)
**Time**: 20 minutes | **Difficulty**: Beginner | **Prerequisites**: Tutorial 1

Master PEL's semantic type system: currencies, rates, durations, time-indexed values.

**You'll learn**:
- Use `Currency<USD>`, `Rate per Month`, `Duration`
- Avoid unit conversion bugs
- Work with time-indexed values
- Write type-safe models

**Next steps**: → Tutorial 4 (Constraints) or Tutorial 6 (Time Series)

---

#### 3. [Uncertainty & Distributions](03_uncertainty_distributions.md)
**Time**: 25 minutes | **Difficulty**: Beginner | **Prerequisites**: Tutorial 1

Model uncertainty with probability distributions: `Normal`, `Beta`, `LogNormal`, `Uniform`.

**You'll learn**:
- Choose appropriate distributions
- Add correlations between parameters
- Interpret Monte Carlo results (P5, P50, P95)
- Model risk and scenarios

**Next steps**: → Tutorial 4 (Constraints) or Tutorial 8 (Calibration)

---

### Governance & Validation

#### 4. [Constraints & Policies](04_constraints_policies.md)
**Time**: 25 minutes | **Difficulty**: Intermediate | **Prerequisites**: Tutorials 1-3

Enforce business rules with executable constraints. Use `fatal` and `warning` severity levels.

**You'll learn**:
- Write constraint expressions
- Choose severity levels
- Debug constraint failures
- Track violation rates in Monte Carlo

**Next steps**: → Tutorial 5 (Provenance) or Tutorial 6 (Time Series)

---

#### 5. [Provenance & Assumption Governance](05_provenance_governance.md)
**Time**: 20 minutes | **Difficulty**: Intermediate | **Prerequisites**: Tutorials 1-2

Document assumptions with mandatory provenance: source, method, confidence.

**You'll learn**:
- Write complete provenance metadata
- Use confidence scoring
- Generate assumption reports
- Track assumption quality over time

**Next steps**: → Tutorial 8 (Calibration) or Tutorial 9 (Migration)

---

### Advanced Modeling

#### 6. [Time-Series Modeling](06_time_series_modeling.md)
**Time**: 30 minutes | **Difficulty**: Intermediate | **Prerequisites**: Tutorials 1-2

Model dynamic values with time series and recurrence relations.

**You'll learn**:
- Declare time series (`TimeSeries<T>`)
- Write recurrence relations (`var[t+1] = f(var[t])`)
- Use lookback references (`var[t-1]`)
- Debug time-series logic

**Next steps**: → Tutorial 7 (Stdlib) or Tutorial 8 (Calibration)

---

#### 7. [Stdlib Functions & Modules](07_stdlib_functions.md)
**Time**: 25 minutes | **Difficulty**: Intermediate | **Prerequisites**: Tutorials 1-6

Leverage PEL's standard library: unit economics, retention, cash flow, capacity, hiring.

**You'll learn**:
- Use stdlib modules (unit_econ, retention, cashflow, etc.)
- Calculate LTV, CAC, NDR, burn multiple
- Compose stdlib functions
- Build complex models faster

**Next steps**: → Tutorial 8 (Calibration) or Tutorial 9 (Migration)

---

#### 8. [Calibration Basics](calibration.md)
**Time**: 30 minutes | **Difficulty**: Advanced | **Prerequisites**: Tutorials 1-7

Fit distribution parameters to real data using CSV import and MLE.

**You'll learn**:
- Connect PEL to CSV data
- Fit distributions with Maximum Likelihood Estimation
- Update models with calibrated parameters
- Generate calibration reports

**Next steps**: → Tutorial 9 (Migration) or Tutorial 10 (Deployment)

---

### Practical Applications

#### 9. [Migration from Spreadsheets](09_migration_spreadsheets.md)
**Time**: 40 minutes | **Difficulty**: Advanced | **Prerequisites**: Tutorials 1-8

Convert Excel/Google Sheets models to PEL with step-by-step guide.

**You'll learn**:
- Audit and extract spreadsheet logic
- Convert formulas to PEL syntax
- Add types and provenance
- Validate migrated models
- Enhance beyond Excel capabilities

**Next steps**: → Tutorial 10 (Deployment)

---

#### 10. [Production Deployment](10_production_deployment.md)
**Time**: 35 minutes | **Difficulty**: Advanced | **Prerequisites**: Tutorials 1-9, Git, CI/CD basics

Deploy PEL models to production with version control, CI/CD, and monitoring.

**You'll learn**:
- Version models with Git
- Write automated tests
- Build CI/CD pipelines (GitHub Actions)
- Deploy models as APIs
- Monitor production models

**Next steps**: Build real-world models!

---

## 🎓 Recommended Learning Paths

### Path 1: Quick Start (1 hour)
For users who want to get productive fast:

1. Tutorial 1: Your First Model (15 min)
2. Tutorial 2: Economic Types (20 min)
3. Tutorial 3: Uncertainty & Distributions (25 min)

**Outcome**: Can build basic models with uncertainty

---

### Path 2: Spreadsheet Migration (~2.5 hours)
For analysts converting Excel models:

1. Tutorial 1: Your First Model (15 min)
2. Tutorial 2: Economic Types (20 min)
3. Tutorial 5: Provenance (20 min)
4. Tutorial 6: Time-Series (30 min)
5. Tutorial 9: Migration from Spreadsheets (40 min)
6. Tutorial 4: Constraints (25 min)

**Outcome**: Can migrate Excel models to PEL

---

### Path 3: Production-Ready (~4 hours)
For teams deploying models in critical workflows:

1. Tutorial 1: Your First Model (15 min)
2. Tutorial 2: Economic Types (20 min)
3. Tutorial 3: Uncertainty & Distributions (25 min)
4. Tutorial 4: Constraints & Policies (25 min)
5. Tutorial 5: Provenance (20 min)
6. Tutorial 6: Time-Series (30 min)
7. Tutorial 7: Stdlib Functions (25 min)
8. Tutorial 8: Calibration (30 min)
9. Tutorial 10: Production Deployment (35 min)

**Outcome**: Can build, test, and deploy production models

---

### Path 4: Full Mastery (4.5 hours)
Complete all tutorials:

All tutorials 1-10 in order.

**Outcome**: Complete PEL expertise

---

## 📖 Additional Learning Resources

### Documentation
- [Language Specification](../../spec/) - Complete PEL syntax reference
- [Type System](../../spec/pel_type_system.md) - Detailed type system docs
- [Standard Library](../../stdlib/README.md) - Stdlib function reference
- [Migration Guide](../MIGRATION_GUIDE.md) - Extended migration examples

### Examples
- [Example Models](../../examples/) - Production-quality PEL models
- [Calibration Examples](../../examples/CALIBRATION_EXAMPLES.md) - Calibration workflows
- [Semantic Contracts](../../examples/semantic_contracts/) - Advanced patterns

### Community
- [GitHub Discussions](https://github.com/Coding-Krakken/pel-lang/discussions) - Ask questions
- [Issue Tracker](https://github.com/Coding-Krakken/pel-lang/issues) - Report bugs, request features
- [Contributing Guide](../../CONTRIBUTING.md) - Contribute to PEL

---

## 🤝 Getting Help

### During Tutorials
Each tutorial includes:
- ✅ **Working examples**: Copy-paste code that runs
- 🧪 **Quiz questions**: Test your understanding
- 🔑 **Key takeaways**: Summary of concepts
- ➡️ **Next steps**: Recommended tutorials

### Beyond Tutorials
- **Stuck?** Check the [examples/](../../examples/) directory for reference implementations
- **Found an error?** [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new)
- **Have a question?** [Start a discussion](https://github.com/Coding-Krakken/pel-lang/discussions)
- **Want more examples?** See [examples/](../../examples/)

---

## 🎯 Tutorial Completion Checklist

Track your progress:

- [ ] Tutorial 1: Your First Model in 15 Minutes
- [ ] Tutorial 2: Understanding Economic Types
- [ ] Tutorial 3: Uncertainty & Distributions
- [ ] Tutorial 4: Constraints & Policies
- [ ] Tutorial 5: Provenance & Assumption Governance
- [ ] Tutorial 6: Time-Series Modeling
- [ ] Tutorial 7: Stdlib Functions & Modules
- [ ] Tutorial 8: Calibration Basics
- [ ] Tutorial 9: Migration from Spreadsheets
- [ ] Tutorial 10: Production Deployment

**Completed all tutorials?** 🎉 You're ready to build production PEL models!

---

## 📊 Tutorial Metadata

| Tutorial | Time | Difficulty | Prerequisites | Status |
|----------|------|------------|---------------|--------|
| 1. Your First Model | 15min | Beginner | None | ✅ Complete |
| 2. Economic Types | 20min | Beginner | Tutorial 1 | ✅ Complete |
| 3. Uncertainty & Distributions | 25min | Beginner | Tutorial 1 | ✅ Complete |
| 4. Constraints & Policies | 25min | Intermediate | Tutorials 1-3 | ✅ Complete |
| 5. Provenance & Governance | 20min | Intermediate | Tutorials 1-2 | ✅ Complete |
| 6. Time-Series Modeling | 30min | Intermediate | Tutorials 1-2 | ✅ Complete |
| 7. Stdlib Functions | 25min | Intermediate | Tutorials 1-6 | ✅ Complete |
| 8. Calibration Basics | 30min | Advanced | Tutorials 1-7 | ✅ Complete |
| 9. Migration from Spreadsheets | 40min | Advanced | Tutorials 1-7 | ✅ Complete |
| 10. Production Deployment | 35min | Advanced | Tutorials 1-9 | ✅ Complete |

**Total time**: ~4.5 hours (Quick Start: 1 hour, Full Path: 4.5 hours)

---

## 🚀 Ready to Start?

Begin with [Tutorial 1: Your First Model in 15 Minutes](your_first_model_15min.md)

---

**Questions?** [Open an issue](https://github.com/Coding-Krakken/pel-lang/issues/new) or [start a discussion](https://github.com/Coding-Krakken/pel-lang/discussions).
