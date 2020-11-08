from quark.core.token_ import Token, TokenTypes, keyword_tokens

from typing import List, Tuple, Union


__all__ = [
    'QuarkScanner', 'QuarkScannerError'
]


class QuarkScannerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class QuarkScanner:
    _EOS_MARKER = '\0'

    def __init__(self, source: str, ignore_skippables=True):
        self._source = source

        self._ignore_skippables = ignore_skippables

        self._source_len = len(source)
        self._source_start, self._source_pos = 0, 0
        self._column_pos, self._line_pos = 0, 0

    def reset(self, source: str, ignore_skippables=True):
        self.__init__(source, ignore_skippables)

    @property
    def _pos(self) -> Tuple[int, int]:
        return self._column_pos, self._line_pos

    @property
    def _current_char(self) -> str:
        return self._source[self._source_pos] if not self._reached_end_of_source() \
            else self._EOS_MARKER

    @property
    def _next_char(self) -> str:
        return self._source[self._source_pos + 1] if not self._reached_end_of_source(off=1) \
            else self._current_char

    @property
    def _consumed_chars(self) -> str:
        return self._source[self._source_start:self._source_pos]

    def _match(self, s: str) -> bool:
        if self._reached_end_of_source(off=len(s) - 1):
            return False
        return self._source[self._source_pos:self._source_pos + len(s)] == s

    def _expect(self, c: str, not_met_msg: str):
        if not self._current_char == c:
            raise QuarkScannerError(
                f'SyntaxError: Expected "{c}" at '
                f'{self._line_pos}:{self._column_pos}. {not_met_msg}'
            )

    def _is_illegal(self, reasoning: str):
        pass

    def _consume_char(self):
        if self._reached_end_of_source():
            return
        elif self._current_char == '\n':
            self._column_pos = 0
            self._line_pos += 1
        self._column_pos += 1
        self._source_pos += 1

    def _discard_consumed_chars(self):
        self._source_start = self._source_pos

    def _reached_end_of_source(self, off=0) -> bool:
        return self._source_pos == self._source_len - off

    def _is_id_start(self) -> bool:
        return 'A' <= self._current_char <= 'Z' or 'a' <= self._current_char <= 'z' \
               or self._current_char == '_' or ord(self._current_char) >= 128

    def _is_id_char(self) -> bool:
        return 'A' <= self._current_char <= 'Z' or 'a' <= self._current_char <= 'z' \
               or '0' <= self._current_char <= '9' or self._current_char == '_' \
               or ord(self._current_char) >= 128

    def _is_num_start(self) -> bool:
        return '0' <= self._current_char <= '9' or self._current_char == '.'

    def _is_num_char(self) -> bool:
        return '0' <= self._current_char <= '9'

    def _is_str_start(self) -> bool:
        return self._current_char == '"'

    def _is_str_char(self) -> bool:
        return self._current_char != '"' and self._current_char.isascii()
        # todo: think of restrictions

    def _is_skippable(self) -> bool:
        return self._current_char in (' ', '\t')

    def _as_keyword(self) -> Union[None, Token]:
        try:
            return keyword_tokens[self._consumed_chars]
        except KeyError:
            return None

    def next_token(self) -> Token:
        token_type = None

        if self._is_skippable():
            while self._is_skippable():
                self._consume_char()
            if self._ignore_skippables:
                self._discard_consumed_chars()
            else:
                ret = self._consumed_chars
                self._discard_consumed_chars()
                return Token(TokenTypes.SKIP, ret, self._pos)

        if self._is_id_start():
            self._consume_char()
            while self._is_id_char():
                self._consume_char()
            if len(self._consumed_chars) > 1:
                if keyword := self._as_keyword():
                    token_type = keyword
                else:
                    token_type = TokenTypes.ID
            else:
                token_type = TokenTypes.ID
        elif self._is_str_start():
            self._consume_char()
            while self._is_str_char():
                self._consume_char()
            self._expect(
                '"', not_met_msg=f'EOL while scanning string literal'
            )
        elif self._match('.'):
            self._consume_char()
            if self._is_num_char():
                self._consume_char()
                while self._is_num_char():
                    self._consume_char()
                if self._match('im'):
                    self._consume_char()
                    self._consume_char()
                    token_type = TokenTypes.COMPLEX
                else:
                    token_type = TokenTypes.REAL
            else:
                token_type = TokenTypes.PERIOD
        elif self._is_num_char():
            if must_be_real := self._current_char == '0':
                self._consume_char()
                if not self._is_num_char() and self._current_char != '.':
                    return Token(TokenTypes.INTEGER, self._consumed_chars, self._pos)
            while self._is_num_char():
                self._consume_char()
            if must_be_real:
                self._expect(
                    '.', not_met_msg=f'Leading zeros in decimal integer literals are not permitted'
                )
                self._consume_char()
                while self._is_num_char():
                    self._consume_char()
                if self._match('im'):
                    self._consume_char()
                    self._consume_char()
                    token_type = TokenTypes.COMPLEX
                else:
                    token_type = TokenTypes.REAL
            else:
                if self._match('.'):
                    self._consume_char()
                    while self._is_num_char():
                        self._consume_char()
                    if self._match('im'):
                        self._consume_char()
                        self._consume_char()
                        token_type = TokenTypes.COMPLEX
                    else:
                        token_type = TokenTypes.REAL
                else:
                    if self._match('im'):
                        self._consume_char()
                        self._consume_char()
                        token_type = TokenTypes.COMPLEX
                    else:
                        token_type = TokenTypes.INTEGER
        elif self._match('+'):
            self._consume_char()
            token_type = TokenTypes.PLUS
        elif self._match('-'):
            self._consume_char()
            token_type = TokenTypes.MINUS
        elif self._match('*'):
            self._consume_char()
            if self._match('*'):
                self._consume_char()
                token_type = TokenTypes.DOUBLE_STAR
            else:
                token_type = TokenTypes.STAR
        elif self._match('%'):
            self._consume_char()
            token_type = TokenTypes.PERCENT
        elif self._match('/'):
            self._consume_char()
            if self._match('/'):
                self._consume_char()
                token_type = TokenTypes.DOUBLE_SLASH
            elif self._match('%'):
                self._consume_char()
                token_type = TokenTypes.SLASH_PERCENT
            else:
                token_type = TokenTypes.SLASH
        elif self._match('@'):
            self._consume_char()
            token_type = TokenTypes.AT
        elif self._match('&'):
            self._consume_char()
            token_type = TokenTypes.AMPERSAND
        elif self._match('<'):
            self._consume_char()
            if self._match('='):
                self._consume_char()
                token_type = TokenTypes.SMALLER_EQUAL
            else:
                token_type = TokenTypes.SMALLER
        elif self._match('>'):
            self._consume_char()
            if self._match('='):
                self._consume_char()
                token_type = TokenTypes.GREATER_EQUAL
            else:
                token_type = TokenTypes.GREATER
        elif self._match('='):
            self._consume_char()
            if self._match('='):
                self._consume_char()
                token_type = TokenTypes.DOUBLE_EQUAL
            else:
                token_type = TokenTypes.EQUAL
        elif self._match(','):
            self._consume_char()
            token_type = TokenTypes.COMMA
        elif self._match('.'):
            self._consume_char()
            token_type = TokenTypes.PERIOD
        elif self._match('{'):
            self._consume_char()
            token_type = TokenTypes.LEFT_CURLY_BRACKET
        elif self._match('}'):
            self._consume_char()
            token_type = TokenTypes.RIGHT_CURLY_BRACKET
        elif self._match('['):
            self._consume_char()
            token_type = TokenTypes.LEFT_BRACKET
        elif self._match(']'):
            self._consume_char()
            token_type = TokenTypes.RIGHT_BRACKET
        elif self._match('('):
            self._consume_char()
            token_type = TokenTypes.LEFT_PARENTHESIS
        elif self._match(')'):
            self._consume_char()
            token_type = TokenTypes.RIGHT_PARENTHESIS
        elif self._match(';'):
            self._consume_char()
            token_type = TokenTypes.SEMICOLON
        elif self._match('~'):
            self._consume_char()
            token_type = TokenTypes.TILDE
        elif self._match('|'):
            self._consume_char()
            token_type = TokenTypes.VERTICAL_BAR
        elif self._match(':'):
            self._consume_char()
            if self._match(':'):
                self._consume_char()
                token_type = TokenTypes.DOUBLE_COLON
            else:
                token_type = TokenTypes.COLON
        elif self._match('\n'):
            self._consume_char()
            token_type = TokenTypes.NEWLINE
        else:
            raise QuarkScannerError(
                f'SyntaxError: invalid character {repr(self._current_char)} in identifier'
            )

        token = Token(token_type, self._consumed_chars, self._pos)
        self._discard_consumed_chars()
        return token

    def tokens(self) -> List[Token]:
        toks = []
        while not self._reached_end_of_source():
            toks.append(self.next_token())
        return toks


if __name__ == '__main__':
    lexer = QuarkScanner('let a = 234 in a * a')
    while test := input('>>> '):
        lexer.reset(test)
        print(
            '\n'.join(repr(t) for t in lexer.tokens())
        )
