# Security Suite

## What this suite measures

- Supply-chain posture (lockfiles, pinning policy)
- Unsafe feature inventory completeness
- Optional SAST/dependency scanner integration
- Secure-defaults checklist coverage

## Output contract

Emit `<outdir>/suite.security.json` with:

- `suite`: `security`
- `status`: `pass|fail`
- `metrics.policy_pass_rate`
- `metrics.critical_findings`
- `metrics.high_findings`
- `metrics.lockfile_present`
- `artifacts.log`
- `artifacts.policies`

## How to add checks

1. Add policy markdown under `policies/`.
2. Wire check logic in `run_suite.sh` security branch.
3. Ensure results map to canonical schema.
