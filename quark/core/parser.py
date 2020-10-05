from quark.core.token_ import Token, TokenTypes
from quark.core.ast import *

from typing import List, Tuple, Generator, Union, Iterator


class QuarkParserError(Exception):
    def __init__(self):
        pass


# todo: make specific methods private finally
class QuarkParser:
    def __init__(self):
        pass

    def __build_ast(self, tokens: List[Token]):
        pass

    def build_ast(self, tokens: List[Token]):
        return self.__build_ast(tokens)
