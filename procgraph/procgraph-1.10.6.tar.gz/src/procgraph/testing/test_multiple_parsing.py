from .utils import PGTestCase

good_examples = \
[
"""--- model ciao
y = 2
""",
"""------ model ciao
y = 2
""",
"""
--- model ciao
y = 2
--- model belle
y = 2
""",

"""

--- model ciao

y = 2

--- model belle
y = 2


""",
"""
# comments at the beginning should not start a model
--- model belle
e = 2
""",
"""
# spacing 
---   model   belle
e = 2
""",

# Testing docstrings
"""
--- model ciao
''' This is the documentation
    for this model.            '''
y = 2
""",
"""

--- model ciao

''' This is the documentation
    for this model.            '''
y = 2
""",

"""
--- model ciao
config ciao "test"

''' this is a documentation for the block '''
|block|

"""



]

bad_examples = \
[

"""
# Mixing

y = 2

--- model belle
y = 2
""",
"""
# Empty
--- model belle

--- model belle
y = 2
""",

"""
# incomplete
--- model belle
e = 2
--- model belle

""",

"""
# bad name
--- model 1belle
e = 2
""",
"""
# bad syntax
-- model 1belle
e = 2
""",

"""
# should be on the same line 
---   model  
belle
e = 2
""",
# docstring should be the first thing
"""
--- model ciao
y = 2
''' This is the documentation
    for this model.            '''

"""

]


class SyntaxTestMultiple(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)

