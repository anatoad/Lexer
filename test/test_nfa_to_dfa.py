import unittest
import itertools
from typing import Iterable

from src.DFA import DFA
from src.NFA import NFA

class TestNFAToDFAConversion(unittest.TestCase):
    tests_passed: int = 0
    tests_count: int = 6

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @classmethod
    def tearDownClass(cls):
        print(f'\nNFA to DFA conversion - Tests passed: {cls.tests_passed}/{cls.tests_count}\n')

    def structural_check(self, dfa: DFA) -> None:
        # Check for emptysets
        self.assertTrue(len(dfa.S) > 0, 'Alphabet is empty')

        self.assertTrue(len(dfa.K) > 0, 'Set of states is empty')

        self.assertTrue(len(dfa.F) > 0, 'DFA cannot accept any input')

        # Check if each symbol in the alphabet is a single character
        for symbol in dfa.S:
            self.assertTrue(len(symbol) == 1, f'Alphabet contains non-characters: {symbol}')

        # Check if the initial state is a valid state
        self.assertTrue(dfa.q0 in dfa.K, 'The initial state is not in the DFA states')

        # Check if the set of final states is a subset of all states
        self.assertTrue(dfa.F.issubset(dfa.K), 'The set of final states must be a subset of all states')

        # Determinism: for each state and input symbol, there is exactly one transition to the next state
        self.assertTrue(len(dfa.d) == len(dfa.K) * len(dfa.S), 'Transition function domain cardinality is wrong')

        for state, symbol in itertools.product(dfa.K, dfa.S):
            self.assertTrue((state, symbol) in dfa.d, f'Transition from state {state} not defined on symbol {symbol}')
    
            self.assertTrue(dfa.d[state, symbol] in dfa.K, f'Destination of transition from state {state} on symbol {symbol} is not in the DFA states')

    def run_tests(self, dfa: DFA, tests: Iterable[tuple[str, bool]]) -> None:
        for input, ref in tests:
            self.assertEqual(dfa.accept(input), ref, f'unexpected behaviour on input "{input}" - expected {"accept" if ref else "reject"}')

    def test_epsilon_closure_1(self):
        nfa = NFA(
            {'x', 'y'},
            {'q0', 'q1', 'q2', 'q3', 'q4'},
            'q0',
            {
                ('q0', ''): {'q3', 'q4'},
                ('q3', ''): {'q2'},
                ('q1', 'x'): {'q0', 'q3', 'q4'},
                ('q4', 'y'): {'q1'},
            },
            {'q4'},
        )

        self.assertCountEqual(nfa.epsilon_closure('q0'), {'q0', 'q2', 'q3', 'q4'})

        self.__class__.tests_passed += 1

    def test_epsilon_closure_2(self):
        nfa = NFA(
            {'a'},
            {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},
            0,
            {
                (0, ''): {1, 2, 3, 4, 9, 12},
                (3, ''): {0, 5, 8, 11},
                (5, ''): {6},
                (10, ''): {7, 8, 9},
                (5, 'a'): {0, 1, 3},
                (7, 'a'): {8},
                (8, 'a'): {9, 10},
            },
            {11, 12},
        )

        self.assertCountEqual(nfa.epsilon_closure(0), {0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 12})

        self.__class__.tests_passed += 1

    def test_dfa_accept_emptyset(self):
        nfa = NFA({'x'}, {'q0', 'q1'}, 'q0', {}, {'q0'})

        tests = [
            ('', True),
            ('x', False),
            ('xx', False),
            ('xyz', False),
        ]

        dfa = nfa.subset_construction()
        self.structural_check(dfa)

        self.run_tests(dfa, tests)

        self.__class__.tests_passed += 1

    def test_dfa_1(self):
        nfa = NFA(
            {'a', 'b'},
            {0, 1, 2, 3},
            0,
            {
                (0, 'a'): {0, 1},
                (0, 'b'): {0},
                (1, 'a'): {2},
                (1, 'b'): {2},
                (2, 'a'): {3},
                (2, 'b'): {3},
            },
            {2, 3},
        )

        tests = [
            ('', False),
            ('a', False),
            ('b', False),
            ('aa', True),
            ('ab', True),
            ('aaa', True),
            ('bbab', True),
        ]

        dfa = nfa.subset_construction()
        self.structural_check(dfa)

        self.run_tests(dfa, tests)

        self.__class__.tests_passed += 1
    
    def test_dfa_2(self):
        nfa = NFA(
            {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'},
            {0, 1, 2, 3, 4, 5},
            0,
            {
                (0, 'a'): {0, 1},
                (0, 'b'): {0},
                (1, 'c'): {2},
                (1, 'd'): {0},
                (1, 'e'): {1},
                (1, 'f'): {0, 1},
                (2, 'g'): {0, 1, 2},
                (2, 'h'): {0, 1},
                (2, 'i'): {0},
                (2, 'j'): {1, 2},
                (2, 'k'): {1},
                (2, 'l'): {0, 2},
                (3, 'm'): {0, 1},
                (3, 'n'): {0},
                (4, 'o'): {2},
            },
            {2},
        )

        tests = [
            ('', False),
            ('aaabbbgh', False),
            ('aaabcdef', False),
            ('acllllllgj', True),
            ('bdaceefdhgggha', False)
        ]

        dfa = nfa.subset_construction()
        self.structural_check(dfa)

        self.run_tests(dfa, tests)

        self.__class__.tests_passed += 1

    def test_dfa_3(self):
        nfa = NFA(
            {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'},
            {'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12'},
            'q0',
            {
                ('q0', 'b'): {'q5', 'q10', 'q9'},
                ('q0', 'e'): {'q3', 'q2', 'q9'},
                ('q0', 'k'): {'q6', 'q10', 'q1', 'q5','q0'},
                ('q1', 'b'): {'q6', 'q3', 'q12'},
                ('q1', 'f'): {'q6', 'q2', 'q8', 'q0'},
                ('q1', 'h'): {'q4', 'q3', 'q7', 'q0'},
                ('q2', 'a'): {'q11', 'q3', 'q5'},
                ('q2', 'c'): {'q6'},
                ('q2', 'd'): {'q12', 'q9', 'q4', 'q0'},
                ('q2', 'f'): {'q4', 'q8'},
                ('q4', 'b'): {'q11', 'q8'},
                ('q4', 'e'): {'q11'},
                ('q4', 'j'): {'q10'},
                ('q4', 'm'): {'q4', 'q7', 'q5', 'q8'},
                ('q5', 'b'): {'q11', 'q10', 'q4', 'q3', 'q0'},
                ('q5', 'd'): {'q5', 'q8'},
                ('q5', 'k'): {'q7'},
                ('q5', 'm'): {'q10', 'q1', 'q7', 'q4', 'q0'},
                ('q6', 'b'): {'q1', 'q9', 'q2', 'q10'},
                ('q6', 'c'): {'q1', 'q5', 'q9'},
                ('q6', 'j'): {'q8'},
                ('q6', 'l'): {'q4', 'q2', 'q0'},
                ('q10', 'd'): {'q11', 'q6', 'q9', 'q12', 'q0'},
                ('q10', 'k'): {'q6', 'q7', 'q8'},
                ('q12', 'a'): {'q6', 'q9', 'q10', 'q7', 'q0'},
                ('q12', 'e'): {'q3', 'q0'},
                ('q12', 'f'): {'q9', 'q10', 'q1', 'q8', 'q4'},
                ('q12', 'k'): {'q4', 'q6', 'q3', 'q2'},
            },
            {'q6', 'q10', 'q12'},
        )

        tests = [
            ('', False),
            ('abcadghi', False),
            ('bcbbdefgjk', False),
            ('kabcaadcbds', False),
            ('bbbbbbbbbbbbbb', True),
            ('edjdkkklked', True),
            ('kbcbcbmbdfdkbkb', True),
            ('edjdkkklkedkbcbcbmbdfdkbkb', True),
        ]

        dfa = nfa.subset_construction()
        self.structural_check(dfa)

        self.run_tests(dfa, tests)

        self.__class__.tests_passed += 1
