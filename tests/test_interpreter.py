from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser


if __name__ == '__main__':
    closure = dict()
    while src_in := input('>>> '):
        scanner = QuarkScanner(src_in)
        tokens = scanner.tokens()
        parser = QuarkParser(tokens)
        ast = parser.build_parse_tree()
        for expr in ast:
            print(
                f'{type(expr)}\n'
                f'{repr(expr)}\n'
                f'{expr.json_repr}\n'
                f'{expr.execute(closure)}'
            )
