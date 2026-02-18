# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""PEL CLI entry point."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from collections.abc import Iterable
from pathlib import Path

from compiler.ir_generator import IRGenerator
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.provenance_checker import ProvenanceChecker
from compiler.typechecker import TypeChecker
from formatter.formatter import PELFormatter
from linter.config import LinterConfig
from linter.linter import PELLinter
from linter.reporter import render_json, render_text
from runtime.runtime import PELRuntime, RuntimeConfig


def _iter_pel_files(paths: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for entry in paths:
        path = Path(entry)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.pel")))
        elif path.is_file():
            files.append(path)
    return files


def cmd_compile(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: File not found: {source_path}")
        return 1

    source_code = source_path.read_text(encoding="utf-8")
    print(f"Compiling {source_path}...")

    try:
        print("  [1/5] Lexical analysis...")
        lexer = Lexer(source_code, str(source_path))
        tokens = lexer.tokenize()
        print(f"        Generated {len(tokens)} tokens")

        print("  [2/5] Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"        Parsed model '{ast.name}'")

        print("  [3/5] Type checking...")
        type_checker = TypeChecker()
        type_checker.check_model(ast)

        if type_checker.has_errors():
            print("        Type errors found:")
            for error in type_checker.get_errors():
                print(f"          - {error}")
            if not args.force:
                return 1

        print("        Type checking passed")

        print("  [4/5] Provenance validation...")
        prov_checker = ProvenanceChecker()
        prov_checker.check(ast)

        if prov_checker.has_errors():
            print("        Provenance errors found:")
            for error in prov_checker.get_errors():
                print(f"          - {error}")
            if not args.force:
                return 1
        else:
            print(f"        Completeness: {prov_checker.get_completeness_score():.1%}")

        print("  [5/5] Generating IR...")
        ir_gen = IRGenerator(str(source_path))
        ir_doc = ir_gen.generate(ast)
        print(f"        Model hash: {ir_doc['metadata']['model_hash'][:16]}...")

        output_path = Path(args.output) if args.output else source_path.with_suffix(".ir.json")
        output_path.write_text(json.dumps(ir_doc, indent=2), encoding="utf-8")

        print("\n✓ Compilation successful!")
        print(f"  Output: {output_path}")
        print(f"  Model: {ast.name}")
        print(f"  Parameters: {len(ast.params)}")
        print(f"  Variables: {len(ast.vars)}")
        print(f"  Constraints: {len(ast.constraints)}")
        print(f"  Policies: {len(ast.policies)}")

        return 0
    except Exception as exc:
        print(f"\n✗ Compilation failed: {exc}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    ir_path = Path(args.ir_file)
    if not ir_path.exists():
        print(f"Error: File not found: {ir_path}")
        return 1

    print(f"Running {ir_path}...")

    try:
        config = RuntimeConfig(
            mode=args.mode,
            seed=args.seed,
            num_runs=args.runs,
            time_horizon=args.horizon,
        )

        runtime = PELRuntime(config)
        print("  Loading IR...")
        ir_doc = runtime.load_ir(ir_path)
        model_name = ir_doc["model"]["name"]
        print(f"  Model: {model_name}")

        print(f"  Executing ({args.mode} mode, seed={args.seed})...")
        results = runtime.run(ir_doc)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
            print(f"\n✓ Results written to {output_path}")
        else:
            print("\n✓ Execution complete")
            print(f"  Status: {results['status']}")
            if results["status"] == "success":
                print(f"  Timesteps: {results.get('timesteps', 0)}")
                print(f"  Constraint violations: {len(results.get('constraint_violations', []))}")
                print(f"  Policy executions: {len(results.get('policy_executions', []))}")

        return 0
    except Exception as exc:
        print(f"\n✗ Execution failed: {exc}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_check(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: File not found: {source_path}")
        return 1

    source_code = source_path.read_text(encoding="utf-8")
    print(f"Checking {source_path}...")

    try:
        lexer = Lexer(source_code, str(source_path))
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        type_checker = TypeChecker()
        type_checker.check_model(ast)

        prov_checker = ProvenanceChecker()
        prov_checker.check(ast)

        print(f"\n✓ Model '{ast.name}' is valid")
        print(f"  Type errors: {len(type_checker.get_errors())}")
        print(f"  Type warnings: {len(type_checker.get_warnings())}")
        print(f"  Provenance errors: {len(prov_checker.get_errors())}")
        print(f"  Provenance completeness: {prov_checker.get_completeness_score():.1%}")

        has_errors = type_checker.has_errors() or prov_checker.has_errors()
        return 1 if has_errors else 0
    except Exception as exc:
        print(f"\n✗ Validation failed: {exc}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_format(args: argparse.Namespace) -> int:
    formatter = PELFormatter(line_length=args.line_length, indent_size=args.indent_size)

    if args.stdin:
        source = sys.stdin.read()
        result = formatter.format_string(source)
        sys.stdout.write(result.formatted)
        return 0

    files = _iter_pel_files(args.paths)
    if not files:
        print("No .pel files found.")
        return 1

    changed = False
    for path in files:
        result = formatter.format_file(str(path), in_place=not args.check and not args.diff)
        if result.changed:
            changed = True
        if args.diff and result.changed:
            diff = difflib.unified_diff(
                path.read_text(encoding="utf-8").splitlines(),
                result.formatted.splitlines(),
                fromfile=str(path),
                tofile=f"{path} (formatted)",
                lineterm="",
            )
            print("\n".join(diff))

    if args.check and changed:
        return 1
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    config = LinterConfig()
    if args.rule:
        config.enabled_rules = args.rule
    if args.line_length:
        config.line_length = args.line_length

    linter = PELLinter(config=config)

    if args.stdin:
        source = sys.stdin.read()
        violations = linter.lint_string(source)
    else:
        files = _iter_pel_files(args.paths)
        if not files:
            print("No .pel files found.")
            return 1
        violations = []
        for path in files:
            violations.extend(linter.lint_file(str(path)))

    if args.severity:
        violations = [v for v in violations if v.severity == args.severity]

    output = render_json(violations) if args.json else render_text(violations)
    if output:
        print(output)

    return 1 if any(v.severity == "error" for v in violations) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PEL - Programmable Economic Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  pel compile model.pel -o model.ir.json\n"
            "  pel run model.ir.json --mode monte_carlo --runs 10000\n"
            "  pel check model.pel\n"
            "  pel format model.pel --check\n"
            "  pel lint model.pel\n"
            "\nFor more information: https://spec.pel-lang.org"
        ),
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--version", action="version", version="PEL 0.2.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile", help="Compile PEL source to IR")
    compile_parser.add_argument("source", type=str, help="Source .pel file")
    compile_parser.add_argument("-o", "--output", type=str, help="Output .ir.json file")
    compile_parser.add_argument("--force", action="store_true", help="Generate IR even with errors")

    run_parser = subparsers.add_parser("run", help="Execute compiled IR")
    run_parser.add_argument("ir_file", type=str, help="Compiled .ir.json file")
    run_parser.add_argument("--mode", choices=["deterministic", "monte_carlo"], default="deterministic")
    run_parser.add_argument("--seed", type=int, default=42, help="Random seed")
    run_parser.add_argument("--runs", type=int, default=1000, help="Monte Carlo runs")
    run_parser.add_argument("--horizon", type=int, help="Time horizon override")
    run_parser.add_argument("-o", "--output", type=str, help="Output results JSON")

    check_parser = subparsers.add_parser("check", help="Validate model without compiling")
    check_parser.add_argument("source", type=str, help="Source .pel file")

    format_parser = subparsers.add_parser("format", help="Format PEL source code")
    format_parser.add_argument("paths", nargs="*", default=[], help="Files or directories")
    format_parser.add_argument("--check", action="store_true", help="Check formatting only")
    format_parser.add_argument("--diff", action="store_true", help="Show formatting diff")
    format_parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    format_parser.add_argument("--line-length", type=int, help="Override line length")
    format_parser.add_argument("--indent-size", type=int, help="Override indent size")

    lint_parser = subparsers.add_parser("lint", help="Lint PEL source code")
    lint_parser.add_argument("paths", nargs="*", default=[], help="Files or directories")
    lint_parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    lint_parser.add_argument("--json", action="store_true", help="Output JSON")
    lint_parser.add_argument("--severity", choices=["error", "warning", "info"], help="Filter by severity")
    lint_parser.add_argument("--rule", action="append", help="Run a specific rule (repeatable)")
    lint_parser.add_argument("--line-length", type=int, help="Override line length")

    return parser


def main() -> int:
    parser = build_parser()
    argv = sys.argv[1:]
    executable = Path(sys.argv[0]).name
    if executable in {"pelformat", "pellint"}:
        default_cmd = "format" if executable == "pelformat" else "lint"
        if not argv or argv[0] not in {"compile", "run", "check", "format", "lint"}:
            argv = [default_cmd, *argv]
    args = parser.parse_args(argv)

    if args.command == "compile":
        return cmd_compile(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "check":
        return cmd_check(args)
    if args.command == "format":
        return cmd_format(args)
    if args.command == "lint":
        return cmd_lint(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
