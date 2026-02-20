# GitHub Issues Created from Comprehensive Assessment
**Date:** February 20, 2026  
**Repository:** Coding-Krakken/pel-lang  
**Total Issues:** 12

---

## P0 - BLOCKERS (Must Fix Before Production)

### Issue #30: Fix beginner example type errors in saas_business.pel
**Priority:** 🔴 P0 BLOCKER  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/30  
**Status:** Open  
**Impact:** Tutorial is broken - users can't onboard  

**Summary:** Beginner examples `saas_business.pel` and `saas_uncertain.pel` fail to compile due to type system rejecting `Count<Customers> * Rate per Month` arithmetic. This is a fundamental pattern in economic modeling but currently produces type errors.

**Fix Options:**
1. Extend type system to support `Count<T> * Rate per Month → Count<T>` arithmetic
2. Rewrite examples to use type-compatible operations

---

### Issue #31: Implement policy execution in runtime
**Priority:** 🔴 P0 BLOCKER  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/31  
**Status:** Open  
**Impact:** Cannot model adaptive strategies (hiring freezes, price adjustments)  

**Summary:** Policy blocks are accepted by parser but not executed by runtime. This prevents modeling dynamic business rules and adaptive strategies that are fundamental to business planning.

**Required:** Policy evaluation engine that checks conditions and mutates variables at each timestep.

---

### Issue #32: Fix Monte Carlo execution (runs count, value normalization, sampling)
**Priority:** 🔴 P0 BLOCKER  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/32  
**Status:** Open  
**Impact:** Monte Carlo is completely unusable for risk analysis  

**Summary:** Three critical bugs:
1. Only 10 runs execute (not 1000 as specified)
2. Results are normalized to 100-scale instead of actual currency values
3. Distributions may not be sampled (all runs identical)

**Required:** Fix runs count, preserve actual unit values, verify distribution sampling.

---

### Issue #33: Make constraint violation messages actionable (include actual values)
**Priority:** 🔴 P0 BLOCKER  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/33  
**Status:** Open  
**Impact:** Constraint violations show generic messages, can't diagnose problems  

**Summary:** Constraint violations detected but messages don't include actual values, violation amounts, or suggestions. Users can't determine what's wrong or how to fix it.

**Required:** Include actual variable values, violation amounts, and interpolated messages in constraint violation output.

---

## P1 - HIGH PRIORITY (Needed for Serious Adoption)

### Issue #34: Complete standard library implementation and make modules importable
**Priority:** ⚠️ P1 HIGH  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/34  
**Status:** Open  
**Impact:** Users must reinvent common patterns (capacity planning, financial metrics)  

**Summary:** Standard library modules documented and referenced in examples but not implemented or importable. Currently 6 of 9 modules complete (67%), but none are callable at runtime.

**Required:** 
- Complete remaining 3 modules
- Implement auto-loading mechanism
- Create golden test results
- Document all functions

---

### Issue #35: Improve error messages with Rust-quality diagnostics
**Priority:** ⚠️ P1 HIGH  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/35  
**Status:** Open  
**Impact:** Poor error messages significantly slow learning curve  

**Summary:** Current error messages are minimal and unhelpful - no code context, line numbers, or suggestions for fixing.

**Required:**
- Code snippets with highlighting
- Detailed error explanations
- Actionable suggestions
- `pel explain EXXXX` command
- Multiple error reporting

---

### Issue #36: Build visualization layer for model results
**Priority:** ⚠️ P1 HIGH  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/36  
**Status:** Open  
**Impact:** Results are hard to present to non-technical stakeholders  

**Summary:** PEL produces JSON that requires custom scripts to visualize. Every user must reinvent visualization tools.

**Required:**
- Time series line charts
- Monte Carlo distribution plots
- Scenario comparison charts
- Constraint violation heatmaps
- Export to PNG/SVG/HTML

---

### Issue #37: Document type system arithmetic rules and edge cases
**Priority:** ⚠️ P1 HIGH  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/37  
**Status:** Open  
**Impact:** Users are guessing what operations are allowed between types  

