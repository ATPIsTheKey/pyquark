from enum import IntEnum
from typing import Tuple, Union


__all__ = [
    'TokenTypes', 'Token', 'tokens', 'is_valid_identifier', 'is_keyword', 'common_prefixes_suffixes'
]


tok_type_names = (
    # Special tokens
    'special_beg'
    'COMMENT',
    'SKIP',
    'MISMATCH',
    'EOF',
    'special_end'

    # Literal tokens
    'literal_beg',
    'ID',
    'INTEGER',
    'REAL',
    'COMPLEX',
    'STRING',
    'literal_end'
    
    # Operator tokens
    'operator_beg',
    'PLUS',
    'MINUS',
    'PERCENT',
    'STAR',
    'DOUBLE_STAR',
    'SLASH',
    'DOUBLE_SLASH',
    'COLON',
    'DOUBLE_COLON',
    'AT',
    'AMPERSAND',
    'COMMA',
    'LESS',
    'LESS_EQUAL',
    'GREATER',
    'GREATER_EQUAL',
    'EQUAL',
    'DOUBLE_EQUAL',
    'EXCLAMATION_EQUAL',
    'NOT',
    'AND',
    'OR',
    'XOR',
    'CAR',
    'CDR',
    'NIL',
    'operator_end',

    # Keyword tokens
    'keyword_beg',
    'IF',
    'THEN',
    'ELSE',
    'WITH',
    'IN',
    'LAMBDA',
    'FUN',
    'keyword_end'
    
    # Separator tokens
    'separator_beg',
    'COMMA',
    'DOT',
    'LEFT_PARENTHESIS',
    'RIGHT_PARENTHESIS',
    'LEFT_CURLY_BRACKET',
    'RIGHT_CURLY_BRACKET',
    'LEFT_BRACKET',
    'RIGHT_BRACKET',
    'QUOTE',
    'ELLIPSIS',
    'SEMICOLON',
    'SPACE',
    'TAB',
    'NEWLINE',
    'separator_end'
)
TokenTypes: IntEnum = IntEnum('TokenTypes', {n: i for i, n in enumerate(tok_type_names)})


single_char_tokens = {
    '+': TokenTypes.PLUS,
    '-': TokenTypes.MINUS,
    '%': TokenTypes.PERCENT,
    '*': TokenTypes.STAR,
    '/': TokenTypes.SLASH,
    '@': TokenTypes.AT,
    '&': TokenTypes.AMPERSAND,
    '<': TokenTypes.LESS,
    '>': TokenTypes.GREATER,
    '=': TokenTypes.EQUAL,
    ',': TokenTypes.COMMA,
    '.': TokenTypes.DOT,
    '{': TokenTypes.LEFT_CURLY_BRACKET,
    '}': TokenTypes.RIGHT_CURLY_BRACKET,
    '(': TokenTypes.LEFT_PARENTHESIS,
    ')': TokenTypes.RIGHT_PARENTHESIS,
    '[': TokenTypes.LEFT_BRACKET,
    ']': TokenTypes.RIGHT_BRACKET,
    '"': TokenTypes.QUOTE,
    ';': TokenTypes.SEMICOLON
}

double_char_tokens = {
    '**': TokenTypes.DOUBLE_STAR,
    '::': TokenTypes.DOUBLE_COLON,
    '//': TokenTypes.DOUBLE_SLASH,
    '<=': TokenTypes.LESS_EQUAL,
    '>=': TokenTypes.GREATER_EQUAL,
    '==': TokenTypes.DOUBLE_EQUAL,
    '!=': TokenTypes.EXCLAMATION_EQUAL,
    'or': TokenTypes.OR
}

triple_char_tokens = {
    'not': TokenTypes.NOT,
    'and': TokenTypes.AND,
    'xor': TokenTypes.XOR,
    'car': TokenTypes.CAR,
    'cdr': TokenTypes.CDR,
    'nil': TokenTypes.NIL,
    '...': TokenTypes.ELLIPSIS
}

keyword_tokens = {
    'if': TokenTypes.IF,
    'then': TokenTypes.THEN,
    'else': TokenTypes.ELSE,
    'with': TokenTypes.WITH,
    'in': TokenTypes.IN,
    'lambda': TokenTypes.LAMBDA,
    'fun': TokenTypes.FUN
}

tokens = {
    **single_char_tokens,
    **double_char_tokens,
    **triple_char_tokens,
    **keyword_tokens
}

common_prefixes_suffixes = {
    '<': ('=',), '=': ('=',), ':': (':',), '!': ('=',),
}


class Token:
    def __init__(self, type_: TokenTypes, value: Union[str, int, float, complex], pos: Tuple[int, int]):
        self.value = value
        self.type = type_
        self.pos = pos

        self._lowest_precedence = 0
        self._highest_precedence = 10

    def is_special(self) -> bool:
        """
        Returns True for tokens corresponding to special tokens; it returns false otherwise.
        """
        return TokenTypes.special_beg < self.type < TokenTypes.special_end

    def is_literal(self) -> bool:
        """
         Returns True for tokens corresponding to identifiers and basic type literals; it returns
         false otherwise.
        """
        return TokenTypes.literal_beg < self.type < TokenTypes.literal_end

    def is_operator(self) -> bool:
        """
        Returns True for tokens corresponding to operators and delimiters; it returns false
        otherwise.
        """
        return TokenTypes.operator_beg < self.type < TokenTypes.operator_end

    def is_keyword(self) -> bool:
        """
        Returns True for tokens corresponding to keywords; it returns false otherwise.
        """
        return TokenTypes.keyword_beg < self.type < TokenTypes.keyword_end

    def is_separator(self) -> bool:
        """
        Returns True for tokens corresponding to separators; it returns false otherwise.
        """
        return TokenTypes.separator_beg < self.type < TokenTypes.separator_end

    def get_precedence(self) -> int:
        """
        Returns the operator precedence of token value. If token value is not a binary operator, the
        result is lowest_precedence.
        """
        if self.type in (TokenTypes.OR, TokenTypes.XOR):
            return 1
        elif self.type == TokenTypes.AND:
            return 2
        elif self.type == TokenTypes.NOT:
            return 3
        elif self.type in (
            TokenTypes.DOUBLE_EQUALS, TokenTypes.EXCLAMATION_EQUALS, TokenTypes.GREATER,
            TokenTypes.SMALLER, TokenTypes.GREATER_EQUALS, TokenTypes.SMALLER_EQUALS
        ):
            return 4
        elif self.type in (TokenTypes.PLUS, TokenTypes.MINUS):
            return 5
        elif self.type in (
            TokenTypes.STAR, TokenTypes.SLASH, TokenTypes.DOUBLE_SLASH, TokenTypes.PERCENT
        ):
            return 6
        elif self.type == TokenTypes.DOUBLE_STAR:
            return 7
        elif self.type == TokenTypes.NIL:
            return 8
        elif self.type in (
            TokenTypes.CAR, TokenTypes.CDR
        ):
            return 9
        elif self.type == TokenTypes.AT:
            return 10
        else:
            return self._lowest_precedence

    def __str__(self):
        return f'<{self.type.name}>:"{self.value}" at {self.pos}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__str__()})'

    def __eq__(self, other: 'Token'):
        return self.value == other.value

    def __hash__(self):
        return hash((self.type, self.value, self.pos))


def is_valid_identifier(s: str) -> bool:
    return s.isidentifier()


def is_keyword(s: str) -> bool:
    return s in keyword_tokens.keys()


def is_common_prefix(c: str) -> bool:
    return c in common_prefixes_suffixes.keys()


if __name__ == '__main__':
    pass
