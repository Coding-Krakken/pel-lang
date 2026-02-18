#!/usr/bin/env python3
import json

data = json.load(open('benchmarks/PEL_100_RESULTS.json'))
compile_fail = [m for m in data if not m['compile_success']]
compile_pass = [m for m in data if m['compile_success']]
run_success = [m for m in data if m['run_success']]

print(f"Total models: {len(data)}")
print(f"Compile Success: {len(compile_pass)}")
print(f"Compile Failure: {len(compile_fail)}")
print(f"Run Success: {len(run_success)}")

if compile_fail:
    print(f"\nModels failing compilation ({len(compile_fail)}):")
    for m in compile_fail[:20]:
        print(f"  {m['category']}/{m['model']}")
else:
    print("\n✓ All models compiling!")
    
# Check run failures
run_fail = [m for m in data if m['compile_success'] and not m['run_success']]
if run_fail:
    print(f"\nModels compiling but not running ({len(run_fail)}):")
