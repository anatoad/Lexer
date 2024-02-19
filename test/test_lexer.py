import unittest
from typing import Iterable

from src.Lexer import Lexer

class TestLexer(unittest.TestCase):
    tests_passed: int = 0
    tests_count: int = 2

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @classmethod
    def tearDownClass(cls):
        print(f'\nLexer - Tests passed: {cls.tests_passed}/{cls.tests_count}\n')

    def run_tests(self, lexer: Lexer, tests: Iterable[tuple[str, list[tuple[str, str]]]]) -> None:
        for word, ref in tests:
            lexemes = lexer.lex(word)

            for lexeme, expected in zip(lexemes, ref):
                assert lexeme == expected, f'lexeme {lexeme} does not match expected value {expected}'
    
    def test_1(self):
        # define the lexer specification
        spec = [
            ("number", r'(\ )*(0|([1-9][0-9]*)+)(\ )*'),
            ("open", r'(\ )*\((\ )*'),
            ("close", r'(\ )*\)(\ )*'),
            ("sum", r'(\ )*\+(\ )*'),
            ("concat", r'(\ )*\+\+(\ )*'),
            ("lambda", r'(\ )*lambda(\ )*'),
            ("id", r'(\ )*([a-z]|[A-Z])+(\ )*:(\ )*'),
            ("var", r'(\ )*([a-z]|[A-Z])+(\ )*')
        ]

        lexer = Lexer(spec)

        tests = [
            (
                "(++ (+ 1 2) 5)",
                [
                    ("open", "("),
                    ("concat", "++ "),
                    ("open", "("),
                    ("sum", "+ "),
                    ("number", "1 "),
                    ("number", "2"),
                    ("close", ") "),
                    ("number", "5"),
                    ("close", ")"),
                ]
            ),
            (
                "(+ (lambda x: (++ (x x)) (105 23)))",
                [
                    ("open", "("),
                    ("sum", "+ "),
                    ("open", "("),
                    ("lambda", "lambda "),
                    ("id", "x: "),
                    ("open", "("),
                    ("concat", "++ "),
                    ("open", "("),
                    ("var", "x "),
                    ("var", "x"),
                    ("close", ")"),
                    ("close", ") "),
                    ("open", "("),
                    ("number", "105 "),
                    ("number", "23"),
                    ("close", ")"),
                    ("close", ")"),
                    ("close", ")"),
                ]
            ),
            (
                "(++ ((lambda x: (+ x 5) 7))   ( 2 7 8 ) (+ 1 5))",
                [
                    ("open", "("),
                    ("concat", "++ "),
                    ("open", "("),
                    ("open", "("),
                    ("lambda", "lambda "),
                    ("id", "x: "),
                    ("open", "("),
                    ("sum", "+ "),
                    ("var", "x "),
                    ("number", "5"),
                    ("close", ") "),
                    ("number", "7"),
                    ("close", ")"),
                    ("close", ")   "),
                    ("open", "( "),
                    ("number", "2 "),
                    ("number", "7 "),
                    ("number", "8 "),
                    ("close", ") "),
                    ("open", "("),
                    ("sum", "+ "),
                    ("number", "1 "),
                    ("number", "5"),
                    ("close", ")"),
                    ("close", ")"),
                ]
            )
        ]

        self.run_tests(lexer, tests)

        self.__class__.tests_passed += 1
    
    def test_2(self):
        spec = [
			("space", "\\ "),
			("newline", "\n"),
            ("token1", "(a|b)*q+cb[0-9]*"),
            ("token2", "(a|b|c)*[A-Z][a-z]+[0-9]*"),
            ("token3", "[a-b]*[x-z]*abc[0-9]*"),
            ("token4", "(0|1)*x+y?"),
            ("token5", "([0-9]|a)*"),
		]

        lexer = Lexer(spec)

        tests = [
            (
                "bbaqcbbyabc67895\n18955aa1a7   Ghj78112a010101x ",
                [
                    ("token1", "bbaqcb"),
                    ("token3", "byabc67895"),
                    ("newline", "\n"),
                    ("token5", "18955aa1a7"),
                    ("space", " "),
                    ("space", " "),
                    ("space", " "),
                    ("token2", "Ghj78112"),
                    ("token5", "a010101"),
                    ("token4", "x"),
                    ("space", " "),
                ]
            ),
        ]

        self.run_tests(lexer, tests)

        self.__class__.tests_passed += 1
