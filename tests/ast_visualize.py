from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser
from quark.core.ast import *
import json


def main():
    src_test = 'let f = lambda n . if n == 0.0 then 1 else n * f on avg on n - 1, n, n + 1 in f 4;'
    scanner = QuarkScanner(src_test)
    tokens = scanner.tokens()
    parser = QuarkParser(tokens)
    parse_tree = parser.build_ast()
    print(
        json.dumps(parse_tree.node_dict_repr())
    )


if __name__ == '__main__':
    main()
