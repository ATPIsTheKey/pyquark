from enum import IntEnum
from typing import Tuple, Union


__all__ = [
    'TokenTypes', 'Token', 'tokens', 'simple_single_char_tokens', 'common_prefix_tokens',
    'simple_double_char_tokens', 'keyword_tokens', 'get_token_type_precedence'
]


tok_type_names = (
    # Special tokens
    'special_beg',
    'COMMENT',
    'SKIP',
    'MISMATCH',
    'EOF',
    'special_end',

    # Literal tokens
    'literal_beg',
    'ID',
    'INTEGER',
    'REAL',
    'COMPLEX',
    'STRING',
    'BOOLEAN',
    'literal_end',
    
    # Operator tokens
    'operator_beg',

    'strictly_unary_operator_beg',
    'TILDE',
    'XOR',
    'HEAD',
    'TAIL',
    'NIL',
    'NOT',
    'strictly_unary_operator_end',

    'unary_binary_operator_beg',
    'PLUS',
    'MINUS',
    'unary_binary_operator_end',

    'PERCENT',
    'STAR',
    'DOUBLE_STAR',
    'SLASH',
    'DOUBLE_SLASH',
    'SLASH_PERCENT',
    'COLON',
    'DOUBLE_COLON',
    'AT',
    'ON',
    'AMPERSAND',
    'COMMA',
    'LESS',
    'LESS_EQUAL',
    'GREATER',
    'GREATER_EQUAL',
    'EQUAL',
    'DOUBLE_EQUAL',
    'EXCLAMATION_EQUAL',
    'AND',
    'OR',
    'operator_end',

    # Keyword tokens
    'keyword_beg',
    'IF',
    'THEN',
    'ELIF',
    'ELSE',
    'LET',
    'LETREC',
    'CONST',
    'WITH',
    'IN',
    'LAMBDA',
    'FUN',
    'IMPORT',
    'EXPORT',
    'AS',
    'COND',
    'OTHERWISE',
    'keyword_end',

    # Separator tokens
    'separator_beg',
    'COMMA',
    'PERIOD',
    'LEFT_PARENTHESIS',
    'RIGHT_PARENTHESIS',
    'LEFT_CURLY_BRACKET',
    'RIGHT_CURLY_BRACKET',
    'LEFT_BRACKET',
    'RIGHT_BRACKET',
    'QUOTE',
    'ELLIPSIS',
    'SEMICOLON',
    'BACKSLASH',
    'VERTICAL_BAR',
    'SPACE',
    'TAB',
    'SPACE',
    'NEWLINE',
    'TAB',
    'separator_end'
)
TokenTypes: IntEnum = IntEnum('TokenTypes', {n: i for i, n in enumerate(tok_type_names)})


simple_single_char_tokens = {
    '+': TokenTypes.PLUS,
    '-': TokenTypes.MINUS,
    '%': TokenTypes.PERCENT,
    '@': TokenTypes.AT,
    '&': TokenTypes.AMPERSAND,
    '\\': TokenTypes.BACKSLASH,
    ',': TokenTypes.COMMA,
    '.': TokenTypes.PERIOD,
    '{': TokenTypes.LEFT_CURLY_BRACKET,
    '}': TokenTypes.RIGHT_CURLY_BRACKET,
    '(': TokenTypes.LEFT_PARENTHESIS,
    ')': TokenTypes.RIGHT_PARENTHESIS,
    '[': TokenTypes.LEFT_BRACKET,
    ']': TokenTypes.RIGHT_BRACKET,
    '|': TokenTypes.VERTICAL_BAR,
    '~': TokenTypes.TILDE,
    '"': TokenTypes.QUOTE,
    ';': TokenTypes.SEMICOLON,
    '\n': TokenTypes.NEWLINE,
}

common_prefix_tokens = {
    '*': (
        ('**', TokenTypes.DOUBLE_STAR),
        ('*', TokenTypes.STAR)
    ),
    '/': (
        ('//', TokenTypes.DOUBLE_SLASH),
        ('/%', TokenTypes.SLASH_PERCENT),
        ('/', TokenTypes.SLASH)
    ),
    '<': (
        ('<=', TokenTypes.LESS_EQUAL),
        ('<', TokenTypes.LESS)
    ),
    '>': (
        ('>=', TokenTypes.GREATER_EQUAL),
        ('>', TokenTypes.GREATER)
    ),
    '=': (
        ('==', TokenTypes.DOUBLE_EQUAL),
        ('=', TokenTypes.EQUAL)
    ),
    ':': (
        ('::', TokenTypes.DOUBLE_COLON),
        (':', TokenTypes.COLON)
    ),
}


simple_double_char_tokens = {
    '!=': TokenTypes.EXCLAMATION_EQUAL
}

keyword_tokens = {
    'not': TokenTypes.NOT,
    'and': TokenTypes.AND,
    'or': TokenTypes.OR,
    'xor': TokenTypes.XOR,
    'head': TokenTypes.HEAD,
    'tail': TokenTypes.TAIL,
    'nil': TokenTypes.NIL,
    'cond': TokenTypes.COND,
    'if': TokenTypes.IF,
    'then': TokenTypes.THEN,
    'elif': TokenTypes.ELIF,
    'else': TokenTypes.ELSE,
    'let': TokenTypes.LET,
    'letrec': TokenTypes.LETREC,
    'const': TokenTypes.CONST,
    'with': TokenTypes.WITH,
    'in': TokenTypes.IN,
    'on': TokenTypes.ON,
    'as': TokenTypes.AS,
    'lambda': TokenTypes.LAMBDA,
    'fun': TokenTypes.FUN,
    'import': TokenTypes.IMPORT,
    'export': TokenTypes.EXPORT,
    'otherwise': TokenTypes.OTHERWISE
}


