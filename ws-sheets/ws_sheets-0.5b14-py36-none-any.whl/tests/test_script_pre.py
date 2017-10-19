import numpy
import unittest

import ws_sheets
import ws_sheets.exception
import ws_sheets.tests.conf.simple

class SetScriptPreTest(unittest.TestCase):
    def test(self):
        b = ws_sheets.Book(ws_sheets.tests.conf.simple.Settings)
    
        b.set_script_pre('import os')
        b.do_all()
        
        print('output')
        print(b.script_pre.output)

        self.assertTrue(isinstance(
                b.script_pre.exec_exc,
                ws_sheets.exception.NotAllowedError))
    
        b.set_script_pre("a = 1\n")
    
        b.set_cell('0', 0, 0, "a")
        
        self.assertEqual(
                b['0'][0, 0],
                1)

