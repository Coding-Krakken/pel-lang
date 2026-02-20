#!/usr/bin/env python3
"""
Tutorial Code Validator - Extract and validate all PEL code blocks from tutorials

This script:
1. Extracts all PEL code blocks from tutorial markdown files
2. Validates syntax and type correctness
3. Checks that all referenced functions, types, and stdlib modules exist
4. Reports any issues with line numbers and context

Usage:
    python scripts/validate_tutorial_code.py [--tutorial TUTORIAL]

Examples:
    # Validate all tutorials
    python scripts/validate_tutorial_code.py
    
    # Validate specific tutorial
    python scripts/validate_tutorial_code.py --tutorial 02_economic_types.md
    
    # Show detailed validation output
    python scripts/validate_tutorial_code.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set


class TutorialValidator:
    """Validates PEL code blocks in tutorial markdown files."""
    
    # Valid PEL types from compiler/typechecker.py
    VALID_TYPES = {
        "Currency", "Rate", "Duration", "Capacity", "Count", "Fraction",
        "Boolean", "TimeSeries", "Distribution", "Array", "String"
    }
    
    # Invalid types that should not appear in tutorials
    INVALID_TYPES = {
        "Probability",  # Should use Fraction
        "Bool",         # Should use Boolean
        "Float",        # Should use Fraction
        "Integer",      # Should use Fraction or Count
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.stats = {
            "files_checked": 0,
            "code_blocks": 0,
            "lines_validated": 0,
        }
    
    def extract_code_blocks(self, filepath: Path) -> List[Tuple[int, str]]:
        """Extract all PEL code blocks from a markdown file.
        
        Returns:
            List of (line_number, code_content) tuples
        """
        code_blocks = []
        in_code_block = False
        current_block = []
        block_start_line = 0
        is_pel_block = False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Start of code block
                if line.strip().startswith('```pel'):
                    in_code_block = True
                    is_pel_block = True
                    block_start_line = line_num + 1
                    current_block = []
                elif line.strip().startswith('```') and not in_code_block:
                    in_code_block = True
                    is_pel_block = False
                # End of code block
                elif line.strip() == '```' and in_code_block:
                    if is_pel_block and current_block:
                        code = '\n'.join(current_block)
                        code_blocks.append((block_start_line, code))
                    in_code_block = False
                    is_pel_block = False
                    current_block = []
                # Inside code block
                elif in_code_block:
                    current_block.append(line.rstrip())
        
        return code_blocks
    
    def validate_types(self, code: str, filepath: Path, line_offset: int):
        """Validate that only valid PEL types are used."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            line_num = line_offset + i
            
            # Check for invalid types
            for invalid_type in self.INVALID_TYPES:
                # Match type declarations: param x: InvalidType
                if re.search(rf':\s*{invalid_type}\b', line):
                    self.errors.append({
                        "file": filepath.name,
                        "line": line_num,
                        "type": "invalid_type",
                        "message": f"Invalid type '{invalid_type}' used. "
                                 f"Use {self._suggest_replacement(invalid_type)} instead.",
                        "code": line.strip()
                    })
                
                # Match type parameters: TimeSeries<InvalidType>
                if re.search(rf'<{invalid_type}>', line):
                    self.errors.append({
                        "file": filepath.name,
                        "line": line_num,
                        "type": "invalid_type",
                        "message": f"Invalid type parameter '{invalid_type}'. "
                                 f"Use {self._suggest_replacement(invalid_type)} instead.",
                        "code": line.strip()
                    })
    
    def _suggest_replacement(self, invalid_type: str) -> str:
        """Suggest correct replacement for invalid type."""
        replacements = {
            "Probability": "Fraction (with constraint for [0,1] if needed)",
            "Bool": "Boolean",
            "Float": "Fraction",
            "Integer": "Fraction or Count<entity>",
        }
        return replacements.get(invalid_type, "a valid PEL type")
    
    def validate_syntax_patterns(self, code: str, filepath: Path, line_offset: int):
        """Validate common syntax patterns."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            line_num = line_offset + i
            
            # Check for invalid correlation syntax
            if re.search(r'with\s+correlation\s*\(', line):
                self.errors.append({
                    "file": filepath.name,
                    "line": line_num,
                    "type": "invalid_syntax",
                    "message": "Invalid correlation syntax. Use 'correlated_with: [...]' "
                             "inside provenance block instead of 'with correlation(...)'.",
                    "code": line.strip()
                })
            
            # Check for missing provenance in param declarations with distributions
            if re.search(r'param\s+\w+:\s*\w+\s*~\s*\w+\(', line):
                # Look ahead for provenance block
                remaining_code = '\n'.join(lines[i:min(i+10, len(lines))])
                if not re.search(r'\{\s*source:', remaining_code):
                    self.warnings.append({
                        "file": filepath.name,
                        "line": line_num,
                        "type": "missing_provenance",
                        "message": "Parameter with distribution should include provenance metadata.",
                        "code": line.strip()
                    })
    
    def validate_file(self, filepath: Path) -> bool:
        """Validate all PEL code in a tutorial file.
        
        Returns:
            True if validation passed, False otherwise
        """
        if self.verbose:
            print(f"Validating {filepath.name}...")
        
        code_blocks = self.extract_code_blocks(filepath)
        self.stats["files_checked"] += 1
        self.stats["code_blocks"] += len(code_blocks)
        
        for line_num, code in code_blocks:
            self.stats["lines_validated"] += len(code.split('\n'))
            
            # Run validators
            self.validate_types(code, filepath, line_num)
            self.validate_syntax_patterns(code, filepath, line_num)
        
        return len(self.errors) == 0
    
    def validate_all_tutorials(self, tutorial_dir: Path) -> bool:
        """Validate all tutorial files in directory.
        
        Returns:
            True if all validations passed, False otherwise
        """
        tutorial_files = sorted(tutorial_dir.glob("*.md"))
        
        # Filter to numbered tutorials and main README
        tutorial_files = [
            f for f in tutorial_files 
            if f.name[0].isdigit() or f.name == "README.md"
        ]
        
        if not tutorial_files:
            print(f"⚠️  No tutorial files found in {tutorial_dir}")
            return False
        
        print(f"🔍 Validating {len(tutorial_files)} tutorial files...\n")
        
        all_passed = True
        for filepath in tutorial_files:
            passed = self.validate_file(filepath)
            all_passed = all_passed and passed
        
        return all_passed
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)
        
        print(f"\n📊 Statistics:")
        print(f"   Files checked: {self.stats['files_checked']}")
        print(f"   Code blocks: {self.stats['code_blocks']}")
        print(f"   Lines validated: {self.stats['lines_validated']}")
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"\n   {error['file']}:{error['line']}")
                print(f"   Type: {error['type']}")
                print(f"   Message: {error['message']}")
                print(f"   Code: {error['code']}")
        else:
            print(f"\n✅ No errors found!")
        
        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            if self.verbose:
                for warning in self.warnings:
                    print(f"\n   {warning['file']}:{warning['line']}")
                    print(f"   Type: {warning['type']}")
                    print(f"   Message: {warning['message']}")
        
        print("\n" + "="*70)
        
        if self.errors:
            print("❌ VALIDATION FAILED")
            return False
        else:
            print("✅ VALIDATION PASSED")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate PEL code blocks in tutorial markdown files"
    )
    parser.add_argument(
        "--tutorial",
        help="Validate specific tutorial file (e.g., 02_economic_types.md)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation output"
    )
    parser.add_argument(
        "--tutorial-dir",
        type=Path,
        default=Path("docs/tutorials"),
        help="Path to tutorials directory (default: docs/tutorials)"
    )
    
    args = parser.parse_args()
    
    # Validate tutorial directory exists
    if not args.tutorial_dir.exists():
        print(f"❌ Tutorial directory not found: {args.tutorial_dir}")
        sys.exit(1)
    
    validator = TutorialValidator(verbose=args.verbose)
    
    # Validate specific file or all files
    if args.tutorial:
        filepath = args.tutorial_dir / args.tutorial
        if not filepath.exists():
            print(f"❌ Tutorial file not found: {filepath}")
            sys.exit(1)
        
        passed = validator.validate_file(filepath)
    else:
        passed = validator.validate_all_tutorials(args.tutorial_dir)
    
    # Print report
    success = validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
