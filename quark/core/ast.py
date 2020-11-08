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
from quark.core.runtime.operations import execute_unary_operation_from_token_type, \
    execute_binary_operation_from_token_type

import abc
from typing import Union, Tuple, List, Callable, Any
import json

__all__ = [
    'StatementList', 'ImportStatement', 'ExportStatement', 'LetExpression', 'LambdaExpression',
    'ConditionalExpression', 'ApplicationExpression', 'BinaryExpression', 'UnaryExpression', 'AtomExpression',
    'ExpressionList', 'IdList', 'AssignmentStatement', 'AnyExpressionType', 'AnyStatementType'
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


class Statement(ASTNode):
    @abc.abstractmethod
    def execute(self, evaluation_context: 'EvaluationContext'):
        raise NotImplementedError


class Expression(ASTNode):
    @property
    @abc.abstractmethod
    def free_variables(self) -> set:
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, evaluation_context: 'EvaluationContext') -> Union[LiteralType, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self):
        raise NotImplementedError


class StatementList(ASTNode, list):
    append: Callable[[AnyStatementType], None]

    def execute(self, evaluation_context: 'EvaluationContext'):
        return [stmt.execute(evaluation_context) for stmt in self]

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

    def execute(self, evaluation_context: 'EvaluationContext'):
        raise NotImplementedError

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

    def execute(self, global_namespace: 'EnvironmentStack'):
        raise NotImplementedError

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

    def execute(self, evaluation_context: 'EvaluationContext'):
        for name, expr_value in zip(self.identifiers.only_raw_ids, self.expr_values.execute(evaluation_context)):
            evaluation_context.environment_stack.update_top_environment(name, expr_value)

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

    def execute(self, evaluation_context: 'EvaluationContext'):
        evaluation_context.environment_stack.push_new_top_environment()
        for name, val in zip(
                self.bound_identifiers.only_raw_ids, self.initialiser_expressions
        ):
            evaluation_context.environment_stack.update_top_environment(name, val)
        ret = self.body_expression.execute(evaluation_context)
        evaluation_context.environment_stack.pop_top_environment()
        return ret

    def __repr__(self):
        return f'let {self.bound_identifiers.__repr__()} = {self.initialiser_expressions.__repr__()} ' \
               f'{self.body_expression.__repr__()}'

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'bound_identifiers': self.bound_identifiers.node_dict_repr,
            'initialiser_expressions': self.initialiser_expressions.node_dict_repr,
            'body_expression': self.body_expression.node_dict_repr
        }


class LambdaExpression(Expression):
    def __init__(self, bound_identifier: 'Token', body_expression: AnyExpressionType):
        self.bound_variable = bound_identifier
        self.body_expression = body_expression

    @functools.cached_property
    def free_variables(self) -> set:
        return {self.bound_variable} | self.body_expression.free_variables

    def execute(self, evaluation_context: 'EvaluationContext') -> Union[LiteralType, 'LambdaExpression']:
        if partial_eval_only := not evaluation_context.call_stack:
            evaluation_context.environment_stack.update_top_environment(
                self.bound_variable.val, evaluation_context.call_stack[0]
            )
            evaluation_context.call_stack.consume()
            evaluation_context.call_stack.pop_consumed()

        ret = self.body_expression.execute(evaluation_context)
        if not isinstance(ret, LambdaExpression) and isinstance(ret, Expression):
            return LambdaExpression(self.bound_variable, ret)
        else:
            return ret

    def __repr__(self):
        return f"lambda {', '.join(self.bound_variable.val)} . {self.body_expression.__repr__()}"

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'bound_variable': self.bound_variable.val,
            'body_expression': self.body_expression.node_dict_repr
        }


