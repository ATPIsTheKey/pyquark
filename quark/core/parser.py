from quark.core.token_ import TokenTypes, Token
from quark.core.ast import (
    LetExpression, FunctionExpression, ConditionalExpression, ApplicationExpression,
    BinaryExpression, UnaryExpression, AtomExpression, ExpressionList, IdList,
    StatementList, ImportStatement, ExportStatement, AssignmentStatement, ListExpression
)

from typing import List, Union, Tuple
import itertools

__all__ = ['QuarkParser', 'QuarkParserError']

AnyExpressionType = Union[
    'LetExpression', 'LambdaExpression', 'IfThenElseExpression', 'ApplicationExpression',
    'BinaryExpression', 'UnaryExpression', 'ExpressionList'
]

AnyStatementType = Union['ImportStatement', 'ExportStatement', 'AnyExpressionType']

LiteralType = Union['Integer', 'Real', 'Complex', 'String', 'List']


unique_id = itertools.count()


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
                f'Expected any from {", ".join(t.name for t in token_types)}, '
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
        elif self._match(TokenTypes.DEF):
            return self._parse_def_statement(**context)
        elif self._match(TokenTypes.DEFUN):
            return self._parse_defun_statement(**context)
        else:
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

    def _parse_defun_body(self, **context) -> Tuple[Token, AnyExpressionType]:
        self._expect(TokenTypes.ID)
        name = self._current_token
        self._consume_token()
        self._expect(TokenTypes.DOUBLE_COLON)
        self._consume_token()
        argument_names = self._parse_id_list(**context)
        self._expect(TokenTypes.EQUAL_GREATER)
        self._consume_token()
        body_expression = self._parse_expression(**context)
        return name, FunctionExpression(argument_names, body_expression)

    def _parse_defun_statement(self, **context) -> AssignmentStatement:
        self._expect(TokenTypes.DEFUN)
        self._consume_token()
        names, function_exprs = IdList([]), ExpressionList([])
        if is_batch_def := self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
        while True:
            name, expr = self._parse_defun_body(**context)
            names.append(name)
            function_exprs.append(expr)
            if self._match(TokenTypes.COMMA):
                self._consume_token()
            else:
                break
        if is_batch_def:
            self._consume_token()
        return AssignmentStatement(names, function_exprs)

    def _parse_def_body(self, **context) -> Tuple[Token, AnyExpressionType]:
        name = self._current_token
        self._consume_token()
        self._expect(TokenTypes.EQUAL)
        self._consume_token()
        expr = self._parse_expression(**context)
        return name, expr

    # todo: batch definition
    def _parse_def_statement(self, **context) -> AssignmentStatement:
        self._expect(TokenTypes.DEF)
        self._consume_token()
        names, exprs = IdList([]), ExpressionList([])
        if is_batch_def := self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
        while True:
            name, expr = self._parse_def_body(**context)
            names.append(name)
            exprs.append(expr)
            if self._match(TokenTypes.COMMA):
                self._consume_token()
            else:
                break
        if is_batch_def:
            self._consume_token()
        return AssignmentStatement(names, exprs)

    def _parse_expression(self, **context) -> AnyExpressionType:
        if self._match_any_from(TokenTypes.LET, TokenTypes.LETREC):
            return self._parse_let_expression(**context)
        elif self._match(TokenTypes.IF):
            return self._parse_conditional_expression(**context)
        elif self._match(TokenTypes.BACKSLASH):
            return self._parse_function_expression(**context)
        elif self._match(TokenTypes.LEFT_BRACKET):
            return self._parse_list_expression(**context)
        elif self._match(TokenTypes.FUN):
            return self._parse_function_expression(**context)
        elif self._match(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS):
            return self._parse_guard_expression(**context)
        else:
            return self._parse_operator_expression(**context)

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
        self._consume_token()
        names = self._parse_id_list(**context)
        self._expect(TokenTypes.EQUAL)
        self._consume_token()
        initialiser_expressions = self._parse_expression_list(**context)
        self._expect(TokenTypes.IN)
        self._consume_token()
        body_expression = self._parse_expression(**context)
        return LetExpression(
            names, initialiser_expressions, body_expression
        )

    def _parse_function_expression(self, **context) -> FunctionExpression:
        """ Function expressions are alpha converted at parse time """
        self._expect(TokenTypes.FUN)
        self._consume_token()
        self._expect(TokenTypes.DOUBLE_COLON)
        self._consume_token()
        argument_names = self._parse_id_list(**context)
        new_vars = IdList([
            Token(TokenTypes.ID, f'${str(next(unique_id))}', (0, 0))
            for _ in range(len(argument_names))
        ])
        if remapped_vars := context.get('remapped_vars'):
            remapped_vars.update(dict(zip(argument_names.raw, new_vars)))
        else:
            remapped_vars = dict(zip(argument_names.raw, new_vars))
        self._expect(TokenTypes.EQUAL_GREATER)
        self._consume_token()
        context.update({'remapped_vars': remapped_vars})
        body_expression = self._parse_expression(**context)
        return FunctionExpression(new_vars, body_expression)

    def _parse_guard_expression(self, **context) -> ConditionalExpression:
        self._expect(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS)
        self._consume_token()
        expr = self._parse_guard_body(**context)
        self._expect(TokenTypes.RIGHT_PARENTHESIS)
        self._consume_token()
        return expr

    def _parse_guard_body(
            self, **context
    ) -> Union[ConditionalExpression, AnyExpressionType]:
        consequent = self._parse_expression(**context)
        self._expect(TokenTypes.VERTICAL_BAR)
        self._consume_token()
        if self._match(TokenTypes.ELLIPSIS):
            self._consume_token()
            return consequent
        condition = self._parse_expression(**context)
        if self._match(TokenTypes.COMMA):
            self._consume_token()
        if not self._match(TokenTypes.RIGHT_PARENTHESIS):
            alternative = self._parse_guard_body(**context)
        else:
            alternative = None
        return ConditionalExpression(condition, consequent, alternative)

    def _parse_conditional_expression(self, **context) -> ConditionalExpression:
        self._expect(TokenTypes.ELIF if context.get('is_continuation') else TokenTypes.IF)
        self._consume_token()
        condition = self._parse_expression(**context)
        self._expect(TokenTypes.THEN)
        self._consume_token()
        consequent = self._parse_expression(**context)
        if self._match(TokenTypes.ELSE):
            self._consume_token()
            context.update({'continuation': False})
            alternative = self._parse_expression(**context)
            return ConditionalExpression(condition, consequent, alternative)
        elif self._match(TokenTypes.ELIF):
            context.update({'continuation': True})
            return ConditionalExpression(
                condition, consequent,
                self._parse_conditional_expression(**context)
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

    def _parse_operator_expression(
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
            binary("&")  : 10
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
                min_precedence, (TokenTypes.AMPERSAND,), **context
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
        lhs_expr = self._parse_operator_expression(precedence + 1, **context)
        if self._match_any_from(*operators):
            operand = self._current_token
            self._consume_token()
            if operand.is_left_associative():
                rhs_expr = self._parse_operator_expression(precedence + 1, **context)
                expr = BinaryExpression(lhs_expr, operand, rhs_expr)
                while self._match_any_from(*operators):
                    operand = self._current_token
                    self._consume_token()
                    expr = BinaryExpression(
                        expr, operand, self._parse_operator_expression(
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
                expr = self._parse_operator_expression(precedence + 1, **context)
            return UnaryExpression(operand, expr)
        else:
            return self._parse_operator_expression(precedence + 1, **context)

    def _parse_application_expression(
            self, **context
    ) -> Union[ApplicationExpression, AnyExpressionType]:
        function = self._parse_atom_expression(**context)
        if self._match(TokenTypes.PERIOD):  # function composition
            self._consume_token()
            return ApplicationExpression(
                function, self._parse_application_expression(**context)
            )
        elif self._match(TokenTypes.LEFT_PARENTHESIS):
            self._consume_token()
            arguments = self._parse_expression_list(**context)
            self._expect(TokenTypes.RIGHT_PARENTHESIS)
            self._consume_token()
            expr = ApplicationExpression(function, arguments)
            while self._match(TokenTypes.LEFT_PARENTHESIS):
                arguments = self._parse_expression_list(**context)
                self._expect(TokenTypes.RIGHT_PARENTHESIS)
                self._consume_token()
                expr = ApplicationExpression(expr, arguments)
            return expr
        else:
            return function  # is atom expression

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
            remapped_vars = context.get('remapped_vars')
            if (
                    remapped_vars and self._current_token.type == TokenTypes.ID
                    and self._current_token.raw in remapped_vars.keys()
            ):
                ret = AtomExpression(remapped_vars[self._current_token.raw])
            else:
                ret = AtomExpression(self._current_token)
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
            id_list.append(self._current_token)
            self._consume_token()
            if got_comma := self._match(TokenTypes.COMMA):
                self._consume_token()
        return id_list

    def build_parse_tree(self) -> AnyExpressionType:
        return self._parse_statement_list()


if __name__ == '__main__':
    from quark.core.scanner import QuarkScanner
    test = ';'
    lexer = QuarkScanner(test)
    parser = QuarkParser(lexer.tokens())
    while test := input('>>> '):
        lexer.reset(test)
        parser.reset(lexer.tokens())
        ast = parser.build_parse_tree()
        print(ast.json_repr)
        for node in ast:
            print(
                f'expr = "{node.__repr__()}"\n'
                f'variables = {node.variables}\n'
                f'free variables = {node.free_variables}\n'
                f'bound variables = {node.bound_variables}\n',
            )
