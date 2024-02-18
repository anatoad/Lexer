from .NFA import NFA
from .NFA import EPSILON
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class Concat(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        # convert the left regex to an NFA
        leftNFA = self.left.thompson()

        # convert the right regex to an NFA, use the remap_states function to shift the states'
        # values by the number of states in the left NFA so there are no duplicate states
        rightNFA = self.right.thompson().remap_states(lambda x: x + len(leftNFA.K))

        # S is the union between the two nfas' alphabets
        S = leftNFA.S | rightNFA.S
    
        # the initial state is the left nfa's initial state
        q0 = leftNFA.q0

        # K contains all the states of the two nfas
        K = leftNFA.K | rightNFA.K
    
        # merge the two dictionaries (transition relations)
        d = leftNFA.d | rightNFA.d

        finalState = list(leftNFA.F)[0]
        finalStateSet = set() if (finalState, EPSILON) not in leftNFA.d else leftNFA.d[(finalState, EPSILON)]

        # add an epsilon transition from the final state of leftNFA to the initial state of rightNFA
        d[(finalState, EPSILON)] = finalStateSet | {rightNFA.q0}

        return NFA(S, K, q0, d, rightNFA.F)
