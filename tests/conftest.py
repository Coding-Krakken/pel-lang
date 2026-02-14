from __future__ import annotations

from pathlib import Path

import pytest

from compiler.compiler import PELCompiler


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def pel_compiler() -> PELCompiler:
    return PELCompiler(verbose=False)
