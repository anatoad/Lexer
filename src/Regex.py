from .NFA import NFA
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Regex(ABC):
    @abstractmethod
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

from .Character import Character
from .Concat import Concat
from .Union import Union
from .Star import Star
from .Question import Question
from .Plus import Plus
from .SyntacticSugar import SyntacticSugar

def isValidChar(c: str):
    return c.isalnum() or (c in ['_', '.', '-', '@', ':'])

def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string
    stack = []
    queue = []

    lastChr = ''

    priority = {'*': 5, '.': 4, '|': 3, '(': 0}
    escapeCharacters = [' ', '*', '+', ')', '(', '|', '?', '/']
    validConcatenationChars = [')', '*', '+', '?', ']', '\\']

    i = 0
    length = len(regex)

    while i < length:
        c = regex[i]

        # check if it's an escaped characted
        if c == '\n' or (c in escapeCharacters and i > 0 and regex[i-1] == '\\'):        
            queue.append(Character(c))

            lastChr = '\\'
            i += 1

            continue

        # ignore whitespace
        if c == ' ':
            i += 1
            continue
        
        # check if a concatenation is required
        if (isValidChar(c) or c in ['(', '[', '\\']) and (isValidChar(lastChr) or lastChr in validConcatenationChars):
            stack.append('.')
        
        if isValidChar(c):
            queue.append(Character(c))

        elif c == '|':
            while len(stack) > 0 and priority[stack[-1]] >= priority['|']:
                op = stack.pop()
                c2 = queue.pop()
                c1 = queue.pop()

                queue.append(Concat(c1, c2) if op == '.' else Union(c1, c2))

            stack.append(c)

        elif c == '*':
            queue.append(Star(queue.pop()))
            
        elif c == '?':
            queue.append(Question(queue.pop()))

        elif c == '+':
            queue.append(Plus(queue.pop()))

        elif c == '(':
            stack.append(c)

        elif c == ')':
            op = stack.pop()
            while op != '(':
                c2 = queue.pop()
                c1 = queue.pop()

                queue.append(Concat(c1, c2) if op == '.' else Union(c1, c2))

                op = stack.pop()
        
        elif c == '[':
            queue.append(SyntacticSugar(regex[i+1], regex[i+3]))
            i += 4

        lastChr = regex[i]
        i += 1

    result = queue.pop()
    while len(stack) > 0:
        op = stack.pop()
        c1 = queue.pop()

        result = Concat(c1, result) if op == '.' else Union(c1, result)

    return result
