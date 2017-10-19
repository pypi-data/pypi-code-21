from .utils import PGTestCase

good_examples = [
('''
--- model master
config  a      "well documented param"
config  b = 3  "well documented param"

|verify x=$a y=$b|
''', {'a': 3, 'b': 3}),
('''
--- model master
config  a      "well documented param"
config  b = 3  "well documented param"

|verify x=$a y=$b|
''', {'a': 3}),
# Now using the dict syntax with "."
('''
--- model master
|verify y=2|
''', {'verify.x': 2}),
# Same thing, but with module name
('''
--- model master
|v:verify y=2|
''', {'v.x': 2}),
]

good_examples_plus = [
# Now using the dict syntax without "."
('''
--- model master
|v:verify y=2|
''', {'v': {'x': 2}}),
# Now using the dict syntax without "."
('''
--- model master
|verify y=2|
''', {'verify': {'x': 2}}),
]

bad_examples = [
('''
# a is not assigned
--- model master
config  a      "well documented param"
config  b = 3  "well documented param"

|verify x=$a y=$b|
''', {'b': 3}),
('''
# double description
--- model master
config  a      "well documented param"
config  a      "well documented param"

b=2
''', {}),
('''
# overwriting configuration
--- model master
config  a      "well documented param"

a=2
''', {}),

('''
--- model master
""" Cannot have a config variable with the same name as a block """
config  a      "well documented param"
|a:verify x=$a y=$a|
''', {})


]


class SemanticsTest(PGTestCase):

#    @unittest.skip('This is not implemented yet')
#    @unittest.expectedFailure
#    def testNewExamples(self):
#        for example, config in good_examples_plus:
#            self.check_semantic_ok(example, config=config)

    def testExamples(self):
        for example, config in good_examples:
            self.check_semantic_ok(example, config=config)

    def testBadExamples(self):
        for example, config in bad_examples:
            self.check_semantic_error(example, config=config)

