# Baseline Management Policy

This document defines the lifecycle of performance/conformance baselines in the Language Evaluation Framework.

## Overview

Baselines are JSON snapshots of language implementation performance/correctness at a specific point in time. They serve as reference points for regression detection and release gating.

**Current Baseline:** `.language-eval/baselines/baseline.example.json`

## Baseline Versioning Scheme

Baselines are versioned by **target+version+environment**:

```json
{
  "target_id": "pel-0.1.0",
  "version": "0.1.0",
  "environment": {
    "os": "linux",
    "arch": "x86_64",
    "python": "3.11",
    "timestamp": "2026-02-19T12:00:00Z"
  },
  "created_at": "2026-02-19T12:00:00Z",
  "overall_score": 3.4,
  ...
}
```

### Naming Convention

```
baselines/
├── baseline.pel-0.1.0.json          # Main release baseline
├── baseline.pel-0.1.0-linux-py311.json
├── baseline.pel-0.1.0-macos-py311.json
├── baseline.pel-0.2.0-dev.json      # Development baseline
├── baseline.pel-0.2.0-rc1.json      # Release candidate
└── baseline.archive/
    ├── baseline.pel-0.0.9-RETIRED.json
    └── baseline.pel-0.0.8-RETIRED.json
```

### Version Numbering

- **X.Y.Z format** (semantic versioning)
- Bumped with language release (not framework version)
- Example: `pel-0.1.0`, `pel-0.2.0-beta`, `pel-0.2.0-rc1`

---

## Baseline Creation & Approval

### Prerequisites

Before creating a baseline:

- [ ] All suites fully implemented (non-placeholder)
- [ ] Framework passes all tests (`pytest .language-eval/tests/ -xvs`)
- [ ] Target configuration finalized in `targets/<target>.yaml`
- [ ] Environment properly documented (OS, arch, Python version, key deps)

### Creation Process

1. **Run Full Evaluation Suite**
   ```bash
   ./.language-eval/scripts/run_all.sh \
     --target .language-eval/targets/<target>.yaml \
     --outdir reports/baseline_candidate
   ```

2. **Validate Output**
   ```bash
   python .language-eval/scripts/ci_gate.py \
     --target .language-eval/targets/<target>.yaml \
     --report-dir reports/baseline_candidate
   ```
   Must pass all schema validation and thresholds.

3. **Review Scores**
   - Check `reports/baseline_candidate/scorecard.json`
   - Verify all 13 categories are populated
   - Investigate any outliers (score < 2.0 or == 5.0)
   - Confirm realistic vs. competitor products

4. **Document Decision**
   ```bash
   cat reports/baseline_candidate/scorecard.json > \
     .language-eval/baselines/baseline.<target_id>.json
   ```

5. **Obtain Approval**
   - Create pull request with new baseline
   - Get maintainer sign-off: "I reviewed the scores and they accurately reflect the language implementation"
   - Include link to full report artifact

### Approval Criteria

Baseline is approved when:

- [x] Framework team has reviewed scores
- [x] Domain experts agree metrics are meaningful
- [x] Scores are not obviously outliers (e.g., not 5.0 across entire scorecard)
- [x] Environment is documented and reproducible
- [x] Expected failures properly tracked with expiry dates
- [x] No CI gate violations

---

## Baseline Usage

### In CI/CD

Baseline is automatically loaded by `ci_gate.py`:

```python
baseline_path = _resolve_path(target.get("baseline"), target_path)
baseline = _load(baseline_path)
```

### Regression Detection

When running evaluation:

```bash
./.language-eval/scripts/run_all.sh --target <target>
# Automatically compares against baseline referenced in target.yaml
# Fails if regressions exceed threshold
```

### Explicit Baseline Comparison

```bash
python .language-eval/scripts/compare_baseline.py \
  --target .language-eval/targets/<target>.yaml \
  --current reports/current/results.normalized.json \
  --scorecard reports/current/scorecard.json \
  --out reports/comparison.json
```

---

## Baseline Maintenance

### Quarterly Baseline Review

Every 3 months:

1. **Check Baseline Age**
   ```bash
   .language-eval/scripts/baseline_report.sh  # future tool
   ```
   Shows all baselines and their age

