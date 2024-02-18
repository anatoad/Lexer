from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented in the transition function of NFAs

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # the epsilon closure of a state q is a set of states which are reachable from state q on epsilon-transitions
        states = set()
        queue = [state]
        
        while len(queue) > 0:
            state = queue.pop(0)
            if state in states:
                continue

            states.add(state)

            if (state, EPSILON) in self.d:
                queue.extend(self.d.get((state, EPSILON)))

        return states

    def find_dfa_final_states(self, dfa_K: set[frozenset[STATE]]) -> set[frozenset[STATE]]:
        return {Q for Q in dfa_K for q in Q if q in self.F}

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a dfa using the subset construction algorithm
        dfa_q0 = frozenset(self.epsilon_closure(self.q0))
        dfa_K = set()
        dfa_d = {}

        queue = [dfa_q0]

        # add a sink state only if neccessary
        sink_needed = False
        sink_state = frozenset(set())

        while len(queue) > 0:
            Q = queue.pop(0)

            # do not add duplicate states in K
            if frozenset(Q) in dfa_K:
                continue

            dfa_K.add(Q)

            for c in self.S:
                newStates = set()

                for q in Q:
                    if (q, c) in self.d:
                        states = self.d.get((q, c))

                        for s in states:
                            newStates.update(self.epsilon_closure(s))

                if newStates != set():
                    dfa_state = frozenset(newStates)

                    queue.append(dfa_state)
                    dfa_d[(Q, c)] = dfa_state
                else:
                    if not sink_needed:
                        sink_needed = True

                        dfa_K.add(sink_state)

                        for ch in self.S:
                            dfa_d[(sink_state, ch)] = sink_state
                    
                    dfa_d[(Q, c)] = sink_state

        dfa_F = self.find_dfa_final_states(dfa_K)

        return DFA(self.S, dfa_K, dfa_q0, dfa_d, dfa_F)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # works similarly to 'remap_states' from the DFA class. See the comments there for more details.

        new_K = {f(state) for state in self.K}

        new_d = {(f(state), str): {f(value) for value in values} for (state, str), values in self.d.items()}

        new_F = {f(state) for state in self.F}

        return NFA(self.S, new_K, f(self.q0), new_d, new_F)
