from quark.core.token_ import TokenTypes, Token
from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser
from quark.core.namespace import EvaluationContext, EnvironmentStack, CallStack


if __name__ == '__main__':
    evaluation_context = EvaluationContext()
    while src_in := input('>>> '):
        scanner = QuarkScanner(src_in)
        tokens = scanner.tokens()
        parser = QuarkParser(tokens)
        ast = parser.build_ast()
        print(
            '\n'.join(repr(ret) for ret in ast.execute(evaluation_context) if ret is not None)
        )
