from .NFA import NFA
from .NFA import EPSILON
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class Union(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        # convert left regex to NFA, shift states' values by 1 in order to add initial state 0
        leftNFA = self.left.thompson().remap_states(lambda x: x + 1)

        # convert right regex to NFA, shift the states' values to prevent duplicate states
        rightNFA = self.right.thompson().remap_states(lambda x: x + len(leftNFA.K) + 1)

        finalState = len(leftNFA.K) + len(rightNFA.K) + 1

        S = leftNFA.S | rightNFA.S
    
        q0 = 0

        # K contains the states from both left and right NFA's, plus the 2 newly added states
        K = leftNFA.K | rightNFA.K | {q0, finalState}
    
        d = leftNFA.d | rightNFA.d

        lastStateLeft = list(leftNFA.F)[0]
        lastStateRight = list(rightNFA.F)[0]
    
        lastStateSetLEFT = set() if (lastStateLeft, EPSILON) not in leftNFA.d else leftNFA.d[(lastStateLeft, EPSILON)]
        lastStateSetRIGHT = set() if (lastStateRight, EPSILON) not in rightNFA.d else rightNFA.d[(lastStateRight, EPSILON)]

        # add the new epsilon transitions
        d[(q0, EPSILON)] = {leftNFA.q0, rightNFA.q0}
        d[(lastStateLeft, EPSILON)] = lastStateSetLEFT | {finalState}
        d[(lastStateRight, EPSILON)] = lastStateSetRIGHT | {finalState}

        return NFA(S, K, q0, d, {finalState})
