from quark.core.scanner import QuarkScanner


if __name__ == '__main__':
    test = ';'
    lexer = QuarkScanner(test)
    while test := input('>>> '):
        lexer.reset(test)
        for t in lexer.get_tokens():
            print(repr(t))
