from .utils import PGTestCase

good_examples = \
[
"""
--- model ciao
input x1
input x2 "output 2"
output o1 

"""
]

bad_examples = \
[
"""
# cannot have newline before doc string
--- model ciao
input x3 
"documentation"
""",
"""
# Names must be strings
--- model ciao
input 0 "not a string" 
"""
]


class SyntaxTestMultiple(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)

