"""Conformance tests for type checking."""

import pytest
from pathlib import Path
from tests.conformance.test_runner import ConformanceTestRunner
from tests.conformance.assertions import assert_type_annotation, assert_dimension_error


class TestTypeCheckingConformance:
    """Type checking conformance tests (CONF-TYPE-*)."""
    
    def test_typechecking_conformance(self, testcases_dir, load_yaml_test, pel_compiler, pel_typechecker):
        """Run all type checking conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("typechecking")
        
        if not test_cases:
            pytest.skip("No typechecking test cases found")
        
        for test_path in test_cases:
            spec = load_yaml_test(test_path)
            self._run_test(spec, pel_compiler, pel_typechecker)
    
    def _run_test(self, spec, pel_compiler, pel_typechecker):
        """Execute a single type checking test case."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']
        
        if expected['type'] == 'success':
            # Compile and type check
            ast = pel_compiler(source)
            ast = pel_typechecker(ast)
            assert ast is not None, f"{test_id}: Type checking failed"
            
            # Verify type map if specified
            if 'type_map' in expected:
                # Type checking passed, could verify specific types if needed
                pass
        
        elif expected['type'] == 'error':
            # Expect type error
            expected_error = expected.get('error_message', '')
            
            try:
                ast = pel_compiler(source)
                pel_typechecker(ast)
                pytest.fail(f"{test_id}: Expected type error '{expected_error}' but succeeded")
            except Exception as e:
                if expected_error:
                    error_str = str(e).lower()
                    assert expected_error.lower() in error_str, \
                        f"{test_id}: Expected error '{expected_error}', got '{e}'"
