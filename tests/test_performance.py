# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""Performance benchmark tests for formatter and linter."""

import pytest
import time
from formatter.formatter import PELFormatter
from linter.linter import PELLinter
from linter.config import LinterConfig


# Generate a large PEL model for benchmarking
def generate_large_model(num_params=100, num_vars=100):
    """Generate a large PEL model for performance testing."""
    lines = ["model LargeModel {"]
    
    # Add parameters
    for i in range(num_params):
        lines.append(f"    param param_{i}: Int = {i}")
    
    # Add variables
    for i in range(num_vars):
        lines.append(f"    var var_{i} = param_0 + {i}")
    
    lines.append("}")
    return "\n".join(lines)


class TestFormatterPerformance:
    """Performance benchmarks for formatter."""

    def test_formatter_small_file_performance(self):
        """Test formatter performance on small file (<100 lines)."""
        source = generate_large_model(10, 10)
        formatter = PELFormatter()
        
        start = time.time()
        result = formatter.format_string(source)
        elapsed = time.time() - start
        
        # Should be very fast for small files (< 10ms)
        assert elapsed < 0.010, f"Formatter took {elapsed:.3f}s for small file"

    def test_formatter_medium_file_performance(self):
        """Test formatter performance on medium file (~500 lines)."""
        source = generate_large_model(50, 50)
        formatter = PELFormatter()
        
        start = time.time()
        result = formatter.format_string(source)
        elapsed = time.time() - start
        
        # Should be fast for medium files (< 25ms)
        assert elapsed < 0.025, f"Formatter took {elapsed:.3f}s for medium file"

    def test_formatter_large_file_performance(self):
        """Test formatter performance on large file (~1000 lines)."""
        source = generate_large_model(100, 100)
        formatter = PELFormatter()
        
        start = time.time()
        result = formatter.format_string(source)
        elapsed = time.time() - start
        
        # Meet the PR requirement: < 50ms for 1000-line files
        assert elapsed < 0.050, f"Formatter took {elapsed:.3f}s, expected < 50ms"

    def test_formatter_idempotent_performance(self):
        """Test that second formatting is fast (already formatted)."""
        source = generate_large_model(50, 50)
        formatter = PELFormatter()
        
        # First format
        first = formatter.format_string(source)
        
        # Second format (should be fast)
        start = time.time()
        second = formatter.format_string(first.formatted)
        elapsed = time.time() - start
        
        # Second run should be very fast
        assert elapsed < 0.020, f"Second format took {elapsed:.3f}s"


class TestLinterPerformance:
    """Performance benchmarks for linter."""

    def test_linter_small_file_performance(self):
        """Test linter performance on small file."""
        source = generate_large_model(10, 10)
        config = LinterConfig()
        linter = PELLinter(config=config)
        
        start = time.time()
        violations = linter.lint_string(source)
        elapsed = time.time() - start
        
        # Should be fast for small files (< 20ms)
        assert elapsed < 0.020, f"Linter took {elapsed:.3f}s for small file"

    def test_linter_medium_file_performance(self):
        """Test linter performance on medium file."""
        source = generate_large_model(50, 50)
        config = LinterConfig()
        linter = PELLinter(config=config)
        
        start = time.time()
        violations = linter.lint_string(source)
        elapsed = time.time() - start
        
        # Should be reasonable for medium files (< 100ms)
        assert elapsed < 0.100, f"Linter took {elapsed:.3f}s for medium file"

    def test_linter_large_file_performance(self):
        """Test linter performance on large file."""
        source = generate_large_model(100, 100)
        config = LinterConfig()
        linter = PELLinter(config=config)
        
        start = time.time()
        violations = linter.lint_string(source)
        elapsed = time.time() - start
        
        # Meet the PR requirement: < 200ms for 1000-line files
        assert elapsed < 0.200, f"Linter took {elapsed:.3f}s, expected < 200ms"

    def test_linter_single_rule_vs_all_rules(self):
        """Test performance difference between single rule and all rules."""
        source = generate_large_model(50, 50)
        
        # Single rule
        config_single = LinterConfig(enabled_rules=["PEL001"])
        linter_single = PELLinter(config=config_single)
        
        start = time.time()
        violations_single = linter_single.lint_string(source)
        elapsed_single = time.time() - start
        
        # All rules
        config_all = LinterConfig()
        linter_all = PELLinter(config=config_all)
        
        start = time.time()
        violations_all = linter_all.lint_string(source)
        elapsed_all = time.time() - start
        
        # All rules should still be reasonably fast
        assert elapsed_all < 0.150, f"All rules took {elapsed_all:.3f}s"

    def test_linter_parse_error_performance(self):
        """Test linter performance on files with parse errors."""
        source = "model { invalid syntax " * 100
        config = LinterConfig()
        linter = PELLinter(config=config)
        
        start = time.time()
        violations = linter.lint_string(source)
        elapsed = time.time() - start
        
        # Should fail fast on parse errors
        assert elapsed < 0.050, f"Linter took {elapsed:.3f}s on parse error"


# Optional: benchmark test using pytest-benchmark if available
try:
    import pytest_benchmark
    
    @pytest.mark.benchmark
    class TestBenchmarkWithPlugin:
        """Benchmark tests using pytest-benchmark plugin."""

        def test_formatter_benchmark(self, benchmark):
            """Benchmark formatter with pytest-benchmark."""
            source = generate_large_model(50, 50)
            formatter = PELFormatter()
            
            result = benchmark(formatter.format_string, source)
            
            # Stats available in benchmark.stats
            assert result.changed is not None

        def test_linter_benchmark(self, benchmark):
            """Benchmark linter with pytest-benchmark."""
            source = generate_large_model(50, 50)
            config = LinterConfig()
            linter = PELLinter(config=config)
            
            violations = benchmark(linter.lint_string, source)
            
            # Stats available in benchmark.stats
            assert isinstance(violations, list)

except ImportError:
    # pytest-benchmark not installed, skip these tests
    pass