2. **Assess Drift**
   - Run framework on current implementation
   - Compare new scores vs baseline
   - If drift > 10%: investigate cause

3. **Expected Failures Audit**
   - Check for expired expected failures
   - Remove or extend entries as needed
   - Verify each has documented remediation

4. **Document Findings**
   - Create issue tracking needed updates
   - Assign owner for regressions

### Annual Baseline Refresh

Once per year (or on major language release):

1. **Plan Refresh**
   - Identify new baselines needed
   - Estimate effort / timeline
   - Get stakeholder buy-in

2. **Collect Baseline Data**
   - Run suite on newly released version
   - Collect across >=3 diverse platforms
   - Average scores to establish baseline

3. **Validate Consistency**
   - Verify determinism (hash matches across runs)
   - Check cross-platform variance < 5%
   - Document any platform-specific notes

4. **Migrate Users**
   - Create PR with new baselines
   - Update `.language-eval/targets/*.yaml` to reference new baseline
   - Announce migration deadline (30 days notice)
   - Retire old baselines

5. **Archive Old Baselines**
   ```bash
   mv .language-eval/baselines/baseline.pel-0.0.9.json \
      .language-eval/baselines/archive/baseline.pel-0.0.9-RETIRED.json
   ```

---

## Baseline Updates / Intentional Regressions

### When Baseline Needs Update

**Scenario 1: Intentional Performance Tradeoff**
- Example: "Improved memory efficiency at cost of 2% CPU slowdown"
- Action: Update baseline + document decision

**Scenario 2: New Platform Support**
- Example: Adding MacOS baseline alongside Linux
- Action: Create new baseline file with platform-specific metrics

**Scenario 3: Framework Formula Change**
- Example: Changing performance baseline from 2000 to 3000 ops/sec
- Action: Recalibrate ALL baselines

### Update Process

1. **Run New Evaluation**
   ```bash
   ./.language-eval/scripts/run_all.sh \
     --target .language-eval/targets/<target>.yaml \
     --outdir reports/updated_baseline
   ```

2. **Create Comparison Report**
   ```bash
   # Manually compare against old baseline  scores
   # Document why each delta exists
   ```

3. **Justify Each Regression**
   - Link to design decision / PR discussion
   - Example: "Intentional tradeoff for memory efficiency (PR #42)"
   - Estimate remediation timeline if not intentional

4. **Get Approval**
   - Pull request with changes
   - Include side-by-side score diff
   - Require explicit maintainer approval

5. **Deploy Updated Baseline**
   ```bash
   # After PR merged:
   cp reports/updated_baseline/scorecard.json \
      .language-eval/baselines/baseline.<target>.json
   ```

### Allowlisting Regressions

If temporary regression is acceptable:

```yaml
# In .language-eval/targets/<target>.yaml
allowlisted_regressions:
  - "category:runtime_performance"  # Allow 5% + perf regression for 6 months
  - "overall"  # Allow overall score drift
```

Must also update expected failures:

```yaml
# In .language-eval/suites/conformance/expected_failures.yaml
- id: perf-tradeoff-202606
  reason: "Intentional: improved memory efficiency at cost of CPU"
  owner: performance-team
  introduced: "2026-03-15"
  expiry: "2026-09-15"  # Force reconsideration after 6 months
  severity: medium
```

---

## Baseline Retirement

### Retirement Criteria

Baseline is retired when:

- [ ] Newer baseline exists for same target
- [ ] Language version is end-of-life (e.g., Python 3.8)
- [ ] Platform is discontinued (e.g., 32-bit x86)
- [ ] Target is no longer actively developed

### Retention Policy

| Baseline Type | Retention Period | Archive After |
|---------------|------------------|---------------|
| Current release | ∞ (indefinite) | Never |
| Previous minor | 12 months | Move to archive/ |
| Previous major | 24 months | Move to archive/ |
| Beta/RC | 6 months | Delete |
| Development | 3 months | Delete |

### Retirement Process

1. **Announce Deprecation**
   - Create issue: "Retiring baseline for pel-X.Y.Z (EOL on YYYY-MM-DD)"
   - Post in team channels / release notes
   - 30-day notice minimum

2. **Migrate Users**
   - Update any `targets/*.yaml` still pointing to old baseline
   - Provide migration guide if needed

