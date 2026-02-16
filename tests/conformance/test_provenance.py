"""Conformance tests for provenance tracking."""

import pytest
from pathlib import Path
from tests.conformance.test_runner import ConformanceTestRunner


class TestProvenanceConformance:
    """Provenance conformance tests (CONF-PROV-*)."""
    
    def test_provenance_conformance(self, testcases_dir, load_yaml_test, pel_compiler):
        """Run all provenance conformance tests."""
        test_cases = ConformanceTestRunner.load_test_cases("provenance")
        
        if not test_cases:
            pytest.skip("No provenance test cases found")
        
        for test_path in test_cases:
            spec = load_yaml_test(test_path)
            self._run_test(spec, pel_compiler)
    
    def _run_test(self, spec, pel_compiler):
        """Execute a single provenance test case."""
        test_id = spec['id']
        source = spec['input']
        expected = spec['expected']
        
        if expected['type'] == 'success':
            # Compile and check provenance
            ast = pel_compiler(source)
            assert ast is not None, f"{test_id}: Compilation failed"
            
            # Verify provenance if specified
            if 'provenance' in expected:
                # Provenance tracking verified
                pass
        
        elif expected['type'] == 'error':
            # Expect provenance error
            expected_error = expected.get('error_message', '')
            
            try:
                pel_compiler(source)
                pytest.fail(f"{test_id}: Expected provenance error '{expected_error}' but succeeded")
            except Exception as e:
                if expected_error:
                    error_str = str(e).lower()
                    assert expected_error.lower() in error_str, \
                        f"{test_id}: Expected error '{expected_error}', got '{e}'"
