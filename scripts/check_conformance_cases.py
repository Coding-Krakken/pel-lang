"""Quick diagnostic: try compiling + typechecking a sample of conformance YAML cases."""
from pathlib import Path

import yaml

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.typechecker import TypeChecker


def check_typechecking_cases(n=20):
    base = Path('tests/conformance/testcases/typechecking')
    files = sorted(base.glob('*.yaml'))[:n]
    results = []
    for p in files:
        spec = yaml.safe_load(p.read_text())
        src = spec['input']
        try:
            lex = Lexer(src)
            tokens = lex.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            TypeChecker().check(ast)
            results.append((p.name, 'OK'))
        except Exception as e:
            results.append((p.name, f'ERROR: {type(e).__name__}: {e}'))
    return results


def check_runtime_cases(n=20):
    base = Path('tests/conformance/testcases/runtime')
    files = sorted(base.glob('*.yaml'))[:n]
    results = []
    for p in files:
        spec = yaml.safe_load(p.read_text())
        src = spec['input']
        try:
            lex = Lexer(src)
            tokens = lex.tokenize()
            parser = Parser(tokens)
            parser.parse()
            results.append((p.name, 'PARSE_OK'))
        except Exception as e:
            results.append((p.name, f'ERROR: {type(e).__name__}: {e}'))
    return results


if __name__ == '__main__':
    print('Typechecking samples:')
    for name, res in check_typechecking_cases(30):
        print(f'  - {name}: {res}')

    print('\nRuntime samples:')
    for name, res in check_runtime_cases(30):
        print(f'  - {name}: {res}')
