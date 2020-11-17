from quark.core.token_ import TokenTypes, Token
from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser
from quark.core.ast import *
from quark.core.namespace import EvaluationContext, EnvironmentStack, CallStack

from typing import Union, List


AnyAstNodeType = Union[
    'LetExpression', 'FunExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList', 'ImportStatement', 'ExportStatement', 'AnyExpressionType'
]


class Compiler:
    def __init__(self, program: AnyAstNodeType):
        pass