tokens = {
    '+': TokenTypes.PLUS,
    '-': TokenTypes.MINUS,
    '%': TokenTypes.PERCENT,
    '*': TokenTypes.STAR,
    '/': TokenTypes.SLASH,
    '\\': TokenTypes.BACKSLASH,
    '@': TokenTypes.AT,
    '&': TokenTypes.AMPERSAND,
    '<': TokenTypes.LESS,
    '>': TokenTypes.GREATER,
    '=': TokenTypes.EQUAL,
    ',': TokenTypes.COMMA,
    '.': TokenTypes.PERIOD,
    ':': TokenTypes.COLON,
    '{': TokenTypes.LEFT_CURLY_BRACKET,
    '}': TokenTypes.RIGHT_CURLY_BRACKET,
    '(': TokenTypes.LEFT_PARENTHESIS,
    ')': TokenTypes.RIGHT_PARENTHESIS,
    '[': TokenTypes.LEFT_BRACKET,
    ']': TokenTypes.RIGHT_BRACKET,
    '"': TokenTypes.QUOTE,
    ';': TokenTypes.SEMICOLON,
    '\n': TokenTypes.NEWLINE,
    '**': TokenTypes.DOUBLE_STAR,
    '::': TokenTypes.DOUBLE_COLON,
    '//': TokenTypes.DOUBLE_SLASH,
    '/%': TokenTypes.SLASH_PERCENT,
    '<=': TokenTypes.LESS_EQUAL,
    '>=': TokenTypes.GREATER_EQUAL,
    '==': TokenTypes.DOUBLE_EQUAL,
    '!=': TokenTypes.EXCLAMATION_EQUAL,
    'not': TokenTypes.NOT,
    'and': TokenTypes.AND,
    'or': TokenTypes.OR,
    'xor': TokenTypes.XOR,
    'head': TokenTypes.HEAD,
    'tail': TokenTypes.TAIL,
    'nil': TokenTypes.NIL,
    'if': TokenTypes.IF,
    'then': TokenTypes.THEN,
    'elif': TokenTypes.ELIF,
    'else': TokenTypes.ELSE,
    'let': TokenTypes.LET,
    'letrec': TokenTypes.LETREC,
    'in': TokenTypes.IN,
    'lambda': TokenTypes.LAMBDA,
    'fun': TokenTypes.FUN,
    'with': TokenTypes.WITH,
    'const': TokenTypes.CONST,
    'cond': TokenTypes.COND,
    'otherwise': TokenTypes.OTHERWISE,
    ' ': TokenTypes.SPACE,
    '\t': TokenTypes.TAB
}


def get_token_type_precedence(type_: TokenTypes) -> int:
    if type_ in (TokenTypes.OR, TokenTypes.XOR):
        return 1
    elif type_ == TokenTypes.AND:
        return 2
    elif type_ == TokenTypes.NOT:
        return 3
    elif type_ in (
        TokenTypes.DOUBLE_EQUAL, TokenTypes.EXCLAMATION_EQUAL, TokenTypes.GREATER, TokenTypes.LESS,
        TokenTypes.GREATER_EQUAL, TokenTypes.LESS_EQUAL
    ):
        return 4
    elif type_ in (TokenTypes.PLUS, TokenTypes.MINUS):
        return 5
    elif type_ in (
        TokenTypes.STAR, TokenTypes.SLASH, TokenTypes.DOUBLE_SLASH, TokenTypes.SLASH_PERCENT, TokenTypes.PERCENT
    ):
        return 6
    elif type_ == TokenTypes.DOUBLE_STAR:
        return 7
    elif type_ == TokenTypes.NIL:
        return 8
    elif type_ in (
        TokenTypes.HEAD, TokenTypes.TAIL
    ):
        return 9
    elif type_ == TokenTypes.VERTICAL_BAR:
        return 10
    elif type_ == TokenTypes.ON:
        return 11
    else:
        return -1  # default


class Token:
    def __init__(self, type_: TokenTypes, value: str, pos: Tuple[int, int]):
        self.raw = value
        self.type = type_
        self.pos = pos

    def is_special(self) -> bool:
        return TokenTypes.special_beg < self.type < TokenTypes.special_end

    def is_literal(self) -> bool:
        return TokenTypes.literal_beg < self.type < TokenTypes.literal_end

    def is_operator(self) -> bool:
        return TokenTypes.operator_beg < self.type < TokenTypes.operator_end

    def is_unary_operator(self) -> bool:
        return TokenTypes.strictly_unary_operator_beg < self.type < TokenTypes.strictly_unary_operator_end

    def is_left_associative(self) -> bool:
        return not self.is_right_associative()

    def is_right_associative(self) -> bool:
        return self.type in (
            TokenTypes.VERTICAL_BAR, TokenTypes.DOUBLE_STAR
        ) or self.is_unary_operator()

    def is_keyword(self) -> bool:
        return TokenTypes.keyword_beg < self.type < TokenTypes.keyword_end

    def is_separator(self) -> bool:
        return TokenTypes.separator_beg < self.type < TokenTypes.separator_end

    @property
    def precedence(self):
        return get_token_type_precedence(self.type)

    def __str__(self):
        return f'<{self.type.name}>: {repr(self.raw)} at {self.pos}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__str__()})'

    def __eq__(self, other: 'Token'):
        return self.type == other.type

    def __hash__(self):
        return hash((self.type, self.raw, self.pos))


if __name__ == '__main__':
    pass
