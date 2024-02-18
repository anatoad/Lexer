from .NFA import NFA
from .NFA import EPSILON
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class Plus(Regex):
    exp: Regex

    def thompson(self) -> NFA[int]:
        # convert the regex to an NFA
        nfa = self.exp.thompson()

        q0 = 0

        finalState = len(nfa.K) - 1
  
        # add epsilon transition
        d = nfa.d
    
        finalStateSet = set() if (finalState, EPSILON) not in nfa.d else nfa.d[(finalState, EPSILON)]

        d[(finalState, EPSILON)] = finalStateSet | {q0}

        return NFA(nfa.S, nfa.K, q0, d, {finalState})
