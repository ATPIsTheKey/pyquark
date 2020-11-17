from quark.core.token_ import TokenTypes, Token
from quark.core.scanner import QuarkScanner
from quark.core.ast import (
    LetExpression, LambdaExpression, ConditionalExpression, ApplicationExpression,
    BinaryExpression, UnaryExpression, AtomExpression, ExpressionList, IdList, StatementList, ImportStatement,
    ExportStatement, AssignmentStatement, ConditionalBranch, ListExpression
)


from typing import List, Union, Tuple


__all__ = [
    'QuarkParser', 'QuarkParserError'
]

AnyExpressionType = Union[
    'LetExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList'
]


AnyStatementType = Union[
    'ImportStatement', 'ExportStatement', 'AnyExpressionType'
]


LiteralType = Union[
    'Integer', 'Real', 'Complex', 'String', 'List'
]


class QuarkParserError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class QuarkParser:
    def __init__(self, source_tokens: List[Token]):
        self._source_tokens = source_tokens
        self._current_pos = 0
        self._source_len = len(source_tokens)
        self._last_rewind_pos = None

    def reset(self, source_tokens: List[Token]):
        self.__init__(source_tokens)

    @property
    def _reached_end_of_source(self) -> bool:
        return self._current_pos >= self._source_len

    @property
    def _current_token(self):
        return self._source_tokens[self._current_pos]

    def _consume_token(self, n=1):
        self._current_pos += n

    def _set_rewind_pos(self):
        self._last_rewind_pos = self._current_pos

    def _rewind(self):
        self._current_pos = self._last_rewind_pos
        self._last_rewind_pos = None

    def _match(self, token_type: TokenTypes) -> bool:
        return not self._reached_end_of_source and self._current_token.type == token_type

    def _match_any_from(self, *token_types: TokenTypes) -> bool:
        for t in token_types:
            if self._match(t):
                return True

    def _expect_any_from(self, *token_types: TokenTypes):
        if not self._reached_end_of_source and not self._match_any_from(token_types):
            raise QuarkParserError(
                f'SyntaxError: invalid syntax at {self._current_token.pos}. '
                f'Expected any from {", ".join([t.name for t in token_types])}, '
                f'got {self._current_token.type.name}'
            )

    def _expect(self, token_type: TokenTypes):
        if not self._reached_end_of_source and not self._match(token_type):
            raise QuarkParserError(
                f'SyntaxError: invalid syntax at {self._current_token.pos}. '
                f'Expected {token_type.name}, '
                f'got {self._current_token.type.name}'
            )

    def _parse_statement_list(self) -> Union[StatementList, None]:
        statement_list = StatementList()
        while not self._reached_end_of_source:
            statement_list.append(t := self._parse_statement())
            self._expect(TokenTypes.SEMICOLON)
            self._consume_token()
        return statement_list

    def _parse_statement(self) -> AnyStatementType:
        if self._match(TokenTypes.IMPORT):
            return self._parse_import_statement()
        elif self._match(TokenTypes.EXPORT):
            return self._parse_export_statement()
        elif self._match(TokenTypes.ID):
            if ret := self._parse_assignment_statement():
                return ret
        return self._parse_expression()  # fallback

    def _parse_import_statement(self) -> ImportStatement:
        self._expect(TokenTypes.IMPORT)
        self._consume_token()
        package_names = self._parse_id_list()
        if self._match(TokenTypes.AS):
            self._consume_token()
            alias_names = self._parse_id_list()
        else:
            alias_names = None
        return ImportStatement(package_names, alias_names)

    def _parse_export_statement(self) -> ExportStatement:
        self._expect(TokenTypes.EXPORT)
        self._consume_token()
        package_names = self._parse_id_list()
        if self._match(TokenTypes.AS):
            self._consume_token()
            alias_names = self._parse_id_list()
        else:
            alias_names = None
        return ExportStatement(package_names, alias_names)

    def _parse_assignment_statement(self) -> Union[AssignmentStatement, None]:
        self._expect(TokenTypes.ID)
        self._set_rewind_pos()
        names = self._parse_id_list()
        if self._match(TokenTypes.EQUAL):
            self._consume_token()
        else:
            self._rewind()
            return
        expr_values = self._parse_expression_list()
        return AssignmentStatement(names, expr_values)

    def _parse_expression(self) -> AnyExpressionType:
        if self._match(TokenTypes.LET):
            return self._parse_let_expression()
        elif self._match(TokenTypes.COND):
            return self._parse_conditional_expression()
        elif self._match(TokenTypes.BACKSLASH):
            return self._parse_lambda_expression()
        elif self._match(TokenTypes.LEFT_BRACKET):
            return self._parse_list_expression()
        else:
            expr = self._parse_logical_arithmetic_expression()  # begin with default precedence
            if self._match(TokenTypes.LEFT_PARENTHESIS):
                self._consume_token()
                arguments = self._parse_expression_list()
                self._expect(TokenTypes.RIGHT_PARENTHESIS)
                self._consume_token()
                return ApplicationExpression(expr, arguments)
            else:
                return expr

    def _parse_let_expression(self) -> LetExpression:
        self._expect(TokenTypes.LET)
        self._consume_token()
        bound_identifiers = self._parse_id_list()
        self._expect(TokenTypes.EQUAL)
        self._consume_token()
        initialiser_expressions = self._parse_expression_list()
        self._expect(TokenTypes.IN)
        self._consume_token()
        body_expressions = self._parse_expression()
        return LetExpression(bound_identifiers, initialiser_expressions, body_expressions)

    def _parse_lambda_expression(self) -> LambdaExpression:
        self._expect(TokenTypes.BACKSLASH)
        self._consume_token()
        bound_variables = self._parse_id_list()
        self._expect(TokenTypes.PERIOD)
        self._consume_token()
        body_expression = self._parse_expression()
        return LambdaExpression(bound_variables, body_expression)

    def _parse_conditional_expression(self) -> ConditionalExpression:
        self._expect(TokenTypes.COND)
        self._consume_token()
        branches = []
        got_comma = True
        while got_comma:
            condition = self._parse_expression()
            self._expect(TokenTypes.THEN)
            self._consume_token()
            consequent = self._parse_expression()
            branches.append(ConditionalBranch(condition, consequent))
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        if self._match(TokenTypes.OTHERWISE):
            self._consume_token()
            return ConditionalExpression(branches, fallback=self._parse_expression())
        else:
            return ConditionalExpression(branches, None)

    def _parse_list_expression(self) -> ListExpression:
        self._expect(TokenTypes.LEFT_BRACKET)
        self._consume_token()
        items = []
        got_comma = True
        while got_comma:
            items.append(self._parse_expression())
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        self._expect(TokenTypes.RIGHT_BRACKET)
        self._consume_token()
        return ListExpression(items)

    @staticmethod
    def _restore_left_associativity(expr: BinaryExpression):  # todo: explain myself...
        while isinstance(expr.rhs_expr, BinaryExpression) and \
                expr.rhs_expr.operand.precedence == expr.operand.precedence:
            expr.rhs_expr.lhs_expr, expr.rhs_expr.rhs_expr = expr.rhs_expr.rhs_expr, expr.rhs_expr.lhs_expr
            expr.rhs_expr.operand, expr.operand = expr.operand, expr.rhs_expr.operand
            expr.rhs_expr.lhs_expr, expr.lhs_expr = expr.lhs_expr, expr.rhs_expr.lhs_expr
            expr.rhs_expr, expr.lhs_expr = expr.lhs_expr, expr.rhs_expr

    def _parse_logical_arithmetic_expression(self, precedence: Union[int, None] = 1):
        """
        Precedence of quark operators from lowest to highest
            binary("or", "xor")  : 1
            binary("and")  : 2
            unary("not")  : 3
            binary("==", "!=", ">=", "<=", ">", "<")  : 4
            binary("+", "-")  : 5
            binary("*", "/", "//", "%", "/%")  : 6
            unary("+", "-")  : 7
            binary("**")  : 8
            unary("nil")  : 9
            binary("|")  : 10
            unary("car", "cdr")  : 11
        """
        if precedence == 1:
            return self._parse_binary_expression(
                precedence, (TokenTypes.XOR, TokenTypes.OR), is_left_associative=True
            )
        elif precedence == 2:
            return self._parse_binary_expression(
                precedence, (TokenTypes.AND,), is_left_associative=True
            )
        elif precedence == 3:
            return self._parse_unary_expression(
                precedence, (TokenTypes.NOT,)
            )
        elif precedence == 4:
            return self._parse_binary_expression(
                precedence, (
                    TokenTypes.DOUBLE_EQUAL, TokenTypes.EXCLAMATION_EQUAL, TokenTypes.GREATER_EQUAL,
                    TokenTypes.LESS_EQUAL, TokenTypes.GREATER, TokenTypes.LESS
                ), is_left_associative=True
            )
        elif precedence == 5:
            return self._parse_binary_expression(
                precedence, (TokenTypes.PLUS, TokenTypes.MINUS), is_left_associative=True
            )
        elif precedence == 6:
            return self._parse_binary_expression(
                precedence, (
                    TokenTypes.STAR, TokenTypes.SLASH, TokenTypes.DOUBLE_SLASH, TokenTypes.PERCENT,
                    TokenTypes.SLASH_PERCENT
                ), is_left_associative=True
            )
        elif precedence == 7:
            return self._parse_unary_expression(
                precedence, (TokenTypes.PLUS, TokenTypes.MINUS)
            )
        elif precedence == 8:
            return self._parse_binary_expression(
                precedence, (TokenTypes.DOUBLE_STAR,)
            )
        elif precedence == 9:
            return self._parse_unary_expression(
                precedence, (TokenTypes.NIL,)
            )
        elif precedence == 10:
            return self._parse_binary_expression(
                precedence, (TokenTypes.VERTICAL_BAR,)
            )
        elif precedence == 11:
            return self._parse_unary_expression(
                precedence, (TokenTypes.HEAD, TokenTypes.TAIL)
            )
        return self._parse_application_expression()

    def _parse_binary_expression(
            self, precedence: int, operators: Tuple[TokenTypes, ...], is_left_associative=False
    ) -> Union[BinaryExpression, AnyExpressionType]:
        lhs_expr = self._parse_logical_arithmetic_expression(precedence + 1)
        if self._match_any_from(*operators):
            operand = self._current_token
            self._consume_token()
            rhs_expr = self._parse_binary_expression(precedence, operators)
            expr = BinaryExpression(lhs_expr, operand, rhs_expr)
            if is_left_associative:
                self._restore_left_associativity(expr)
            return expr
        else:
            return lhs_expr

    def _parse_unary_expression(
            self, precedence: int, operators: Tuple[TokenTypes, ...]
    ) -> Union[UnaryExpression, AnyExpressionType]:
        if self._match_any_from(*operators):
            operand = self._current_token
            self._consume_token()
            if self._match_any_from(*operators):
                expr = self._parse_unary_expression(precedence, operators)
            else:
                expr = self._parse_logical_arithmetic_expression(precedence + 1)
            return UnaryExpression(operand, expr)
        else:
            return self._parse_logical_arithmetic_expression(precedence + 1)

    def _parse_application_expression(self) -> Union[ApplicationExpression, AnyExpressionType]:
        expr = self._parse_atom_expression()
        if self._match(TokenTypes.AT):  # function composition
            self._consume_token()
            return ApplicationExpression(expr, ExpressionList([self._parse_application_expression()]))
        elif self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
            arguments = self._parse_expression_list()
            self._expect(TokenTypes.RIGHT_PARENTHESIS)
            self._consume_token()
            return ApplicationExpression(expr, arguments)
        else:
            return expr

    def _parse_atom_expression(self) -> Union[AtomExpression, ApplicationExpression]:
        if self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
            ret = self._parse_expression()
            self._expect(TokenTypes.RIGHT_PARENTHESIS)
            self._consume_token()
            return ret
        elif self._match_any_from(TokenTypes.STRING, TokenTypes.INTEGER, TokenTypes.REAL,
                                  TokenTypes.ID, TokenTypes.COMPLEX):
            ret = AtomExpression(self._current_token)
            self._consume_token()
            return ret
        else:
            return self._parse_expression()  # todo
        raise QuarkParserError(
            f'SyntaxError: invalid syntax at {self._current_token.pos}, currently at {self._source_tokens[self._current_pos:]}'
        )

    def _parse_expression_list(self) -> ExpressionList:
        expr_list = ExpressionList()
        got_comma = True
        while got_comma and not self._reached_end_of_source:
            expr_list.append(self._parse_expression())
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        return expr_list

    def _parse_id_list(self) -> IdList:
        id_list = IdList()
        got_comma = True
        while got_comma and not self._reached_end_of_source:
            self._expect(TokenTypes.ID)
            id_list.append(self._current_token)
            self._consume_token()
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        return id_list

    def build_parse_tree(self) -> AnyExpressionType:
        return self._parse_statement_list()
