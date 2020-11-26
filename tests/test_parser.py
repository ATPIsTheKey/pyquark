from quark.core.parser import QuarkParser
from quark.core.scanner import QuarkScanner
from quark.core import ast

if __name__ == '__main__':
    src_test = 'a;'
    lexer = QuarkScanner(src_test)
    parser = QuarkParser(lexer.tokens())
    while test := input('>>> '):
        lexer.reset(test)
        parser.reset(lexer.tokens())
        ast = parser.build_parse_tree()
        print(ast.node_json_repr)
        # if isinstance(ast[0], ast.Expression):
        #     print(
        #         f'variables={repr(ast[0].variables)}',
        #         f'free_variables={repr(ast[0].free_variables)}',
        #         f'bound_variables={repr(ast[0].bound_variables)}'
        #     )
        # else:
        print(ast[0].__repr__())