class ConditionalExpression(Expression):
    def __init__(self, condition: AnyExpressionType, consequent: AnyExpressionType,
                 alternative: Union[AnyExpressionType, None]):
        self.condition = condition
        self.consequent = consequent
        self.alternative = alternative

    @functools.cached_property
    def free_variables(self) -> set:
        if self.alternative:
            return self.condition.free_variables | self.consequent.free_variables | self.alternative.free_variables
        else:
            return self.condition.free_variables | self.consequent.free_variables

    def execute(self, evaluation_context: 'EvaluationContext'):
        if self.condition.execute(evaluation_context) == BooleanObject(True):
            return self.consequent.execute(evaluation_context)
        elif self.alternative:
            return self.alternative.execute(evaluation_context)

    def __repr__(self):
        return f'if {self.condition.__repr__()} then {self.consequent.__repr__()} else {self.alternative.__repr__()}'

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'condition': self.condition.node_dict_repr,
            'consequent': self.consequent.node_dict_repr,
            'alternative': self.alternative.node_dict_repr if self.alternative else None
        }


class ApplicationExpression(Expression):
    def __init__(self, function: AnyExpressionType, argument_value: AnyExpressionType):
        self.function = function
        self.argument_value = argument_value

    @functools.cached_property
    def free_variables(self) -> set:
        return self.function.free_variables | self.argument_value.free_variables

    def execute(self, evaluation_context: 'EvaluationContext'):
        if type(self.function) is LambdaExpression:
            applicable_function = self.function
        elif type(self.function) is AtomExpression:
            if self.function.expr_token.type == TokenTypes.ID:
                applicable_function = evaluation_context.environment_stack.deep_search_name(
                    self.function.expr_token.val
                )
                if not type(applicable_function) == LambdaExpression:
                    return applicable_function.execute(evaluation_context)
            else:
                return self.function.execute(evaluation_context)
        elif type(self.function) is ApplicationExpression:
            applicable_function = self.function.execute(evaluation_context)
        else:
            raise Exception  # todo
        
        if is_literal(applicable_function):
            return applicable_function
        
        evaluation_context.environment_stack.push_new_top_environment()
        evaluation_context.call_stack.append(self.argument_value.execute(evaluation_context))
        ret = applicable_function.execute(evaluation_context)
        evaluation_context.environment_stack.pop_top_environment()

        return ret

    def __repr__(self):
        return f'{self.function.__repr__()}({", ".join(str(arg) for arg in self.argument_value.__repr__())})'

    @property
    def node_dict_repr(self) -> dict:
        return {
            'ast_node_name': self.__class__.__name__,
            'function': self.function.node_dict_repr,
            'arguments': self.argument_value.node_dict_repr if isinstance(self.argument_value, Expression)
            else self.argument_value.__repr__()
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
    
    def execute(self, evaluation_context: 'EvaluationContext') -> Union[AnyExpressionType, LiteralType]:
        left_val = self.lhs_expr.execute(evaluation_context) if isinstance(self.lhs_expr, Expression) else self.lhs_expr
        right_val = self.rhs_expr.execute(evaluation_context) if isinstance(self.rhs_expr, Expression) else self.rhs_expr
        print(left_val, right_val)
        return execute_binary_operation_from_token_type(self.operand.type, left_val, right_val)

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

    def execute(self, evaluation_context: 'EvaluationContext') -> LiteralType:
        val = self.expr.execute(evaluation_context)
        return execute_unary_operation_from_token_type(self.operand.type, val)

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


class AtomExpression(Expression):
    def __init__(self, token: 'Token'):
        self.expr_token = token

    @functools.cached_property
    def free_variables(self) -> set:
        return {self.expr_token.val} if self.expr_token.type == TokenTypes.ID else set()

    def execute(self, evaluation_context: 'EvaluationContext') -> Union[LiteralType, 'AtomExpression']:
        tok_type, tok_val = self.expr_token.type, self.expr_token.val
        if tok_type == TokenTypes.INTEGER:
            return IntegerObject(tok_val)
        elif tok_type == TokenTypes.REAL:
            return RealObject(tok_val)
        if tok_type == TokenTypes.COMPLEX:
            return ComplexObject(tok_val)
        elif tok_type == TokenTypes.STRING:
            return StringObject(tok_val)
        else:  # token is an ID
            if evaluation_context.environment_stack.contains_name_in_any_environment(tok_val):
                ret = evaluation_context.environment_stack.deep_search_name(tok_val)
                return ret.execute(evaluation_context) if isinstance(ret, Expression) else ret
            else:
                return self

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

    def execute(self, evaluation_context: 'EvaluationContext'):
        return [expr.execute(evaluation_context) for expr in self]

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
