from quark.core.token_ import TokenTypes, Token

import abc
from typing import Union, List, Iterator


AnyExpressionType = ...  # todo


class Program:
    def __init__(self, expressions: Union[Iterator[AnyExpressionType], List[AnyExpressionType]]):
        self.expressions = iter(expressions)

    def __iter__(self):
        return next(self.expressions)


class Expression:  # todo: make full abc class
    # @abc.abstractmethod
    # @property
    def semantic_description(self):
        pass

    @abc.abstractmethod
    def dump(self) -> dict:
        raise NotImplemented


class LetExpression(Expression):
    def __init__(self, argument_name: Token, argument_value: AnyExpressionType,
                 application_term: AnyExpressionType):
        self.argument_name = argument_name
        self.argument_value = argument_value
        self.application_term = application_term

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'argument_name': repr(self.argument_name),
            'argument_value': self.argument_value.dump(),
            'application_term': self.application_term.dump()
        }


class FunExpression(Expression):
    def __init__(self, name: Token, argument_names: 'IdList',
                 argument_values: 'ExpressionList', application_term: AnyExpressionType):
        self.name = name
        self.argument_names = argument_names
        self.argument_values = argument_values
        self.application_term = application_term

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'name': repr(self.name),
            'argument_names': self.argument_names.dump(),
            'argument_values': self.argument_values.dump(),
            'application_term': self.application_term.dump()
        }


class LambdaExpression(Expression):
    def __init__(self, bound_variables: 'IdList', application_term: AnyExpressionType):
        self.bound_variables = bound_variables
        self.application_term = application_term

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'bound_variables': self.bound_variables.dump(),
            'application_term': self.application_term.dump()
        }


class IfThenElseExpression(Expression):
    def __init__(self, condition: AnyExpressionType, consequent: AnyExpressionType,
                 alternative: Union[AnyExpressionType, None]):
        self.condition = condition
        self.consequent = consequent
        self.alternative = alternative

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'condition': self.condition.dump(),
            'consequent': self.consequent.dump(),
            'alternative': self.alternative.dump() if self.alternative else None
        }


class ApplicationExpression(Expression):
    def __init__(self, function: AnyExpressionType, argument_values: 'ExpressionList'):
        self.function = function
        self.argument_values = argument_values

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'function': self.function.dump(),
            'arguments': self.argument_values.dump()
        }


class BinaryExpression(Expression):
    def __init__(self, lhs_expr: AnyExpressionType, operand: Token, rhs_expr: AnyExpressionType):
        self.lhs_expr = lhs_expr
        self.operand = operand
        self.rhs_expr = rhs_expr

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs_expr': self.rhs_expr.dump(),
            'operand': repr(self.operand),
            'rhs_expr': self.rhs_expr.dump() if self.rhs_expr else None
        }


class UnaryExpression(Expression):
    def __init__(self, operand, expr):
        self.operand = operand
        self.expr = expr

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand),
            'expr': self.expr
        }


class AtomExpression(Expression):
    def __init__(self, val: Union['ExpressionList', 'Token']):
        self.val = val

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'val': repr(self.val) if isinstance(self.val, Token) else self.val.dump()
        }


class ExpressionList(Expression):
    def __init__(self, lhs: AnyExpressionType, rhs: Union['ExpressionList', None]):
        self.lhs = lhs
        self.rhs = rhs

    def __getitem__(self, i):
        if i == 0:
            return self.lhs
        else:
            return self.rhs[i - 1]

    def __setitem__(self, i, val):
        if i == 0:
            self.lhs = val
        else:
            self.rhs[i - 1] = val

    def __len__(self):
        return 1 + len(self.rhs) if self.rhs else 1

    def __iter__(self):
        yield self.lhs
        if self.rhs:
            yield from self.rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class IdList:
    def __init__(self, lhs: 'Token', rhs: Union['IdList', None]):
        self.lhs = lhs
        self.rhs = rhs

    def __getitem__(self, i):
        if i == 0:
            return self.lhs
        else:
            return self.rhs[i - 1]

    def __setitem__(self, i, val):
        if i == 0:
            self.lhs = val
        else:
            self.rhs[i - 1] = val

    def __len__(self):
        return 1 + len(self.rhs) if self.rhs else 1

    def __iter__(self):
        yield self.lhs
        if self.rhs:
            yield from self.rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': repr(self.lhs),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class AST:
    def __init__(self):
        pass

    def _annotate_tree(self):
        pass


if __name__ == '__main__':
    pass
