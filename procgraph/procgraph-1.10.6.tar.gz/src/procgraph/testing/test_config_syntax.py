from .utils import PGTestCase

good_examples = [
"""
--- model ciao
config x1
config x2 = 2
config x3 = 2 "documentation"
config x4     "documentation"
config x5     '''Very long
documentation string'''

"""
]

bad_examples = [
"""
# cannot have newline before doc string
--- model ciao
config x3 = 2 
"documentation"
config x4     "documentation"

"""
]


class SyntaxTestMultiple(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)
