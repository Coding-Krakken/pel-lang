# PR-21: Formatter and Linter Implementation - Microsoft-Grade Review

**Reviewer:** GitHub Copilot  
**Review Date:** February 18, 2026  
**PR Branch:** `feature/formatter-linter`  
**Target Branch:** `main`  
**PR Status:** OPEN  

---

## Executive Summary

PR-21 implements a code formatter (`pelformat`) and linter (`pellint`) for the PEL programming language. The implementation demonstrates **solid engineering fundamentals** with functional formatter and linter capabilities, CLI integration, and configuration support. However, there are **significant gaps** between the PR description's ambitious scope and the actual deliverables, particularly around testing, CI integration, and git hooks.

### Overall Assessment: **APPROVE WITH CONDITIONS** ✅⚠️

**Strengths:**
- ✅ Working formatter and linter implementations (~1,330 LOC)
- ✅ Clean architecture with proper separation of concerns
- ✅ CLI integration with multiple entry points (`pel format`, `pel lint`, `pelformat`, `pellint`)
- ✅ Configuration system with `.pelformat.toml` and `.pellint.toml`
- ✅ 6 lint rules implemented (PEL001, PEL002, PEL004, PEL005, PEL008, PEL010)
- ✅ JSON and text output formats for linter
- ✅ Smoke tests pass (formatter and linter work on actual PEL files)

**Critical Gaps:**
- ❌ **ZERO test coverage** for formatter and linter modules (0%)
- ❌ **NO CI integration** for format checking or linting in GitHub Actions
- ❌ **NO pre-commit hooks** implemented (`.pre-commit-hooks.yaml` missing)
- ❌ **NO LSP integration** despite VS Code references in README
- ❌ **NO performance benchmarks** (PR claims <50ms formatter, <200ms linter)
- ⚠️ **Unrelated scope creep** (LSP server and VS Code extension deleted)

---

## 1. Architecture & Design Quality

### 1.1 Module Structure ✅ **EXCELLENT**

The implementation follows clean architecture principles:

```
formatter/
├── __init__.py           # Clean public API exports
├── config.py            # Configuration loader with TOML support
├── formatter.py         # Core formatter implementation
└── README.md            # User documentation

linter/
├── __init__.py          # Clean public API exports  
├── config.py            # Configuration loader with TOML support
├── linter.py            # Core linter engine
├── reporter.py          # Output formatters (text, JSON)
├── rules.py             # Lint rule implementations (432 LOC)
├── types.py             # Shared types (LintViolation, LintContext)
└── README.md            # User documentation

pel_cli/
├── __init__.py
└── main.py              # Unified CLI entry point (342 LOC)
```

**Strengths:**
- Clear separation of concerns (config, core logic, rules, reporting)
- Proper use of dataclasses for structured data
- Type hints throughout (`from __future__ import annotations`)
- Logging infrastructure in place

**Design Pattern Analysis:**
- **Formatter:** Uses regex-based transformation + AST validation (hybrid approach)
- **Linter:** Classic visitor pattern for AST traversal with rule registry
- **CLI:** Clean subcommand architecture with argparse

### 1.2 API Design ✅ **GOOD**

```python
# Formatter API
formatter = PELFormatter(line_length=100, indent_size=4)
result = formatter.format_string(source)  # Returns FormatResult
result = formatter.format_file("model.pel", in_place=True)

# Linter API  
linter = PELLinter(config=LinterConfig())
violations = linter.lint_string(source)  # Returns list[LintViolation]
violations = linter.lint_file("model.pel")
```

**Observations:**
- ✅ Simple, predictable APIs
- ✅ Immutable result objects (`FormatResult`, `LintViolation`)
- ✅ Consistent parameter naming across modules
- ⚠️ No async support (acceptable for CLI tools, but limits LSP integration)

### 1.3 Configuration System ✅ **GOOD**

Both tools support TOML configuration with sensible defaults:

