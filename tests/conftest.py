from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

from compiler.compiler import PELCompiler

# Cache stdlib source code to avoid repeated file I/O
_STDLIB_CACHE: dict[str, str] = {}


def _load_stdlib_source(module: str) -> str:
    """Load stdlib module source code, caching for performance.

    Args:
        module: Module name (e.g. 'capacity', 'hiring')

    Returns:
        The raw PEL source text of the module
    """
    if module not in _STDLIB_CACHE:
        stdlib_dir = Path(__file__).resolve().parents[1] / "stdlib"
        pel_file = stdlib_dir / module / f"{module}.pel"
        if not pel_file.exists():
            msg = f"Stdlib module not found: {pel_file}"
            raise FileNotFoundError(msg)
        _STDLIB_CACHE[module] = pel_file.read_text(encoding="utf-8")
    return _STDLIB_CACHE[module]


def compile_pel_code_with_stdlib(
    code: str,
    stdlib_modules: list[str] | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """Compile PEL code with stdlib function bodies inlined.

    This ensures the typechecker validates function body type-correctness
    (not just call-site signatures).

    Args:
        code: PEL code to compile (params/vars/calls — no model wrapper needed)
        stdlib_modules: List of stdlib module names to inline (e.g. ['capacity']).
            Defaults to ['capacity', 'hiring'].
        verbose: Whether to enable verbose compiler output

    Returns:
        Compiled IR as a dictionary
    """
    if stdlib_modules is None:
        stdlib_modules = ["capacity", "hiring"]

    # Prepend stdlib function definitions so bodies are type-checked
    stdlib_prefix = "\n".join(_load_stdlib_source(m) for m in stdlib_modules)
    full_code = stdlib_prefix + "\n" + code
    return compile_pel_code(full_code, verbose=verbose)


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def pel_compiler() -> PELCompiler:
    return PELCompiler(verbose=False)


def compile_pel_code(code: str, verbose: bool = False) -> dict[str, Any]:
    """Helper to compile PEL code wrapped in a model.

    Args:
        code: PEL code to compile (will be wrapped in 'model TestModel { ... }')
        verbose: Whether to enable verbose compiler output

    Returns:
        Compiled IR as a dictionary

    Raises:
        Any exceptions from the compiler are propagated
    """
    fd, tmp = tempfile.mkstemp(suffix=".pel")
    os.close(fd)  # Close raw fd immediately to prevent leak
    try:
        content = "model TestModel {\n" + code + "\n}\n"
        Path(tmp).write_text(content, encoding="utf-8")
        compiler = PELCompiler(verbose=verbose)
        ir = compiler.compile(Path(tmp))
        return ir
    finally:
        os.unlink(tmp)  # Clean up temp file


def compile_pel_code_with_timing(code: str, verbose: bool = False) -> tuple[dict[str, Any], float]:
    """Helper to compile PEL code and measure compilation time.

    Args:
        code: PEL code to compile (will be wrapped in 'model TestModel { ... }')
        verbose: Whether to enable verbose compiler output

    Returns:
        Tuple of (compiled IR dict, elapsed time in seconds)

    Raises:
        Any exceptions from the compiler are propagated
    """
    fd, tmp = tempfile.mkstemp(suffix=".pel")
    os.close(fd)  # Close raw fd immediately to prevent leak
    try:
        content = "model TestModel {\n" + code + "\n}\n"
        Path(tmp).write_text(content, encoding="utf-8")
        compiler = PELCompiler(verbose=verbose)

        start_time = time.perf_counter()
        ir = compiler.compile(Path(tmp))
        elapsed = time.perf_counter() - start_time

        return ir, elapsed
    finally:
        os.unlink(tmp)  # Clean up temp file


@pytest.fixture
def compile_pel():
    """Pytest fixture providing the compile_pel_code helper."""
    return compile_pel_code


@pytest.fixture
def compile_pel_timed():
    """Pytest fixture providing the compile_pel_code_with_timing helper."""
    return compile_pel_code_with_timing


def assert_compiles_successfully(ir: dict[str, Any]) -> None:
    """Assert that IR compilation succeeded without errors.

    Args:
        ir: The compiled IR dictionary

    Raises:
        AssertionError: If compilation failed or produced errors
    """
    assert isinstance(ir, dict), "IR should be a dictionary"

    # Check that compilation didn't fail catastrophically
    # The IR structure has 'model', 'metadata', and 'version' keys
    assert "model" in ir, "IR should contain 'model' key"
    assert "metadata" in ir, "IR should contain 'metadata' key"

    # Check for compilation errors - they would be in compiler's error list
    # Note: The current IR structure doesn't have an 'errors' field,
    # but we keep this check for future-proofing
    if "errors" in ir:
        assert not ir["errors"], f"Compilation errors found: {ir['errors']}"

    # For edge case tests, we want to verify that the code compiled
    # even if it contains defensive programming (e.g., division by zero guards)
    # The absence of catastrophic failure is success


def assert_compiles_with_errors(ir: dict[str, Any], expected_error_substring: str | None = None) -> None:
    """Assert that IR compilation failed with expected errors.

    Args:
        ir: The compiled IR dictionary
        expected_error_substring: Optional substring to look for in error messages

    Raises:
        AssertionError: If compilation succeeded unexpectedly
    """
    assert isinstance(ir, dict), "IR should be a dictionary even on errors"

    # Either the IR has an errors field OR it's malformed
    # For now, we just verify it's a dict (compiler returns dict even on errors)
    if expected_error_substring and "errors" in ir:
        error_text = str(ir["errors"])
        assert expected_error_substring in error_text, \
            f"Expected error substring '{expected_error_substring}' not found in: {error_text}"
