from quark.core.token_ import Token, TokenTypes
from quark.core.scanner import QuarkScanner
from quark.core.ast import *

from typing import List, Union


AnyExpressionType = Union[
    LetExpression, FunExpression, LambdaExpression, IfThenElseExpression, ApplicationExpression,
    OrExpression, AndExpression, NotExpression, ComparisonExpression, ArithmeticExpression,
    TermExpression, FactorExpression, PowerExpression, NilExpression, ListExpression, 
    ListAccessExpression, AtomExpression, ExpressionList
]

AnyExpressionRhsType = Union[
    OrExpressionRhs, AndExpressionRhs, ComparisonExpressionRhs, ArithmeticExpressionRhs,
    TermExpressionRhs, ListExpressionRhs
]


class QuarkParserError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


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
        return self._source_tokens and self._current_token.type == token_type

    def _match_any_from(self, *token_types: TokenTypes):
        for t in token_types:
            if self._match(t):
                return True

    def _expect_any_from(self, *token_types: TokenTypes):
        if not self._match_any_from(token_types):
            raise QuarkParserError(
                f'SyntaxError: invalid syntax at {self._current_token.pos}'
            )

    def _expect(self, token_type: TokenTypes):
        if not self._match(token_type):
            raise QuarkParserError(
                f'SyntaxError: invalid syntax at {self._current_token.pos}. Expected {str(token_type)}.'
            )

    def _parse_expression(self) -> AnyExpressionType:
        if self._match(TokenTypes.LET):
            return self._parse_let_expression()
        elif self._match(TokenTypes.FUN):
            return self._parse_fun_expression()
        elif self._match(TokenTypes.IF):
            return self._parse_if_then_else_expression()
        elif self._match(TokenTypes.LAMBDA):
            return self._parse_lambda_expression()
        else:  # must be or expression
            return self._parse_or_expression()

    def _parse_let_expression(self) -> LetExpression:
        self._expect(TokenTypes.LET)
        self._consume_token()
        self._expect(TokenTypes.ID)
        argument_name = self._current_token
        self._consume_token()
        self._expect(TokenTypes.EQUAL)
        self._consume_token()
        argument_value = self._parse_expression()
        self._expect(TokenTypes.IN)
        self._consume_token()
        application_term = self._parse_expression()
        return LetExpression(argument_name, argument_value, application_term)

    def _parse_fun_expression(self) -> FunExpression:
        self._expect(TokenTypes.FUN)
        self._consume_token()
        self._expect(TokenTypes.ID)
        name = self._current_token
        self._consume_token()
        self._expect(TokenTypes.WITH)
        self._consume_token()
        argument_names = self._parse_id_list()
        self._expect(TokenTypes.EQUAL)
        self._consume_token()
        arguments = self._parse_expression_list()
        self._expect(TokenTypes.IN)
        self._consume_token()
        application_term = self._parse_expression()
        return FunExpression(name, argument_names, arguments, application_term)

    def _parse_lambda_expression(self) -> LambdaExpression:
        self._expect(TokenTypes.LAMBDA)
        self._consume_token()
        bound_variables = self._parse_id_list()
        self._expect(TokenTypes.PERIOD)
        self._consume_token()
        application_term = self._parse_expression()
        return LambdaExpression(bound_variables, application_term)

    def _parse_if_then_else_expression(self) -> IfThenElseExpression:
        self._expect(TokenTypes.IF)
        self._consume_token()
        condition = self._parse_expression()
        self._expect(TokenTypes.THEN)
        self._consume_token()
        consequent = self._parse_expression()
        if self._match(TokenTypes.ELSE):
            self._consume_token()
            alternative = self._parse_expression()
        else:
            alternative = None
        return IfThenElseExpression(condition, consequent, alternative)

    def _parse_or_expression(self):
        lhs = self._parse_and_expression()
        rhs = self._parse_or_expression_rhs()
        return lhs if not rhs else OrExpression(lhs, rhs)

    def _parse_or_expression_rhs(self) -> Union[OrExpressionRhs, None]:
        if self._match(TokenTypes.OR):
            self._consume_token()
            lhs = self._parse_and_expression()
            rhs = self._parse_or_expression_rhs()
            return OrExpressionRhs(lhs, rhs)
        else:
            return None

    def _parse_and_expression(self):
        lhs = self._parse_not_expression()
        rhs = self._parse_and_expression_rhs()
        return lhs if not rhs else AndExpression(lhs, rhs)

    def _parse_and_expression_rhs(self) -> Union[AndExpressionRhs, None]:
        if self._match_any_from(TokenTypes.AND):
            self._consume_token()
            lhs = self._parse_not_expression()
            rhs = self._parse_and_expression_rhs()
            return AndExpressionRhs(lhs, rhs)
        else:
            return None

    def _parse_not_expression(self) -> Union[NotExpression, ComparisonExpression]:
        if self._match(TokenTypes.NOT):
            operand = self._current_token
            self._consume_token()
            if self._match(TokenTypes.NOT):
                lhs = self._parse_not_expression()
            else:
                lhs = self.parse_comparison_expression()
            return NotExpression(operand, lhs)
        else:
            return self.parse_comparison_expression()

    def parse_comparison_expression(self) -> Union[ComparisonExpression, ArithmeticExpression]:
        lhs = self._parse_arithmetic_expression()
        rhs = self._parse_comparison_expression_rhs()
        return lhs if not rhs else ComparisonExpression(lhs, rhs)

    def _parse_comparison_expression_rhs(self) -> Union[ComparisonExpressionRhs, None]:
        if self._match_any_from(
            TokenTypes.DOUBLE_EQUAL, TokenTypes.EXCLAMATION_EQUAL, TokenTypes.GREATER,
            TokenTypes.GREATER_EQUAL, TokenTypes.LESS, TokenTypes.LESS_EQUAL
        ):
            operand = self._current_token
            self._consume_token()
            lhs = self._parse_arithmetic_expression()
            rhs = self._parse_comparison_expression_rhs()
            return ComparisonExpressionRhs(operand, lhs, rhs)
        else:
            return None

    def _parse_arithmetic_expression(self) -> Union[ArithmeticExpression, TermExpression]:
        lhs = self._parse_term_expression()
        rhs = self._parse_arithmetic_expression_rhs()
        return lhs if not rhs else ArithmeticExpression(lhs, rhs)

    def _parse_arithmetic_expression_rhs(self) -> Union[ArithmeticExpressionRhs, None]:
        if self._match_any_from(
                TokenTypes.PLUS, TokenTypes.MINUS
        ):
            operand = self._current_token
            self._consume_token()
            lhs = self._parse_term_expression()
            rhs = self._parse_arithmetic_expression_rhs()
            return ArithmeticExpressionRhs(operand, lhs, rhs)
        else:
            return None

    def _parse_term_expression(self) -> Union[TermExpression, FactorExpression]:
        lhs = self._parse_factor_expression()
        rhs = self._parse_term_expression_rhs()
        return lhs if not rhs else TermExpression(lhs, rhs)

    def _parse_term_expression_rhs(self) -> Union[TermExpressionRhs, None]:
        if self._match_any_from(
                TokenTypes.STAR, TokenTypes.SLASH, TokenTypes.DOUBLE_SLASH, TokenTypes.PERCENT
        ):
            operand = self._current_token
            self._consume_token()
            lhs = self._parse_factor_expression()
            rhs = self._parse_term_expression_rhs()
            return TermExpressionRhs(operand, lhs, rhs)
        else:
            return None

    def _parse_factor_expression(self) -> Union[FactorExpression, PowerExpression]:
        if self._match_any_from(
                TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.TILDE
        ):
            operand = self._current_token
            self._consume_token()
            if self._match_any_from(
                    TokenTypes.PLUS, TokenTypes.MINUS, TokenTypes.TILDE
            ):
                lhs = self._parse_factor_expression()
            else:
                lhs = self._parse_power_expression()
            return FactorExpression(operand, lhs)
        else:
            return self._parse_power_expression()

    def _parse_power_expression(self) -> PowerExpression:
        lhs = self._parse_nil_expression()
        rhs = self._parse_power_expression_rhs()
        return lhs if not rhs else PowerExpression(lhs, rhs)

    def _parse_power_expression_rhs(self) -> Union[PowerExpressionRhs, None]:
        if self._match(TokenTypes.DOUBLE_STAR):
            self._consume_token()
            lhs = self._parse_nil_expression()
            if self._match(TokenTypes.DOUBLE_STAR):
                rhs = self._parse_power_expression_rhs()
            else:
                rhs = None
            return PowerExpressionRhs(lhs, rhs)
        else:
            return None

    def _parse_nil_expression(self) -> Union[NilExpression, ListExpression]:
        if self._match(TokenTypes.NIL):
            operand = self._current_token
            self._consume_token()
            if self._match(TokenTypes.NIL):
                lhs = self._parse_nil_expression()
            else:
                lhs = self._parse_list_expression()
            return NilExpression(operand, lhs)
        else:
            return self._parse_list_expression()

    def _parse_list_expression(self) -> ListExpression:
        lhs = self._parse_list_access_expression()
        rhs = self._parse_list_expression_rhs()
        return lhs if not rhs else ListExpression(lhs, rhs)

    def _parse_list_expression_rhs(self) -> Union[ListExpressionRhs, None]:
        if self._match(TokenTypes.VERTICAL_BAR):
            self._consume_token()
            lhs = self._parse_list_access_expression()
            if self._match(TokenTypes.VERTICAL_BAR):
                rhs = self._parse_list_expression_rhs()
            else:
                rhs = None
            return ListExpressionRhs(lhs, rhs)
        else:
            return None

    def _parse_list_access_expression(self) -> Union[ListAccessExpression, AtomExpression]:
        if self._match_any_from(TokenTypes.CAR, TokenTypes.CDR):
            operand = self._current_token
            self._consume_token()
            if self._match_any_from(TokenTypes.CAR, TokenTypes.CDR):
                lhs = self._parse_list_access_expression()
            else:
                lhs = self._parse_application_expression()
            return ListAccessExpression(operand, lhs)
        else:
            return self._parse_application_expression()

    def _parse_application_expression(self):
        lhs = self._parse_atom_expression()
        if self._match(TokenTypes.ON):
            self._consume_token()
            rhs = self._parse_expression_list()
            return ApplicationExpression(lhs, rhs)
        return lhs

    def _parse_atom_expression(self) -> Union[AtomExpression, ApplicationExpression]:
        if self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
            atom = AtomExpression(self._parse_expression_list())
            self._consume_token()  # right parenthesis
            return atom
        elif self._match_any_from(TokenTypes.STRING, TokenTypes.INTEGER, TokenTypes.REAL,
                                  TokenTypes.ID, TokenTypes.COMPLEX):
            atom = AtomExpression(self._current_token)
            self._consume_token()
            return atom
        raise QuarkParserError()  # todo

    def _parse_expression_list(self) -> ExpressionList:
        lhs = self._parse_expression()
        if self._match(TokenTypes.COMMA):
            self._consume_token()
            rhs = self._parse_expression_list()
        else:
            rhs = None
        return ExpressionList(lhs, rhs)

    def _parse_id_list(self) -> IdList:
        self._expect(TokenTypes.ID)
        lhs = self._current_token
        self._consume_token()
        if self._match(TokenTypes.COMMA):
            self._consume_token()
            rhs = self._parse_id_list()
        else:
            rhs = None
        return IdList(lhs, rhs)

    def build_parse_tree(self) -> AnyExpressionType:
        return self._parse_expression()


if __name__ == '__main__':
    src_test = 'sin on 1'
    scanner = QuarkScanner(src_test)
    tokens = scanner.tokens()
    print(
        '\n'.join(repr(t) for t in tokens)
    )
    parser = QuarkParser(tokens)
    ast = parser.build_parse_tree()
