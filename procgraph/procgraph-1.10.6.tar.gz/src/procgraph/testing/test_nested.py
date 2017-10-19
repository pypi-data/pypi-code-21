from .utils import PGTestCase

good_examples = [
    "x = 1",
    "x = [1]",
    "x = [1,2]",
    "x = {}",
    "x = {a: b}",
    'x = {"a": "b"}',
    'x = {"a": "b", a: d}',
    'x = {"a": "b", a: {a:1}}',
    'x = []',
    'x = [1]',
]


bad_examples = [
    # empty string gives error
    "x = [1",
    "x = [1 2]",
    'x = {0: a}'
]


class SyntaxTest2(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            print 'Trying: %s' % example
            self.check_syntax_ok(example)

