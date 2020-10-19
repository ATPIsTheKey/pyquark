from quark.core.token_ import get_token_type_precedence
from quark.core.scanner import QuarkScanner
from quark.core.ast2 import *

from typing import List, Union, Tuple

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
        else:
            # begin with default precedence
            return self._parse_logical_arithmetic_expression()

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

    def _parse_logical_arithmetic_expression(self, precedence: Union[int, None] = 1):
        # Precedence of quark operators from lowest to highest
        # binary("or", "xor")  : 1
        # binary("and")  : 2
        # unary("not")  : 3
        # binary("==", "!=", ">=", "<=", ">", "<")  : 4
        # binary("+", "-")  : 5
        # binary("*", "/", "//", "%", "/%")  : 6
        # unary("+", "-")  : 7
        # binary("**")  : 8
        # unary("nil")  : 9
        # binary("|")  : 10
        # unary("car", "cdr")  : 11
        # binary("on")  : 12
        if precedence == 1:
            return self._parse_unary_expression(precedence, (TokenTypes.XOR, TokenTypes.OR))
        elif precedence == 2:
            return self._parse_binary_expression(precedence, (TokenTypes.AND,))
        elif precedence == 3:
            return self._parse_unary_expression(precedence, (TokenTypes.NOT,))
        elif precedence == 4:
            return self._parse_binary_expression(
                precedence, (
                    TokenTypes.DOUBLE_EQUAL, TokenTypes.EXCLAMATION_EQUAL, TokenTypes.GREATER_EQUAL,
                    TokenTypes.LESS_EQUAL, TokenTypes.GREATER, TokenTypes.LESS
                )
            )
        elif precedence == 5:
            return self._parse_binary_expression(precedence, (TokenTypes.PLUS, TokenTypes.MINUS))
        elif precedence == 6:
            return self._parse_binary_expression(
                precedence, (
                    TokenTypes.STAR, TokenTypes.SLASH, TokenTypes.DOUBLE_SLASH, TokenTypes.PERCENT,
                    TokenTypes.SLASH_PERCENT
                )
            )
        elif precedence == 7:
            return self._parse_unary_expression(precedence, (TokenTypes.PLUS, TokenTypes.MINUS))
        elif precedence == 8:
            return self._parse_binary_expression(precedence, (TokenTypes.DOUBLE_STAR,))
        elif precedence == 9:
            return self._parse_unary_expression(precedence, (TokenTypes.NIL,))
        elif precedence == 10:
            return self._parse_binary_expression(precedence, (TokenTypes.VERTICAL_BAR,))
        elif precedence == 11:
            return self._parse_unary_expression(precedence, (TokenTypes.CAR, TokenTypes.CDR))
        elif precedence == 12:
            return self._parse_application_expression()
        else:
            return self._parse_atom_expression()

    def _parse_binary_expression(self, precedence: int, operators: Tuple[TokenTypes, ...]):
        lhs_expr = self._parse_logical_arithmetic_expression(precedence + 1)
        rhs_expr = self._parse_binary_expression_rhs(precedence, operators)
        return lhs_expr if not rhs_expr else BinaryExpression(lhs_expr)

    def _parse_binary_expression_rhs(
            self, precedence: int, operators: Tuple[TokenTypes, ...]
    ) -> Union[BinaryExpression, None]:
        if self._match_any_from(*operators):
            operand = self._current_token
            self._consume_token()
            lhs_expr = self._parse_logical_arithmetic_expression(precedence + 1)
            if self._match_any_from(*operators):
                rhs_expr = self._parse_binary_expression_rhs(precedence, operators)
            else:
                rhs_expr = None
            return BinaryExpression(lhs_expr, operand, rhs_expr)
        else:
            return None

    def _parse_unary_expression(self, precedence: int, operators: Tuple[TokenTypes, ...]):
        pass

    def _parse_unary_expression_rhs(self, operators: Tuple[TokenTypes]):
        pass

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
