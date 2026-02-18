#!/usr/bin/env python3
"""
Fix the 5 failing models by carefully correcting duplicated type annotations
- Only fix the 'Rate per Month per Month...' issue
- Leave TimeSeries syntax alone initially
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

def fix_rate_duplication(content):
    """Fix duplicated 'Rate per Month' patterns"""
    
    fixes = []
    original = content
    
    # Pattern 1: 'Rate per Month per Month per Month' -> 'Rate per Month'
    # Pattern 2: 'Rate per Month per Month per Year' -> 'Rate per Year'
    # Keep the last 'per X' part
    
    def fix_rate(match):
        full = match.group(0)
        # Extract the individual parts: "Rate", "per Month", "per Month", "per Month" etc
        parts = full.split()
        
        # Find all "per X" phrases (keeping indices)
        rate_keyword = 'Rate'
        per_phrases = []
        
        i = 1  # Skip 'Rate'
        while i < len(parts):
            if parts[i].lower() == 'per' and i + 1 < len(parts):
                per_phrases.append(' '.join(parts[i:i+2]))
                i += 2
            else:
                i += 1
        
        if per_phrases:
            # Keep only the last per phrase
            return f'Rate {per_phrases[-1]}'
        
        return full
    
    # Match: Rate followed by 2+ occurrences of "per X" pattern
    # This regex is complex, so let's use a simpler approach:
    # Find "Rate per X per X" patterns and deduplicate
    
    # Loop until no more changes
    iterations = 0
    max_iterations = 10
    
    while iterations < max_iterations:
        iterations += 1
        # Find pattern: "Rate per WORD per WORD..."
        pattern = r'Rate(\s+per\s+\w+){2,}(?=\s*[=:\[])'
        
        match = re.search(pattern, content)
        if not match:
            break
        
        full_match = match.group(0)
        # Extract all "per X" phrases
        per_parts = re.findall(r'per\s+\w+', full_match)
        
        if per_parts:
            # Keep only the last one
            replacement = f'Rate {per_parts[-1]}'
            content = content[:match.start()] + replacement + content[match.end():]
            fixes.append(f"Fixed: '{full_match}' -> '{replacement}'")
    
    if fixes:
        return content, fixes
    else:
        return original, []

def fix_timeseries_closing(content):
    """Fix malformed TimeSeries closing with '>>' followed by identifier"""
    
    fixes = []
    original = content
    
    # Pattern: "TimeSeries<Type>>varname[" should be "TimeSeries<Type>" and varname on next line
    # But be very careful - we just want to remove the ">>varname" part, not change the structure
    
    # Actually, let's check if this syntax is even used elsewhere successfully
    # If not, we might need to change the entire structure
    
    # For now, let's try: "TimeSeries<Type>>varname[0]" -> "TimeSeries<Type>\n  varname[0]"
    pattern = r'(var\s+\w+:\s*TimeSeries<[^>]+)>+(\w+)(\[)'
    
    def fix_ts(match):
        prefix = match.group(1)  # "var name: TimeSeries<Type"
        varname = match.group(2)  # duplicated var name  
        bracket = match.group(3)  # "["
        
        # Just return the first part with one closing >
        # The varname and bracket will be on line starting with varname
        return prefix + '>\n  ' + varname + bracket
    
    new_content = re.sub(pattern, fix_ts, content)
    if new_content != original:
        fixes.append("Fixed malformed TimeSeries variable syntax")
        return new_content, fixes
    
    return original, []

def fix_model(model_path):
    """Apply all fixes to a single model"""
    
    model_name = Path(model_path).name
    print(f"\nFixing {model_name}...", end='')
    
    with open(model_path, 'r') as f:
        content = f.read()
    
    original_content = content
    all_fixes = []
    
    # Apply fixes in order - only safe fixes
    content, fixes = fix_rate_duplication(content)
    all_fixes.extend(fixes)
    
    # TimeSeries fix is more risky, skip for now
    # content, fixes = fix_timeseries_closing(content)
    # all_fixes.extend(fixes)
    
    if content != original_content and all_fixes:
        with open(model_path, 'w') as f:
            f.write(content)
        
        print(f" ✓ {len(all_fixes)} fix(es)")
        for fix in all_fixes:
            print(f"    • {fix}")
        return True
    else:
        print(f" -  No safe fixes found")
        return False

def main():
    print("="*60)
    print("PEL-100: Fixing Duplicated Type Annotations")  
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
