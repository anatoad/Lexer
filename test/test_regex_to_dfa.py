import unittest
from typing import Iterable

from src.Regex import parse_regex

class TestNFAToDFAConversion(unittest.TestCase):
    tests_passed: int = 0
    tests_count: int = 10

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @classmethod
    def tearDownClass(cls):
        print(f'\nRegex to DFA - Tests passed: {cls.tests_passed}/{cls.tests_count}\n')

    def run_tests(self, regex: str, tests: Iterable[tuple[str, bool]]) -> None:
        dfa = parse_regex(regex).thompson().subset_construction()
        for input, ref in tests:
            self.assertEqual(dfa.accept(input), ref, f'unexpected behaviour on input "{input}" - expected {"accept" if ref else "reject"}')

    def test_character(self):
        regex = 'x'

        tests = [
            ('', False),
            ('a', False),
            ('x', True),
            ('xx', False)
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1
    
    def test_concat_1(self):
        regex = 'xxyz'

        tests = [
            ('xxyz', True),
            ('aaaa', False),
            ('abcddf', False),
            ('xyz', False),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1

    def test_concat_2(self):
        regex = '(ab)(c(de)f)'

        tests = [
            ('abcdef', True),
            ('aaaa', False),
            ('abcddf', False),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1
    
    def test_plus(self):
        regex = 'abc+de+(fgh)+'

        tests = [
            ('abcde', False),
            ('abcdefg', False),
            ('abcdefgh', True),
            ('aaabcdefgh', False),
            ('abccccdefghfghfgh', True),
            ('abccdeeeeeefghfghfgh', True),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1
    
    def test_question(self):
        regex = 'user_+0?x+@mail.com?'

        tests = [
            ('use_@com', False),
            ('user_x@mail.co', True),
            ('user_0x@mail.com', True),
            ('user___0xx@mail.com', True),
            ('user____xxxx@mail.co', True),
            ('user_____0000x@mail.com', False),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1

    def test_star(self):
        regex = 'a*b*(12d+aq?)*'

        tests = [
            ('', True),
            ('a', True),
            ('b12', False),
            ('b12da', True),
            ('abba12', False),
            ('aaaaabb', True),
            ('ab12daqq', False),
            ('abbbbbbbbbb12da12ddddaq12ddda', True),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1

    def test_syntactic_sugar(self):
        regex = '[a-g]*_?[0-9]+'

        tests = [
            ('5', True),
            ('abcdef3', True),
            ('axe_12', False),
            ('aba_110', True),
            ('baggg114856320', True),
            ('123456711202356932145869521456895326532', True),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1

    def test_union(self):
        regex = '(a|[0-9])*_?(0|1)+'

        tests = [
            ('1', True),
            ('aaa', False),
            ('aaaaaaa_', False),
            ('0_0111001', True),
            ('a1a0a00a111', True),
            ('a1a3aa0115a48a_0110101', True),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1

    def test_1(self):
        regex = '\/\*([A-Z]|[a-z]|[0-9]|\ )*\*\/'

        tests = [
            ('/**/', True),
            ('/* This is a comment */', True),
            ('/* not allowed here */ because of this', False),
            ('/ * invalid whitespace means comment is not recognized */', False),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1

    def test_2(self):
        regex = 'while\ *\(\ *([a-z]|[A-Z]|_)+[0-9]*([a-z]|[A-Z]|_)*\ *\)\ *'

        tests = [
            ('while()', False),
            ('while(x)', True),
            ('while (  1 )', False),
            ('while ( a_5 )', True),
            ('while (True)  ', True),
            ('while (x y12) ', False),
            ('while ( _cond12 )', True),
        ]

        self.run_tests(regex, tests)

        self.__class__.tests_passed += 1
