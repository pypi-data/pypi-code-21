from .utils import PGTestCase

# Note that you have to escape the slash in python strings.
good_examples = \
[
"""
y --> |block| --> z --> |block| 
""",
""" # without whitespace after 
y \\
  --> |block| --> z --> |block| 
""",
""" # with whitespace after 
y \\ 
  --> |block| --> z --> |block| 
""",
""" 
y --> |block| --> \\
    z --> |block| 
""",
""" 
y --> |block| --> z \\ 
    --> |block| 
"""
""" 
y --> |block| --> z --> \\ 
    |block| 
"""
]

bad_examples = \
[

]


class TestLineContinuations(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)