**Summary:** Type system arithmetic rules are completely undocumented. Users don't know what operations produce what result types.

**Required:**
- Type compatibility matrix
- Dimensional analysis rules
- Common pattern cookbook
- Error code explanations
- Type system philosophy documentation

---

## P2 - MEDIUM PRIORITY (Ecosystem Growth)

### Issue #38: Implement calibration tools (data connectors and parameter fitting)
**Priority:** 📝 P2 MEDIUM  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/38  
**Status:** Open  
**Impact:** Models need real-world data but require manual external analysis  

**Summary:** No built-in calibration tools. Users must manually analyze data externally and copy parameters into PEL models.

**Required:**
- Data connectors (CSV, SQL, JSON)
- Parameter fitting (regression, MLE)
- Distribution inference
- Model validation with holdout data

---

### Issue #39: Implement package manager for importing external models and libraries
**Priority:** 📝 P2 MEDIUM  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/39  
**Status:** Open  
**Impact:** No code reuse, every user reinvents common patterns  

**Summary:** PEL has no way to import external models or share reusable components. No community model sharing or ecosystem.

**Required:**
- Import syntax (local files, Git repos)
- Dependency resolution (semver)
- Package manifest format
- `pel install/add/update` commands

---

### Issue #40: Create public conformance test suite for alternative implementations
**Priority:** 📝 P2 MEDIUM  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/40  
**Status:** Open  
**Impact:** Cannot verify alternative implementations, risk of fragmentation  

**Summary:** PEL aims for multiple implementations but has no conformance test suite to verify compatibility.

**Required:**
- Test suite for Level 0 (PEL-Core)
- Test suite for Level 1 (PEL-Extended)
- Test suite for Level 2 (PEL-Calibration)
- Golden test results
- CI integration

---

### Issue #41: Fix horizon flag to override compiled horizon at runtime
**Priority:** 📝 P2 MEDIUM  
**Link:** https://github.com/Coding-Krakken/pel-lang/issues/41  
**Status:** Open  
**Impact:** Must recompile to change forecast period  

**Summary:** The `--horizon` flag may not properly override the compiled time horizon. Users must recompile models to test different timeframes.

**Required:**
- Runtime horizon override
- TimeSeries arrays extend/truncate correctly
- Works with both deterministic and Monte Carlo modes

---

## Summary Statistics

**Total Issues Created:** 12  
**P0 Blockers:** 4 (33%)  
**P1 High Priority:** 4 (33%)  
**P2 Medium Priority:** 4 (33%)  

**Breakdown by Component:**
- Runtime: 3 issues (#31, #32, #41)
- Compiler/Type System: 2 issues (#30, #37)
- Tooling: 4 issues (#34, #35, #36, #39)
- Testing/Quality: 2 issues (#33, #40)
- Calibration: 1 issue (#38)

**Estimated Timeline:**
- **P0 Fixes:** 4-6 weeks (blocking production use)
- **P1 Improvements:** 2-3 months (smooth adoption)
- **P2 Ecosystem:** 2-3 months (growth enablers)

**Total to Production-Ready:** 4-6 months with focused execution

---

## Next Steps

1. **Triage P0 Issues** (This Week)
   - Prioritize runtime bugs (#31, #32, #33)
   - Fix beginner examples (#30)
   - Create sprint plan

2. **Short-Term** (1-2 Months)
   - Fix all P0 blockers
   - Improve error messages (#35)
   - Add basic visualization (#36)

3. **Medium-Term** (3-6 Months)
   - Complete standard library (#34)
   - Document type system (#37)
   - Build calibration tools (#38)

4. **Long-Term** (6-12 Months)
   - Package manager (#39)
   - Conformance tests (#40)
   - Second implementation (to prove spec works)

---

**Related Documents:**
- [COMPREHENSIVE_ASSESSMENT.md](COMPREHENSIVE_ASSESSMENT.md) - Full 8,500-word analysis
- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - Quick reference with key findings