```toml
# .pelformat.toml
[format]
line_length = 100
indent_size = 4
max_blank_lines = 2
ensure_final_newline = true

# .pellint.toml
[linter]
enabled_rules = ["PEL001", "PEL002", "PEL004", "PEL005", "PEL008", "PEL010"]
line_length = 100

[rules.PEL010]
severity = "info"
```

**Strengths:**
- ✅ Config files are discovered by walking up directory tree
- ✅ Command-line overrides supported (`--line-length`, `--indent-size`)
- ✅ Graceful fallback when config files missing
- ✅ Handles both `tomllib` (Python 3.11+) and `tomli` (backport)

---

## 2. Code Quality & Implementation

### 2.1 Formatter Implementation ✅ **SOLID**

**File:** [formatter/formatter.py](formatter/formatter.py) (194 LOC)

**Approach:** Hybrid regex + AST validation
1. Split lines into code and comments (string-aware)
2. Apply spacing/operator rules via regex
3. Track brace nesting for indentation
4. Validate syntax with parser (optional)
5. Return formatted code with change detection

**Key Functions:**
```python
def _split_comment(line: str) -> tuple[str, str | None]
    """String-aware comment detection."""
    
def _format_code_segment(code: str) -> str
    """Apply spacing rules via regex substitutions."""
    
def _brace_delta(code: str) -> int
    """Calculate indentation change from braces."""
```

**Smart Details:**
- ✅ Preserves strings during formatting (extraction/restoration pattern)
- ✅ Handles escape sequences in strings correctly
- ✅ Comment preservation with position tracking
- ✅ Idempotency check via `changed` flag
- ✅ Graceful degradation on parse errors (returns original source)

**Potential Issues:**
- ⚠️ Regex-based approach may have edge cases with complex expressions
- ⚠️ No line-wrapping implementation (README claims "best-effort")
- ⚠️ Brace tracking doesn't account for braces in strings/comments (mitigated by `_strip_strings`)

**Manual Testing:**
```bash
$ python -m pel_cli.main format examples/simple_growth.pel --check
# Exit code 1 (changes needed) - correct behavior

$ python -m pel_cli.main lint examples/simple_growth.pel
examples/simple_growth.pel:11:2: WARNING PEL008 Trailing whitespace
examples/simple_growth.pel:33:7: WARNING PEL002 Variable 'profit' is never referenced
# Linter correctly detects violations
```

### 2.2 Linter Implementation ✅ **VERY GOOD**

**File:** [linter/linter.py](linter/linter.py) (75 LOC)  
**File:** [linter/rules.py](linter/rules.py) (432 LOC)

**Architecture:**
- Main linter engine loads enabled rules from config
- Each rule implements `LintRule.run(context) -> list[LintViolation]`
- Rules sorted by severity (error > warning > info) and location

**Implemented Rules:**

| Rule Code | Description | Severity | Implementation Quality |
|-----------|-------------|----------|------------------------|
| PEL001 | Unused parameter | warning | ✅ Complete - AST traversal with bound variable tracking |
| PEL002 | Unreferenced variable | warning | ✅ Complete - Similar to PEL001 |
| PEL004 | Type mismatch | error | ✅ Delegates to existing TypeChecker |
| PEL005 | Circular dependency | error | ✅ Complete - Proper cycle detection with DFS |
| PEL008 | Style violations | warning | ✅ Line length + trailing whitespace |
| PEL010 | Naming conventions | info | ✅ PascalCase models, snake_case params/vars |

**Code Quality Highlights:**

```python
def _collect_expression_uses(expr: Expression, uses: set[str], bound: set[str]) -> None:
    """Recursively collect variable references with proper scoping."""
    if isinstance(expr, Variable):
        if expr.name not in bound:  # Respects lambda/function scopes
            uses.add(expr.name)
    elif isinstance(expr, Lambda):
        lambda_bound = bound | {name for name, _ in expr.params}
        _collect_expression_uses(expr.body, uses, lambda_bound)
    # ... handles 15 expression types
```

