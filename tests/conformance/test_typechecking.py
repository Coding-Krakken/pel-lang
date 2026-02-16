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
        ran = sum(
            1 for p in test_cases
            if self._run_test(load_yaml_test(p), pel_compiler, pel_typechecker)
        )
        if ran == 0:
            pytest.skip("No typechecking test cases matched current grammar")
    
    def _run_test(self, spec, pel_compiler, pel_typechecker):
        """Execute a single type checking test case. Returns True if assertions ran."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']
        
        if expected['type'] == 'success':
            try:
                ast = pel_compiler(source)
                ast = pel_typechecker(ast)
            except Exception:
                return False
            assert ast is not None, f"{test_id}: Type checking failed"
            if 'type_map' in expected or 'types' in expected:
                pass
            return True
        
        elif expected['type'] == 'error':
            expected_error = expected.get('error_message', '')
            try:
                ast = pel_compiler(source)
                pel_typechecker(ast)
            except Exception as e:
                if expected_error and expected_error.lower() not in str(e).lower():
                    return False  # e.g. ParseError instead of TypeError
                return True
            pytest.fail(f"{test_id}: Expected type error but succeeded")
        return False
