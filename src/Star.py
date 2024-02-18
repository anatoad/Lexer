from .NFA import NFA
from .NFA import EPSILON
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class Star(Regex):
    exp: Regex

    def thompson(self) -> NFA[int]:
        # convert regex to an NFA and shift the states' values by 1 in order to add the initial state 0
        nfa = self.exp.thompson().remap_states(lambda x: x+1)

        lastState = len(nfa.K)
        finalState = len(nfa.K) + 1

        q0 = 0

        # add initial state (0) and final state
        K = nfa.K.union({0, finalState})
    
        # add epsilon transitions
        d = nfa.d

        lastStateSet = set() if (lastState, EPSILON) not in d else d[(lastState, EPSILON)]

        d[(q0, EPSILON)] = {1, finalState}
        d[(lastState, EPSILON)] = lastStateSet | {1, finalState}
    
        return NFA(nfa.S, K, q0, d, {finalState})