**Strengths:**
- ✅ Comprehensive AST traversal handling all expression types
- ✅ Proper scope tracking for lambda/function parameters
- ✅ Circular dependency detection with clean DFS implementation
- ✅ Reuses existing TypeChecker (no duplication)
- ✅ Declaration location tracking from tokens

**Observations:**
- The rule implementations are production-quality
- Error messages include file, line, column, severity, and rule code
- JSON output is CI-friendly with structured data

### 2.3 CLI Integration ✅ **EXCELLENT**

**File:** [pel_cli/main.py](pel_cli/main.py) (342 LOC)

**Features:**
- ✅ Unified `pel` command with subcommands (compile, run, check, format, lint)
- ✅ Convenience entry points (`pelformat`, `pellint`) that auto-inject subcommand
- ✅ Stdin support for editor integration (`--stdin`)
- ✅ Diff mode for reviewing changes (`--diff`)
- ✅ Check mode for CI (`--check` exits 1 if formatting needed)
- ✅ Recursive directory formatting (`pel format src/`)

**Code Quality:**
```python
def _iter_pel_files(paths: Iterable[str]) -> list[Path]:
    """Recursively find .pel files in directories."""
    files: list[Path] = []
    for entry in paths:
        path = Path(entry)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.pel")))
        elif path.is_file():
            files.append(path)
    return files
```

**Smart Design:**
```python
# pyproject.toml
[project.scripts]
pel = "pel_cli.main:main"
pelformat = "pel_cli.main:main"  # Auto-injects "format" subcommand
pellint = "pel_cli.main:main"    # Auto-injects "lint" subcommand
```

This allows both:
```bash
pel format mymodel.pel
pelformat mymodel.pel  # Shortcut
```

---

## 3. Testing & Quality Assurance

### 3.1 Test Coverage ❌ **CRITICAL FAILURE**

**Current Coverage:** **0%** for formatter and linter modules

```bash
$ find tests -name "*format*" -o -name "*lint*"
tests/unit/test_errors_formatting.py  # Unrelated (error message formatting)
```

**Impact:**
- ❌ No unit tests for formatter logic
- ❌ No unit tests for lint rules
- ❌ No idempotency tests (Format(Format(x)) == Format(x))
- ❌ No edge case tests (empty files, syntax errors, comments)
- ❌ No configuration loading tests
- ❌ No CLI argument parsing tests
- ❌ No integration tests

**PR Description Claims:**
> Target: >90% coverage for `formatter/` and `linter/` modules

**Reality:** 0% coverage

### 3.2 CI Integration ❌ **NOT IMPLEMENTED**

Current CI workflow:
```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pytest tests/ -v --cov=compiler --cov=runtime --cov-report=term
```

**Missing:**
- ❌ `--cov=formatter --cov=linter` not added to coverage collection
- ❌ No `pel format --check` step before tests
- ❌ No `pel lint --severity error` gate
- ❌ No GitHub annotations from linter violations

**PR Description Claims:**
> CI Integration: `.github/workflows/lint.yml` - CI workflow for linting

**Reality:** No such file exists

### 3.3 Pre-commit Hooks ❌ **NOT IMPLEMENTED**

**PR Description Claims:**
> Git Hooks: `.pre-commit-hooks.yaml`, `hooks/pre-commit` template

**Reality:**
```bash
$ find . -name ".pre-commit-hooks.yaml"
# No results

$ find . -name "pre-commit"
# No results
```

**Impact:**
- Developers won't automatically format code before commits
- Linter violations can be committed without warning
- Manual enforcement required

### 3.4 Performance Benchmarks ❌ **NOT IMPLEMENTED**

**PR Description Claims:**
> Performance: Formatter < **50ms**, Linter < **200ms** (benchmark tests)

**Reality:**
```bash
$ find tests -name "*performance*" -o -name "*benchmark*"
# No results
```

**Informal Testing:**
Manual testing on [examples/simple_growth.pel](examples/simple_growth.pel) (36 lines) shows:
- Formatter: Instant (<10ms subjectively)
- Linter: Instant (<50ms subjectively)

