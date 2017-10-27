import unittest
from dxpy.collections import dicts





class TestTreeDict(unittest.TestCase):
    def test_basic(self):
        td = dicts.TreeDict()
        td.add_dict('main', '/', {'key1': 'value1'})
        td.add_dict('test', '/main', {'key2': 'value2'})
        td.compile()
        self.assertEqual(td['/main/test']['key1'], 'value1')
        self.assertEqual(td['/main/test']['key2'], 'value2')

    
