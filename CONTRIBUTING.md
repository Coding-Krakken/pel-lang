# Contributing to PEL

Thank you for your interest in contributing to PEL (Programmable Economic Language)! This document provides guidelines for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Specification Change Process (PEPs)](#specification-change-process-peps)
5. [Code Contribution Guidelines](#code-contribution-guidelines)
6. [Testing Requirements](#testing-requirements)
7. [Documentation Standards](#documentation-standards)
8. [Conformance Requirements for Runtime Implementers](#conformance-requirements-for-runtime-implementers)
9. [Community](#community)

---

## Code of Conduct

### Our Pledge

PEL is committed to providing a welcoming and harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Violations can be reported to [conduct@pel-lang.org](mailto:conduct@pel-lang.org). All complaints will be reviewed and investigated promptly and fairly. Consequences may include temporary bans or permanent expulsion from the community.

---

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
1. Check existing issues to avoid duplicates
2. Verify the bug exists in the latest version
3. Collect the minimum reproducible example

**Bug report should include:**
- PEL version (`pel --version`)
- Operating system and version
- Complete error message and stack trace
- Minimal PEL code that reproduces the issue
- Expected vs actual behavior

**Submit bugs at:** [github.com/pel-lang/pel/issues/new?template=bug_report.md](https://github.com/pel-lang/pel/issues/new?template=bug_report.md)

### Suggesting Enhancements

**Enhancement suggestions should include:**
- Clear use case description
- Why existing features don't solve the problem
- Proposed API or syntax (if applicable)
- Backward compatibility considerations
- Comparison to how other languages/tools solve this

**For major language changes:** Follow the PEP (PEL Enhancement Proposal) process (see below).

**Submit enhancements at:** [github.com/pel-lang/pel/issues/new?template=feature_request.md](https://github.com/pel-lang/pel/issues/new?template=feature_request.md)

### Contributing Models

The PEL community thrives on shared models!

**To contribute a model:**
1. Ensure it compiles without errors
2. Include comprehensive provenance metadata (source, confidence, etc.)
3. Add a README explaining the business archetype
4. Include test cases with expected outputs
5. Submit to [github.com/pel-lang/model-gallery](https://github.com/pel-lang/model-gallery)

**Model contribution checklist:**
- [ ] Compiles with latest PEL version
- [ ] All parameters have provenance metadata
- [ ] Assumption completeness score ≥ 90%
- [ ] README includes business context and usage examples
- [ ] Golden test results included
- [ ] License compatible with AGPL-3.0 (specify if different weighting)

### Improving Documentation

Documentation improvements are always welcome!

**Types of documentation contributions:**
- Fixing typos or unclear explanations
- Adding examples and tutorials
- Translating documentation
- Improving API documentation
- Creating video tutorials or blog posts

**Documentation style guide:**
- Use active voice
- Provide runnable examples
- Explain *why*, not just *what*
- Include common pitfalls and edge cases
- Link to relevant specification sections

---

## Development Setup

### Prerequisites

- **Python 3.10+** (reference implementation is in Python)
- **Git**
- **Make** (optional, for convenience scripts)

### Clone the Repository

```bash
git clone https://github.com/pel-lang/pel.git
cd pel
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install PEL in editable mode
pip install -e .
```

### Verify Installation

```bash
# Run compiler tests
pytest compiler/tests/

# Run runtime tests
pytest runtime/tests/

# Run full test suite
make test

# Check formatting
make fmt-check

# Run linter
make lint
```

### Development Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes, add tests

# Run tests
pytest

# Format code
make fmt

# Lint
make lint

# Commit with descriptive message
git commit -m "feat: Add support for X"

# Push and open pull request
git push origin feature/your-feature-name
```

---

## Specification Change Process (PEPs)

**PEP = PEL Enhancement Proposal**

### When to Write a PEP

PEPs are required for:
- New language syntax or semantics
- Changes to the type system
- New IR node types
- Changes to standard library APIs
- Changes to conformance requirements

PEPs are **not** required for:
- Bug fixes
- Documentation improvements
- Performance optimizations (without semantic changes)
- New standard library modules (if they follow existing patterns)

### PEP Lifecycle

```
Proposed → Under Discussion → Accepted → Implemented → Final
                ↓
            Rejected (with rationale)
```

### How to Submit a PEP

1. **Draft Your PEP**  
   Use the template: `/spec/pep_template.md`

2. **PEP Structure**
   - **Metadata:** PEP number (assigned by editors), title, authors, status
   - **Abstract:** 1-paragraph summary
   - **Motivation:** Why is this needed? What problem does it solve?
   - **Specification:** Precise technical description
   - **Rationale:** Design choices and alternatives considered
   - **Backward Compatibility:** Impact on existing models
   - **Reference Implementation:** Link to prototype or PR
   - **Examples:** Before/after code samples
   - **Open Issues:** Unresolved questions

3. **Submit for Discussion**  
   Open a pull request to `/spec/peps/pep-NNNN-title.md`

4. **Discussion Period**  
   Minimum 2 weeks. PEP may be revised based on feedback.

5. **Core Team Vote**  
   Requires 2/3 majority for acceptance.

6. **Implementation**  
   Once accepted, implementation can proceed. PEP status moves to "Implemented" when merged.

7. **Finalization**  
   When released in a stable version, PEP status moves to "Final."

### PEP Numbering

- **PEP 1-99:** Meta-PEPs (process, governance)
- **PEP 100-199:** Core language syntax and semantics
- **PEP 200-299:** Type system
- **PEP 300-399:** Standard library
- **PEP 400-499:** Tooling and ecosystem
- **PEP 500+:** Reserved for future categories

### Current PEPs

See [/spec/peps/README.md](/spec/peps/README.md) for list of all PEPs and their status.

---

## Code Contribution Guidelines

### Code Style

**Python (reference implementation):**
- Follow **PEP 8** with line length 100 (not 79)
- Use **type hints** for all function signatures
- Use **Black** for formatting (`make fmt`)
- Use **Ruff** for linting (`make lint`)

**File organization:**
```python
"""Module docstring explaining purpose."""

from __future__ import annotations

# Standard library imports
import sys
from typing import Any

# Third-party imports
import numpy as np

# Local imports
from pel.ast import Node
from pel.types import EconomicType


class MyClass:
    """Docstring explaining class."""
    
    def __init__(self, param: str) -> None:
        """Initialize with param."""
        self.param = param
    
    def method(self, arg: int) -> str:
        """
        Method docstring.
        
        Args:
            arg: Description of arg.
        
        Returns:
            Description of return value.
        
        Raises:
            ValueError: When arg is negative.
        """
        if arg < 0:
            raise ValueError("arg must be non-negative")
        return f"{self.param}_{arg}"
```

### Commit Message Format

Follow **Conventional Commits:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring without behavior change
- `perf`: Performance improvement
- `test`: Adding or fixing tests
- `chore`: Build process, tooling, dependencies

**Examples:**
```
feat(compiler): Add support for correlated distributions

Implements PEP-234 for correlation matrix syntax.
Uses Cholesky decomposition for sampling.

Closes #123
```

```
fix(runtime): Correct constraint violation detection

Previously, soft constraints were treated as fatal.
Now correctly records slack for soft constraints.

Fixes #456
```

### Pull Request Process

1. **One PR = One Logical Change**  
   Don't mix refactoring with new features.

2. **PR Description Must Include:**
   - What: Summary of changes
   - Why: Motivation and context
   - How: Technical approach (for non-trivial changes)
   - Testing: How you verified correctness
   - Backward compatibility: Any breaking changes?

3. **PR Checklist:**
   - [ ] Tests added/updated (coverage ≥ 90% for new code)
   - [ ] Documentation updated
   - [ ] Changelog entry added (for user-facing changes)
   - [ ] All CI checks passing
   - [ ] Reviewed by at least one core team member

4. **Review Process:**
   - Core team reviews within 3 business days
   - Feedback is constructive and focused on design/correctness
   - Requested changes must be addressed or discussed
   - Approved PRs are squash-merged by core team

---

## Testing Requirements

### Test Philosophy

PEL follows **property-based testing** where applicable:
- Determinism: Same input → same output
- Dimensional correctness: Type operations preserve units
- Constraint preservation: Violations always caught
- Idempotence: Format twice = format once

### Test Types

**1. Unit Tests**
- Test individual functions/classes in isolation
- Fast (<1ms per test)
- No external dependencies

**2. Integration Tests**
- Test compiler passes together (AST → IR → validation)
- Test runtime with stdlib modules
- Moderate speed (<100ms per test)

**3. End-to-End Tests**
- Full PEL model compilation and execution
- Test complete workflows
- Slower (< 5s per test)

**4. Property Tests**
- Use Hypothesis for random input generation
- Test invariants (e.g., "any valid model compiles without crashes")

**5. Golden Tests**
- Test against known-good reference outputs
- Detect unintended behavior changes
- Used extensively in stdlib

### Test Coverage

**Requirements:**
- New code: ≥ 90% coverage
- Critical paths (type checker, runtime engine): 100% coverage
- Overall project: ≥ 85% coverage

**Check coverage:**
```bash
pytest --cov=pel --cov-report=html
open htmlcov/index.html
```

### Test Naming

```python
def test_<what>_<condition>_<expected_result>():
    """Test that <what> does <expected> when <condition>."""
```

Examples:
```python
def test_typechecker_rejects_currency_rate_addition():
    """Test that adding Currency and Rate fails at compile time."""

def test_monte_carlo_preserves_correlation_within_tolerance():
    """Test that sampled correlation matches specified within 0.02."""
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest compiler/tests/test_typechecker.py

# Run tests matching pattern
pytest -k "correlation"

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=pel

# Run only fast tests (< 100ms)
pytest -m "not slow"

# Run in parallel (faster)
pytest -n auto
```

---

## Documentation Standards

### Documentation Types

**1. Specifications (`/spec`)**
- Formal, precise language
- Mathematical notation where appropriate
- Examples for each construct
- Non-goals explicitly stated

**2. API Documentation**
- Docstrings for all public functions/classes
- Google-style docstring format
- Type hints required

**3. Tutorials (`/docs/tutorials`)**
- Step-by-step, beginner-friendly
- Runnable code examples
- Explain "why" not just "how"

**4. How-To Guides (`/docs/howto`)**
- Task-oriented
- Assumes basic familiarity
- Multiple approaches when applicable

**5. Reference (`/docs/reference`)**
- Comprehensive, exhaustive
- Auto-generated from code where possible
- Organized by topic

### Writing Style

**DO:**
- Use active voice ("The compiler rejects..." not "The code is rejected...")
- Use present tense ("Returns X" not "Will return X")
- Be specific ("Must include source, method, confidence" not "Should have metadata")
- Provide examples
- Explain edge cases

**DON'T:**
- Use jargon without explanation
- Assume deep prior knowledge (unless in advanced sections)
- Write ambiguous requirements ("should", "might", "could" → specify exactly)

### Building Documentation

```bash
# Install docs dependencies
pip install -r docs/requirements.txt

# Build HTML docs
cd docs && make html

# Serve locally
python -m http.server --directory docs/_build/html

# Check for broken links
make linkcheck
```

---

## Conformance Requirements for Runtime Implementers

Want to build your own PEL runtime? Here's what's required.

### Conformance Levels

**Level 1: PEL Core**
- Parse PEL-IR (read JSON schema)
- Execute deterministic simulations
- Enforce type system (units, scope, time)
- Support basic stdlib modules

**Level 2: PEL Extended**
- Monte Carlo simulation with seeding
- Correlation preservation (Cholesky decomposition)
- Sensitivity analysis (tornado charts minimum)
- Full stdlib support

**Level 3: PEL Calibration**
- Data ingestion (CSV minimum)
- Parameter fitting (MLE minimum)
- Drift detection (K-S test minimum)

### Conformance Test Suite

**Location:** `/tests/conformance/`

**Test categories:**
1. **IR parsing:** Correctly parse all IR node types
2. **Type enforcement:** Reject invalid unit operations
3. **Determinism:** Bit-identical results with same seed
4. **Correlation:** Spearman ρ within 0.02 of target
5. **Stdlib golden:** Match reference outputs exactly

**Running conformance tests:**
```bash
# Against reference runtime (should pass 100%)
pytest tests/conformance/ --runtime=reference

# Against your runtime
pytest tests/conformance/ --runtime=your_runtime --runtime-path=/path/to/executable
```

### Certification Process

1. **Implement runtime** according to IR spec
2. **Pass conformance tests** (100% for desired level)
3. **Submit certification request**  
   Email: [conformance@pel-lang.org](mailto:conformance@pel-lang.org)  
   Include: Runtime name, version, conformance level, test results
4. **Core team review** (2 weeks)
5. **Certification issued** (valid for 1 year or until spec major version change)

**Certified runtimes listed at:** [pel-lang.org/runtimes](https://pel-lang.org/runtimes)

### Runtime Implementation Checklist

- [ ] IR parser (all node types)
- [ ] Type checker (units, scope, time)
- [ ] Deterministic engine
- [ ] Monte Carlo engine (if Level 2+)
- [ ] Correlation engine (if Level 2+)
- [ ] Stdlib modules (required subset)
- [ ] Run artifact generation (hash, seed, metadata)
- [ ] Conformance tests passing
- [ ] Documentation (API, usage)
- [ ] License compatible with ecosystem (AGPL-3.0 preferred)

---

## Community

### Communication Channels

**GitHub Discussions**  
For questions, proposals, and general discussion:  
[github.com/pel-lang/pel/discussions](https://github.com/pel-lang/pel/discussions)

**Discord**  
Real-time chat and community support:  
[discord.gg/pel-lang](https://discord.gg/pel-lang)  
Channels: #general, #help, #dev, #models, #papers

**Mailing List**  
Low-traffic announcements and RFC discussion:  
[groups.google.com/g/pel-lang](https://groups.google.com/g/pel-lang)

**Monthly Community Calls**  
First Tuesday of each month, 10am PT  
Video link posted in Discord and mailing list  
Meeting notes published to GitHub wiki

**Twitter/X**  
[@pel_lang](https://twitter.com/pel_lang)

### Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** (all contributors)
- **Release notes** (for significant contributions)
- **Annual community awards** (most impactful contributions)

### Licensing

PEL is dual-licensed under **AGPL-3.0-or-later** and a **Commercial License**. By contributing to PEL, you agree to the terms of the [Contributor License Agreement (CLA)](CLA.md).

**Important:** Before your first contribution, you must sign the CLA. See [CLA-SIGNING.md](CLA-SIGNING.md) for instructions.

#### Why a CLA?

The CLA allows us to:
- Maintain dual licensing (AGPL-3.0 for open source, Commercial for proprietary use)
- Accept your contributions legally
- Protect you, the project, and all users
- Sustain long-term project development

You retain copyright to your contributions, but grant us the right to distribute them under both licenses.

#### Signing the CLA

**First-time contributors:**
1. Read the [CLA.md](CLA.md) carefully
2. Follow the signing process in [CLA-SIGNING.md](CLA-SIGNING.md)
3. Send a signed CLA email to davidtraversmailbox@gmail.com
4. Wait for confirmation (usually 1-2 business days)
5. Your name will be added to [AUTHORS](AUTHORS)
6. You can then submit pull requests!

**Returning contributors:**
If you've already signed the CLA, you don't need to sign again. Just include "CLA signed on [date]" in your PR description.

#### License Headers

All source files must include the standard AGPL-3.0 header:

**Python files:**
```python
# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.
```

**PEL language files (.pel):**
```
// Copyright 2026 PEL Project Contributors
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// This file is part of PEL (Programmable Economic Language).
// PEL is dual-licensed under AGPL-3.0 and a commercial license.
// See LICENSE and COMMERCIAL-LICENSE.md for details.
```

**Markdown files:**
```markdown
<!--
Copyright 2026 PEL Project Contributors
SPDX-License-Identifier: AGPL-3.0-or-later

This file is part of PEL (Programmable Economic Language).
PEL is dual-licensed under AGPL-3.0 and a commercial license.
See LICENSE and COMMERCIAL-LICENSE.md for details.
-->
```

---

## Questions?

- **General questions:** [GitHub Discussions](https://github.com/pel-lang/pel/discussions)
- **Security vulnerabilities:** [security@pel-lang.org](mailto:security@pel-lang.org) (see SECURITY.md)
- **Code of conduct violations:** [conduct@pel-lang.org](mailto:conduct@pel-lang.org)
- **Media inquiries:** [press@pel-lang.org](mailto:press@pel-lang.org)

---

**Thank you for contributing to PEL!**

Together, we're building the future of economic modeling: executable, auditable, and trustworthy by design.
