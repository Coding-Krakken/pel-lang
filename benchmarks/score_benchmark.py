#!/usr/bin/env python3
"""
PEL-100 Benchmark Scoring Script

Compiles and scores benchmark models across multiple dimensions:
- Lines of code (LOC)
- Compilation time
- Execution time (deterministic)
- Model complexity

Generates benchmarks/PEL_100_RESULTS.md
"""

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path


class BenchmarkScorer:
    """Score and analyze PEL benchmark models."""

    def __init__(self, benchmarks_dir: Path):
        self.benchmarks_dir = benchmarks_dir
        self.pel_100_dir = benchmarks_dir / "pel_100"
        self.results = []

    def count_loc(self, pel_file: Path) -> int:
        """Count non-blank, non-comment lines of code.

        Handles:
        - Single-line comments: //
        - Multi-line comments: /* */
        - Inline comments: code // comment
        - Mixed scenarios: /* comment */ code
        """
        lines = pel_file.read_text().split('\n')
        loc = 0
        in_comment = False

        for line in lines:
            code_part = ""
            i = 0
            line_len = len(line)

            while i < line_len:
                # Currently in a multi-line comment
                if in_comment:
                    if i + 1 < line_len and line[i:i+2] == '*/':
                        in_comment = False
                        i += 2
                        continue
                    i += 1
                    continue

                # Not in comment - check for comment starts
                if i + 1 < line_len:
                    two_chars = line[i:i+2]
                    # Start of multi-line comment
                    if two_chars == '/*':
                        in_comment = True
                        i += 2
                        continue
                    # Start of single-line comment (rest of line is comment)
                    if two_chars == '//':
                        break

                # Regular code character
                code_part += line[i]
                i += 1

            # Count line if it has code (not just whitespace)
            if code_part.strip():
                loc += 1

        return loc

    def compile_model(self, pel_file: Path) -> tuple[bool, float, str]:
        """
        Compile model and measure time.

        Returns:
            (success, compile_time_ms, output_path or error)
        """
        output_path = pel_file.with_suffix('.ir.json')

        start = time.time()
        try:
            result = subprocess.run(
                ['python3', './pel', 'compile', str(pel_file), '-o', str(output_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.benchmarks_dir.parent
            )
            end = time.time()

            if result.returncode == 0:
                return True, (end - start) * 1000, str(output_path)
            else:
                return False, 0, result.stderr
        except Exception as e:
            return False, 0, str(e)

    def run_model(self, ir_file: Path) -> tuple[bool, float]:
        """
        Run model deterministically and measure time.

        Returns:
            (success, run_time_ms)
        """
        output_path = ir_file.with_suffix('.results.json')

        start = time.time()
        try:
            result = subprocess.run(
                ['python3', './pel', 'run', str(ir_file),
                 '--mode', 'deterministic', '--seed', '42',
                 '-o', str(output_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.benchmarks_dir.parent
            )
            end = time.time()

            if result.returncode == 0:
                return True, (end - start) * 1000
            else:
                return False, 0
        except Exception:
            return False, 0

    def score_model(self, pel_file: Path) -> dict:
        """Score a single model."""
        print(f"Scoring {pel_file.name}...")

        category = pel_file.parent.name
        model_name = pel_file.stem

        # Count LOC
        loc = self.count_loc(pel_file)

        # Compile
        compile_success, compile_time, compile_output = self.compile_model(pel_file)

        # Run (if compilation succeeded)
        run_success = False
        run_time = 0
        if compile_success:
            ir_file = Path(compile_output)
            run_success, run_time = self.run_model(ir_file)

        return {
            'category': category,
            'model': model_name,
            'loc': loc,
            'compile_success': compile_success,
            'compile_time_ms': compile_time,
            'run_success': run_success,
            'run_time_ms': run_time,
            'status': 'success' if (compile_success and run_success) else 'failed'
        }

    def find_all_models(self) -> list[Path]:
        """Find all .pel files in pel_100 directory."""
        return list(self.pel_100_dir.rglob("*.pel"))

    def run_all_benchmarks(self):
        """Score all benchmark models."""
        models = self.find_all_models()
        print(f"Found {len(models)} benchmark models\n")

        for model_file in models:
            result = self.score_model(model_file)
            self.results.append(result)

        print(f"\nScored {len(self.results)} models")

    def generate_report(self, output_path: Path):
        """Generate Markdown results table."""
        md = []

        md.append("# PEL-100 Benchmark Results\n")
        md.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        md.append(f"**Models Tested:** {len(self.results)}\n")

        # Summary statistics
        successful = [r for r in self.results if r['status'] == 'success']
        md.append(f"**Success Rate:** {len(successful)}/{len(self.results)} ({len(successful)/len(self.results)*100:.1f}%)\n")

        if successful:
            avg_loc = statistics.mean(r['loc'] for r in successful)
            avg_compile = statistics.mean(r['compile_time_ms'] for r in successful)
            avg_run = statistics.mean(r['run_time_ms'] for r in successful)

            md.append("## Summary Statistics\n")
            md.append(f"- **Average LOC:** {avg_loc:.1f}")
            md.append(f"- **Average Compile Time:** {avg_compile:.2f}ms")
            md.append(f"- **Average Run Time:** {avg_run:.2f}ms\n")

        # Results table
        md.append("## Detailed Results\n")
        md.append("| Category | Model | LOC | Compile (ms) | Run (ms) | Status |")
        md.append("|----------|-------|-----|--------------|----------|--------|")

        for r in sorted(self.results, key=lambda x: (x['category'], x['model'])):
            compile_time = f"{r['compile_time_ms']:.2f}" if r['compile_success'] else "FAILED"
            run_time = f"{r['run_time_ms']:.2f}" if r['run_success'] else "FAILED"
            status_emoji = "✅" if r['status'] == 'success' else "❌"

            md.append(f"| {r['category']} | {r['model']} | {r['loc']} | {compile_time} | {run_time} | {status_emoji} |")

        md_content = "\n".join(md)
        output_path.write_text(md_content)
        print(f"\nReport written to: {output_path}")

        return md_content

    def get_success_rate_percent(self) -> float:
        """Return benchmark success rate as percentage."""
        if not self.results:
            return 0.0
        successful = sum(1 for r in self.results if r.get('status') == 'success')
        return (successful / len(self.results)) * 100.0


def main():
    """Run benchmark scoring."""
    parser = argparse.ArgumentParser(description="Run PEL-100 benchmark scoring")
    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=None,
        help="Fail with non-zero exit code if success rate is below this percentage",
    )
    args = parser.parse_args()

    benchmarks_dir = Path(__file__).parent

    scorer = BenchmarkScorer(benchmarks_dir)
    scorer.run_all_benchmarks()

    output_path = benchmarks_dir / "PEL_100_RESULTS.md"
    scorer.generate_report(output_path)

    # Also save JSON
    json_path = benchmarks_dir / "PEL_100_RESULTS.json"
    with open(json_path, 'w') as f:
        json.dump(scorer.results, f, indent=2)
    print(f"JSON results: {json_path}")

    success_rate = scorer.get_success_rate_percent()
    print(f"Success rate: {success_rate:.1f}%")

    if args.min_success_rate is not None and success_rate < args.min_success_rate:
        print(
            f"ERROR: Success rate {success_rate:.1f}% is below required threshold "
            f"{args.min_success_rate:.1f}%"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
