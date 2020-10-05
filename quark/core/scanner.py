from quark.core.token_ import Token, TokenTypes, is_valid_identifier, is_keyword

import io
from typing import List, Tuple, TextIO, Union, Generator


class QuarkScannerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class QuarkScanner:
    def __init__(self, source: Union[TextIO, str], error_report=True, skip_wst=True, mode=1):
        self._from_fp = isinstance(source, io.IOBase)
        if not self._from_fp or not isinstance(source, str):
            raise QuarkScannerError(f'Expected TextIO or str for source, got {type(source)} instead.')
        self._source = source

        self._error_report = error_report
        self._skip_wst = skip_wst
        self._mode = mode

        self._line_buff = ''
        self._column_start, self._column_pos, self._line_pos = 0, 0, 0

    def reset(self, source: Union[TextIO, str], error_report=True, skip_wst=True, mode=1):
        self.__init__(source, error_report, skip_wst, mode)

    def _refill_buffer(self, keep=None):
        self._line_buff = self._line_buff[keep] if keep else ''
        self._line_buff += next(self._source)
        self._line_pos += 1
        self._column_start, self._column_pos = 0, 0

    @property
    def _current_char(self):
        return self._line_buff[self._column_pos]

    @property
    def _next_char(self):
        if len(self._line_buff) == 1:
            if self._from_fp:
                try:
                    self._refill_buffer(keep=self._column_pos)
                except StopIteration:
                    raise QuarkScannerError('Cannot peek; last source char!')
            else:
                raise QuarkScannerError('Cannot peek; last source char!')
        return self._line_buff[self._column_pos + 1]

    def _consume_char(self):
        if not self._line_buff:
            if self._from_fp:
                try:
                    self._refill_buffer()
                except StopIteration:
                    raise QuarkScannerError('Cannot consume; no more source chars!')
            else:
                raise QuarkScannerError('Cannot consume; no more source chars!')
        self._column_pos += 1

    def _expect(self, c: str):
        if not self._current_char == c:
            raise QuarkScannerError(f'Expected "{c}" at {self._line_pos}:{self._column_pos}')

    def _match(self, c: str) -> bool:
        return self._current_char == c

    def _get_consumed_chars(self) -> str:
        return self._line_buff[self._column_start:self._column_pos]

    def _is_potential_id_start(self) -> bool:
        return 'A' <= self._current_char <= 'Z' or 'a' <= self._current_char <= 'z' \
               or self._current_char == '_' or ord(self._current_char) >= 128

    def _is_potentials_id_char(self) -> bool:
        return 'A' <= self._current_char <= 'Z' or 'a' <= self._current_char <= 'z' \
               or '0' <= self._current_char <= '9' or self._current_char == '_' or ord(self._current_char) >= 128

    def _is_potential_num_start(self) -> bool:
        return '0' <= self._current_char <= '9' or self._current_char == '.'

    def _is_num_char(self) -> bool:
        return '0' <= self._current_char <= '9'

    def _must_be_real(self) -> bool:
        return self._current_char == '0' or self._current_char == '.'

    def _consume_num(self):
        must_be_real = self._must_be_real()
        while self._is_num_char():
            self._consume_char()
        if must_be_real:
            self._expect('.')
            self._consume_char()
            while self._is_num_char():
                self._consume_char()
        elif self._match('.'):
            self._consume_char()
            while self._is_num_char():
                self._consume_char()
        if self._match('im'):
            token_value = float(self._get_consumed_chars()) * 1j
            token_type = TokenTypes.COMPLEX
        else:
            token_value = float(self._get_consumed_chars())
            token_type = TokenTypes.REAL

        return Token(token_type, token_value, (self._line_pos, self._column_pos))


if __name__ == '__main__':
    lexer = QuarkScanner()
    test_source = '>== fact with n >== if n == 2 then 1 \t else n* (fact (n-1)) in fact 4j */'
    print('\n'.join(str(t) for t in lexer.get_tokens(test_source)))
