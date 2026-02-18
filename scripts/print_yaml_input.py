from pathlib import Path

import yaml

p = Path('tests/conformance/testcases/typechecking/CONF-TYPE-001.yaml')
if not p.exists():
    print('MISSING')
else:
    spec = yaml.safe_load(p.read_text())
    print('RAW INPUT:')
    print(spec['input'])
    print('REPR:')
    print(repr(spec['input']))
