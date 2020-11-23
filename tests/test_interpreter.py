from quark.core.token_ import TokenTypes, Token
from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser
from quark.core.namespace import EvaluationContext, EnvironmentStack, CallStack


if __name__ == '__main__':
    closure = dict()
    while src_in := input('>>> '):
        scanner = QuarkScanner(src_in)
        tokens = scanner.tokens()
        parser = QuarkParser(tokens)
        ast = parser.build_parse_tree()
        for expr in ast:
            print(type(expr))
            print(repr(expr))
            print(expr.node_json_repr)
            print(expr.execute(closure))
