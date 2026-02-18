from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker
import yaml
from pathlib import Path

p = Path('tests/conformance/testcases/typechecking/CONF-TYPE-001.yaml')
if not p.exists():
    print('Test YAML not found:', p)
    raise SystemExit(1)

spec = yaml.safe_load(p.read_text())
source = spec['input']
print('=== SOURCE ===')
print(source)
print('=== COMPILE/TYPECHECK ===')
try:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    checker = TypeChecker()
    checker.check(ast)
    print('OK: parsed and typechecked')
except Exception as e:
    import traceback
    print('ERROR:', type(e).__name__, str(e))
    traceback.print_exc()
