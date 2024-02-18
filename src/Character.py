from .NFA import NFA
from .Regex import Regex
from dataclasses import dataclass

@dataclass
class Character(Regex):
    c: str

    def thompson(self) -> NFA[int]:
        # convert Character regex to a dfa
        #  (0) -----c----> (1)
        return NFA({self.c}, {0, 1},  0, {(0, self.c): {1}}, {1})