**Recommendation:**
Add `pytest-benchmark` tests to validate claims.

---

## 4. Documentation Quality

### 4.1 User Documentation ✅ **GOOD**

**Formatter README:** [formatter/README.md](formatter/README.md)
- ✅ Clear status indicator (Available)
- ✅ Installation instructions
- ✅ Usage examples (CLI commands)
- ✅ Configuration example
- ✅ Limitations documented

**Linter README:** [linter/README.md](linter/README.md)
- ✅ Rule list with codes
- ✅ Usage examples
- ✅ Configuration example
- ✅ JSON output demonstrated

**Style Guide:** [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md)
- ⚠️ **TOO MINIMAL** - Only 18 lines
- Missing: Rationale for rules, complex examples, best practices
- Compare to: [Black's documentation](https://black.readthedocs.io/) (~50 pages)

### 4.2 Code Comments ✅ **ADEQUATE**

All files have:
- ✅ SPDX license headers
- ✅ Module-level docstrings
- ✅ Function docstrings for public APIs
- ⚠️ Minimal inline comments (implementation is self-documenting)

### 4.3 PR Description ⚠️ **MISLEADING**

The PR description is **exceptionally detailed** (292 lines) but contains significant misrepresentations:

**Overpromises:**
1. "20+ lint rules" → **6 rules implemented** (PEL001-PEL010, sparse)
2. "Pre-commit hooks" → **Not implemented**
3. "CI integration" → **Not implemented**
4. "VS Code integration" → **LSP deleted, not added**
5. "Comprehensive tests" → **Zero tests**
6. "Performance benchmarks" → **Not implemented**

**Accurate Claims:**
- ✅ Formatter and linter exist
- ✅ CLI commands work
- ✅ Configuration system implemented
- ✅ AST-based linting

---

## 5. Integration Concerns

### 5.1 Scope Creep ⚠️ **CONCERNING**

**Unrelated Deletions:**
```diff
 40 files changed, 4468 insertions(+), 5016 deletions(-)

Deleted:
- editors/vscode/ (entire VS Code extension)
- lsp/ (entire LSP server implementation)
- tests/lsp/ (LSP tests)
```

**Analysis:**
- The PR title is "Implement Formatter and Linter"
- **Why delete LSP server and VS Code extension?**
- This creates merge conflicts with other PRs (PR-20 LSP work)
- Violates single-responsibility principle for PRs

**Recommendation:**
These deletions should be in a separate cleanup PR with proper justification.

### 5.2 Dependencies ✅ **MINIMAL**

New dependencies (none beyond existing):
- Uses existing `compiler.lexer`, `compiler.parser`, `compiler.typechecker`
- Optional `tomllib` (stdlib in Python 3.11+) or `tomli` (PyPI)
- No heavyweight dependencies (good)

### 5.3 Breaking Changes ✅ **NONE**

- CLI changes are additive (new subcommands)
- Existing `pel compile`, `pel run`, `pel check` unchanged
- Formatter/linter are opt-in tools

---

## 6. Security & Reliability

### 6.1 Input Validation ✅ **GOOD**

```python
# formatter/formatter.py
if self.config.validate_syntax:
    try:
        Parser(tokens).parse()
    except Exception as exc:
        logger.warning("Skipping formatting due to parse error: %s", exc)
        return FormatResult(formatted=source, changed=False)
```

- ✅ Graceful handling of malformed input
- ✅ No arbitrary code execution
- ✅ File path validation via `Path` API

### 6.2 Error Handling ✅ **ADEQUATE**

```python
# linter/linter.py
model = None
try:
    model = Parser(tokens).parse()
except Exception as exc:
    logger.warning("Linting parse error: %s", exc)
```

- ✅ Continues linting with partial AST
- ✅ Logs errors without crashing
- ⚠️ Broad `except Exception` (acceptable for tools, not libraries)

### 6.3 Resource Limits ⚠️ **MISSING**

**Potential Issues:**
- No timeout for formatting large files
- No memory limits for recursive AST traversal
- Regex could be vulnerable to catastrophic backtracking

**Recommendation:**
Add resource limits for production use:
```python
import signal

def format_with_timeout(source: str, timeout: int = 5):
    signal.alarm(timeout)
    try:
        return formatter.format_string(source)
    finally:
        signal.alarm(0)
```

---

## 7. Comparison to Industry Standards

### 7.1 Formatter Comparison

| Feature | PEL Formatter | Black (Python) | Prettier (JS) |
|---------|---------------|----------------|---------------|
| Idempotent | ✅ Yes | ✅ Yes | ✅ Yes |
| Configurable | ⚠️ Limited | ❌ Minimal | ✅ Yes |
| Line wrapping | ❌ No | ✅ Yes | ✅ Yes |
| AST-based | ⚠️ Hybrid | ✅ Full | ✅ Full |
| Editor integration | ❌ No | ✅ LSP | ✅ LSP |
| Tests | ❌ None | ✅ 1000+ | ✅ 5000+ |

**Assessment:** Basic implementation, needs maturity.

### 7.2 Linter Comparison

| Feature | PEL Linter | Ruff (Python) | ESLint (JS) |
|---------|------------|---------------|-------------|
| Rule count | 6 | 800+ | 400+ |
| Auto-fix | ❌ No | ✅ Yes | ✅ Yes |
| Plugin system | ❌ No | ✅ Yes | ✅ Yes |
| Performance | Unknown | <10ms/KLOC | ~100ms/KLOC |
| Tests | ❌ None | ✅ 5000+ | ✅ 10000+ |

**Assessment:** Solid foundation, room for growth.

---

## 8. Critical Issues Requiring Resolution

### 8.1 Blocking Issues ❌

**Must be fixed before merge:**

1. **Add test coverage** (target: 80%+ minimum)
   ```bash
   tests/formatter/
   ├── test_formatter_basic.py      # Basic formatting cases
   ├── test_formatter_idempotent.py # Idempotency checks
   ├── test_formatter_config.py     # Configuration loading
   └── test_formatter_cli.py        # CLI argument parsing
   
   tests/linter/
   ├── test_rules_pel001.py         # Unused parameter
   ├── test_rules_pel002.py         # Unreferenced variable
   ├── test_rules_pel005.py         # Circular dependency
   └── test_linter_integration.py   # End-to-end
   ```

2. **Add CI integration**
   ```yaml
   # .github/workflows/ci.yml
   - name: Check code formatting
     run: pel format . --check
   
   - name: Run linter
     run: pel lint . --severity error
   
   - name: Collect coverage
     run: pytest --cov=compiler --cov=runtime --cov=formatter --cov=linter
   ```

3. **Remove unrelated deletions**
   - Revert deletion of `editors/vscode/`, `lsp/`, `tests/lsp/`
   - Create separate cleanup PR if deletion is intentional

### 8.2 High-Priority Issues ⚠️

**Should be addressed before merge:**

4. **Add pre-commit hooks**
   ```yaml
   # .pre-commit-hooks.yaml
   - id: pelformat
     name: PEL Formatter
     entry: pelformat
     language: python
     types: [file]
     files: \.pel$
   ```

5. **Improve documentation**
   - Expand [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md) with examples and rationale
   - Add troubleshooting section to READMEs
   - Document limitations clearly

6. **Update PR description**
   - Mark unimplemented items as "TODO" or "Future work"
   - Accurately reflect current state

### 8.3 Nice-to-Have Improvements 💡

**Recommended for future PRs:**

7. **Performance benchmarks**
   ```python
   @pytest.mark.benchmark
   def test_formatter_performance(benchmark):
       result = benchmark(formatter.format_string, large_source)
       assert benchmark.stats.median < 0.050  # 50ms
   ```

8. **LSP integration**
   - Implement `textDocument/formatting` using `pel format --stdin`
   - Implement `textDocument/publishDiagnostics` using `pel lint --json`

9. **Auto-fix support**
   ```python
   class UnusedParamRule(LintRule):
       def auto_fix(self, violation: LintViolation) -> str:
           # Remove unused parameter
           ...
   ```

---

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Formatter corrupts code** | Low | Critical | ✅ Validates syntax before/after |
| **Regex edge cases** | Medium | Medium | ⚠️ Add comprehensive tests |
| **Performance regression** | Low | Low | ⚠️ Add benchmark tests |
| **False positive lint violations** | Low | Low | ✅ Severity configurable |

### 9.2 Process Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Merge conflicts with PR-20** | High | High | ❌ Revert LSP deletions |
| **Zero test coverage** | High | Critical | ❌ Add tests before merge |
| **CI doesn't enforce formatting** | High | Medium | ❌ Add CI steps |
| **Developers bypass tools** | Medium | Medium | ⚠️ Add pre-commit hooks |

---

## 10. Final Recommendation

### 10.1 Approval Status: **CONDITIONAL APPROVE** ✅⚠️

**Code Quality:** ⭐⭐⭐⭐ (4/5 stars)
- Implementation is solid and production-quality
- Architecture is clean and extensible
- CLI integration is excellent

**Completeness:** ⭐⭐ (2/5 stars)
- Many PR description promises unmet
- Zero test coverage is unacceptable
- Missing critical infrastructure (CI, hooks)

**Overall:** ⭐⭐⭐ (3/5 stars)

### 10.2 Conditions for Merge

**Must Complete (Blocking):**
1. ✅ Add test suite with 80%+ coverage for formatter and linter
2. ✅ Update CI to run `pel format --check` and `pel lint`
3. ✅ Revert unrelated deletions (LSP server, VS Code extension)

**Should Complete (Highly Recommended):**
4. ✅ Add `.pre-commit-hooks.yaml` and installation docs
5. ✅ Expand [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md) with rationale and examples
6. ✅ Update PR description to reflect actual state (not aspirational)

**Optional (Future Work):**
7. Performance benchmarks
8. LSP integration for formatter/linter
9. Auto-fix support for select lint rules

### 10.3 Estimated Effort to Complete

| Task | Estimate | Priority |
|------|----------|----------|
| Add test suite | 2-3 days | P0 |
| Update CI | 2 hours | P0 |
| Revert deletions | 1 hour | P0 |
| Pre-commit hooks | 4 hours | P1 |
| Documentation improvements | 4 hours | P1 |
| Update PR description | 1 hour | P1 |

**Total:** ~3-4 days of additional work

---

## 11. Positive Highlights

Despite the gaps, this PR has significant strengths:

1. **Clean Architecture** ✅
   - Proper separation of concerns
   - Type-safe implementation
   - Extensible rule system

2. **Production-Quality Code** ✅
   - Comprehensive AST traversal
   - Proper scope tracking in linter
   - Smart string/comment handling in formatter

3. **User Experience** ✅
   - Intuitive CLI commands
   - Helpful error messages
   - Configurable behavior

4. **Integration Patterns** ✅
   - Stdin/stdout support for editor integration
   - JSON output for CI tooling
   - Configuration file discovery

---

## 12. Conclusion

PR-21 delivers **high-quality implementations** of a formatter and linter for PEL, but suffers from **incomplete infrastructure and testing**. The code itself is production-ready, but the **ecosystem around it** (tests, CI, hooks, documentation) needs completion.

**Recommendation:** Request changes to address blocking issues (tests, CI, scope cleanup), then approve. The core implementation is excellent and forms a solid foundation for PEL's developer tooling.

**Suggested Merge Strategy:**
1. Author addresses blocking issues
2. Re-review with focus on test coverage
3. Merge to `main`
4. Follow-up PRs for nice-to-haves

---

**Review Completed:** February 18, 2026  
**Reviewer:** GitHub Copilot (Claude Sonnet 4.5)  
**Review Type:** Microsoft-Grade Comprehensive Review
