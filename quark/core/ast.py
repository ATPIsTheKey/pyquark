from quark.core.token_ import TokenTypes, Token

from typing import Type, Union, List, Tuple


class Program:
    pass


class Expression:
    pass


class LetExpression(Expression):
    pass


class FunExpression(Expression):
    pass


class LambdaExpression(Expression):
    pass


class IfThenElseExpression(Expression):
    pass


class ApplicationExpression(Expression):
    pass


class OrExpression(Expression):
    def __init__(self, lhs: 'AndExpression', rhs: 'OrExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class OrExpressionRhs(OrExpression):
    pass


class AndExpression(Expression):
    def __init__(self, lhs: 'NotExpression', rhs: 'AndExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class AndExpressionRhs(AndExpression):
    pass


class NotExpression(Expression):
    def __init__(self, lhs: 'ComparisonExpression', rhs: 'NotExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class NotExpressionRhs(NotExpression):
    pass


class ComparisonExpression(Expression):
    def __init__(self, lhs: 'ArithmeticExpression', rhs: 'ComparisonExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class ComparisonExpressionRhs(ComparisonExpression):
    pass


class ArithmeticExpression(Expression):
    def __init__(self, lhs: 'TermExpression', rhs: 'ArithmeticExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class ArithmeticExpressionRhs(ArithmeticExpression):
    pass


class TermExpression(Expression):
    def __init__(self, lhs: 'FactorExpression', rhs: 'TermExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class TermExpressionRhs(TermExpression):
    pass


class FactorExpression(Expression):
    def __init__(self, lhs: 'PowerExpression', rhs: 'FactorExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class FactorExpressionRhs(FactorExpression):
    pass


class PowerExpression(Expression):
    def __init__(self, lhs: 'NilExpression', rhs: 'PowerExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class PowerExpressionRhs(PowerExpression):
    pass


class NilExpression(Expression):
    def __init__(self, lhs: 'ListExpression', rhs: 'NilExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class NilExpressionRhs(NilExpression):
    pass


class ListExpression(Expression):
    def __init__(self, lhs: 'ListAccessExpression', rhs: 'ListExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class ListExpressionRhs(ListExpression):
    pass


class ListAccessExpression(Expression):
    def __init__(self, lhs: 'AtomExpression', rhs: 'ListAccessExpressionRhs'):
        self.lhs = lhs
        self.rhs = rhs


class ListAccessExpressionRhs(Expression):
    pass


class AtomExpression(Expression):
    def __init__(self, val: Union['ExpressionList', 'Token']):
        self.val = val


class ExpressionList(Expression):
    def __init__(self, expressions: List['Expression']):
        self.expressions = expressions


class IdList:
    def __init__(self, ids: List['Token']):
        self.ids = ids
