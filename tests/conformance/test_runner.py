# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
Conformance Test Runner
Discovers and executes YAML-based conformance test cases.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import yaml

import pytest

# Import assertions for use in tests
from tests.conformance.assertions import (
    assert_tokens_match,
    assert_ast_structure,
    assert_type,
    assert_dimension_error,
    assert_parse_error,
    assert_runtime_value,
)


def discover_test_cases(testcases_root: Path) -> List[Path]:
    """
    Discover all YAML test case files.
    
    Args:
        testcases_root: Root directory of test cases
    
    Returns:
        List of paths to YAML test files
    """
    return sorted(testcases_root.glob("**/*.yaml"))


def load_test_case(path: Path) -> Dict[str, Any]:
    """
    Load a YAML test case file.
    
    Args:
        path: Path to YAML file
    
    Returns:
        Test case data as dict
    """
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def validate_test_case_schema(test_case: Dict[str, Any], path: Path) -> None:
    """
    Validate test case schema.
    
    Args:
        test_case: Test case data
        path: Path to test case file
    
    Raises:
        ValueError: If schema is invalid
    """
    required_fields = ['id', 'category', 'description', 'input']
    for field in required_fields:
        if field not in test_case:
            raise ValueError(f"Missing required field '{field}' in {path}")
    
    # Validate ID format
    test_id = test_case['id']
    parts = test_id.split('-')
    if len(parts) != 3 or parts[0] != 'CONF':
        raise ValueError(f"Invalid test ID format '{test_id}' in {path}. Expected: CONF-XXX-NNN")
    
    # Validate category
    valid_categories = ['lexical', 'parsing', 'typechecking', 'provenance', 'runtime']
    if test_case['category'] not in valid_categories:
        raise ValueError(f"Invalid category '{test_case['category']}' in {path}")


# Pytest test generation
def pytest_generate_tests(metafunc):
    """
    Generate pytest tests from YAML test cases.
    
    This is called by pytest during test collection to parameterize test functions.
    """
    if "test_case_path" in metafunc.fixturenames:
        # Get testcases root
        conformance_root = Path(__file__).resolve().parent
        testcases_root = conformance_root / "testcases"
        
        # Discover all test cases
        test_case_paths = discover_test_cases(testcases_root)
        
        # Generate test IDs from file names
        test_ids = [p.stem for p in test_case_paths]
        
        # Parameterize the test
        metafunc.parametrize("test_case_path", test_case_paths, ids=test_ids)


def test_conformance(test_case_path: Path, compiler, lexer, parser, yaml_loader):
    """
    Execute a single conformance test case.
    
    Args:
        test_case_path: Path to YAML test case file
        compiler: PELCompiler fixture
        lexer: Lexer factory fixture
        parser: Parser factory fixture
        yaml_loader: YAML loader fixture
    """
    # Load test case
    test_case = yaml_loader(test_case_path)
    
    category = test_case['category']
    input_code = test_case['input']
    
    # Execute test based on category
    if category == 'lexical':
        execute_lexical_test(test_case, lexer)
    elif category == 'parsing':
        execute_parsing_test(test_case, lexer, parser)
    elif category == 'typechecking':
        execute_typechecking_test(test_case, compiler)
    elif category == 'provenance':
        execute_provenance_test(test_case, compiler)
    elif category == 'runtime':
        execute_runtime_test(test_case, compiler)
    else:
        pytest.fail(f"Unknown test category: {category}")


def execute_lexical_test(test_case: Dict[str, Any], lexer_factory):
    """Execute a lexical analysis test."""
    input_code = test_case['input']
    expected = test_case.get('expected', {})
    
    # Tokenize
    lexer_instance = lexer_factory(input_code)
    tokens = lexer_instance.tokenize()
    
    # Check expected tokens
    if 'tokens' in expected:
        assert_tokens_match(tokens, expected['tokens'])
    
    # Check for expected errors
    if 'error' in expected:
        # This test expects an error, but we got tokens
        pytest.fail(f"Expected lexer error but tokenization succeeded")


