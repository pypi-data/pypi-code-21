from __future__ import print_function

import larch

from larch.inputText import InputText

_larch = larch.Interpreter()

inp = InputText(prompt='>', _larch=_larch, interactive=False)


text = """
a = 1.030
b = '''line 1
multiline string
line 3
'''

ox = 12.

print('''
multiline %s
''' % 'a')


a = '''
multiline comment
with a ' or two.
here's one!
'''

"""

inp.put(text)


while len(inp) > 0:
    block, fname, lineno = inp.get()
    print(">  ", block)
    _larch.eval(block, fname=fname, lineno=lineno)

print("######### ")
