from .NFA import NFA
from .NFA import EPSILON
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class Question(Regex):
    exp: Regex

    def thompson(self) -> NFA[int]:
        # convert regex to an NFA and shift the states' values by 1 in order to add the initial state 0
        nfa = self.exp.thompson().remap_states(lambda x: x+1)

        q0 = 0
        finalState = len(nfa.K)
        
        # add initial and final states
        K = nfa.K | {q0, finalState}
    
        # add epsilon transitions
        d = nfa.d
        d[(q0, EPSILON)] = {1, finalState}
    
        return NFA(nfa.S, K, q0, d, {finalState})
