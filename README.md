## Lexer
> [!NOTE]
> :construction: *work in progress*

### About
Program splits an input text into lexical tokens defined in the specification.It does so by building a finite automata from the regular expressions given in the specification.\
Lexical analysis is the first step of a compiler.

**Input**\
Lexer **specification** consists of a list of pairs of *(\<token\>, \<regular expression\>)* specifying the legal tokens.\
**token** - represents a lexical unit such as a keyword, identifier or punctuation symbol\
**regular expression** - specifies a match pattern in text corresponding to a given token

**Output**\
The output is a list of lexemes:\
`[(token1, lexeme1), (token2, lexeme2), ...]`

**Longest Match Rule**\
The lexer identifies the longest matching substring as the token when multiple regular expressions match.

### Tests
Unit tests are located in the **test** directory.

*To run tests:*\
`python3.12 -m unittest`

### Interpreter for a overly-simplified functional language
The output of the lexer can be used by a parser to perform further analysis, such as building\
an abstract syntax tree used to evaluate all function invocations and generate an output which\
may be either a number or a list (which may contain both numbers and other lists).

The input of the parser is a list of atoms, where an atom may be:
- *a natural number*
- *an empty list ()*
- *a lambda expression*
- *a function invocation*
- *a list of atoms*
