from quark.core.token_ import Token, TokenTypes
# todo: fix those imports
from quark.core.runtime.list import ListObject
from quark.core.runtime.integer import IntegerObject
from quark.core.runtime.real import RealObject
from quark.core.runtime.complex import ComplexObject
from quark.core.runtime.string import StringObject
from quark.core.runtime.boolean import BooleanObject

import functools
import itertools
from collections import namedtuple
import abc
from typing import Union, List, Callable
from copy import copy
import json

__all__ = [
    'StatementList', 'ImportStatement', 'ExportStatement', 'LetExpression',
    'FunctionExpression', 'ConditionalExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'AtomExpression', 'ExpressionList',
    'IdList', 'AssignmentStatement', 'AnyExpressionType', 'AnyStatementType',
    'ListExpression', 'Expression', 'Statement'
]

AnyAstNodeType = Union[
    'LetExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList', 'ImportStatement',
    'ExportStatement', 'AnyExpressionType'
]

AnyExpressionType = Union[
    'LetExpression', 'FunExpression', 'LambdaExpression', 'IfThenElseExpression',
    'ApplicationExpression', 'BinaryExpression', 'UnaryExpression', 'ExpressionList'
]

AnyStatementType = Union['ImportStatement', 'ExportStatement', 'AnyExpressionType']

LiteralType = type('LiteralType', (), {})()

NoneType = type('NoneType', (), {})()

ExecutionResult = namedtuple('ExecutionResult', ('type', 'val'))


class ASTNode(abc.ABC):
    @abc.abstractmethod
    def dict_repr(self) -> dict:
        raise NotImplementedError

    @property
    def json_repr(self) -> str:
        return json.dumps(self.dict_repr)


class Statement(ASTNode, abc.ABC):
    @abc.abstractmethod
    def execute(
            self, closure: dict, parent_closure: dict,
            callstack: List[AnyExpressionType] = None
    ) -> ExecutionResult:
        raise NotImplementedError


class Expression(Statement, abc.ABC):
    @property
    @abc.abstractmethod
    def variables(self) -> set:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def free_variables(self) -> set:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def bound_variables(self) -> set:
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self):
        raise NotImplementedError


class StatementList(ASTNode, list):
    append: Callable[[AnyStatementType], None]

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None,
            parent_closure: dict = None
    ) -> List[ExecutionResult]:
        return [stmt.execute(closure, callstack, parent_closure) for stmt in self]

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'statements': [stmt.dict_repr for stmt in self]
        }


class ImportStatement(Statement):
    def __init__(self, package_names: 'IdList', alias_names: Union['IdList', None]):
        self.package_names = package_names
        self.alias_names = alias_names

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None,
            parent_closure: dict = None
    ) -> ExecutionResult:
        return ExecutionResult(NoneType, None)

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'package_names': self.package_names.dict_repr,
            'alias_names': self.alias_names.dict_repr if self.alias_names else None
        }


class ExportStatement(Statement):
    def __init__(self, package_names: 'IdList', alias_names: Union['IdList', None]):
        self.package_names = package_names
        self.alias_names = alias_names

    def execute(
            self, closure: dict, parent_closure: dict,callstack: List[AnyExpressionType] = None
    ) -> ExecutionResult:
        raise NotImplementedError

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'package_names': self.package_names.dict_repr,
            'alias_names': self.alias_names.dict_repr if self.alias_names else None
        }


class AssignmentStatement(Statement):
    def __init__(self, names: 'IdList', exprs: 'ExpressionList'):
        self.names = names
        self.exprs = exprs

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        closure_copy = closure.copy()
        for name, expr in zip(self.names.raw, self.exprs):
            closure[name] = (expr, closure_copy if name in closure.keys() else None)
        return ExecutionResult(NoneType, None)

    def __repr__(self):
        return f"def ({', '.join(f'{name.raw} = {expr}' for name, expr in zip(self.names, self.exprs))})"

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'names': self.names.dict_repr,
            'value': self.exprs.dict_repr
        }


