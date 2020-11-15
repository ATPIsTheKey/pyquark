from quark.core.parser import QuarkParser
from quark.core.scanner import QuarkScanner


if __name__ == '__main__':
    src_test = 'a;'
    lexer = QuarkScanner(src_test)
    parser = QuarkParser(lexer.tokens())
    while test := input('>>> '):
        lexer.reset(test)
        parser.reset(lexer.tokens())
        parse_tree = parser.build_parse_tree()
        print(parse_tree.node_json_repr)
        print(repr(parse_tree))
