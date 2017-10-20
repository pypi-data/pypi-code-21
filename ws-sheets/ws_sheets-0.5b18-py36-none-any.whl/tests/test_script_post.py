import numpy

import ws_sheets
import ws_sheets.tests.conf

def test_script_post(settings):
    b = ws_sheets.Book(settings)

    b.set_script_pre('import math\na=math.pi')

    b['0'][0, 0] = 'a'

    b.set_script_post("print(book['0'][0, 0])")

    b.do_all()
   
    print('script post output', repr(b.script_post.output))

    assert b.script_post.output == '3.141592653589793\n'