class LetExpression(Expression):
    def __init__(
            self, names: 'IdList', initialiser_expressions: 'ExpressionList',
            body_expression: Union[AnyExpressionType, None]
    ):
        self.names = names
        self.initialiser_expressions = initialiser_expressions
        self.body_expression = body_expression

    @functools.cached_property
    def variables(self) -> set:
        return functools.reduce(
            lambda x, y: x | y.variables, self.initialiser_expressions,
            self.body_expression.variables
        )

    @functools.cached_property
    def free_variables(self) -> set:
        return functools.reduce(
            lambda x, y: x | y.free_variables, self.initialiser_expressions,
            self.body_expression.free_variables
        ) - set(self.names.raw)

    @functools.cached_property
    def bound_variables(self) -> set:
        return functools.reduce(
            lambda x, y: x | y.bound_variables, self.initialiser_expressions,
            self.body_expression.bound_variables
        ) & set(self.names.raw)

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        closure_copy = closure.copy()
        for name, expr in zip(self.names.raw, self.initialiser_expressions):
            closure_copy[name] = (expr, None)
        result = self.body_expression.execute(closure_copy, callstack)
        return result if result.type == LiteralType else ExecutionResult(LetExpression, self)

    def __repr__(self):
        return (
            f'let {self.names.__repr__()} = '
            f'{self.initialiser_expressions.__repr__()} in {self.body_expression.__repr__()}'
        )

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'binding_variables': self.names.dict_repr,
            'initialiser_expressions': self.initialiser_expressions.dict_repr,
            'body_expression': self.body_expression.dict_repr
        }


class FunctionExpression(Expression):
    def __init__(self, argument_names: 'IdList', body_expression: AnyExpressionType):
        self.argument_names = argument_names
        self.body_expression = body_expression

    @functools.cached_property
    def variables(self) -> set:
        return self.body_expression.variables

    @functools.cached_property
    def free_variables(self) -> set:
        return self.body_expression.free_variables - set(self.argument_names.raw)

    @functools.cached_property
    def bound_variables(self) -> set:
        return set(self.argument_names.raw) & self.body_expression.free_variables

    def uncurry(self):
        if isinstance(self.body_expression, FunctionExpression):
            self.argument_names.extend(self.body_expression.uncurried.argument_names)
            self.body_expression = self.body_expression.uncurried.body_expression

    @functools.cached_property
    def uncurried(self) -> 'FunctionExpression':
        self_copy = copy(self)
        self_copy.uncurry()
        return self_copy

    def curry(self):
        for name in reversed(self.argument_names[1:]):
            self.body_expression = FunctionExpression(IdList([name]), self.body_expression)
        self.argument_names = IdList(self.argument_names[:1])

    @functools.cached_property
    def curried(self) -> 'FunctionExpression':
        self_copy = copy(self)
        self_copy.curry()
        return self_copy

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        closure_copy = closure.copy()
        if callstack:
            for name in self.argument_names.raw:
                closure_copy[name] = (
                    callstack.pop(),
                    (parent_closure if parent_closure else closure)
                    if name in closure_copy.keys() else None
                )
        if callstack:
            return self.body_expression.execute(closure_copy, callstack, closure)
        else:
            return self.body_expression.execute(closure_copy, callstack)

    def __repr__(self):
        return (
            f'fun :: {self.argument_names.__repr__()}'
            f' => {self.body_expression.__repr__()}'
        )

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'argument_names': self.argument_names.dict_repr,
            'body_expression': self.body_expression.dict_repr
        }


class ConditionalExpression(Expression):
    def __init__(
            self, condition: AnyExpressionType, consequent: AnyExpressionType,
            alternative: Union['AnyExpressionType', None] = None
    ):
        self.condition = condition
        self.consequent = consequent
        self.alternative = alternative

    @functools.cached_property
    def variables(self) -> set:
        if self.alternative:
            return (
                self.condition.variables | self.consequent.variables |
                self.alternative.variables
            )
        else:
            return self.condition.variables | self.consequent.variables

    @functools.cached_property
    def free_variables(self) -> set:
        if self.alternative:
            return (
                self.condition.free_variables | self.consequent.free_variables |
                self.alternative.free_variables
            )
        else:
            return self.condition.free_variables | self.consequent.free_variables

    @functools.cached_property
    def bound_variables(self) -> set:
        if self.alternative:
            return (
                self.condition.bound_variables | self.consequent.bound_variables |
                self.alternative.bound_variables
            )
        else:
            return self.condition.bound_variables | self.consequent.bound_variables

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        condition_result = self.condition.execute(closure)
        if condition_result.type == LiteralType:
            if condition_result.val == BooleanObject(True):
                return self.consequent.execute(closure)
            else:
                return self.alternative.execute(closure)
        else:
            return ExecutionResult(ConditionalExpression, self)

    def __repr__(self):
        fmt = f'if {self.condition.__repr__()} then {self.consequent.__repr__()}'
        if self.alternative:
            fmt += f' else {self.alternative.__repr__()}'
        return fmt

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'condition': self.condition.dict_repr,
            'consequent': self.consequent.dict_repr,
            'alternative': self.alternative.dict_repr if self.alternative else None
        }


