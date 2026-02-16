"""Conformance tests for parsing."""

import pytest
from pathlib import Path
from tests.conformance.test_runner import ConformanceTestRunner
from tests.conformance.assertions import assert_ast_structure, assert_parse_error


class TestParsingConformance:
    """Parsing conformance tests (CONF-PARSE-*)."""
    
    def test_parsing_conformance(self, testcases_dir, load_yaml_test, pel_compiler):
        """Run all parsing conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("parsing")
        
        if not test_cases:
            pytest.skip("No parsing test cases found")
        
        for test_path in test_cases:
            spec = load_yaml_test(test_path)
            self._run_test(spec, pel_compiler)
    
    def _run_test(self, spec, pel_compiler):
        """Execute a single parsing test case."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']
        
        if expected['type'] == 'success':
            # Parse and verify AST
            ast = pel_compiler(source)
            assert ast is not None, f"{test_id}: Failed to parse source"
            
            if 'ast' in expected:
                assert_ast_structure(ast, expected['ast'])
        
        elif expected['type'] == 'error':
            # Expect parse error
            expected_error = expected.get('error_message', '')
            with pytest.raises(Exception) as exc_info:
                pel_compiler(source)
            
            if expected_error:
                error_str = str(exc_info.value).lower()
                assert expected_error.lower() in error_str, \
                    f"{test_id}: Expected error '{expected_error}', got '{exc_info.value}'"
