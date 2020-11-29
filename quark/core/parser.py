from quark.core.token_ import TokenTypes, Token
from quark.core.ast import (
    LetExpression, LambdaExpression, ConditionalExpression, ApplicationExpression,
    BinaryExpression, UnaryExpression, AtomExpression, ExpressionList, IdList,
    StatementList, ImportStatement, ExportStatement, AssignmentStatement, ListExpression
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
        return (
            not self._reached_end_of_source and
            self._current_token.type == token_type
        )

    def _match_any_from(self, *token_types: TokenTypes) -> bool:
        for t in token_types:
            if self._match(t):
                return True
        else:
            return False

    def _expect_any_from(self, *token_types: TokenTypes):
        if not self._reached_end_of_source and not self._match_any_from(*token_types):
            raise QuarkParserError(
                f'Expected any from {", ".join([t.name for t in token_types])}, '
                f'got {self._current_token.type.name}'
            )

    def _expect(self, token_type: TokenTypes):
        if not self._reached_end_of_source and not self._match(token_type):
            self._fmt_and_raise_syntax_error(
                f'Expected {token_type.name}, got {self._current_token.type.name}'
            )

    def _fmt_and_raise_syntax_error(self, msg: str):
        remaining_tokens_in_line, current_line_pos = '', self._current_token.line_pos
        for t in self._source_tokens[self._current_pos + 1:]:
            if t.line_pos != current_line_pos:
                return
            else:
                remaining_tokens_in_line += f'<{t.raw}> '
        raise QuarkParserError(
            f'SyntaxError at {self._current_token.pos}: {msg}\n'
            f'Remaining tokens in line: {remaining_tokens_in_line}'
        )

    def _parse_statement_list(self, **context) -> Union[StatementList, None]:
        statement_list = StatementList()
        while not self._reached_end_of_source:
            statement_list.append(self._parse_statement(**context))
            self._expect(TokenTypes.SEMICOLON)
            self._consume_token()
        return statement_list

    def _parse_statement(self, **context) -> AnyStatementType:
        if self._match(TokenTypes.IMPORT):
            return self._parse_import_statement(**context)
        elif self._match(TokenTypes.EXPORT):
            return self._parse_export_statement(**context)
        elif self._match(TokenTypes.ID):
            if ret := self._parse_assignment_statement(**context):
                return ret
        return self._parse_expression(**context)  # fallback

    def _parse_import_statement(self, **context) -> ImportStatement:
        self._expect(TokenTypes.IMPORT)
        self._consume_token()
        package_names = self._parse_id_list(**context)
        if self._match(TokenTypes.AS):
            self._consume_token()
            alias_names = self._parse_id_list(**context)
        else:
            alias_names = None
        return ImportStatement(package_names, alias_names)

    def _parse_export_statement(self, **context) -> ExportStatement:
        self._expect(TokenTypes.EXPORT)
        self._consume_token()
        package_names = self._parse_id_list(**context)
        if self._match(TokenTypes.AS):
            self._consume_token()
            alias_names = self._parse_id_list(**context)
        else:
            alias_names = None
        return ExportStatement(package_names, alias_names)

    def _parse_assignment_statement(self, **context) -> Union[AssignmentStatement, None]:
        self._expect(TokenTypes.ID)
        self._set_rewind_pos()
        names = self._parse_id_list(**context)
        if self._match(TokenTypes.EQUAL):
            self._consume_token()
        else:
            self._rewind()
            return
        expr_values = self._parse_expression_list()
        return AssignmentStatement(names, expr_values)

    def _parse_expression(self, **context) -> AnyExpressionType:
        if self._match_any_from(TokenTypes.LET, TokenTypes.LETREC):
            return self._parse_let_expression(**context)
        elif self._match(TokenTypes.IF):
            return self._parse_conditional_expression(**context)
        elif self._match(TokenTypes.BACKSLASH):
            return self._parse_lambda_expression(**context)
        elif self._match(TokenTypes.LEFT_BRACKET):
            return self._parse_list_expression(**context)
        else:
            return self._parse_logical_arithmetic_expression(**context)

    def _match_expression(self) -> bool:
        return not self._reached_end_of_source and (
                self._current_token.type in {
                    TokenTypes.LET, TokenTypes.IF, TokenTypes.LEFT_BRACKET,
                    TokenTypes.LEFT_PARENTHESIS, TokenTypes.ID
                } or
                self._current_token.is_literal()
            )

    def _parse_let_expression(self, **context) -> LetExpression:
        self._expect_any_from(TokenTypes.LET, TokenTypes.LETREC)
        make_rec = self._match(TokenTypes.LETREC)
        self._consume_token()
        binding_identifiers = self._parse_id_list(**context)
        self._expect(TokenTypes.EQUAL)
        self._consume_token()
        initialiser_expressions = self._parse_expression_list(**context)
        self._expect(TokenTypes.IN)
        self._consume_token()
        body_expression = self._parse_expression(**context)
        if make_rec:
            for i in range(len(binding_identifiers)):
                initialiser_expressions[i] = ApplicationExpression(
                    LambdaExpression.make_y_combinator(),
                    LambdaExpression(binding_identifiers[i], initialiser_expressions[i])
                )
        return LetExpression(
            binding_identifiers, initialiser_expressions, body_expression
        )

    def _make_desugared_lambda_expression(
            self, binding_identifiers: List[str], body_expression: AnyExpressionType,
    ) -> LambdaExpression:
        if binding_identifiers:
            return LambdaExpression(
                binding_identifiers[0],
                self._make_desugared_lambda_expression(
                    binding_identifiers[1:], body_expression
                )
            )
        else:
            return body_expression

    def _parse_lambda_expression(self, **context) -> LambdaExpression:
        self._expect(TokenTypes.BACKSLASH)
        self._consume_token()
        binding_identifiers = self._parse_id_list(**context)
        self._expect(TokenTypes.PERIOD)
        self._consume_token()
        body_expression = self._parse_expression(**context)
        return self._make_desugared_lambda_expression(
            binding_identifiers, body_expression
        )

    def _parse_conditional_expression(
            self, **context
    ) -> ConditionalExpression:
        self._expect(TokenTypes.ELIF if context.get('is_continuation') else TokenTypes.IF)
        self._consume_token()
        condition = self._parse_expression(**context)
        self._expect(TokenTypes.THEN)
        self._consume_token()
        consequent = self._parse_expression(**context)
        if self._match(TokenTypes.ELSE):
            self._consume_token()
            alternative = self._parse_expression()
            return ConditionalExpression(condition, consequent, alternative)
        elif self._match(TokenTypes.ELIF):
            return ConditionalExpression(
                condition, consequent,
                self._parse_conditional_expression(is_continuation=True)
            )
        else:
            return ConditionalExpression(condition, consequent)

    def _parse_list_expression(self, **context) -> ListExpression:
        self._expect(TokenTypes.LEFT_BRACKET)
        self._consume_token()
        items = []
        got_comma = True
        while got_comma:
            items.append(self._parse_expression(**context))
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        self._expect(TokenTypes.RIGHT_BRACKET)
        self._consume_token()
        return ListExpression(items)

    def _parse_logical_arithmetic_expression(
            self, min_precedence: Union[int, None] = 1, **context
    ):
        """
        Precedence of operators from lowest to highest
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
        if min_precedence == 1:
            return self._parse_binary_expression(
                min_precedence, (TokenTypes.XOR, TokenTypes.OR), **context
            )
        elif min_precedence == 2:
            return self._parse_binary_expression(
                min_precedence, (TokenTypes.AND,), **context
            )
        elif min_precedence == 3:
            return self._parse_unary_expression(
                min_precedence, (TokenTypes.NOT,), **context
            )
        elif min_precedence == 4:
            return self._parse_binary_expression(
                min_precedence, (
                    TokenTypes.DOUBLE_EQUAL, TokenTypes.EXCLAMATION_EQUAL,
                    TokenTypes.GREATER_EQUAL, TokenTypes.LESS_EQUAL, TokenTypes.GREATER,
                    TokenTypes.LESS
                ), **context
            )
        elif min_precedence == 5:
            return self._parse_binary_expression(
                min_precedence, (TokenTypes.PLUS, TokenTypes.MINUS), **context
            )
        elif min_precedence == 6:
            return self._parse_binary_expression(
                min_precedence, (
                    TokenTypes.STAR, TokenTypes.SLASH, TokenTypes.DOUBLE_SLASH,
                    TokenTypes.PERCENT, TokenTypes.SLASH_PERCENT
                ), **context
            )
        elif min_precedence == 7:
            return self._parse_unary_expression(
                min_precedence, (TokenTypes.PLUS, TokenTypes.MINUS), **context
            )
        elif min_precedence == 8:
            return self._parse_binary_expression(
                min_precedence, (TokenTypes.DOUBLE_STAR,), **context
            )
        elif min_precedence == 9:
            return self._parse_unary_expression(
                min_precedence, (TokenTypes.NIL,), **context
            )
        elif min_precedence == 10:
            return self._parse_binary_expression(
                min_precedence, (TokenTypes.VERTICAL_BAR,), **context
            )
        elif min_precedence == 11:
            return self._parse_unary_expression(
                min_precedence, (TokenTypes.HEAD, TokenTypes.TAIL), **context
            )
        else:
            return self._parse_application_expression(**context)

    def _parse_binary_expression(
            self, precedence: int, operators: Tuple[TokenTypes, ...], **context
    ) -> Union[BinaryExpression, AnyExpressionType]:
        lhs_expr = self._parse_logical_arithmetic_expression(
            precedence + 1, **context
        )
        if self._match_any_from(*operators):
            operand = self._current_token
            self._consume_token()
            if operand.is_left_associative():
                rhs_expr = self._parse_logical_arithmetic_expression(
                    precedence + 1, **context
                )
                expr = BinaryExpression(lhs_expr, operand, rhs_expr)
                while self._match_any_from(*operators):
                    operand = self._current_token
                    self._consume_token()
                    expr = BinaryExpression(
                        expr, operand, self._parse_logical_arithmetic_expression(
                            precedence + 1, **context
                        )
                    )
            else:
                rhs_expr = self._parse_binary_expression(precedence, operators, **context)
                expr = BinaryExpression(lhs_expr, operand, rhs_expr)
            return expr
        else:
            return lhs_expr

    def _parse_unary_expression(
            self, precedence: int, operators: Tuple[TokenTypes, ...], **context
    ) -> Union[UnaryExpression, AnyExpressionType]:
        if self._match_any_from(*operators):
            operand = self._current_token
            self._consume_token()
            if self._match_any_from(*operators):
                expr = self._parse_unary_expression(precedence, operators, **context)
            else:
                expr = self._parse_logical_arithmetic_expression(precedence + 1, **context)
            return UnaryExpression(operand, expr)
        else:
            return self._parse_logical_arithmetic_expression(precedence + 1, **context)

    def _parse_application_expression(
            self, **context
    ) -> Union[ApplicationExpression, AnyExpressionType]:
        function = self._parse_atom_expression(**context)
        if self._match(TokenTypes.AT):  # function composition
            self._consume_token()
            return ApplicationExpression(
                function, self._parse_application_expression(**context)
            )
        elif self._match_expression() and not context.get('without_application'):
            context['without_application'] = True
            expr = ApplicationExpression(
                function, self._parse_expression(**context))
            while self._match_expression():
                expr = ApplicationExpression(expr, self._parse_expression(**context))
            return expr
        else:
            return function

    def _parse_atom_expression(
            self, **context
    ) -> Union[AtomExpression, ApplicationExpression]:
        if self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
            context['without_application'] = False
            ret = self._parse_expression(**context)
            self._expect(TokenTypes.RIGHT_PARENTHESIS)
            self._consume_token()
            return ret
        elif self._current_token.is_literal():
            ret = AtomExpression(self._current_token.raw, self._current_token.type)
            self._consume_token()
            return ret
        else:
            return self._parse_expression(**context)  # todo
        self._fmt_and_raise_syntax_error()  # todo

    def _parse_expression_list(self, **context) -> ExpressionList:
        expr_list = ExpressionList()
        got_comma = True
        while got_comma and not self._reached_end_of_source:
            expr_list.append(self._parse_expression(**context))
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        return expr_list

    def _parse_id_list(self, **context) -> IdList:
        id_list = IdList()
        got_comma = True
        while got_comma and not self._reached_end_of_source:
            self._expect(TokenTypes.ID)
            id_list.append(self._current_token.raw)
            self._consume_token()
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        return id_list

    def build_parse_tree(self) -> AnyExpressionType:
        return self._parse_statement_list()
