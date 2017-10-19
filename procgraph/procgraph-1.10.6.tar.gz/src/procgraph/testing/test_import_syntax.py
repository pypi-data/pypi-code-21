from .utils import PGTestCase

good_examples = [
"import a",
"import a.b",
"import a.b.c",
"import a .b. c",
"import a. b .c",
"import a .b. c"
]

bad_examples = [
"import 0a",
"import 0a.",
"import .0a"
]


class SyntaxTestImport(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)
