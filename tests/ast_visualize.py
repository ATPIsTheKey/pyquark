from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser
from quark.core.ast import *
import json


def transform_ast_for_d5(ast: dict):
    name = ast['expr_name']
    ast.pop('expr_name')
    children = [
        transform_ast_for_d5(sub_ast) if isinstance(sub_ast, dict) else sub_ast for sub_ast in ast.values()
    ]
    return {
        'name': name,
        'children': children
    }


def main():
    src_test = 'not a * a'
    scanner = QuarkScanner(src_test)
    tokens = scanner.tokens()
    parser = QuarkParser(tokens)
    parse_tree = parser.build_parse_tree()
    print(
        json.dumps(parse_tree.dump())
    )


if __name__ == '__main__':
    main()
