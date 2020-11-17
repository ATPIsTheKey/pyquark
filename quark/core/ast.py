import functools

from quark.core.runtime.boolean import BooleanObject
from quark.core.token_ import Token, TokenTypes
from quark.core.namespace import EvaluationContext, EnvironmentStack
# todo: fix those imports
from quark.core.runtime.list import ListObject
from quark.core.runtime.integer import IntegerObject
from quark.core.runtime.real import RealObject
from quark.core.runtime.complex import ComplexObject
from quark.core.runtime.string import StringObject

import abc
from typing import Union, Tuple, List, Callable, Any
import json

__all__ = [
    'StatementList', 'ImportStatement', 'ExportStatement', 'LetExpression', 'LambdaExpression',
    'ConditionalExpression', 'ApplicationExpression', 'BinaryExpression', 'UnaryExpression', 'AtomExpression',
    'ExpressionList', 'IdList', 'AssignmentStatement', 'AnyExpressionType', 'AnyStatementType', 'ConditionalBranch',
    'ListExpression'
]

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


def is_literal(val: Any) -> bool:
    return isinstance(val, (IntegerObject, RealObject, ComplexObject, StringObject, ListObject))


class ASTNode(abc.ABC):
    @abc.abstractmethod
    def node_dict_repr(self) -> dict:
        raise NotImplementedError

    @property
    def node_json_repr(self) -> str:
        return json.dumps(self.node_dict_repr)


class Statement(ASTNode, abc.ABC):
    pass


class Expression(ASTNode):
    @property
    @abc.abstractmethod
    def free_variables(self) -> set:
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self):
        raise NotImplementedError


class StatementList(ASTNode, list):
    append: Callable[[AnyStatementType], None]

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'statements': [stmt.node_dict_repr for stmt in self]
        }


class ImportStatement(Statement):
    def __init__(self, package_names: 'IdList', alias_names: Union['IdList', None]):
        self.package_names = package_names
        self.alias_names = alias_names

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'package_names': self.package_names.node_dict_repr,
            'alias_names': self.alias_names.node_dict_repr if self.alias_names else None
        }


class ExportStatement(Statement):
    def __init__(self, package_names: 'IdList', alias_names: Union['IdList', None]):
        self.package_names = package_names
        self.alias_names = alias_names

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'package_names': self.package_names.node_dict_repr,
            'alias_names': self.alias_names.node_dict_repr if self.alias_names else None
        }


class AssignmentStatement(Statement):
    def __init__(self, identifiers: 'IdList', expr_values: 'ExpressionList'):
        self.identifiers = identifiers
        self.expr_values = expr_values

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'names': self.identifiers.node_dict_repr,
            'values': self.expr_values.node_dict_repr
        }


class LetExpression(Expression):
    def __init__(self, bound_identifiers: 'IdList', initialiser_expressions: 'ExpressionList',
                 body_expression: Union[AnyExpressionType, None]):
        self.bound_identifiers = bound_identifiers
        self.initialiser_expressions = initialiser_expressions
        self.body_expression = body_expression

    @functools.cached_property
    def free_variables(self):
        return {*self.bound_identifiers.only_raw_ids} | self.initialiser_expressions.free_variables | \
               self.body_expression.free_variables

    def __repr__(self):
        return f'let {self.bound_identifiers.__repr__()} = ' \
               f'{self.initialiser_expressions.__repr__()} in {self.body_expression.__repr__()}'

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'bound_identifiers': self.bound_identifiers.node_dict_repr,
            'initialiser_expressions': self.initialiser_expressions.node_dict_repr,
            'body_expression': self.body_expression.node_dict_repr
        }


class LambdaExpression(Expression):
    def __init__(self, bound_identifiers: 'IdList', body_expression: AnyExpressionType):
        self.bound_variables = bound_identifiers
        self.body_expression = body_expression

    @functools.cached_property
    def free_variables(self) -> set:
        return set(self.bound_variables) | self.body_expression.free_variables

    @functools.cached_property
    def as_desugared_expression(self) -> 'LambdaExpression':
        inner_expr = LambdaExpression(IdList([self.bound_variables[-1]]), self.body_expression)
        for bound_var in reversed(self.bound_variables[:-1]):
            inner_expr = LambdaExpression(IdList([bound_var]), inner_expr)
        return inner_expr

    def __repr__(self):
        return f"\\{', '.join(var.val for var in self.bound_variables)} . {self.body_expression.__repr__()}"

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'bound_variable': self.bound_variables.node_dict_repr,
            'body_expression': self.body_expression.node_dict_repr
        }


class ConditionalBranch(ASTNode):
    def __init__(self, condition: AnyExpressionType, consequent: AnyExpressionType):
        self.condition = condition
        self.consequent = consequent

    @functools.cached_property
    def free_variables(self) -> set:
        return {self.condition.free_variables} | {self.consequent.free_variables}

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'condition': self.condition.node_dict_repr,
            'consequent': self.consequent.node_dict_repr
        }


