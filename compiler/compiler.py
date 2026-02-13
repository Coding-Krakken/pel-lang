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
from typing import Optional

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker
from compiler.provenance_checker import ProvenanceChecker
from compiler.ir_generator import IRGenerator
from compiler.errors import CompilerError


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
    
    def compile(self, source_path: Path, output_path: Optional[Path] = None) -> dict:
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
        with open(source_path, 'r', encoding='utf-8') as f:
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
"""
    )
    
    parser.add_argument('source', type=Path, help='Source .pel file')
    parser.add_argument('-o', '--output', type=Path, help='Output .ir.json file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--version', action='version', version='pel-compiler 0.1.0')
    
    args = parser.parse_args()
    
    # Validate input
    if not args.source.exists():
        print(f"error: File not found: {args.source}", file=sys.stderr)
        sys.exit(1)
    
    if not args.source.suffix == '.pel':
        print(f"error: Expected .pel file, got: {args.source.suffix}", file=sys.stderr)
        sys.exit(1)
    
    # Compile
    try:
        compiler = PELCompiler(verbose=args.verbose)
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
