from collections.abc import Callable
from dataclasses import dataclass

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word; return true if the dfa accepts the word, false otherwise
        state = self.q0

        for c in word:
            if (state, c) not in self.d:
                return False

            state = self.d.get((state, c))

        return state in self.F

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        new_K = {f(state) for state in self.K}

        new_d = {(f(state), str): f(value) for (state, str), value in self.d.items()}

        new_F = {f(state) for state in self.F}

        return DFA(self.S, new_K, f(self.q0), new_d, new_F)
