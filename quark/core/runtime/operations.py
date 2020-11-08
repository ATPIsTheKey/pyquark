from quark.core.token_ import TokenTypes
from quark.core.runtime.boolean import BooleanObject


from typing import Union

__all__ = [
    'execute_unary_operation_from_token_type', 'execute_binary_operation_from_token_type'
]

LiteralType = Union[
    'IntegerObject', 'RealObject', 'ComplexObject', 'StringObject', 'ListObject'
]


class QuarkTypeError(Exception):
    def __init__(self, msg):
        super().__init__(msg)  # todo


_token_unary_operation_mapping = {
    TokenTypes.MINUS: lambda x: -x,
    TokenTypes.HEAD: lambda x: x.head,
    TokenTypes.TAIL: lambda x: x.tail,
    TokenTypes.NIL: lambda x: x.is_nil,
    TokenTypes.NOT: lambda x: not x
}


_token_binary_operation_mapping = {
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


def execute_unary_operation_from_token_type(t: TokenTypes, val: LiteralType):
    return _token_unary_operation_mapping[t](val)


def execute_binary_operation_from_token_type(t: TokenTypes, left_val: LiteralType, right_val: LiteralType):
    return _token_binary_operation_mapping[t](left_val, right_val)
