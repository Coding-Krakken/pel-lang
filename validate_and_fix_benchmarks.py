#!/usr/bin/env python3
"""
PEL-100 Benchmark Validator and Fixer
- Tests each model's compilation status
- Applies systematic fixes to failing models
- Tracks progress toward 100/100 compilation
"""

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Determine project root dynamically
PROJECT_ROOT = Path(__file__).parent.absolute()
BENCHMARK_DIR = PROJECT_ROOT / 'benchmarks' / 'pel_100'
RESULTS_FILE = PROJECT_ROOT / 'benchmarks' / 'PEL_100_RESULTS.json'
COMPILER = PROJECT_ROOT / 'pel'

# Load existing results
def load_results():
    if RESULTS_FILE.exists():
        return json.load(open(RESULTS_FILE))
    return []

def get_all_models():
    """Get all .pel files from benchmark directory"""
    models = []
    for pel_file in sorted(BENCHMARK_DIR.rglob('*.pel')):
        rel_path = pel_file.relative_to(BENCHMARK_DIR)
        category = rel_path.parts[0] if len(rel_path.parts) > 1 else 'other'
        model_name = rel_path.stem
        models.append({
            'path': str(pel_file),
            'category': category,
            'model': model_name,
            'rel_path': str(rel_path)
        })
    return models

