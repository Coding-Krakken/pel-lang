"""Test runner for YAML-based conformance tests."""

from pathlib import Path
from typing import Any

import yaml


class ConformanceTestRunner:
    """Loads and executes conformance tests from YAML specifications."""

    @staticmethod
    def load_test_cases(category: str) -> list[Path]:
        """Load all YAML test cases for a category.

        Args:
            category: Test category (lexical, parsing, typechecking, provenance, runtime)

        Returns:
            List of paths to YAML test files
        """
        test_dir = Path(__file__).parent / "testcases" / category
        if not test_dir.exists():
            return []
        return sorted(test_dir.glob("*.yaml"))

    @staticmethod
    def load_yaml(test_path: Path) -> dict[str, Any]:
        """Load and validate YAML test case.

        Args:
            test_path: Path to YAML test file

        Returns:
            Parsed test specification
        """
        with open(test_path) as f:
            spec = yaml.safe_load(f)

        # Validate required fields
        required = ['id', 'category', 'spec_ref', 'description', 'input', 'expected']
        for field in required:
            if field not in spec:
                raise ValueError(f"Missing required field '{field}' in {test_path}")

        return spec

    @staticmethod
    def validate_all_tests():
        """Validate YAML schema for all test cases."""
        categories = ['lexical', 'parsing', 'typechecking', 'provenance', 'runtime']
        errors = []

        for category in categories:
            test_cases = ConformanceTestRunner.load_test_cases(category)
            for test_path in test_cases:
                try:
                    ConformanceTestRunner.load_yaml(test_path)
                except Exception as e:
                    errors.append(f"{test_path}: {e}")

        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


def pytest_generate_tests(metafunc):
    """Generate parameterized tests from YAML files."""
    if "test_case_path" in metafunc.fixturenames:
        category = metafunc.function.__module__.split('_')[-1]
        test_cases = ConformanceTestRunner.load_test_cases(category)
        metafunc.parametrize("test_case_path", test_cases,
                           ids=[p.stem for p in test_cases])


if __name__ == "__main__":
    """Validate all test case YAML files."""
    import sys
    if "--validate-all" in sys.argv:
        if ConformanceTestRunner.validate_all_tests():
            print("✓ All test cases valid")
            sys.exit(0)
        else:
            sys.exit(1)
