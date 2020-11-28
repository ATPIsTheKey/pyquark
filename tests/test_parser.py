from quark.core.parser import QuarkParser
from quark.core.scanner import QuarkScanner

if __name__ == '__main__':
    src_test = 'a;'
    lexer = QuarkScanner(src_test)
    parser = QuarkParser(lexer.tokens())
    while test := input('>>> '):
        lexer.reset(test)
        parser.reset(lexer.tokens())
        ast = parser.build_parse_tree()
        print(ast.node_json_repr)
        print(ast[0].__repr__())
