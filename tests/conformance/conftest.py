# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Conformance Test Fixtures
Provides reusable fixtures for PEL specification conformance testing.
"""

from pathlib import Path
from typing import Dict, Any
import yaml

import pytest

from compiler.compiler import PELCompiler
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker
from runtime.runtime import PELRuntime


@pytest.fixture
def conformance_root() -> Path:
    """Get the conformance test root directory."""
    return Path(__file__).resolve().parent


@pytest.fixture
def testcases_root(conformance_root: Path) -> Path:
    """Get the testcases directory."""
    return conformance_root / "testcases"


@pytest.fixture
def compiler() -> PELCompiler:
    """Get a PEL compiler instance."""
    return PELCompiler(verbose=False)


@pytest.fixture
def lexer():
    """Get a lexer factory function."""
    def _lexer(source: str) -> Lexer:
        return Lexer(source)
    return _lexer


@pytest.fixture
def parser():
    """Get a parser factory function."""
    def _parser(tokens) -> Parser:
        return Parser(tokens)
    return _parser


@pytest.fixture
def typechecker():
    """Get a typechecker factory function."""
    def _typechecker() -> TypeChecker:
        return TypeChecker()
    return _typechecker


@pytest.fixture
def runtime() -> PELRuntime:
    """Get a PEL runtime instance."""
    return PELRuntime()


@pytest.fixture
def yaml_loader():
    """Get a YAML test case loader function."""
    def _load_yaml(path: Path) -> Dict[str, Any]:
        """Load and validate a YAML test case file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Basic schema validation
        required_fields = ['id', 'category', 'description', 'input']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in {path}")
        
        # Validate ID format (CONF-XXX-NNN)
        test_id = data['id']
        parts = test_id.split('-')
        if len(parts) != 3 or parts[0] != 'CONF':
            raise ValueError(f"Invalid test ID format '{test_id}' in {path}. Expected: CONF-XXX-NNN")
        
        return data
    
    return _load_yaml
