# Conformance Suite

## What this suite measures

- Parser + AST behavior consistency
- Type error and diagnostic golden tests
- Stdlib behavior conformance hooks
- Cross-implementation consistency hooks (when multiple implementations exist)

## Output contract

Suite runner must emit JSON to `<outdir>/suite.conformance.json`:

- `suite`: `conformance`
- `status`: `pass|fail|skip`
- `metrics.pass_rate`
- `metrics.total_tests`
- `metrics.failed_tests`
- `artifacts.log`
- `artifacts.expected_failures_file`

## Performance Targets (SLA)

| Milestone | Target Time | Notes |
|-----------|------------|-------|
| Fast mode (50 tests) | < 30 seconds | PR validation |
| Standard (500 tests) | < 5 minutes | Standard CI |
| Full suite (2000+ tests) | < 15 minutes | Release validation |
| Timeout | 10 minutes | Hard limit; suite considered failed if exceeded |

**Memory:** < 500 MB peak RSS during execution

## Expected failures

Known misses live in `expected_failures.yaml`. Each entry needs reason, owner, introduced date, and expiry date.

**Maintenance:** Review expired entries quarterly; enforce via `ci_gate.py`.

## How to add a workload

1. Add test fixtures under project conformance tests.
2. Add invocation hook in `scripts/run_suite.sh` if needed.
3. Ensure failures are represented in canonical fields.
4. Update `expected_failures.yaml` only when justified.
