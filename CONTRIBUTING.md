# Contributing to PEL

Thanks for contributing to PEL.

This guide is the canonical contributor workflow for this repository.

---

## Repository

- Source: https://github.com/Coding-Krakken/pel-lang
- Issues: https://github.com/Coding-Krakken/pel-lang/issues
- Discussions: https://github.com/Coding-Krakken/pel-lang/discussions

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Make (recommended)

### Install

```bash
git clone https://github.com/Coding-Krakken/pel-lang.git
cd pel-lang
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Before running `make` targets, ensure `.venv` is active in your current shell (`source .venv/bin/activate`) or prepend `PATH="$PWD/.venv/bin:$PATH"`.

---

## Common Commands

```bash
make format      # ruff format
make lint        # ruff check
make typecheck   # mypy
make security    # bandit
make test        # pytest
make coverage    # pytest + coverage html output
make ci          # full local CI sequence
```

---

## Pull Request Checklist

Before opening a PR:

- [ ] `make ci` passes locally
- [ ] New behavior has tests or explicit rationale for no test
- [ ] Documentation is updated for behavior, CLI, or workflow changes
- [ ] No unrelated refactors mixed into the PR
- [ ] PR description includes scope, risk, and validation steps

---

## Documentation Standards

When changing docs:

- Keep examples runnable against current repo commands
- Prefer repository-relative links for internal references
- Note deferred/removed features explicitly (avoid ambiguous “coming soon”)
- Keep tutorial content aligned with actual CLI behavior

---

## Test Organization (High Level)

- `tests/unit/` — component-level tests
- `tests/integration/` — cross-component workflows
- `tests/conformance/` — language/runtime conformance cases
- `tests/performance/` — performance-focused checks
- `tests/language_eval/` — language-eval framework tests

See [docs/TESTING.md](docs/TESTING.md) for full test guidance.

---

## Security and Compliance

- Report security issues via [SECURITY.md](SECURITY.md)
- Contribution terms: [CLA.md](CLA.md), [CLA-SIGNING.md](CLA-SIGNING.md)
- Licensing details: [LICENSE](LICENSE), [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)
