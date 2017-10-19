from .utils import PGTestCase

good_examples = [
"u = -1",
"|GENERATOR| --> result",
"result --> |SINK|",
"u -> |FUNCTION| --> result",
"u ,v -> |FUNCTION| --> result, d",
"u -> |opa:FUNCTION| ->  result",
"u --> |op1:FUNCTION op=tan| -> result",
"u -> |FUNCTION| -> |FUNCTION2| -> result",
"u -> |FUNCTION| -> a -> |FUNCTION2| -> result",
"u -> |FUNCTION| -> a -> |FUNCTION2| -> |FUNCTION2| -> result",
"u -> |FUNCTION| -> a -> |FUNCTION2| ---> a,d --> |FUNCTION2| -> result",
"""  |origin| -> a  -> |block| """,
""" |constant value=12| -> [0] a  -> |block| """,
"u = 1",
"""u = 1
u = 2
u =3 """, """u = 2
x -> |func2| -> res3""",
"""x -> |func2| 
u = 2""",
"""

x -> |func2| 

u = 2

""",
" a -> |block| ",
" a[o] -> |block| ",
" a.s[o] -> |block| ",
" [i]a -> |block| ",
" [i]a[d] -> |block| ",
" [i]a[d], b -> |block| ",
" [i]a[d], b[c] -> |block| ",
" b1.f [input_name] -> |test| -> [t] y [U], z [t] -> |test| -> res",
""" 
b1.f [input_name] -> |test| -> [t] y [U], z [t] -> |test| -> res
""",
"""
# this is a comment
u = 1
""",
# I don't think we use it anymore
# in case, readd:
# # parameter_list = delimitedList(key_value_pair) ^ OneOrMore(key_value_pair)
# " |generic in=0,out=2|  ",
" |generic in=0 out=2|  ",
# assignment with object
""" 
g1.in = 2
""",
# quoted strings
"""
g1.in = "ciao"
""",
"""
g1.in = 'ciao'
""",
# Triple quotes
"""
g1.in = '''ciao
come va'''
""",
'''
g1.in = """ciao
come va"""
''',

"""
g1.in = "ci\\"a/o"
""",
# underscores 
" |output name=x_old|  ",

# new syntax: allow whitespace

"""
|a| -> |b| \ 
-> |c|
""",
"""
|a| -> |b| -> 
    -> |c|
""",

"""
|a| -> |b|  
    -> |c|
""",

" (in) -> |a| ",
" (in) -> in ",

" a -> |a| -> (out) ",
" |a| -> (out) ",
" a -> (out) ",
" (in) -> |a| -> (out) ",





]


bad_examples = [
# empty string gives error
"   \n \n ",
"u = -1a",
"|GENERATOR| --> result resu",
"|GENERATOR GENERATOR| --> result resu",
"result x --> |SINK|",
"u -> |FUNCTION| |FUNCTION| --> result",
# invalid names
".u = 2",
".u.d = 2",
"1u = 2",
# bad quotation
""" a = "ci"ao" """

]


class SyntaxTest(PGTestCase):

    def testBadExamples(self):
        for example in bad_examples:
            self.check_syntax_error(example)

    def testExamples(self):
        for example in good_examples:
            self.check_syntax_ok(example)

