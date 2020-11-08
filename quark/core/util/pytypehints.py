from typing import Union

__all__ = [
    'AnyExpressionType', 'LiteralType', 'AnyStatementType'
]

AnyExpressionType = Union[
    'LetExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList'
]


AnyStatementType = Union[
    'ImportStatement', 'ExportStatement', AnyExpressionType
]


LiteralType = Union[
    'Integer', 'Real', 'Complex', 'String', 'List'
]