class ApplicationExpression(Expression):
    def __init__(self, function: AnyExpressionType, arguments: 'ExpressionList'):
        self.function = function
        self.arguments = arguments

    @functools.cached_property
    def variables(self) -> set:
        return functools.reduce(
            lambda x, y: x | y.variables, self.arguments, self.function.variables
        )

    @functools.cached_property
    def free_variables(self) -> set:
        return functools.reduce(
            lambda x, y: x | y.free_variables, self.arguments,
            self.function.free_variables
        )

    @functools.cached_property
    def bound_variables(self) -> set:
        return functools.reduce(
            lambda x, y: x | y.bound_variables, self.arguments,
            self.function.bound_variables
        )

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        if callstack:
            callstack.extend(list(reversed(self.arguments)))  # todo: reversed? Why called stack then
        else:
            callstack = list(reversed(self.arguments))
        result = self.function.execute(closure, callstack)
        if result.type is not LiteralType:
            return ExecutionResult(ApplicationExpression, self)
        else:
            return result

    def __repr__(self):
        return f'({self.function.__repr__()})({self.arguments.__repr__()})'

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'function': self.function.dict_repr,
            'arguments': self.arguments.dict_repr
        }


def repr_must_be_parenthesised(
        cls: Union['BinaryExpression', 'UnaryExpression'],
        expr: Union['BinaryExpression', 'UnaryExpression']
) -> bool:
    return (
        type(expr) in {BinaryExpression, UnaryExpression} and
        cls.operand.precedence > expr.operand.precedence
    )


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


class BinaryExpression(Expression):
    def __init__(self, lhs_expr: AnyExpressionType, operand: Token, rhs_expr: AnyExpressionType):
        self.lhs_expr = lhs_expr
        self.operand = operand
        self.rhs_expr = rhs_expr

    @functools.cached_property
    def variables(self) -> set:
        return self.lhs_expr.variables | self.rhs_expr.variables

    @functools.cached_property
    def free_variables(self) -> set:
        return self.lhs_expr.free_variables | self.rhs_expr.free_variables

    @functools.cached_property
    def bound_variables(self) -> set:
        return self.lhs_expr.bound_variables | self.rhs_expr.bound_variables

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        if self.free_variables.issubset(closure.keys()):
            left_result = self.lhs_expr.execute(closure)
            right_result = self.rhs_expr.execute(closure)
            return ExecutionResult(
                LiteralType,
                _token_binary_operation_mapping[self.operand.type](
                    left_result.val, right_result.val
                )
            )
        else:
            return ExecutionResult(BinaryExpression, self)

    def __repr__(self):
        left_repr, right_repr = self.lhs_expr.__repr__(), self.rhs_expr.__repr__()
        return (
            f"{f'({left_repr})' if repr_must_be_parenthesised(self, self.lhs_expr) else left_repr}"
            f' {self.operand.raw} '
            f"{f'({right_repr})' if repr_must_be_parenthesised(self, self.rhs_expr) else right_repr}"
        )

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'lhs_expr': (
                self.lhs_expr.dict_repr if isinstance(self.lhs_expr, Expression) else
                self.lhs_expr
            ),
            'operand': repr(self.operand),
            'rhs_expr': (
                self.rhs_expr.dict_repr if isinstance(self.lhs_expr, Expression) else
                self.rhs_expr
            ),
        }


