# Tooling Suite

## What this suite measures

- Formatter idempotence
- LSP latency/correctness hooks
- Linter false-positive sanity checks

## Output contract

Emit `<outdir>/suite.tooling.json` with:

- `suite`: `tooling`
- `status`: `pass|fail|skip`
- `metrics.formatter_idempotence_rate`
- `metrics.lsp_p95_ms`
- `metrics.lsp_correctness_rate`
- `metrics.linter_false_positive_rate`
- `artifacts.log`

## Performance Targets (SLA)

| Tool | Target Time | Notes |
|------|------------|-------|
| Formatter (idempotence test) | < 2 minutes | 2x format over ~100 files |
| LSP server startup | < 5 seconds | Per language session |
| LSP completion (one call) | < 250 ms p95 | Performance target |
| LSP symbol navigation (10 calls) | < 2 seconds | Batch responsiveness |
| Linter scan (1000 files) | < 30 seconds | Standard corpus |
| Full suite | < 5 minutes | All tools together |
| Timeout | 10 minutes | Hard limit |

**Memory:** 
- Formatter: < 100 MB
- LSP server: < 500 MB
- Linter: < 200 MB

## Critical Failure Modes

- **Formatter non-idempotent:** FAIL suite (binary failure; indicates bug)
- **LSP missing:** SKIP LSP metrics
- **Linter not found:** SKIP linter metrics
- **Timeouts >10min:** FAIL suite

## How to add checks

1. Add docs in `lsp/` or `formatter/`.
2. Add executable check in `run_suite.sh tooling` branch.
3. Normalize into canonical metrics.
