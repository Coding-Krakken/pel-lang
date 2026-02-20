# Supply Chain Policy

Required checks:

- Lockfile exists where ecosystem expects one
- Direct dependencies are version-constrained
- High-risk dependencies are reviewed and documented
- Build/install path is reproducible in CI

Fail criteria:

- Missing required lockfile for selected target ecosystem
- Unbounded direct dependency specifications in production path
