# Security Suite

## What this suite measures

- Supply-chain posture (lockfiles, pinning policy)
- Unsafe feature inventory completeness
- Optional SAST/dependency scanner integration
- Secure-defaults checklist coverage

## Output contract

Emit `<outdir>/suite.security.json` with:

- `suite`: `security`
- `status`: `pass|fail|skip`
- `metrics.policy_pass_rate`
- `metrics.critical_findings`
- `metrics.high_findings`
- `metrics.lockfile_present`
- `artifacts.log`
- `artifacts.policies`

## Performance Targets (SLA)

| Milestone | Target Time | Notes |
|-----------|------------|-------|
| Policy check only | < 1 minute | Fast path for CI |
| With SAST scan | 5-10 minutes | Optional deep scan |
| Full suite (policies + SAST + deps) | < 15 minutes | Release validation |
| Timeout | 20 minutes | Hard limit |

**Memory:** < 200 MB peak RSS (SAST may require more; document tool requirements)

## How to add checks

1. Add policy markdown under `policies/`.
2. Wire check logic in `run_suite.sh` security branch.
3. Ensure results map to canonical schema.
