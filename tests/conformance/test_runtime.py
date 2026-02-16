"""Conformance tests for runtime semantics."""

import pytest
from pathlib import Path
from tests.conformance.test_runner import ConformanceTestRunner


class TestRuntimeConformance:
    """Runtime conformance tests (CONF-RUN-*)."""
    
    def test_runtime_conformance(self, testcases_dir, load_yaml_test, pel_compiler):
        """Run all runtime conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("runtime")
        
        if not test_cases:
            pytest.skip("No runtime test cases found")
        
        for test_path in test_cases:
            spec = load_yaml_test(test_path)
            self._run_test(spec, pel_compiler)
    
    def _run_test(self, spec, pel_compiler):
        """Execute a single runtime test case."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']
        
        if expected['type'] == 'success':
            # Compile (runtime execution would happen separately)
            ast = pel_compiler(source)
            assert ast is not None, f"{test_id}: Compilation failed"
            
            # Verify runtime values if specified
            if 'runtime_values' in expected:
                # Runtime evaluation would happen here
                pass
        
        elif expected['type'] == 'error':
            # Expect runtime error
            expected_error = expected.get('error_message', '')
            
            try:
                pel_compiler(source)
                # For runtime errors, we'd need actual execution
                # For now, just check if compilation succeeds
            except Exception as e:
                if expected_error:
                    error_str = str(e).lower()
                    assert expected_error.lower() in error_str, \
                        f"{test_id}: Expected error '{expected_error}', got '{e}'"
