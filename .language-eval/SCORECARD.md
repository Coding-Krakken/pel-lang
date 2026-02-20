# Scorecard Rubric

Scoring scale for each category: **0–5**.

- **0** = missing or nonfunctional
- **1** = ad-hoc / severe gaps
- **2** = partial / high risk
- **3** = acceptable baseline
- **4** = strong
- **5** = best-in-class

Required artifacts across categories:

- Suite logs (`*.log`)
- Canonical metrics in `results.normalized.json`
- Final scored output `scorecard.json`
- Summary + report (`summary.md`, `report.md`, `report.json`)

## Correctness & Semantics
- **Metric definition:** parser/typechecker/runtime conformance to language spec and expected diagnostics.
- **Measurement method:** conformance suite pass rate minus justified `expected_failures`.
- **Pass/fail thresholds:** pass if >= 95% adjusted pass rate and no critical semantic mismatch.
- **Scoring (0–5):** 0 (<50%), 1 (50–69%), 2 (70–84%), 3 (85–94%), 4 (95–98%), 5 (>=99%).
- **Required artifacts:** conformance logs, expected-failure ledger, pass-rate metrics.

## Security Properties
- **Metric definition:** secure defaults, supply-chain hygiene, unsafe feature visibility.
- **Measurement method:** lockfile/pin checks, unsafe feature inventory completeness, optional SAST/depscan findings.
- **Pass/fail thresholds:** fail if critical unmitigated finding or no dependency pinning policy.
- **Scoring (0–5):** weighted by policy pass ratio and unresolved severity distribution.
- **Required artifacts:** policy checks, vulnerability summary, unsafe inventory.

## Runtime Performance
- **Metric definition:** latency, throughput, memory footprint, startup overhead.
- **Measurement method:** micro + macro + real-world workloads; compute p50/p95/p99 and RSS.
- **Pass/fail thresholds:** fail if p95 or RSS regresses beyond tolerance.
- **Scoring (0–5):** score by normalized baseline ratio and tail-latency stability.
- **Required artifacts:** latency histogram, percentile table, memory + startup metrics.

## Compiler/Toolchain Performance
- **Metric definition:** compile/transpile/build time and incremental rebuild cost.
- **Measurement method:** repeated build timing on controlled workload.
- **Pass/fail thresholds:** fail on > configured slowdown versus baseline.
- **Scoring (0–5):** normalized speedup/slowdown mapping with repeatability confidence.
- **Required artifacts:** timing samples, variance stats, environment manifest.

## Reliability
- **Metric definition:** flake resistance, deterministic outputs, crash/error rates.
- **Measurement method:** repeated suite runs + report hash checks.
- **Pass/fail thresholds:** fail on nondeterministic report hashes or unhandled crashes.
- **Scoring (0–5):** derived from deterministic run ratio and error incidence.
- **Required artifacts:** run manifests, hash comparison, failure taxonomy.

## DX/Productivity
- **Metric definition:** developer friction for common tasks.
- **Measurement method:** scripted task timing + human-factors checklists.
- **Pass/fail thresholds:** fail if critical workflow lacks docs/automation.
- **Scoring (0–5):** blended from task completion success, median time, and docs coverage.
- **Required artifacts:** task checklists, timings, study notes.

## Tooling/Static Analysis
- **Metric definition:** formatter/linter/LSP quality and responsiveness.
- **Measurement method:** formatter idempotence, LSP latency hooks, linter sanity checks.
- **Pass/fail thresholds:** fail if formatter non-idempotent or LSP hooks absent.
- **Scoring (0–5):** weighted average of tooling metrics.
- **Required artifacts:** idempotence logs, latency samples, false-positive checks.

## Interop/Integration
- **Metric definition:** packaging, API boundaries, foreign-system integration readiness.
- **Measurement method:** contract checks and integration smoke tests.
- **Pass/fail thresholds:** fail if required integration path is broken.
- **Scoring (0–5):** based on successful integration matrix coverage.
- **Required artifacts:** smoke logs, compatibility matrix, dependency manifest.

## Portability/Deployment
- **Metric definition:** platform coverage and deployment repeatability.
- **Measurement method:** run suites on target OS/arch matrix where available.
- **Pass/fail thresholds:** fail if declared supported platform is red.
- **Scoring (0–5):** support matrix completeness and reproducibility confidence.
- **Required artifacts:** platform matrix report and reproducibility notes.

## Concurrency Model
- **Metric definition:** correctness and performance under parallelism/async load.
- **Measurement method:** representative concurrent workloads and race-safety checks.
- **Pass/fail thresholds:** fail on deadlock/data race in standard scenarios.
- **Scoring (0–5):** safety + scalability blend.
- **Required artifacts:** workload traces, race/deadlock findings.

## Large-Codebase Fitness
- **Metric definition:** maintainability at scale (build, navigation, refactor viability).
- **Measurement method:** large-project compile/lint/index timings + memory behavior.
- **Pass/fail thresholds:** fail if core operations exceed target SLA or crash.
- **Scoring (0–5):** normalized against baseline SLOs.
- **Required artifacts:** timing profiles, memory usage, indexing logs.

## Ecosystem Health
- **Metric definition:** package maturity, maintenance activity, quality signals.
- **Measurement method:** curated indicators (release cadence, issue latency, dependency trust).
- **Pass/fail thresholds:** fail if ecosystem risk score exceeds policy cap.
- **Scoring (0–5):** policy-based weighted indicator score.
- **Required artifacts:** ecosystem snapshot and indicator inputs.

## Governance & Long-Term Risk
- **Metric definition:** bus factor, roadmap credibility, licensing/governance clarity.
- **Measurement method:** governance checklist and documented risk register.
- **Pass/fail thresholds:** fail if license/governance is unclear for production usage.
- **Scoring (0–5):** checklist completeness + risk severity adjustments.
- **Required artifacts:** governance review, risk log, ownership model notes.
