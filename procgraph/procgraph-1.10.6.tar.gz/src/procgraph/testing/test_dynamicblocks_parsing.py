from .utils import PGTestCase

good_examples = [
    " y -> |$block| -> x ",
    ' y -> |"block"| -> x ',
    ' y -> |block| -> x '
]


bad_examples = [
    " y -> |1| -> x ",
    ' y -> |[1,2]| -> x '
]


class SyntaxTest(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)