class ConditionalExpression(Expression):
    def __init__(self, branches: List[ConditionalBranch], fallback: Union['AnyExpressionType', None] = None):
        self.branches = branches
        self.fallback = fallback

    @functools.cached_property
    def free_variables(self) -> set:
        if self.fallback:
            return {branch.free_variables for branch in self.branches}

    def __repr__(self):
        fmt = f"cond {', '.join(f'{branch.condition.__repr__()} then {branch.consequent.__repr__()}' for branch in self.branches)}"
        if self.fallback:
            fmt += f' otherwise {self.fallback.__repr__()}'
        return fmt

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'branches': [branch.node_dict_repr for branch in self.branches],
            'fallback': self.fallback.node_dict_repr if self.fallback else None
        }


class ApplicationExpression(Expression):
    def __init__(self, function: AnyExpressionType, argument_values: 'ExpressionList'):
        self.function = function
        self.argument_values = argument_values

    @functools.cached_property
    def free_variables(self) -> set:
        return self.function.free_variables | self.argument_values.free_variables

    @functools.cached_property
    def as_desugared_expression(self) -> 'ApplicationExpression':
        inner_expr = ApplicationExpression(self.function, ExpressionList(self.argument_values[0:1]))
        for arg in self.argument_values[1:]:
            inner_expr = ApplicationExpression(ExpressionList([inner_expr]), ExpressionList([arg]))
        return inner_expr

    def __repr__(self):
        return f'{self.function.__repr__()}({", ".join(arg.__repr__() for arg in self.argument_values)})'

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'function': self.function.node_dict_repr,
            'arguments': self.argument_values.node_dict_repr
        }


def repr_must_be_parenthesised(cls: Union['BinaryExpression', 'UnaryExpression'],
                               expr: Union['BinaryExpression', 'UnaryExpression']):
    return type(expr) in (BinaryExpression, UnaryExpression) and cls.operand.precedence > expr.operand.precedence


class BinaryExpression(Expression):
    def __init__(self, lhs_expr: AnyExpressionType, operand: Token, rhs_expr: AnyExpressionType):
        self.lhs_expr = lhs_expr
        self.operand = operand
        self.rhs_expr = rhs_expr
        
    @functools.cached_property
    def free_variables(self) -> set:
        return self.lhs_expr.free_variables | self.rhs_expr.free_variables

    def __repr__(self):
        left_repr, right_repr = self.lhs_expr.__repr__(), self.rhs_expr.__repr__()
        fmt = f"{f'({left_repr})' if repr_must_be_parenthesised(self, self.lhs_expr) else left_repr}"
        fmt += f' {self.operand.val} '
        fmt += f"{f'({right_repr})' if repr_must_be_parenthesised(self, self.rhs_expr) else right_repr}"
        return fmt

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'lhs_expr': self.lhs_expr.node_dict_repr if isinstance(self.lhs_expr, Expression) else self.lhs_expr,
            'operand': repr(self.operand),
            'rhs_expr': self.rhs_expr.node_dict_repr if isinstance(self.rhs_expr, Expression) else self.rhs_expr
        }


class UnaryExpression(Expression):
    def __init__(self, operand: Token, expr: AnyExpressionType):
        self.operand = operand
        self.expr = expr

    @functools.cached_property
    def free_variables(self) -> set:
        return self.expr.free_variables

    def __repr__(self):
        repr_ = self.expr.__repr__()
        return f"{self.operand.val} {f'({repr_})' if repr_must_be_parenthesised(self, self.expr) else repr_}"

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'operand': repr(self.operand),
            'expr': self.expr.node_dict_repr
        }


class ListExpression(Expression):
    def __init__(self, items: List[AnyExpressionType]):
        self.items = items

    @functools.cached_property
    def free_variables(self) -> set:
        return {item.free_variables for item in self.items}

    def __repr__(self):
        return f"[{', '.join(item.__repr__() for item in self.items)}]"

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'exprs': [item.node_dict_repr for item in self.items]
        }


class AtomExpression(Expression):
    def __init__(self, token: 'Token'):
        self.expr_token = token

    @functools.cached_property
    def free_variables(self) -> set:
        return {self.expr_token.val} if self.expr_token.type == TokenTypes.ID else set()

    def __repr__(self):
        return self.expr_token.val

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'expr_token': repr(self.expr_token)
        }


class ExpressionList(Expression, list):
    append: Callable[[AnyExpressionType], None]

    @functools.cached_property
    def free_variables(self) -> set:
        ret = set()
        for expr in self:
            ret |= expr.free_variables
        return ret

    def __repr__(self):
        return f"{', '.join(repr(item) for item in self)}"

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'expressions': [expr.node_dict_repr for expr in self]
        }


class IdList(ASTNode, list):
    append: Callable[[Token], None]

    @property
    def only_raw_ids(self):
        return [t.val for t in self]

    def __repr__(self):
        return f"{', '.join(t.val for t in self)}"

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'identifiers': [repr(id_) for id_ in self]
        }


if __name__ == '__main__':
    pass
