import re

from typing import List, Tuple, AnyStr
from enum import Enum

from quark.core.token import Token, TokTypes, all_token_defs


class LexerError(Exception):
    def __init__(self, pos):
        self.pos = pos


class QuarkLexer:
    def __init__(self):
        pass
