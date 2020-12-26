import unittest

from quark.core.token_ import Token, TokenTypes
from quark.core.scanner import QuarkScanner, QuarkScannerError


class TestScanner(unittest.TestCase):
    def test_num_literals(self):
        source = "1im * .2 + 2 / 0.2 - 2. + 10 - 0 // .2im"
        should = [
            Token(TokenTypes.COMPLEX, '1im', (0, 0)),
            Token(TokenTypes.STAR, '*', (3, 0)),
            Token(TokenTypes.REAL, '.2', (5, 0)),
            Token(TokenTypes.PLUS, '+', (8, 0)),
            Token(TokenTypes.INTEGER, '2', (10, 0)),
            Token(TokenTypes.SLASH, '/', (12, 0)),
            Token(TokenTypes.REAL, '0.2', (14, 0)),
            Token(TokenTypes.MINUS, '-', (18, 0)),
            Token(TokenTypes.REAL, '2.', (20, 0)),
            Token(TokenTypes.PLUS, '+', (23, 0)),
            Token(TokenTypes.INTEGER, '10', (25, 0)),
            Token(TokenTypes.MINUS, '-', (28, 0)),
            Token(TokenTypes.INTEGER, '0', (30, 0)),
            Token(TokenTypes.DOUBLE_SLASH, '//', (32, 0)),
            Token(TokenTypes.COMPLEX, '.2im', (35, 0))
        ]
        scanner = QuarkScanner(source)
        self.assertEqual(scanner.tokens(), should)

    def test_leading_zeros_int_literals(self):
        source = "002"
        scanner = QuarkScanner(source)
        with self.assertRaises(QuarkScannerError):
            scanner.tokens()

    def test_eol_string_literal(self):
        source = '"test'
        scanner = QuarkScanner(source)
        with self.assertRaises(QuarkScannerError):
            scanner.tokens()

    def test_triple_char_literals(self):
        source = "::= == = ... ."
        should = [
            Token(TokenTypes.DOUBLE_COLON_EQUAL, '::=', (0, 0)),
            Token(TokenTypes.DOUBLE_EQUAL, '==', (3, 0)),
            Token(TokenTypes.EQUAL, '=', (6, 0)),
            Token(TokenTypes.ELLIPSIS, '...', (8, 0)),
            Token(TokenTypes.PERIOD, '.', (12, 0))
        ]
        scanner = QuarkScanner(source)
        self.assertEqual(scanner.tokens(), should)

    def test_double_char_literals(self):
        source = ">== >>= =>> %/% /// != :: ::= ?( ?)"
        should = [
            Token(TokenTypes.GREATER_EQUAL, '>=', (0, 0)),
            Token(TokenTypes.EQUAL, '=', (2, 0)),
            Token(TokenTypes.GREATER, '>', (3, 0)),
            Token(TokenTypes.GREATER_EQUAL, '>=', (5, 0)),
            Token(TokenTypes.EQUAL_GREATER, '=>', (7, 0)),
            Token(TokenTypes.GREATER, '>', (10, 0)),
            Token(TokenTypes.PERCENT, '%', (11, 0)),
            Token(TokenTypes.SLASH_PERCENT, '/%', (13, 0)),
            Token(TokenTypes.DOUBLE_SLASH, '//', (15, 0)),
            Token(TokenTypes.SLASH, '/', (18, 0)),
            Token(TokenTypes.EXCLAMATION_EQUAL, '!=', (19, 0)),
            Token(TokenTypes.DOUBLE_COLON, '::', (22, 0)),
            Token(TokenTypes.DOUBLE_COLON_EQUAL, '::=', (25, 0)),
            Token(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS, '?(', (29, 0)),
            Token(TokenTypes.QUESTION_MARK, '?', (32, 0)),
            Token(TokenTypes.RIGHT_PARENTHESIS, ')', (34, 0))
        ]
        scanner = QuarkScanner(source)
        self.assertEqual(scanner.tokens(), should)

    def test_common_source_code(self):
        sources = (
            'defun gcd :: a, b => ?( a | b == 0, gcd(b, a % b) | ...)',
            'def Y = fun :: f => (fun :: x => f(x(x)))(fun :: x => f(x(x)))',
            'let fact = fun :: n => ?( 1 | n == 1, n * fact(n - 1) | ...) in fact(2)',
            'defun pair :: a, b, f => (f(a, b)); defun first :: a, b => a; defun second :: a, b => b',
            '(let a, b = 1, 2 in fun :: x => a + b + x)(1)',
            'let gcd = fun :: a, b => ?( a | b == 0, gcd(b, a % b) | ...) in gcd (14, 14)',
            'def ack = fun :: m, n => ?( n + 1 | m == 0, ack(m - 1, 1) | n == 0, ack(m - 1, ack(m, n - 1))  | ...)'
        )
        shoulds = (
            [
                Token(TokenTypes.DEFUN, 'defun', (0, 0)),
                Token(TokenTypes.ID, 'gcd', (5, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (9, 0)),
                Token(TokenTypes.ID, 'a', (12, 0)), Token(TokenTypes.COMMA, ',', (14, 0)),
                Token(TokenTypes.ID, 'b', (15, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (17, 0)),
                Token(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS, '?(', (20, 0)),
                Token(TokenTypes.ID, 'a', (23, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (25, 0)),
                Token(TokenTypes.ID, 'b', (27, 0)),
                Token(TokenTypes.DOUBLE_EQUAL, '==', (29, 0)),
                Token(TokenTypes.INTEGER, '0', (32, 0)),
                Token(TokenTypes.COMMA, ',', (34, 0)),
                Token(TokenTypes.ID, 'gcd', (35, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (39, 0)),
                Token(TokenTypes.ID, 'b', (40, 0)), Token(TokenTypes.COMMA, ',', (41, 0)),
                Token(TokenTypes.ID, 'a', (42, 0)),
                Token(TokenTypes.PERCENT, '%', (44, 0)),
                Token(TokenTypes.ID, 'b', (46, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (48, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (49, 0)),
                Token(TokenTypes.ELLIPSIS, '...', (51, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (55, 0))
            ],
            [
                Token(TokenTypes.DEF, 'def', (0, 0)), Token(TokenTypes.ID, 'Y', (3, 0)),
                Token(TokenTypes.EQUAL, '=', (5, 0)),
                Token(TokenTypes.FUN, 'fun', (7, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (11, 0)),
                Token(TokenTypes.ID, 'f', (14, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (16, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (19, 0)),
                Token(TokenTypes.FUN, 'fun', (21, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (24, 0)),
                Token(TokenTypes.ID, 'x', (27, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (29, 0)),
                Token(TokenTypes.ID, 'f', (32, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (34, 0)),
                Token(TokenTypes.ID, 'x', (35, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (36, 0)),
                Token(TokenTypes.ID, 'x', (37, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (38, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (39, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (40, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (41, 0)),
                Token(TokenTypes.FUN, 'fun', (42, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (45, 0)),
                Token(TokenTypes.ID, 'x', (48, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (50, 0)),
                Token(TokenTypes.ID, 'f', (53, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (55, 0)),
                Token(TokenTypes.ID, 'x', (56, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (57, 0)),
                Token(TokenTypes.ID, 'x', (58, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (59, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (60, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (61, 0))
            ],
            [
                Token(TokenTypes.LET, 'let', (0, 0)),
                Token(TokenTypes.ID, 'fact', (3, 0)),
                Token(TokenTypes.EQUAL, '=', (8, 0)),
                Token(TokenTypes.FUN, 'fun', (10, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (14, 0)),
                Token(TokenTypes.ID, 'n', (17, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (19, 0)),
                Token(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS, '?(', (22, 0)),
                Token(TokenTypes.INTEGER, '1', (25, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (27, 0)),
                Token(TokenTypes.ID, 'n', (29, 0)),
                Token(TokenTypes.DOUBLE_EQUAL, '==', (31, 0)),
                Token(TokenTypes.INTEGER, '1', (34, 0)),
                Token(TokenTypes.COMMA, ',', (36, 0)), Token(TokenTypes.ID, 'n', (37, 0)),
                Token(TokenTypes.STAR, '*', (39, 0)),
                Token(TokenTypes.ID, 'fact', (41, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (46, 0)),
                Token(TokenTypes.ID, 'n', (47, 0)), Token(TokenTypes.MINUS, '-', (48, 0)),
                Token(TokenTypes.INTEGER, '1', (50, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (52, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (53, 0)),
                Token(TokenTypes.ELLIPSIS, '...', (55, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (59, 0)),
                Token(TokenTypes.IN, 'in', (60, 0)),
                Token(TokenTypes.ID, 'fact', (63, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (68, 0)),
                Token(TokenTypes.INTEGER, '2', (69, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (70, 0))
            ],
            [
                Token(TokenTypes.DEFUN, 'defun', (0, 0)),
                Token(TokenTypes.ID, 'pair', (5, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (10, 0)),
                Token(TokenTypes.ID, 'a', (13, 0)), Token(TokenTypes.COMMA, ',', (15, 0)),
                Token(TokenTypes.ID, 'b', (16, 0)), Token(TokenTypes.COMMA, ',', (18, 0)),
                Token(TokenTypes.ID, 'f', (19, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (21, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (24, 0)),
                Token(TokenTypes.ID, 'f', (26, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (27, 0)),
                Token(TokenTypes.ID, 'a', (28, 0)), Token(TokenTypes.COMMA, ',', (29, 0)),
                Token(TokenTypes.ID, 'b', (30, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (32, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (33, 0)),
                Token(TokenTypes.SEMICOLON, ';', (34, 0)),
                Token(TokenTypes.DEFUN, 'defun', (35, 0)),
                Token(TokenTypes.ID, 'first', (41, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (47, 0)),
                Token(TokenTypes.ID, 'a', (50, 0)), Token(TokenTypes.COMMA, ',', (52, 0)),
                Token(TokenTypes.ID, 'b', (53, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (55, 0)),
                Token(TokenTypes.ID, 'a', (58, 0)),
                Token(TokenTypes.SEMICOLON, ';', (60, 0)),
                Token(TokenTypes.DEFUN, 'defun', (61, 0)),
                Token(TokenTypes.ID, 'second', (67, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (74, 0)),
                Token(TokenTypes.ID, 'a', (77, 0)), Token(TokenTypes.COMMA, ',', (79, 0)),
                Token(TokenTypes.ID, 'b', (80, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (82, 0)),
                Token(TokenTypes.ID, 'b', (85, 0))
            ],
            [
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (0, 0)),
                Token(TokenTypes.LET, 'let', (1, 0)), Token(TokenTypes.ID, 'a', (4, 0)),
                Token(TokenTypes.COMMA, ',', (6, 0)), Token(TokenTypes.ID, 'b', (7, 0)),
                Token(TokenTypes.EQUAL, '=', (9, 0)),
                Token(TokenTypes.INTEGER, '1', (11, 0)),
                Token(TokenTypes.COMMA, ',', (13, 0)),
                Token(TokenTypes.INTEGER, '2', (14, 0)),
                Token(TokenTypes.IN, 'in', (16, 0)),
                Token(TokenTypes.FUN, 'fun', (19, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (23, 0)),
                Token(TokenTypes.ID, 'x', (26, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (28, 0)),
                Token(TokenTypes.ID, 'a', (31, 0)), Token(TokenTypes.PLUS, '+', (33, 0)),
                Token(TokenTypes.ID, 'b', (35, 0)), Token(TokenTypes.PLUS, '+', (37, 0)),
                Token(TokenTypes.ID, 'x', (39, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (41, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (42, 0)),
                Token(TokenTypes.INTEGER, '1', (43, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (44, 0))
            ],
            [
                Token(TokenTypes.LET, 'let', (0, 0)), Token(TokenTypes.ID, 'gcd', (3, 0)),
                Token(TokenTypes.EQUAL, '=', (7, 0)),
                Token(TokenTypes.FUN, 'fun', (9, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (13, 0)),
                Token(TokenTypes.ID, 'a', (16, 0)), Token(TokenTypes.COMMA, ',', (18, 0)),
                Token(TokenTypes.ID, 'b', (19, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (21, 0)),
                Token(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS, '?(', (24, 0)),
                Token(TokenTypes.ID, 'a', (27, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (29, 0)),
                Token(TokenTypes.ID, 'b', (31, 0)),
                Token(TokenTypes.DOUBLE_EQUAL, '==', (33, 0)),
                Token(TokenTypes.INTEGER, '0', (36, 0)),
                Token(TokenTypes.COMMA, ',', (38, 0)),
                Token(TokenTypes.ID, 'gcd', (39, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (43, 0)),
                Token(TokenTypes.ID, 'b', (44, 0)), Token(TokenTypes.COMMA, ',', (45, 0)),
                Token(TokenTypes.ID, 'a', (46, 0)),
                Token(TokenTypes.PERCENT, '%', (48, 0)),
                Token(TokenTypes.ID, 'b', (50, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (52, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (53, 0)),
                Token(TokenTypes.ELLIPSIS, '...', (55, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (59, 0)),
                Token(TokenTypes.IN, 'in', (60, 0)), Token(TokenTypes.ID, 'gcd', (63, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (67, 0)),
                Token(TokenTypes.INTEGER, '14', (69, 0)),
                Token(TokenTypes.COMMA, ',', (71, 0)),
                Token(TokenTypes.INTEGER, '14', (72, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (75, 0))
            ],
            [
                Token(TokenTypes.DEF, 'def', (0, 0)), Token(TokenTypes.ID, 'ack', (3, 0)),
                Token(TokenTypes.EQUAL, '=', (7, 0)),
                Token(TokenTypes.FUN, 'fun', (9, 0)),
                Token(TokenTypes.DOUBLE_COLON, '::', (13, 0)),
                Token(TokenTypes.ID, 'm', (16, 0)), Token(TokenTypes.COMMA, ',', (18, 0)),
                Token(TokenTypes.ID, 'n', (19, 0)),
                Token(TokenTypes.EQUAL_GREATER, '=>', (21, 0)),
                Token(TokenTypes.QUESTION_MARK_LEFT_PARENTHESIS, '?(', (24, 0)),
                Token(TokenTypes.ID, 'n', (27, 0)), Token(TokenTypes.PLUS, '+', (29, 0)),
                Token(TokenTypes.INTEGER, '1', (31, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (33, 0)),
                Token(TokenTypes.ID, 'm', (35, 0)),
                Token(TokenTypes.DOUBLE_EQUAL, '==', (37, 0)),
                Token(TokenTypes.INTEGER, '0', (40, 0)),
                Token(TokenTypes.COMMA, ',', (42, 0)),
                Token(TokenTypes.ID, 'ack', (43, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (47, 0)),
                Token(TokenTypes.ID, 'm', (48, 0)), Token(TokenTypes.MINUS, '-', (49, 0)),
                Token(TokenTypes.INTEGER, '1', (51, 0)),
                Token(TokenTypes.COMMA, ',', (53, 0)),
                Token(TokenTypes.INTEGER, '1', (54, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (56, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (57, 0)),
                Token(TokenTypes.ID, 'n', (59, 0)),
                Token(TokenTypes.DOUBLE_EQUAL, '==', (61, 0)),
                Token(TokenTypes.INTEGER, '0', (64, 0)),
                Token(TokenTypes.COMMA, ',', (66, 0)),
                Token(TokenTypes.ID, 'ack', (67, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (71, 0)),
                Token(TokenTypes.ID, 'm', (72, 0)), Token(TokenTypes.MINUS, '-', (73, 0)),
                Token(TokenTypes.INTEGER, '1', (75, 0)),
                Token(TokenTypes.COMMA, ',', (77, 0)),
                Token(TokenTypes.ID, 'ack', (78, 0)),
                Token(TokenTypes.LEFT_PARENTHESIS, '(', (82, 0)),
                Token(TokenTypes.ID, 'm', (83, 0)), Token(TokenTypes.COMMA, ',', (84, 0)),
                Token(TokenTypes.ID, 'n', (85, 0)), Token(TokenTypes.MINUS, '-', (87, 0)),
                Token(TokenTypes.INTEGER, '1', (89, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (91, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (92, 0)),
                Token(TokenTypes.VERTICAL_BAR, '|', (93, 0)),
                Token(TokenTypes.ELLIPSIS, '...', (96, 0)),
                Token(TokenTypes.RIGHT_PARENTHESIS, ')', (100, 0))
            ]
        )
        for source, should in zip(sources, shoulds):
            scanner = QuarkScanner(source)
            self.assertEqual(scanner.tokens(), should)


if __name__ == '__main__':
    unittest.main()
