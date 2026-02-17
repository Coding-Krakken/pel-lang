#!/usr/bin/env python3
"""
Fix the 5 failing models by correcting duplicated type annotations
"""

import re
from pathlib import Path

FAILING_MODELS = [
    'benchmarks/pel_100/ecommerce/subscription_box.pel',
    'benchmarks/pel_100/other/fintech_lending.pel',
    'benchmarks/pel_100/saas/saas_cybersecurity_platform.pel',
    'benchmarks/pel_100/saas/saas_subscription.pel',
    'benchmarks/pel_100/saas/saas_tiered_pricing.pel',
]

def fix_duplicated_types(content):
    """Remove duplicated type parts like 'Rate per Month per Month per Month'"""
    
    fixes = []
    original = content
    
    # Fix: Rate per Month per Month per Month -> Rate per Month
    # Also handles: Rate per Month per Month per Year -> Rate per Year, etc.
    # Pattern: Rate followed by multiple "per X" clauses
    pattern = r'Rate(\s+per\s+\w+)+(?=\s*[=:\[])'
    
    def replace_rate(match):
        # Keep only the last "per X" part
        full_match = match.group(0)
        # Extract all "per X" phrases
        per_parts = re.findall(r'per\s+\w+', full_match, re.IGNORECASE)
        if per_parts:
            # Keep the last one
            last_per = per_parts[-1]
            return f'Rate {last_per}'
        return full_match
    
    new_content = re.sub(pattern, replace_rate, content, flags=re.IGNORECASE)
    if new_content != original:
        count = len(re.findall(pattern, original, flags=re.IGNORECASE))
        fixes.append(f"Fixed {count} duplicated rate type annotations")
        content = new_content
    
    # Fix: Fraction Fraction Fraction -> Fraction
    pattern = r'Fraction(\s+Fraction)+'
    replacement = 'Fraction'
    
    new_content = re.sub(pattern, replacement, content)
    if new_content != original:
        count = len(re.findall(pattern, original))
        fixes.append(f"Fixed {count} duplicated 'Fraction' annotations")
        content = new_content
    
    # Fix similar duplicates for other types
    for type_name in ['Currency', 'Count', 'TimeSeries']:
        # Match the type followed by its own name repeated
        pattern = f'{type_name}(?:\\s+{type_name})+' 
        replacement = type_name
        
        new_content = re.sub(pattern, replacement, content)
        if new_content != original:
            count = len(re.findall(pattern, original))
            if count > 0:
                fixes.append(f"Fixed {count} duplicated '{type_name}' annotations")
            content = new_content
    
    return content, fixes

def fix_malformed_timeseries(content):
    """Fix malformed TimeSeries syntax like 'TimeSeries<Type>>name[0]'"""
    
    fixes = []
    original = content
    
    # Pattern: var name: TimeSeries<Type>>name[...]
    # Should be: var name: TimeSeries<Type>
    # And the assignment should follow
    pattern = r'(var\s+\w+:\s*TimeSeries<[^>]+)>+(\w+)\['
    replacement = r'\1>\n  \2['
    
    new_content = re.sub(pattern, replacement, content)
    if new_content != original:
        fixes.append("Fixed malformed TimeSeries variable declarations")
        content = new_content
    
    return content, fixes

def fix_missing_type_colons(content):
    """Ensure all var/param have type colons"""
    
    fixes = []
    original = content
    
    # Find var declarations that look malformed
    # var name: TimeSeries<Type>>name[0] = value
    # This doubled closing bracket indicates a problem
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Fix: TimeSeries<Type>>name becomes TimeSeries<Type>
        if 'TimeSeries' in line and '>>' in line:
            # Extract the var name from pattern like "var name: TimeSeries<Type>>name"
            match = re.search(r'(var\s+(\w+):\s*TimeSeries<[^>]+)>>(\w+)(\[.+\])', line)
            if match:
                var_decl = match.group(1)
                var_name = match.group(2)
                index = match.group(4)
                # Reconstruct: "var name: TimeSeries<Type>"
                post_colon = line.find(':')
                post_equals = line.find('=')
                if post_equals > 0:
                    equation_part = line[post_equals:]
                    new_line = var_decl + '>' + '\n  ' + var_name + index + ' ' + equation_part
                    new_lines.append(new_line)
                    fixes.append("Fixed malformed TimeSeries var declaration")
                    continue
        
        new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    return new_content, fixes

def fix_model(model_path):
    """Apply all fixes to a single model"""
    
    print(f"\nFixing {Path(model_path).name}...")
    
    with open(model_path, 'r') as f:
        content = f.read()
    
    original_content = content
    all_fixes = []
    
    # Apply fixes in order
    content, fixes = fix_duplicated_types(content)
    all_fixes.extend(fixes)
    
    content, fixes = fix_malformed_timeseries(content)
    all_fixes.extend(fixes)
    
    content, fixes = fix_missing_type_colons(content)
    all_fixes.extend(fixes)
    
    if content != original_content:
        with open(model_path, 'w') as f:
            f.write(content)
        
        print(f"  ✓ Applied {len(all_fixes)} fix(es):")
        for fix in all_fixes:
            print(f"    • {fix}")
        return True
    else:
        print(f"  - No fixes needed")
        return False

def main():
    print("="*60)
    print("PEL-100: Fixing 5 Failing Model Compilation Issues")  
    print("="*60)
    
    fixed_count = 0
    for model_path in FAILING_MODELS:
        if Path(model_path).exists():
            if fix_model(model_path):
                fixed_count += 1
        else:
            print(f"\n✗ File not found: {model_path}")
    
    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count}/{len(FAILING_MODELS)} models")
    print(f"{'='*60}")
    
    return fixed_count

if __name__ == '__main__':
    main()
