from quark.core.token_ import Token, TokenTypes
from quark.core.ast import *

from typing import List, Tuple, Generator, Union, Iterator, Type


class QuarkParserError(Exception):
    def __init__(self):
        pass


class QuarkParser:
    def __init__(self, source_tokens: List[Token]):
        self._source_tokens = source_tokens

    @property
    def _current_token(self):
        return self._source_tokens[0]

    def _consume_token(self, n=1):
        for _ in range(n):
            self._source_tokens.pop(0)

    def _match(self, token_type: TokenTypes):
        return self._current_token.type == token_type

    def _match_let_expression(self) -> bool:
        return self._match(TokenTypes.LET)

    def _match_fun_expression(self) -> bool:
        return self._match(TokenTypes.FUN)

    def _match_lambda_expression(self) -> bool:
        return self._match(TokenTypes.LAMBDA)

    def _match_if_then_else_expression(self) -> bool:
        return self._match(TokenTypes.IF)

    def _match_application_expression(self) -> bool:
        return self._match(TokenTypes.LEFT_BRACKET)

    def _parse_program(self) -> Program:
        pass

    def _parse_expression(self) -> Type[Expression]:
        if self._match_let_expression():
            pass
        elif self._match_fun_expression():
            pass
        elif self._match_if_then_else_expression():
            pass
        elif self._match_lambda_expression():
            pass
        elif self._match_application_expression():
            pass
        else:  # must be or expression
            pass

    def _parse_let_expression(self) -> LetExpression:
        pass

    def _parse_fun_expression(self) -> FunExpression:
        pass

    def _parse_lambda_expression(self) -> LambdaExpression:
        pass

    def _parse_if_then_else_expression(self) -> IfThenElseExpression:
        pass

    def _parse_application_expression(self) -> ApplicationExpression:
        pass

    def _parse_or_expression(self) -> OrExpression:
        return OrExpression(
            self._parse_and_expression(), self._parse_or_expression_rhs()
        )

    def _parse_or_expression_rhs(self) -> Union[OrExpressionRhs, None]:
        pass

    def _parse_and_expression(self) -> AndExpression:
        return AndExpression(
            self._parse_not_expression(), self._parse_and_expression_rhs()
        )

    def _parse_and_expression_rhs(self) -> Union[AndExpressionRhs, None]:
        pass

    def _parse_not_expression(self) -> NotExpression:
        return NotExpression(
            self.parse_comparison_expression(), self._parse_not_expression_rhs()
        )

    def _parse_not_expression_rhs(self) -> Union[NotExpressionRhs, None]:
        pass

    def parse_comparison_expression(self) -> ComparisonExpression:
        return ComparisonExpression(
            self._parse_arithmetic_expression(), self._parse_comparison_expression_rhs()
        )

    def _parse_comparison_expression_rhs(self) -> Union[ComparisonExpressionRhs, None]:
        pass

    def _parse_arithmetic_expression(self) -> ArithmeticExpression:
        return ArithmeticExpression(
            self._parse_term_expression(), self._parse_arithmetic_expression_rhs()
        )

    def _parse_arithmetic_expression_rhs(self) -> Union[ArithmeticExpressionRhs, None]:
        pass

    def _parse_term_expression(self) -> TermExpression:
        return TermExpression(
            self._parse_factor_expression(), self._parse_term_expression_rhs()
        )

    def _parse_term_expression_rhs(self) -> Union[TermExpressionRhs, None]:
        pass

    def _parse_factor_expression(self) -> FactorExpression:
        return FactorExpression(
            self._parse_power_expression(), self._parse_factor_expression_rhs()
        )

    def _parse_factor_expression_rhs(self) -> Union[FactorExpressionRhs, None]:
        pass

    def _parse_power_expression(self) -> PowerExpression:
        return PowerExpression(
            self._parse_nil_expression(), self._parse_power_expression_rhs()
        )

    def _parse_power_expression_rhs(self) -> Union[PowerExpressionRhs, None]:
        pass

    def _parse_nil_expression(self) -> NilExpression:
        return NilExpression(
            self._parse_list_expression(), self._parse_nil_expression_rhs()
        )

    def _parse_nil_expression_rhs(self) -> Union[NilExpressionRhs, None]:
        pass

    def _parse_list_expression(self) -> ListExpression:
        return ListExpression(
            self._parse_list_access_expression(), self._parse_list_expression_rhs()
        )

    def _parse_list_expression_rhs(self) -> Union[ListExpressionRhs, None]:
        pass

    def _parse_list_access_expression(self) -> ListAccessExpression:
        return ListAccessExpression(
            self._parse_atom_expression(), self._parse_list_access_expression_rhs()
        )

    def _parse_list_access_expression_rhs(self) -> Union[ListAccessExpressionRhs, None]:
        pass

    def _parse_atom_expression(self) -> AtomExpression:

        if self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
            atom = AtomExpression(self._parse_expression_list())
            self._consume_token()
            return atom
        elif self._match(TokenTypes.STRING) or self._match(TokenTypes.INTEGER) \
                or self._match(TokenTypes.REAL) or self._match(TokenTypes.COMPLEX) \
                or self._match(TokenTypes.ID):
            atom = AtomExpression(self._current_token)
            self._consume_token()
            return atom
        raise QuarkParserError()  # todo

    def _parse_expression_list(self) -> ExpressionList:
        pass

    def _parse_id_list(self) -> IdList:
        pass
