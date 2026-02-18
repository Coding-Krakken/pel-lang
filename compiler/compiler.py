# Copyright 2026 PEL Project Contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This file is part of PEL (Programmable Economic Language).
# PEL is dual-licensed under AGPL-3.0 and a commercial license.
# See LICENSE and COMMERCIAL-LICENSE.md for details.

"""
PEL Compiler - Main Entry Point
Reference implementation v0.1.0
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from compiler.errors import CompilerError
from compiler.ir_generator import IRGenerator
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.provenance_checker import ProvenanceChecker
from compiler.typechecker import TypeChecker


class PELCompiler:
    """
    PEL compiler: source code (.pel) -> PEL-IR (JSON)

    Pipeline:
        1. Lexer: source -> tokens
        2. Parser: tokens -> AST
        3. Type Checker: AST -> typed AST (with dimensional analysis)
        4. Provenance Checker: ensure all params have metadata
        5. IR Generator: typed AST -> PEL-IR JSON
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def analyze_contracts(self, source_path: Path) -> str:
        """
        Analyze semantic contracts in a PEL model.

        Args:
            source_path: Path to .pel file

        Returns:
            Contract analysis report (string)

        Raises:
            CompilerError: If analysis fails
        """
        if self.verbose:
            print(f"Analyzing contracts in {source_path}...")

        # Read source
        with open(source_path, encoding='utf-8') as f:
            source_code = f.read()

        # Stage 1: Lexical analysis
        if self.verbose:
            print("  [1/3] Lexer...")
        lexer = Lexer(source_code, filename=str(source_path))
        tokens = lexer.tokenize()

        # Stage 2: Parsing
        if self.verbose:
            print("  [2/3] Parser...")
        parser = Parser(tokens)
        ast = parser.parse()

        # Stage 3: Contract analysis
        if self.verbose:
            print("  [3/3] Contract analyzer...")
        type_checker = TypeChecker()
        report = type_checker.generate_contract_report(ast)

        if self.verbose:
            print("✓ Analysis complete\n")

        return report

    def compile(self, source_path: Path, output_path: Path | None = None) -> dict:
        """
        Compile PEL source to IR.

        Args:
            source_path: Path to .pel file
            output_path: Path to output .ir.json (optional, defaults to source_path.ir.json)

        Returns:
            IR document (dict)

        Raises:
            CompilerError: If compilation fails
        """
        if self.verbose:
            print(f"Compiling {source_path}...")

        # Read source
        with open(source_path, encoding='utf-8') as f:
            source_code = f.read()

        # Stage 1: Lexical analysis
        if self.verbose:
            print("  [1/5] Lexer...")
        lexer = Lexer(source_code, filename=str(source_path))
        tokens = lexer.tokenize()

        # Stage 2: Parsing
        if self.verbose:
            print("  [2/5] Parser...")
        parser = Parser(tokens)
        ast = parser.parse()

        # Stage 3: Type checking
        if self.verbose:
            print("  [3/5] Type checker...")
        type_checker = TypeChecker()
        typed_ast = type_checker.check(ast)

        # Stage 4: Provenance checking
        if self.verbose:
            print("  [4/5] Provenance checker...")
        provenance_checker = ProvenanceChecker()
        provenance_checker.check(typed_ast)

        # Stage 5: IR generation
        if self.verbose:
            print("  [5/5] IR generator...")
        ir_generator = IRGenerator(source_path=str(source_path))
        ir_document = ir_generator.generate(typed_ast)

        # Write output
        if output_path is None:
            output_path = source_path.with_suffix('.ir.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ir_document, f, indent=2)

        if self.verbose:
            print(f"✓ Compiled successfully: {output_path}")

        return ir_document


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PEL Compiler - Compile PEL source to PEL-IR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pel compile model.pel
  pel compile model.pel -o build/model.ir.json
  pel compile model.pel --verbose
  pel compile model.pel --contract-report
"""
    )

    parser.add_argument('source', type=Path, help='Source .pel file')
    parser.add_argument('-o', '--output', type=Path, help='Output .ir.json file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--contract-report', action='store_true',
                        help='Generate semantic contract analysis report instead of compiling')
    parser.add_argument('--version', action='version', version='pel-compiler 0.1.0')

    args = parser.parse_args()

    # Validate input
    if not args.source.exists():
        print(f"error: File not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    if not args.source.suffix == '.pel':
        print(f"error: Expected .pel file, got: {args.source.suffix}", file=sys.stderr)
        sys.exit(1)

    # Compile or analyze
    try:
        compiler = PELCompiler(verbose=args.verbose)

        if args.contract_report:
            # Generate contract analysis report
            report = compiler.analyze_contracts(args.source)
            print(report)
            sys.exit(0)
        else:
            # Normal compilation
            compiler.compile(args.source, args.output)
            sys.exit(0)
    except CompilerError as e:
        print(f"{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Internal compiler error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
