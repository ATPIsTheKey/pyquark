from enum import Enum
from typing import Tuple


__all__ = [
    'TokTypes', 'generals_token_defs', 'operator_token_defs', 'keyword_token_defs', 'separator_token_defs', 'all_token_defs'
]


tok_type_names = (
    'ID',
    'INTEGER',
    'REAL',
    'COMPLEX',
    'STRING',
    'OPERATOR',
    'RESERVED',
    'SEPARATOR',
    'COMMENT',
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
    'IF',
    'THEN',
    'ELSE',
    'WITH',
    'IN',
    'LAMBDA',
    'FUN',
    'COMMA',
    'DOT',
    'LEFT_PARENTHESIS',
    'RIGHT_PARENTHESIS',
    'LEFT_BRACE',
    'RIGHT_BRACE',
    'LEFT_BRACKET',
    'RIGHT_BRACKET',
    'QUOTE',
    'ELLIPSIS',
    'SEMICOLON'
)
TokTypes: Enum = Enum('TokTypes', {n: i for i, n in enumerate(tok_type_names)})


generals_token_defs = {
    TokTypes.ID: '[a-zA-Z_$]+[a-zA-Z0-9_$]*',
    TokTypes.COMMENT: r"(\\/\\*[\\w\\'\\s\\r\\n\\*]*\\*\\/)|(\\/\\/[\\w\\s\\']*)|(\\<![\\-\\-\\s\\w\\>\\/]*\\>)",
    TokTypes.STRING: r'\\"[^\\"\\n]*\\"',
    TokTypes.INTEGER: r'[-+]?[1-9]\\d*',
    TokTypes.REAL: r'[-+]?(\\d+\\.\\d*|\\d*\\.\\d+)',
    TokTypes.COMPLEX: r'[-+]?(\\d+\\.\\d*|\\d*\\.\\d+)j'
}


operator_token_defs = {
    TokTypes.PLUS: r'+',
    TokTypes.MINUS: r'-',
    TokTypes.PERCENT: r'%',
    TokTypes.STAR: r'*',
    TokTypes.DOUBLE_STAR: r'**',
    TokTypes.DOUBLE_COLON: r'::',
    TokTypes.SLASH: r'/',
    TokTypes.DOUBLE_SLASH: r'//',
    TokTypes.AT: r'@',
    TokTypes.AMPERSAND: r'&',
    TokTypes.LESS: r'<',
    TokTypes.GREATER: r'>',
    TokTypes.GREATER_EQUAL: r'>=',
    TokTypes.LESS_EQUAL: r'<=',
    TokTypes.EQUAL: r'=',
    TokTypes.DOUBLE_EQUAL: r'==',
    TokTypes.EXCLAMATION_EQUAL: r'!=',
    TokTypes.NOT: r'not',
    TokTypes.AND: r'and',
    TokTypes.OR: r'or',
    TokTypes.XOR: r'xor'
}


keyword_token_defs = {
    TokTypes.IF: r'if',
    TokTypes.THEN: r'then',
    TokTypes.ELSE: r'else',
    TokTypes.WITH: r'with',
    TokTypes.LAMBDA: r'lambda',
    TokTypes.FUN: r'fun'
}


separator_token_defs = {
    TokTypes.COMMA: r',',
    TokTypes.DOT: r'.',
    TokTypes.LEFT_BRACE: r'{',
    TokTypes.RIGHT_BRACE: r'}',
    TokTypes.LEFT_PARENTHESIS: r'(',
    TokTypes.RIGHT_PARENTHESIS: r')',
    TokTypes.LEFT_BRACKET: r'[',
    TokTypes.RIGHT_BRACKET: r']',
    TokTypes.QUOTE: r'"',
    TokTypes.ELLIPSIS: r'...',
    TokTypes.SEMICOLON: r';'
}


all_token_defs = {
    **generals_token_defs,
    **operator_token_defs,
    **keyword_token_defs,
    **separator_token_defs
}


class Token:
    def __init__(self, raw: str, its_type: TokTypes, pos: Tuple[int, int]):
        self.raw = raw
        self.type = its_type
        self.pos = pos

    def __str__(self):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__str__()})'


if __name__ == '__main__':
    print(all_token_defs)