def test_compilation(model_path):
    """Test if a model compiles successfully"""
    try:
        result = subprocess.run(
            [str(COMPILER), 'compile', model_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout + result.stderr

        # Check for success marker
        if '✓ Compilation successful!' in output:
            return True, None

        # Extract error if compilation failed
        error_lines = [line for line in output.split('\n') if 'error[' in line.lower()]
        if error_lines:
            return False, error_lines[0]

        # If we don't see success marker and no errors, check return code
        if result.returncode != 0:
            return False, f"Compiler returned code {result.returncode}"

        return True, None

    except subprocess.TimeoutExpired:
        return False, "Compilation timeout"
    except Exception as e:
        return False, str(e)

def test_all_models():
    """Test all models and return compilation status"""
    models = get_all_models()
    print(f"Found {len(models)} models to test\n")

    passing = []
    failing = []

    for i, model in enumerate(models, 1):
        model_id = f"[{i}/{len(models)}]"
        success, error = test_compilation(model['path'])

        if success:
            print(f"{model_id} ✓ {model['category']}/{model['model']}")
            passing.append(model)
        else:
            print(f"{model_id} ✗ {model['category']}/{model['model']}")
            if error:
                print(f"       Error: {error[:80]}")
            failing.append({**model, 'error': error})

    print(f"\n{'='*60}")
    print(f"Results: {len(passing)}/100 compiling, {len(failing)}/100 failing")
    print(f"{'='*60}\n")

    return passing, failing

def apply_fix_type_annotations(content):
    """Fix missing type annotations"""
    fixes_applied = []

    # Fix pattern 1: param/var without type colons
    # param name = value -> param name: Currency<USD> = value
    # But we need to be careful not to break existing annotations

    # Pattern: "param IDENTIFIER (" or "param IDENTIFIER =" where no ":" follows IDENTIFIER
    def fix_param_var(match):
        match.group(1)  # "param" or "var"
        match.group(2)
        rest = match.group(3)

        # If there's already a colon, don't modify
        if rest.startswith(':'):
            return match.group(0)

        # For params/vars without types, infer from context
        # This is a simplified attempt - may need per-file tuning
        if rest.startswith('='):
            # No type annotation, try to add one
            # For now, just return as-is since we can't reliably infer
            return match.group(0)

        return match.group(0)

    # Look for untyped param/var declarations

    # Count how many untyped ones we find
    untyped_count = len(re.findall(r'(param|var)\s+(\w+)\s*=', content))

    if untyped_count > 0:
        fixes_applied.append(f"Found {untyped_count} untyped param/var declarations")

    return content, fixes_applied

def apply_fix_type_dimensioning(content):
    """Fix bare types to include dimensions"""
    fixes_applied = []
    original = content

    # Replace bare type references with dimensioned ones
    replacements = [
        (r':\s*Currency\b(?!<)', ': Currency<USD>'),
        (r':\s*Count\b(?!<)', ': Count<Item>'),
        (r':\s*Rate\b(?!per)', ': Rate per Month'),
        (r':\s*Fraction\b(?!<)', ': Fraction'),
    ]

    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, content)
        if new_content != original:
            count = len(re.findall(pattern, original))
            fixes_applied.append(f"Fixed {count} bare type refs: {pattern}")
            content = new_content

    return content, fixes_applied

def apply_fix_constraint_simplification(content):
    """Simplify complex constraint blocks"""
    fixes_applied = []

    # Pattern: constraint with complex metadata
    # constraint name { ... }  ->  constraint name: ...
    # This is complex and risky, so we'll be conservative

    return content, fixes_applied

def apply_fix_line_continuation(content):
    """Fix expression continuation across lines"""
    fixes_applied = []
    original = content

    # Pattern: operator at end of line followed by operand
    # This typically means the line was broken mid-expression

    lines = content.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if line ends with operator and next line continues
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip()
            stripped = line.rstrip()

            # Common operators that shouldn't end a line
            if any(stripped.endswith(op) for op in ['+', '-', '*', '/', '=', '>', '<', '>=']):
                # This line likely continues
                # Try to join it with next line if next doesn't start with a new statement
                if next_line and not any(next_line.startswith(kw) for kw in ['param', 'var', 'constraint', 'policy']):
                    combined = stripped + ' ' + next_line
                    new_lines.append(combined)
                    i += 2
                    fixes_applied.append("Joined broken expression line")
                    continue

        new_lines.append(line)
        i += 1

    new_content = '\n'.join(new_lines)
    if new_content != original:
        passes = len([1 for line in original.split('\n') if any(line.rstrip().endswith(op) for op in ['+', '-', '*', '/', '=', '>'])])
        if passes > 0:
            fixes_applied.append("Fixed broken line continuations")

    return new_content, fixes_applied

def fix_model(model_path):
    """Apply all fixes to a model file"""
    print(f"\nFixing: {model_path}")

    with open(model_path) as f:
        content = f.read()

    original_content = content
    all_fixes = []

    # Apply fixes in priority order
    content, fixes = apply_fix_type_annotations(content)
    all_fixes.extend(fixes)

    content, fixes = apply_fix_type_dimensioning(content)
    all_fixes.extend(fixes)

    content, fixes = apply_fix_constraint_simplification(content)
    all_fixes.extend(fixes)

    content, fixes = apply_fix_line_continuation(content)
    all_fixes.extend(fixes)

    if content != original_content:
        with open(model_path, 'w') as f:
            f.write(content)
        print("  Applied fixes:")
        for fix in all_fixes:
            print(f"    - {fix}")
        return True, all_fixes
    else:
        return False, []

def main():
    print("PEL-100 Benchmark Compiler Validator")
    print("=" * 60)

    # Test all models
    passing, failing = test_all_models()

    # Report failures
    if failing:
        print(f"\n{len(failing)} models are not compiling:\n")
        by_category = defaultdict(list)
        for m in failing:
            by_category[m['category']].append(m)

        for category in sorted(by_category.keys()):
            models = by_category[category]
            print(f"  {category}/ ({len(models)})")
            for m in sorted(models, key=lambda x: x['model']):
                print(f"    - {m['model']}")
                if m['error']:
                    print(f"      {m['error'][:70]}")

        # Try to fix them
        print(f"\n{'='*60}")
        print("Attempting automated fixes...")
        print(f"{'='*60}\n")

        fixed_count = 0
        for model in failing:
            fixed, fixes = fix_model(model['path'])
            if fixed:
                fixed_count += 1

        if fixed_count > 0:
            print(f"\nApplied fixes to {fixed_count} models")
            print("Re-testing compilation...")

            # Re-test
            passing2, failing2 = test_all_models()
            improvement = len(passing2) - len(passing)

            print(f"\nImprovement: {improvement} additional models fixed")
            print(f"New status: {len(passing2)}/100 compiling\n")

    else:
        print("\n✓ All models are compiling successfully!")

    return len(failing)

if __name__ == '__main__':
    sys.exit(min(1, main()))
