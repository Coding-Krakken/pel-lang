# Runtime Reliability Notes

This note documents runtime behavior introduced for PR-1 reliability work and how to troubleshoot common failures.

## Verification Commands

```bash
.venv-lint/bin/ruff check compiler/ runtime/ tests/
python -m pytest -q
python -m pytest tests/unit/test_runtime_more_branches.py -q
python benchmarks/score_benchmark.py --min-success-rate 90
```

## Constraint Behavior

- Constraints are evaluated in deterministic order per timestep using `(name, constraint_id)` sorting.
- `fatal` violations stop execution immediately and return `status: failed`.
- `warning` violations are recorded in `constraint_violations` and execution continues.

If results unexpectedly stop early, inspect:

- `reason`
- `timesteps_completed`
- the first `fatal` item in `constraint_violations`

## Correlation Sampling Behavior

Monte Carlo mode validates correlation input before sampling:

- Matrix must be square and symmetric.
- Diagonal entries must be `1.0`.
- All coefficients must be in `[-1, 1]`.
- Matrix must be positive semidefinite (checked via Cholesky decomposition).

Expected failure messages include:

- `Invalid correlation coefficient ...`
- `Conflicting correlation values ...`
- `Correlation matrix must be positive semidefinite`

## Expression Evaluation Notes

- String literals are preserved as strings during runtime evaluation.
- Numeric-like strings are still converted when applicable (for compatibility with legacy shapes).
- Unknown expression types continue to evaluate to `0` as a fallback.