3. **Archive Baseline**
   ```bash
   mkdir -p .language-eval/baselines/archive/v0.0.X
   mv .language-eval/baselines/baseline.pel-0.0.X.json \
      .language-eval/baselines/archive/v0.0.X/baseline.pel-0.0.X-RETIRED.json
   ```

4. **Document Retirement**
   ```
   baselines/
   └── archive/
       └── v0.0.X/
           └── README.md (explains why retired, links to replacement)
   ```

5. **Remove from CI/CD**
   - Delete any CI workflows testing old baseline
   - Update sample targets to use current baseline

---

## Baseline Troubleshooting

### "Baseline Not Found" Error

```
SystemExit: Baseline not found: baselines/baseline.missing.json
```

**Causes:**
- Typo in target config `baseline:` path
- Baseline file accidentally deleted
- Path is relative but cwd is wrong

**Resolution:**
```bash
# Check baseline exists:
ls -la .language-eval/baselines/

# Fix target path:
grep "baseline:" .language-eval/targets/<target>.yaml

# Verify from repo root:
cd /path/to/PEL
./.language-eval/scripts/run_all.sh --target .language-eval/targets/<target>.yaml
```

### "Regression Exceeds Threshold"

```
SystemExit: Regressions exceed threshold: [{'id': 'category:security_properties', ...}]
```

**Options:**
1. **Investigate legitimate regression** → Fix in code
2. **Update baseline if intentional** → Follow update process above
3. **Increase tolerance temporarily** → Update `thresholds.regression_tolerance_pct`
4. **Allowlist expected regression** → Add to `allowlisted_regressions`

### "Missing Expected Failure"

```json
{"error": "Expected failure entry missing expiry: conformance-old-001"}
```

**Action:**
- Edit `.language-eval/suites/conformance/expected_failures.yaml`
- Add `expiry: YYYY-MM-DD` to every entry
- Baseline enforcement prevents stale exclusions

---

## Baseline Analytics (Future)

### Planned Tools (v1.1)

```bash
# Show all baselines and metadata
.language-eval/scripts/baseline_report.sh

# Visualize score trends over time
.language-eval/scripts/baseline_trends.py --target pel-*.json --output trends.html

# Compare two baselines
.language-eval/scripts/baseline_diff.py \
  baselines/baseline.pel-0.1.0.json \
  baselines/baseline.pel-0.2.0.json
```

---

## Examples

### Creating First Baseline for New Target

```bash
# 1. Run evaluation
./.language-eval/scripts/run_all.sh \
  --target .language-eval/targets/my-language.yaml \
  --outdir reports/baseline_my_language

# 2. Validate
python .language-eval/scripts/ci_gate.py \
  --target .language-eval/targets/my-language.yaml \
  --report-dir reports/baseline_my_language

# 3. Create baseline
cp reports/baseline_my_language/scorecard.json \
   .language-eval/baselines/baseline.my-language-1.0.0.json

# 4. Get approval, merge PR
git add .language-eval/baselines/baseline.my-language-1.0.0.json
git commit -m "baseline: add my-language 1.0.0 reference"
git push origin feature/add-my-language-target
```

### Intentional Performance Regression

```yaml
# .language-eval/targets/pel.yaml
allowlisted_regressions:
  - "category:runtime_performance"  # Allow 5% perf regression (plus threshold)
  
# .language-eval/suites/conformance/expected_failures.yaml
- id: feature-x-perf-tradeoff
  reason: "Implemented lazy evaluation (feature-x) with 8% startup cost"
  owner: language-team
  introduced: "2026-03-01"
  expiry: "2026-12-31"  # Revisit in Q4 2026
  severity: medium
```

---

## Document Ownership

**Maintainer:** Framework Team  
**Last Updated:** 2026-02-19  
**Review Cycle:** Quarterly (with baseline refresh)

---

## See Also

- [RELEASE_READINESS.md](.language-eval/RELEASE_READINESS.md) — When baselines can be used for release gating
- [FORMULA_DERIVATION.md](.language-eval/FORMULA_DERIVATION.md) — Scoring formulas & recalibration
- [GOVERNANCE.md](.language-eval/GOVERNANCE.md) — Approval processes for changes
