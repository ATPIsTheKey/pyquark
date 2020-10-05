from quark.core.token_ import Token, TokenTypes, is_valid_identifier, is_keyword

from typing import List, Tuple, TextIO, Union, Generator


class QuarkScannerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class QuarkScanner:
    def __init__(self, error_report=True, skip_wst=True, mode=1):
        self._error_report = error_report
        self._skip_wst = True
        self._mode = mode

    def _scan_source_line(self, source_line: str, init_line_num=0, init_column_num=0) -> Generator[Token, None, None]:
        column_num, line_num = 0, init_column_num

        for c in source_line:
            pass

    def get_token_iter(self, source: Union[TextIO, str]) -> Generator[Token, None, None]:
        if isinstance(source, TextIO):
            for line_num, line in enumerate(source):
                yield from self._scan_source_line(line, init_line_num=line_num)
        elif isinstance(source, str):
            yield from self._scan_source_line(source)
        else:
            raise QuarkScannerError(f'Expected TextIO or str for source, got {type(source)} instead.')

    def get_tokens(self, source: Union[TextIO, str]):
        return list(self.get_token_iter(source))


if __name__ == '__main__':
    lexer = QuarkScanner()
    test_source = '>== fact with n >== if n == 2 then 1 \t else n* (fact (n-1)) in fact 4j */'
    print('\n'.join(str(t) for t in lexer.get_tokens(test_source)))
