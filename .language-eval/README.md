# Language Evaluation Framework

This framework provides a repeatable way to evaluate a language implementation (compiler/runtime/tooling version) across correctness, security, performance, developer experience, interoperability, and long-term governance risk.

## What this is

`.language-eval/` defines:

- A metric taxonomy and scoring rubric
- Suite contracts for conformance, security, performance, tooling, and human factors
- A canonical results model (`results.raw.json`, `results.normalized.json`, `scorecard.json`, `report.json`)
- CI gates for schema validity, artifact completeness, determinism, and regression thresholds

## Add a target language

1. Copy `.language-eval/targets/example-target.yaml`.
2. Fill in language/runtime metadata and commands.
3. Select enabled suites and required suites.
4. Choose a weight profile (`systems`, `web_backend`, `scripting`, `embedded`, `data_ml`) or use target overrides.
5. Point to a baseline file in `.language-eval/baselines/`.

## Run locally

```bash
./.language-eval/scripts/run_all.sh --target .language-eval/targets/example-target.yaml
```

Useful flags:

- `--outdir <path>` custom output location
- `--repeat <n>` benchmark repetitions (default: 5)
- `--warmup <n>` warmup runs (default: 1)
- `--timeout <n>` per-suite timeout in seconds (default: 600, 0 = no timeout)
- `--jobs <n>` number of parallel suite jobs (default: 1 = sequential)
- `--fast` run fast subset (`conformance`, `security`, `tooling`)

Optional behavior:

- Set `LANG_EVAL_EXECUTE_TARGET_COMMANDS=1` to execute `commands.<suite>` from target config during suite runs.
- Default behavior remains scaffold-mode metrics emission for portability.

Outputs are written under `.language-eval/reports/<timestamp>/`.

## CI gates

CI validates:

- Target config against `target.schema.json`
- Raw/normalized/report outputs against schemas
- Presence of all required suite outputs
- No regressions beyond configured tolerance against baseline (scoped to categories covered by executed suites)
- Deterministic `report.json` hash across two equivalent runs

## Baseline management

Check baseline age to ensure baselines remain relevant:

```bash
# Check if baselines are stale (warns at 90 days, errors at 180 days)
python .language-eval/scripts/check_baseline_age.py \
  .language-eval/baselines/*.json

# Custom thresholds
python .language-eval/scripts/check_baseline_age.py \
  --warning-days 60 \
  --error-days 120 \
  .language-eval/baselines/baseline.example.json
```

See [BASELINE_MANAGEMENT.md](BASELINE_MANAGEMENT.md) for full baseline lifecycle documentation.

## Interpret reports

- `results.raw.json`: per-suite raw measurements
- `results.normalized.json`: canonical metric structure
- `scorecard.json`: weighted category scores (0.0–5.0) + overall score
- `report.json`: machine-readable release artifact
- `report.md`: human-readable report
- `summary.md`: PR-friendly short summary

## Quick workflow

```bash
# 1) Run all suites (with parallel execution for speed)
./.language-eval/scripts/run_all.sh \
  --target .language-eval/targets/example-target.yaml \
  --jobs 3 \
  --timeout 300

# 2) Compare with baseline
python .language-eval/scripts/compare_baseline.py \
  --target .language-eval/targets/example-target.yaml \
  --current .language-eval/reports/<timestamp>/results.normalized.json \
  --scorecard .language-eval/reports/<timestamp>/scorecard.json \
  --out .language-eval/reports/<timestamp>/comparison.json

# 3) Apply CI gate locally
python .language-eval/scripts/ci_gate.py \
  --target .language-eval/targets/example-target.yaml \
  --report-dir .language-eval/reports/<timestamp>

# 4) Determinism-only compare gate (recommended for fast-mode reruns)
python .language-eval/scripts/ci_gate.py \
  --target .language-eval/targets/example-target.yaml \
  --report-dir .language-eval/reports/<timestamp_a> \
  --compare-report-dir .language-eval/reports/<timestamp_b> \
  --determinism-only
```

## Performance optimization

**Parallel execution:** Use `--jobs N` to run multiple suites concurrently:
```bash
# Run 3 suites in parallel (reduces total execution time)
./.language-eval/scripts/run_all.sh --target <target> --jobs 3
```

**Timeouts:** Prevent slow suites from blocking CI:
```bash
# Each suite must complete within 300 seconds
./.language-eval/scripts/run_all.sh --target <target> --timeout 300
```