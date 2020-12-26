from quark.core.token_ import (
    Token, TokenTypes, single_char_tokens, double_char_tokens, triple_char_tokens,
    keyword_tokens
)

from typing import List, Tuple, Union, Generator

__all__ = [
    'QuarkScanner', 'QuarkScannerError'
]


class QuarkScannerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class QuarkScanner:
    def __init__(self, source: str, ignore_skippables: bool = True):
        self._source_chars = source
        self._source_len = len(source)
        self._source_start, self._source_pos = 0, 0
        self._column_pos, self._line_pos = 0, 0
        self._ignore_skippables = ignore_skippables

    def reset(self, source: str, ignore_skippables: bool = True):
        self.__init__(source, ignore_skippables)

    @property
    def _current_pos(self) -> Tuple[int, int]:
        return self._column_pos, self._line_pos

    @property
    def _current_char(self) -> str:
        return (
            self._source_chars[self._source_pos] if not self._reached_end_of_source() else
            None
        )

    def _current_nchars(self, n: int) -> str:
        return (
            self._source_chars[self._source_pos:self._source_pos + n] if not
            self._reached_end_of_source(off=n - 1) else
            None
        )

    @property
    def _consumed_chars(self) -> str:
        return self._source_chars[self._source_start:self._source_pos]

    def _match(self, s: str) -> bool:
        return (
            False if self._reached_end_of_source(off=len(s) - 1) else
            self._source_chars[self._source_pos:self._source_pos + len(s)] == s
        )

    def _expect(self, s: str, not_met_msg: str):
        if not self._match(s):
            self._fmt_and_raise_syntax_error(not_met_msg)

    def _fmt_and_raise_syntax_error(self, msg: str):
        remaining_chars_in_line = ''
        for c in self._source_chars[self._source_pos + 1:]:
            if c == '\n':
                return
            else:
                remaining_chars_in_line += c
        raise QuarkScannerError(
            f'LexicalError at {self._current_pos}: {msg}\n'
            f'Remaining chars in line: {remaining_chars_in_line}'
        )

    def _consume_char(self):
        if self._reached_end_of_source():
            return
        elif self._current_char == '\n':
            self._column_pos = 0
            self._line_pos += 1
        self._column_pos += 1
        self._source_pos += 1

    def _consume_nchars(self, n: int):
        for _ in range(n):
            self._consume_char()

    def _discard_consumed_chars(self):
        self._source_start = self._source_pos

    def _reached_end_of_source(self, off: int = 0) -> bool:
        return self._source_pos == self._source_len - off

    def _is_id_start(self) -> bool:
        return (
            False if self._reached_end_of_source() else
            'A' <= self._current_char <= 'Z' or 'a' <= self._current_char <= 'z' or
            self._current_char == '_' or ord(self._current_char) >= 128
        )

    def _is_id_char(self) -> bool:
        return (
            False if self._reached_end_of_source() else
            'A' <= self._current_char <= 'Z' or 'a' <= self._current_char <= 'z' or
            '0' <= self._current_char <= '9' or self._current_char == '_' or
            ord(self._current_char) >= 128
        )

    def _is_num_char(self) -> bool:
        return (
            False if self._reached_end_of_source() else
            '0' <= self._current_char <= '9'
        )

    def _is_str_start(self) -> bool:
        return (
            False if self._reached_end_of_source() else
            self._current_char == '"'
        )

    def _is_str_char(self) -> bool:
        return (
            False if self._reached_end_of_source() else
            self._current_char != '"' and self._current_char.isascii()
        )  # todo: think of restrictions

    def _is_skippable(self) -> bool:
        return (
            False if self._reached_end_of_source() else
            self._current_char in {' ', '\t'}
        )

    def next_token(self) -> Union[Token, None]:
        pos = self._current_pos

        if self._is_skippable():
            self._consume_char()
            while self._is_skippable():
                self._consume_char()
            if self._ignore_skippables:
                self._discard_consumed_chars()
                if self._reached_end_of_source():
                    return None
            else:
                ret = self._consumed_chars
                self._discard_consumed_chars()
                return Token(TokenTypes.SKIP, ret, pos)

        if self._current_nchars(3) in triple_char_tokens.keys():
            self._consume_nchars(3)
            type_ = triple_char_tokens[self._consumed_chars]
        elif self._is_num_char():
            must_be_real_or_zero = self._match('0')
            self._consume_char()
            while self._is_num_char():
                if must_be_real_or_zero:
                    self._expect(
                        '0', 'leading zeros in decimal integer literals are not permitted'
                    )
                self._consume_char()
            if self._match('.'):
                self._consume_char()
                while self._is_num_char():
                    self._consume_char()
                type_ = TokenTypes.REAL
            else:
                type_ = TokenTypes.INTEGER
            if self._match('im'):
                type_ = TokenTypes.COMPLEX
                self._consume_nchars(2)
        elif self._match('.'):
            self._consume_char()
            if self._is_num_char():
                self._consume_char()
                while self._is_num_char():
                    self._consume_char()
                if self._match('im'):
                    type_ = TokenTypes.COMPLEX
                    self._consume_nchars(2)
                else:
                    type_ = TokenTypes.REAL
            else:
                type_ = TokenTypes.PERIOD
        elif self._is_str_start():
            self._consume_char()
            while self._is_str_char():
                self._consume_char()
            self._expect('"', 'EOL while scanning string literal')
            self._consume_char()
            type_ = TokenTypes.STRING
        elif self._current_nchars(2) in double_char_tokens.keys():
            self._consume_nchars(2)
            type_ = double_char_tokens[self._consumed_chars]
        elif self._current_char in single_char_tokens.keys():
            self._consume_char()
            type_ = single_char_tokens[self._consumed_chars]
        elif self._is_id_start():
            self._consume_char()
            while self._is_id_char():
                self._consume_char()
            if self._consumed_chars in keyword_tokens.keys():
                type_ = keyword_tokens[self._consumed_chars]
            else:
                type_ = TokenTypes.ID
        else:
            self._fmt_and_raise_syntax_error(
                f'invalid character {repr(self._current_char)} in identifier'
            )
            return

        ret = Token(type_, self._consumed_chars, pos)
        self._discard_consumed_chars()
        return ret

    def tokens(self) -> List[Token]:
        toks = []
        while not self._reached_end_of_source():
            toks.append(self.next_token())
        return toks

    def get_tokens(self) -> Generator[Token, None, None]:
        while not self._reached_end_of_source():
            yield self.next_token()


if __name__ == '__main__':
    test = ';'
    lexer = QuarkScanner(test)
    while test := input('>>> '):
        lexer.reset(test)
        for t in lexer.get_tokens():
            print(repr(t))
