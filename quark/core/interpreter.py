from quark.core.token_ import TokenTypes, Token
from quark.core.scanner import QuarkScanner
from quark.core.parser import QuarkParser
from quark.core.ast import *

from quark.core.runtime.list import ListObject
from quark.core.runtime.integer import IntegerObject
from quark.core.runtime.real import RealObject
from quark.core.runtime.complex import ComplexObject
from quark.core.runtime.string import StringObject
from quark.core.runtime.boolean import BooleanObject

from typing import Tuple, Union, Dict, List
from enum import IntEnum


AnyAstNodeType = Union[
    'LetExpression', 'FunExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList', 'ImportStatement', 'ExportStatement', 'AnyExpressionType'
]

AnyExpressionType = Union[
    'LetExpression', 'FunExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList'
]

AnyStatementType = Union[
    'ImportStatement', 'ExportStatement', 'AnyExpressionType'
]

LiteralType = Union[
    'IntegerObject', 'RealObject', 'ComplexObject', 'StringObject', 'ListObject'
]

ExecutionResultType = Tuple[bool, Union[AnyExpressionType, LiteralType]]


ResultTypes: IntEnum = IntEnum(
    'TokenTypes', {n: i for i, n in enumerate( ('LITERAL_TYPE', 'EXPRESSION_TYPE', 'NONE_TYPE') )}
)


token_unary_operation_mapping = {
    TokenTypes.MINUS: lambda x: -x,
    TokenTypes.HEAD: lambda x: x.head,
    TokenTypes.TAIL: lambda x: x.tail,
    TokenTypes.NIL: lambda x: x.is_nil,
    TokenTypes.NOT: lambda x: not x
}


token_binary_operation_mapping = {
    TokenTypes.PLUS: lambda x, y: x + y,
    TokenTypes.MINUS: lambda x, y: x - y,
    TokenTypes.STAR: lambda x, y: x * y,
    TokenTypes.SLASH: lambda x, y: x / y,
    TokenTypes.DOUBLE_SLASH: lambda x, y: x // y,
    TokenTypes.DOUBLE_STAR: lambda x, y: x ** y,
    TokenTypes.PERCENT: lambda x, y: x % y,
    TokenTypes.SLASH_PERCENT: lambda x, y: None,  # todo
    TokenTypes.GREATER: lambda x, y: x > y,
    TokenTypes.LESS: lambda x, y: x < y,
    TokenTypes.GREATER_EQUAL: lambda x, y: x >= y,
    TokenTypes.LESS_EQUAL: lambda x, y: x <= y,
    TokenTypes.DOUBLE_EQUAL: lambda x, y: x == y,
    TokenTypes.EXCLAMATION_EQUAL: lambda x, y: x != y,
    TokenTypes.AND: lambda x, y: BooleanObject(x) and BooleanObject(y),
    TokenTypes.OR: lambda x, y: BooleanObject(x) or BooleanObject(y),
    TokenTypes.XOR: lambda x, y: BooleanObject(x) ^ BooleanObject(y)
}


class Interpreter:
    def __init__(self, ast):
        self._ast = ast
        self._root_closure: Dict[str, ExecutionResultType] = dict()

    def _execute_assignment_statement(self, stmt: AssignmentStatement, closure: dict) -> ExecutionResultType:
        vals = [self._execute_node(expr) for expr in stmt.expr_values]
        for name, val in zip(stmt.identifiers.only_raw_ids, vals):
            closure[name] = val
        return ResultTypes.NONE_TYPE, None

    def _execute_unary_expression(self, expr: UnaryExpression, closure: dict) -> ExecutionResultType:
        pass

    def _execute_binary_expression(self, expr: BinaryExpression, closure: dict) -> ExecutionResultType:
        pass

    def _execute_lambda_expression(self, expr: LambdaExpression, closure: dict) -> ExecutionResultType:
        pass

    def _execute_conditional_expression(self, expr: ConditionalExpression, closure: dict) -> ExecutionResultType:
        pass

    def _execute_node(self, node: AnyAstNodeType) -> ExecutionResultType:
        pass