def execute_parsing_test(test_case: Dict[str, Any], lexer_factory, parser_factory):
    """Execute a parsing test."""
    input_code = test_case['input']
    expected = test_case.get('expected', {})
    
    # Parse
    lexer_instance = lexer_factory(input_code)
    tokens = lexer_instance.tokenize()
    parser_instance = parser_factory(tokens)
    
    if 'error' in expected:
        # Expect parse error
        assert_parse_error(input_code, expected['error'], lexer_factory, parser_factory)
    else:
        # Expect successful parse
        ast = parser_instance.parse()
        
        # Check AST structure if specified
        if 'ast' in expected:
            assert_ast_structure(ast, expected['ast'])


def execute_typechecking_test(test_case: Dict[str, Any], compiler):
    """Execute a type checking test."""
    input_code = test_case['input']
    expected = test_case.get('expected', {})
    
    if 'error' in expected:
        # Expect type error
        assert_dimension_error(input_code, expected['error'], compiler)
    else:
        # Expect successful type checking
        import tempfile
        from pathlib import Path
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pel', delete=False) as f:
            f.write(input_code)
            temp_path = Path(f.name)
        
        try:
            ir = compiler.compile(temp_path)
            
            # Check types if specified
            if 'types' in expected:
                # TODO: Implement type checking validation
                pass
        finally:
            temp_path.unlink()


def execute_provenance_test(test_case: Dict[str, Any], compiler):
    """Execute a provenance test."""
    input_code = test_case['input']
    expected = test_case.get('expected', {})
    
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pel', delete=False) as f:
        f.write(input_code)
        temp_path = Path(f.name)
    
    try:
        if 'error' in expected:
            # Expect provenance error
            from compiler.errors import CompilerError
            try:
                compiler.compile(temp_path)
                pytest.fail("Expected provenance error but compilation succeeded")
            except CompilerError as e:
                assert expected['error'].lower() in str(e).lower()
        else:
            # Expect successful compilation with provenance
            ir = compiler.compile(temp_path)
            
            # Validate provenance metadata
            if 'provenance' in expected:
                # TODO: Implement provenance validation
                pass
    finally:
        temp_path.unlink()


def execute_runtime_test(test_case: Dict[str, Any], compiler):
    """Execute a runtime semantics test."""
    input_code = test_case['input']
    expected = test_case.get('expected', {})
    
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pel', delete=False) as f:
        f.write(input_code)
        temp_path = Path(f.name)
    
    try:
        # Compile to IR
        ir = compiler.compile(temp_path)
        
        # Check runtime values if specified
        if 'values' in expected:
            # TODO: Implement runtime value checking
            pass
    finally:
        temp_path.unlink()


def validate_all_test_cases():
    """
    Validate all test case YAML files.
    
    Returns:
        Tuple of (valid_count, invalid_cases)
    """
    conformance_root = Path(__file__).resolve().parent
    testcases_root = conformance_root / "testcases"
    
    test_cases = discover_test_cases(testcases_root)
    invalid = []
    
    for path in test_cases:
        try:
            test_case = load_test_case(path)
            validate_test_case_schema(test_case, path)
        except Exception as e:
            invalid.append((path, str(e)))
    
    return len(test_cases) - len(invalid), invalid


def main():
    """Command-line entry point for validation."""
    if len(sys.argv) > 1 and sys.argv[1] == '--validate-all':
        valid_count, invalid = validate_all_test_cases()
        
        if invalid:
            print(f"❌ Validation failed: {len(invalid)} invalid test cases")
            for path, error in invalid:
                print(f"  - {path.name}: {error}")
            sys.exit(1)
        else:
            print(f"✅ All {valid_count} test cases valid")
            sys.exit(0)
    else:
        print("Usage: python3 test_runner.py --validate-all")
        sys.exit(1)


if __name__ == '__main__':
    main()
