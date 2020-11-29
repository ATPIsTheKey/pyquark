from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser


if __name__ == '__main__':
    test = ';'
    lexer = QuarkScanner(test)
    parser = QuarkParser(lexer.tokens())
    while test := input('>>> '):
        lexer.reset(test)
        parser.reset(lexer.tokens())
        ast = parser.build_parse_tree()
        print(ast.json_repr)
        for node in ast:
            print(
                f'expr = "{node.__repr__()}"\n'
                f'variables = {node.variables}\n'
                f'free variables = {node.free_variables}\n'
                f'bound variables = {node.bound_variables}\n',
            )
