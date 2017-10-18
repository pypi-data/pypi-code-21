from parglare import Grammar, NonTerminal, Terminal, RegExRecognizer


# Expression grammar with float numbers
E, T, F = [NonTerminal(name) for name in ['E', 'T', 'F']]
PLUS, MULT, OPEN, CLOSE = [
    Terminal(value) for value in ['+', '*', '(', ')']]
NUMBER = Terminal('number', RegExRecognizer(r'\d+(\.\d+)?'))
productions = [
    (E, (E, PLUS, T)),
    (E, (T, )),
    (T, (T, MULT, F)),
    (T, (F, )),
    (F, (OPEN, E, CLOSE)),
    (F, (NUMBER,))
]


def get_grammar():
    return Grammar.from_struct(productions, E)
