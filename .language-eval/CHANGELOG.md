# Language Evaluation Framework - Change Log

## Infrastructure Improvements (February 20, 2026)

### Cross-Platform CI Testing ✅

**What:** Extended CI/CD pipeline to test on macOS and Windows in addition to Linux.

**Why:** Ensures framework portability across development platforms.

**Changes:**
- Updated `.github/workflows/language-eval.yml` with matrix strategy
- Tests now run on: `ubuntu-latest`, `macos-latest`, `windows-latest`
- Added `shell: bash` directives for cross-platform compatibility
- Conditional `chmod` step (skips on Windows)
- Separate artifact uploads per platform

**Usage:**
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.11"]
  fail-fast: false
```

**Benefits:**
- Early detection of platform-specific issues
- Improved confidence for Windows/macOS users
- Better shell script portability

---

### Automated Baseline Review ✅

**What:** New `check_baseline_age.py` script automates baseline staleness checking.

**Why:** Prevents outdated baselines from being used for release decisions without review.

**Changes:**
- Added `.language-eval/scripts/check_baseline_age.py`
- Configurable warning/error thresholds (default: 90/180 days)
- Supports multiple baselines in one invocation
- Test-friendly with `--today` override

**Usage:**
```bash
# Check all baselines with default thresholds (90/180 days)
python .language-eval/scripts/check_baseline_age.py \
  .language-eval/baselines/*.json

# Custom thresholds
python .language-eval/scripts/check_baseline_age.py \
  --warning-days 60 \
  --error-days 120 \
  .language-eval/baselines/baseline.example.json

# Fail on warnings (for CI enforcement)
python .language-eval/scripts/check_baseline_age.py \
  --fail-on-warning \
  .language-eval/baselines/*.json
```

**Exit Codes:**
- `0`: All baselines fresh
- `1`: Some baselines need review (warning threshold)
- `2`: Some baselines critically stale (error threshold)

**Benefits:**
- Automated quarterly baseline review
- Clear visibility into baseline age
- Prevents "set it and forget it" anti-pattern

---

### Suite Timeout Enforcement ✅

**What:** Added configurable per-suite timeout to prevent hanging executions.

**Why:** Protects CI pipeline from slow or stuck suite executions.

**Changes:**
- Added `--timeout` flag to `run_suite.sh` (default: 600s)
- Added `--timeout` flag to `run_all.sh`
- Timeout value recorded in suite config metadata
- Clear error message on timeout: "Suite execution timed out after N seconds"

**Usage:**
```bash
# Set global timeout for all suites
./.language-eval/scripts/run_all.sh \
  --target <target> \
  --timeout 300  # 5 minutes per suite

# Disable timeout (use with caution)
./.language-eval/scripts/run_all.sh \
  --target <target> \
  --timeout 0
```

**Default Timeouts by Suite:**
- Conformance: 600s (10 min)
- Security: 600s (10 min)
- Performance: 600s (10 min)
- Tooling: 600s (10 min)
- Human Factors: 600s (10 min)

**Benefits:**
- Prevents CI hangs
- Forces suite implementations to be performant
- Clear failure signals for debugging

---

### Parallel Suite Execution ✅

**What:** Added `--jobs` flag for concurrent suite execution.

**Why:** Reduces total evaluation time when suites are independent.

**Changes:**
- Added `--jobs` flag to `run_all.sh` (default: 1 = sequential)
- Implemented background job management with semaphore-like control
- Waits for all jobs to complete before proceeding to normalization
- Compatible with `--timeout` for safe parallel execution

**Usage:**
```bash
# Run 3 suites concurrently
./.language-eval/scripts/run_all.sh \
  --target <target> \
  --jobs 3

# Combine with timeout for safety
./.language-eval/scripts/run_all.sh \
  --target <target> \
  --jobs 3 \
  --timeout 300
```

**Implementation Details:**
- Uses Bash background jobs (`&`) and `wait -n`
- Tracks active job count to enforce `--jobs` limit
- Portable across Linux/macOS/WSL
- No external dependencies (GNU parallel not required)

**Performance Impact:**
| Scenario | Sequential (--jobs 1) | Parallel (--jobs 3) | Speedup |
|----------|----------------------|---------------------|---------|
| 3 suites @ 1min each | 3 minutes | ~1 minute | 3x |
| 5 suites @ 1min each | 5 minutes | ~2 minutes | 2.5x |

**Benefits:**
- Faster CI feedback
- Better resource utilization
- Scales with suite count

---

### Updated Documentation ✅

**What:** Enhanced README with new features and best practices.

**Changes:**
- Documented `--timeout` and `--jobs` flags
- Added "Performance Optimization" section
- Added "Baseline Management" section with age checking examples
- Updated quick workflow examples

**New Sections:**
- **Baseline Management:** How to check baseline age
- **Performance Optimization:** Parallel execution and timeout best practices

---

## Testing Coverage ✅

**New Tests:**

1. `test_check_baseline_age.py` (8 tests):
   - Fresh baseline detection
   - Warning threshold enforcement
   - Error threshold enforcement
   - Custom threshold configuration
   - Missing timestamp handling
   - ISO datetime format parsing
   - `--fail-on-warning` flag behavior

**Test Execution:**
```bash
pytest tests/language_eval/test_check_baseline_age.py -v
```

---

## Migration Guide

### For Existing Users

**No breaking changes.** All new features are backward-compatible:

- Default `--timeout` is 600s (same as previous hardcoded value)
- Default `--jobs` is 1 (sequential execution, current behavior)
- Baseline age checking is optional

**Recommended Actions:**

1. **Add baseline age checks to CI:**
   ```yaml
   - name: Check baseline age
     run: |
       python .language-eval/scripts/check_baseline_age.py \
         .language-eval/baselines/*.json
   ```

2. **Enable parallel execution for faster local runs:**
   ```bash
   # In your local workflow
   ./.language-eval/scripts/run_all.sh --target <target> --jobs 3
   ```

3. **Set tighter timeouts for CI:**
   ```bash
   # In CI workflow
   ./.language-eval/scripts/run_all.sh --target <target> --timeout 300
   ```

### For CI/CD Pipelines

**GitHub Actions:** No changes required. Workflows will continue to work with sequential execution.

**Optional Optimizations:**
```yaml
- name: Run language eval with parallel execution
  run: |
    ./.language-eval/scripts/run_all.sh \
      --target .language-eval/targets/example-target.yaml \
      --jobs 3 \
      --timeout 300 \
      --fast
```

---

## Future Enhancements (Deferred)

The following items from the review are deferred to future iterations:

1. **Real Suite Workloads** — Requires test fixture development
2. **Empirical Formula Validation** — Requires reference language datasets
3. **Reference Baseline Publication** — Requires production baseline establishment
4. **Advanced Reporting** — Requires charting library integration

See `RELEASE_READINESS.md` for production criteria.

---

## Credits

Improvements implemented based on comprehensive Microsoft-grade code review (EXTENSIVE_MICROSOFT_REVIEW_PR29.md).

**Implemented by:** AI Engineering Agent  
**Review Date:** February 20, 2026  
**Implementation Date:** February 20, 2026
