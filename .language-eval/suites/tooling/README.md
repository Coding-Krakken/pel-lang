# Tooling Suite

## What this suite measures

- Formatter idempotence
- LSP latency/correctness hooks
- Linter false-positive sanity checks

## Output contract

Emit `<outdir>/suite.tooling.json` with:

- `suite`: `tooling`
- `status`: `pass|fail`
- `metrics.formatter_idempotence_rate`
- `metrics.lsp_p95_ms`
- `metrics.lsp_correctness_rate`
- `metrics.linter_false_positive_rate`
- `artifacts.log`

## How to add checks

1. Add docs in `lsp/` or `formatter/`.
2. Add executable check in `run_suite.sh tooling` branch.
3. Normalize into canonical metrics.
