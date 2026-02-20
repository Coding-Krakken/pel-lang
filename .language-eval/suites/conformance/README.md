# Conformance Suite

## What this suite measures

- Parser + AST behavior consistency
- Type error and diagnostic golden tests
- Stdlib behavior conformance hooks
- Cross-implementation consistency hooks (when multiple implementations exist)

## Output contract

Suite runner must emit JSON to `<outdir>/suite.conformance.json`:

- `suite`: `conformance`
- `status`: `pass|fail`
- `metrics.pass_rate`
- `metrics.total_tests`
- `metrics.failed_tests`
- `artifacts.log`
- `artifacts.expected_failures_file`

## Expected failures

Known misses live in `expected_failures.yaml`. Each entry needs reason, owner, introduced date, and expiry date.

## How to add a workload

1. Add test fixtures under project conformance tests.
2. Add invocation hook in `scripts/run_suite.sh` if needed.
3. Ensure failures are represented in canonical fields.
4. Update `expected_failures.yaml` only when justified.
