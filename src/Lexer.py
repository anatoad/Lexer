from .DFA import DFA
from .NFA import NFA
from .NFA import EPSILON
from .Regex import parse_regex
from dataclasses import dataclass

@dataclass
class Lexer:
    spec: list[tuple[str, str]]
    dfa: DFA[str]

    # initialisation should convert the specification to a dfa which will be used in the lex method
    # the specification is a list of pairs (TOKEN_NAME:REGEX)
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = spec

        # introduce a new, initial state of the nfa
        q0 = '0'
        S = set()
        K = set(q0)
        F = set()
        d = {}

        for index, (_, regex) in enumerate(spec):
            # parse regex into an NFA
            nfa = parse_regex(regex).thompson()

            # remap states to remember the position of the token in the list
            # each state will have the form: <nfa_index>_<state_number>
            nfa = nfa.remap_states(lambda state: str(index) + '_' + str(state))

            # remap final states to: <nfa_index>_<state_number>_f
            for finalState in list(nfa.F):
                f = finalState + "_f"

                # update nfa.K, nfa.F
                nfa.K.remove(finalState)
                nfa.K.add(f)

                nfa.F.remove(finalState)
                nfa.F.add(f)

                # update nfa.d, replace finalState with newly remapped f
                for (state, c), nextStatesSet in list(nfa.d.items()):
                    if finalState in nextStatesSet:
                        nextStatesSet.remove(finalState)
                        nextStatesSet.add(f)

                        nfa.d[(state, c)] = nextStatesSet

                    if state == finalState:
                        nfa.d[(f, c)] = nfa.d[(state, c)]
                        del nfa.d[(state, c)]

            # add the states from the current nfa to K
            K |= nfa.K

            # add the final state of the current nfa to F
            F |= nfa.F

            d |= nfa.d
            S |= nfa.S

            # add an epsilon transition from the initial state q0 to the current nfa's initial state
            initialStateSet = set() if (q0, EPSILON) not in d else d[(q0, EPSILON)]
            d[((q0, EPSILON))] = initialStateSet | {nfa.q0}

        # transform nfa to dfa using subset construction algorithm
        self.dfa = NFA(S, K, q0, d, F).subset_construction()

    # a state is a sink if all transitions are from and to the same state
    def isSinkState(self, state: str) -> bool:
        return all([self.dfa.d.get((state, c)) == state for c in self.dfa.S])

    # this method splits the lexer into tokens based on the specification
    # the result is a list of tokens in the form (TOKEN_NAME, MATCHED_STRING)
    def lex(self, word: str) -> list[tuple[str, str]] | None:
        state = self.dfa.q0
        result = []

        lastStartIndex = 0
        lastAcceptedToken = -1
        lastAcceptedIndex = -1

        charIndex = 0
        index = 0
        line = 0
        lastNewLineIndex = -1

        while index < len(word):
            c = word[index]

            # account newlines
            if c == '\n' and lastNewLineIndex != index:
                line += 1
                lastNewLineIndex = index

            charIndex = index - lastNewLineIndex - 1

            # character c is not in the spec alphabet
            if c not in self.dfa.S:
                return [("", f"No viable alternative at character {charIndex}, line {line}")]

            # continue to the next state and consume another character in the word
            state = self.dfa.d.get((state, c))
            
            if self.isSinkState(state):
                # if got to a sink state without previously getting to a final state -> lexer error
                if lastAcceptedIndex == -1:
                    return [("", f"No viable alternative at character {charIndex}, line {line}")]

                # append to the result a tuple in the form (TOKEN_NAME, MATCHED_STRING)
                result.append((self.spec[lastAcceptedToken][0], word[lastStartIndex : lastAcceptedIndex+1]))

                lastStartIndex = lastAcceptedIndex + 1
                index = lastStartIndex
                state = self.dfa.q0
                lastAcceptedIndex = -1
                lastAcceptedToken = -1
                continue
        
            # final state reached
            if state in self.dfa.F:
                lastAcceptedIndex = index
                lastAcceptedToken = -1

                # get the first token from the spec
                for s in state:
                    if "_f" in s and (lastAcceptedToken == -1 or lastAcceptedToken > int(s[0])):
                        lastAcceptedToken = int(s[0])
            
            index += 1
        
        # lexer consumed the whole word without reaching any final or sink states -> lexer error
        if lastAcceptedIndex == -1:
            return [("", f"No viable alternative at character EOF, line {line}")]

        result.append((self.spec[lastAcceptedToken][0], word[lastStartIndex : lastAcceptedIndex+1]))

        return result
