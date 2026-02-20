# Governance Model

## Purpose

Define controlled procedures for changing weights, workloads, expected failures, and baselines.

## Weight updates

- Default profile lives in `WEIGHTS.default.json`.
- Role-specific templates live under `WEIGHTS.templates/`.
- Any weight change must:
  - keep category sum at `1.0` (within floating tolerance),
  - include rationale in PR description,
  - include before/after score impact for at least one target.

## Add or modify workloads

- Add workload under the relevant suite `README.md` contract.
- Document input shape, command, and expected outputs.
- Include reproducibility notes (seed, dataset version, environment assumptions).
- Update schema and normalization logic if output structure changes.

## Expected failures policy

- Conformance exceptions go in `suites/conformance/expected_failures.yaml`.
- Every entry must include:
  - `id`
  - `reason`
  - `owner`
  - `introduced`
  - `expiry`
- CI should fail expired expected failures.

## Baseline changes

- Baselines are versioned JSON snapshots in `baselines/`.
- Baseline update must include:
  - target id + version,
  - environment fingerprint,
  - reason (e.g., intentional perf tradeoff),
  - explicit approval from maintainers.

## Gate threshold changes

- Thresholds are controlled per target in target config.
- Raising tolerance requires documented justification and a rollback plan.

## Ownership and review

- At least one maintainer for evaluation framework and one for target domain should review changes.
- CI gate policy changes require maintainer approval.
