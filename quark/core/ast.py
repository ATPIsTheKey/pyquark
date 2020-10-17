from quark.core.token_ import TokenTypes, Token

import abc
from typing import Union, List, Iterator


AnyExpressionType = Union[
    'LetExpression', 'FunExpression', 'LambdaExpression', 'IfThenElseExpression',
    'ApplicationExpression', 'OrExpression', 'AndExpression', 'NotExpression',
    'ComparisonExpression', 'ArithmeticExpression', 'TermExpression', 'FactorExpression',
    'PowerExpression', 'NilExpression', 'ListExpression', 'ListAccessExpression', 'AtomExpression',
    'ExpressionList'
]


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


class ExpressionRhs:  # todo: make full abc class
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
            'argument_value': self.argument_values.dump(),
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


class OrExpression(Expression):
    def __init__(self, lhs: 'AndExpression', rhs: Union['OrExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class OrExpressionRhs(ExpressionRhs):
    def __init__(self, lhs: 'AndExpression', rhs: Union['OrExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class AndExpression(Expression):
    def __init__(self, lhs: 'NotExpression', rhs: Union['AndExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class AndExpressionRhs:
    def __init__(self, lhs: 'NotExpression', rhs: Union['AndExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class NotExpression(Expression):
    def __init__(self, operand: Union[Token, None],
                 lhs: Union['NotExpression', 'ComparisonExpression']):
        self.operand = operand
        self.lhs = lhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand) if self.operand else None,
            'lhs': self.lhs.dump()
        }


class ComparisonExpression(Expression):
    def __init__(self, lhs: 'ArithmeticExpression',
                 rhs: Union['ComparisonExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class ComparisonExpressionRhs(ExpressionRhs):
    def __init__(self, operand: Token, lhs: 'ArithmeticExpression',
                 rhs: Union['ComparisonExpressionRhs', None]):
        self.operand = operand
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand),
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class ArithmeticExpression(Expression):
    def __init__(self, lhs: 'TermExpression',
                 rhs: Union['ArithmeticExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class ArithmeticExpressionRhs:
    def __init__(self, operand: Token, lhs: 'TermExpression',
                 rhs: Union['ArithmeticExpressionRhs', None]):
        self.operand = operand
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand),
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class TermExpression(Expression):
    def __init__(self, lhs: 'FactorExpression', rhs: Union['TermExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class TermExpressionRhs(ExpressionRhs):
    def __init__(self, operand: Token, lhs: 'FactorExpression', 
                 rhs: Union['TermExpressionRhs', None]):
        self.operand = operand
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand),
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class FactorExpression(Expression):
    def __init__(self, operand: Union[None, Token],
                 lhs: Union['FactorExpression', 'PowerExpression']):
        self.operand = operand
        self.lhs = lhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand) if self.operand else None,
            'lhs': self.lhs.dump()
        }


class PowerExpression(Expression):
    def __init__(self, lhs: 'NilExpression', rhs: Union['PowerExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class PowerExpressionRhs:
    def __init__(self, lhs: 'NilExpression', rhs: Union['NilExpression', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class NilExpression(Expression):
    def __init__(self, operand: Union[Token, None],
                 lhs: Union['ListExpression', 'AtomExpression']):
        self.operand = operand
        self.lhs = lhs

    @property
    def has_operand(self) -> bool:
        return bool(self.operand)

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand) if self.operand else None,
            'lhs': self.lhs.dump()
        }


class ListExpression(Expression):
    def __init__(self, lhs: 'ListAccessExpression', rhs: Union['ListExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class ListExpressionRhs(ExpressionRhs):
    def __init__(self, lhs: 'ListAccessExpression', rhs: Union['ListExpressionRhs', None]):
        self.lhs = lhs
        self.rhs = rhs

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'lhs': self.lhs.dump(),
            'rhs': self.rhs.dump() if self.rhs else None
        }


class ListAccessExpression(Expression):
    def __init__(self, operand: Union[Token, None],
                 lhs: Union['ListAccessExpression', 'AtomExpression']):
        self.operand = operand
        self.lhs = lhs

    @property
    def has_operand(self) -> bool:
        return bool(self.operand)

    def dump(self) -> dict:
        return {
            'expr_name': self.__class__.__name__,
            'operand': repr(self.operand) if self.operand else None,
            'lhs': self.lhs.dump() if self.lhs else None
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
    def __init__(self, root_expression: AnyExpressionType):
        self.root_expression = self._build_reduced_parse_tree(root_expression)

    def _build_reduced_parse_tree(
            self, root_expression: Union[AnyExpressionType, None]) -> AnyExpressionType:
        t = type(root_expression)

        if t == LetExpression:
            return LetExpression(
                root_expression.argument_name,
                self._build_reduced_parse_tree(root_expression.argument_value),
                self._build_reduced_parse_tree(root_expression.application_term)
            )
        elif t == IfThenElseExpression:
            return IfThenElseExpression(
                self._build_reduced_parse_tree(root_expression.condition),
                self._build_reduced_parse_tree(root_expression.consequent),
                self._build_reduced_parse_tree(root_expression.alternative)
            )
        elif t == FunExpression:
            return FunExpression(
                root_expression.name,
                root_expression.argument_names,
                self._build_reduced_parse_tree(root_expression.argument_values),
                self._build_reduced_parse_tree(root_expression.application_term)
            )
        elif t == LambdaExpression:
            return LambdaExpression(
                root_expression.bound_variables,
                self._build_reduced_parse_tree(root_expression.application_term)
            )
        elif t == ApplicationExpression:
            return ApplicationExpression(
                self._build_reduced_parse_tree(root_expression.function),
                self._build_reduced_parse_tree(root_expression.argument_values)
            )
        elif t == ExpressionList:
            return ExpressionList(
                self._build_reduced_parse_tree(root_expression.lhs),
                self._build_reduced_parse_tree(root_expression.rhs)
            )
        elif t in [
            OrExpression, AndExpression, ComparisonExpression, ArithmeticExpression,
            TermExpression, PowerExpression, ListExpression
        ]:
            if not root_expression.rhs:
                return self._build_reduced_parse_tree(root_expression.lhs)
            else:
                return type(root_expression)(
                    self._build_reduced_parse_tree(root_expression.lhs),
                    root_expression.rhs
                )
        elif t in [
            OrExpressionRhs, AndExpressionRhs, ComparisonExpressionRhs, ArithmeticExpressionRhs,
            TermExpressionRhs, PowerExpressionRhs, ListExpressionRhs
        ]:
            return type(root_expression)(
                    self._build_reduced_parse_tree(root_expression.lhs),
                    self._build_reduced_parse_tree(root_expression.rhs)
                )
        elif t in [
            NotExpression, FactorExpression, ListAccessExpression, NilExpression
        ]:
            if not root_expression.operand:
                return self._build_reduced_parse_tree(root_expression.lhs)
            else:
                return type(root_expression)(
                    root_expression.operand,
                    self._build_reduced_parse_tree(root_expression.lhs)
                )
        elif t == AtomExpression:
            if type(root_expression.val) == ExpressionList:
                return ExpressionList(
                    self._build_reduced_parse_tree(root_expression.val.lhs),
                    self._build_reduced_parse_tree(root_expression.val.rhs)
                )
        return root_expression


if __name__ == '__main__':
    pass