class UnaryExpression(Expression):
    def __init__(self, operand: Token, expr: AnyExpressionType):
        self.operand = operand
        self.expr = expr

    @functools.cached_property
    def variables(self) -> set:
        return self.expr.variables

    @functools.cached_property
    def free_variables(self) -> set:
        return self.expr.free_variables

    @functools.cached_property
    def bound_variables(self) -> set:
        return self.expr.bound_variables

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        if self.free_variables.issubset(closure.keys()):
            result = self.expr.execute(closure)
            return ExecutionResult(
                LiteralType, _token_unary_operation_mapping[self.operand.type](result)
            )
        else:
            return ExecutionResult(Expression, self)

    def __repr__(self):
        repr_ = self.expr.__repr__()
        return (
            f"{self.operand.raw} "
            f"{f'({repr_})' if repr_must_be_parenthesised(self, self.expr) else repr_}"
        )

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'operand': repr(self.operand),
            'expr': self.expr.dict_repr
        }


class ListExpression(Expression):
    def __init__(self, items: List[AnyExpressionType]):
        self.items = items

    @functools.cached_property
    def variables(self) -> set:
        return functools.reduce(lambda x, y: x | y.variables, self.items, set())

    @functools.cached_property
    def free_variables(self) -> set:
        return functools.reduce(lambda x, y: x | y.free_variables, self.items, set())

    @functools.cached_property
    def bound_variables(self) -> set:
        return functools.reduce(lambda x, y: x | y.bound_variables, self.items, set())

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        raise NotImplementedError

    def __repr__(self):
        return f"[{', '.join(item.__repr__() for item in self.items)}]"

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'exprs': [item.dict_repr for item in self.items]
        }


class AtomExpression(Expression):
    def __init__(self, expr: Token):
        self.token = expr

    @functools.cached_property
    def variables(self) -> set:
        return {self.token.raw} if self.token.type == TokenTypes.ID else set()

    @functools.cached_property
    def free_variables(self) -> set:
        return self.variables

    @property
    def bound_variables(self) -> set:
        return set()

    def execute(
            self, closure: dict, callstack: List[AnyExpressionType] = None, 
            parent_closure: dict = None
    ) -> ExecutionResult:
        if self.token.type == TokenTypes.INTEGER:
            return ExecutionResult(LiteralType, IntegerObject(self.token.raw))
        elif self.token.type == TokenTypes.REAL:
            return ExecutionResult(LiteralType, RealObject(self.token.raw))
        elif self.token.type == TokenTypes.COMPLEX:
            return ExecutionResult(LiteralType, ComplexObject(self.token.raw[:-2] + 'j'))
        elif self.token.type == TokenTypes.STRING:
            return ExecutionResult(LiteralType, StringObject(self.token))
        elif self.token.type == TokenTypes.BOOLEAN:
            return ExecutionResult(
                LiteralType, BooleanObject(1 if self.token.raw == 'true' else 0)
            )
        else:  # type ID
            if self.token.raw in closure.keys():
                expr, eval_closure = closure[self.token.raw]
                return expr.execute(eval_closure or closure, callstack)
            else:
                return ExecutionResult(AtomExpression, self)

    def __repr__(self):
        return self.token.raw

    @functools.cached_property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'type': self.token.type.name,
            'expr': self.token.raw
        }


class ExpressionList(ASTNode, list):
    append: Callable[[AnyExpressionType], None]

    def __repr__(self):
        return ', '.join(repr(item) for item in self)

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'expressions': [expr.dict_repr for expr in self]
        }


# todo: implement slicing
class IdList(ASTNode, list):
    append: Callable[[Token], None]

    @property
    def raw(self):
        return [id_.raw for id_ in self]

    def __repr__(self):
        return f"{', '.join(id_.raw for id_ in self)}"

    @property
    def dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'identifiers': [repr(id_) for id_ in self]
        }


if __name__ == '__main__':
    from quark.core.scanner import QuarkScanner
    from quark.core.parser import QuarkParser
    closure_, parent_closure_ = dict(), dict()
    while src_in := input('>>> '):
        scanner = QuarkScanner(src_in)
        tokens = scanner.tokens()
        parser = QuarkParser(tokens)
        ast = parser.build_parse_tree()
        for expr_ in ast:
            print(
                f'{type(expr_)}\n'
                f'{repr(expr_)}\n'
                f'{expr_.json_repr}\n'
                f'{expr_.execute(closure_, parent_closure_)}'
            )
