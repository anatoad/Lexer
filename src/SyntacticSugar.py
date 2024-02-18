from .NFA import NFA
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class SyntacticSugar(Regex):
    start: str
    end: str

    def thompson(self) -> NFA[int]:
        # the alphabet contains all characters in range start - end
        S = {chr(i) for i in range(ord(self.start), ord(self.end)+1)}

        # nfa will have a transition from initial state 0 to final state 1 for each character in the alphabet
        d = {(0, c): {1} for c in S}

        return NFA(S, {0, 1}, 0, d, {1})
