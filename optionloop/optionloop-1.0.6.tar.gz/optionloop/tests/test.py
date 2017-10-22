"""
Simple unit tests for OptionLoop, requires unittest
"""
import unittest
from collections import OrderedDict

from ..optionloop import OptionLoop


class TestOptionLoop(unittest.TestCase):

    def test_empty(self):
        d = {}
        op = OptionLoop(d)
        i = None
        for i in op:
            pass
        self.assertTrue(i is None)

    def test_default_dict(self):
        d = {'test': [True]}
        op = OptionLoop(d, lambda: False)
        for i in op:
            self.assertTrue(i['notakey'] == False)
        op = OptionLoop(d, lambda: True)
        for i in op:
            self.assertTrue(i['notakey'] == True)

    def test_string1(self):
        d = {'a': 'a'}
        op = OptionLoop(d)
        for i in op:
            self.assertTrue(i['a'] == 'a')

    def test_string2(self):
        d = {'a': 'abc'}
        op = OptionLoop(d)
        for i in op:
            self.assertTrue(i['a'] == 'abc')

    def test_multiple_values1(self):
        d = {'a': [False, True]}
        op = OptionLoop(d)
        for i, state in enumerate(op):
            self.assertTrue(state['a'] == i)

    def test_multiple_values2(self):
        d = OrderedDict()
        d['a'] = [False, True]
        d['b'] = [False]
        op = OptionLoop(d)
        for i, state in enumerate(op):
            self.assertTrue(state['a'] == i % 2)
            self.assertTrue(state['b'] == False)

    def test_multiple_values3(self):
        d = OrderedDict()
        d['a'] = [False, True]
        d['b'] = [False]
        d['c'] = [1, 2, 3]
        op = OptionLoop(d)
        for i, state in enumerate(op):
            self.assertTrue(state['a'] == i % 2)
            self.assertTrue(state['b'] == False)
            self.assertTrue(state['c'] == int(i / 2) + 1)

    def test_no_len(self):
        d = {'a': None}
        op = OptionLoop(d)
        for i in op:
            self.assertTrue(i['a'] is None)

    def test_add_oploops(self):
        d = {'a': [False, True]}
        op1 = OptionLoop(d)
        d = {'a': [1, 2]}
        op2 = OptionLoop(d)
        op = op1 + op2
        for i, state in enumerate(op):
            if i < 2:
                self.assertTrue(state['a'] == i % 2)
            else:
                self.assertTrue(state['a'] == i - 1)

    def test_add_oploops2(self):
        d = {'a': [False]}
        op1 = OptionLoop(d)
        d = {'a': [True]}
        op2 = OptionLoop(d)
        op = op1 + op2
        d = {'a': [1, 2]}
        op3 = OptionLoop(d)
        op = op + op3
        for i, state in enumerate(op):
            if i < 2:
                self.assertTrue(state['a'] == i % 2)
            else:
                self.assertTrue(state['a'] == i - 1)

    def test_add_oploops2(self):
        d = {'a': [False]}
        op1 = OptionLoop(d)
        d = {'a': [True]}
        op2 = OptionLoop(d)
        op = op1 + op2
        d = {'a': [1, 2]}
        op3 = OptionLoop(d)
        op = op3 + op
        for i, state in enumerate(op):
            if i >= 2:
                self.assertTrue(state['a'] == i % 2)
            else:
                self.assertTrue(state['a'] == i + 1)

    def test_add_oploops_bad(self):
        d = {'a': [False, True]}
        op1 = OptionLoop(d)
        for i, state in enumerate(op1):
            op2 = OptionLoop(d)
            try:
                op = op1 + op2
                self.assertTrue(False)
            except Exception:
                self.assertTrue(True)

    def test_copy(self):
        d = {'a': [False, True]}
        # test copy interface of oploop
        op1 = OptionLoop(d, lambda: False)

        # run out loop
        for i, state in enumerate(op1):
            pass

        op2 = op1.copy()

        # copy should have same dictionary properties
        self.assertTrue(op2.mydict ==
                        op1.mydict)
        self.assertTrue(op2.default_dict_factory ==
                        op1.default_dict_factory)
        # and a reset index
        self.assertTrue(op2.index == 0)
        # but a same end index
        self.assertTrue(op2.end_index == op1.end_index)

    def test_copy_concat(self):
        d = {'a': [False, True]}
        d2 = {'b': ['a', 'b']}
        # test copy interface of oploop
        op1 = OptionLoop(d, lambda: False)
        op2 = OptionLoop(d2, lambda: False)

        op = op1 + op2

        # run out loop
        for i, state in enumerate(op):
            pass

        op_copy = op.copy()

        # copy should have same dictionary properties
        self.assertTrue(len(op_copy.oplooplist) == len(op.oplooplist))
        for i in range(len(op.oplooplist)):
            # check that the dicts of each oploop in list are same
            self.assertTrue(op.oplooplist[i].mydict ==
                            op_copy.oplooplist[i].mydict)
            self.assertTrue(op.oplooplist[i].default_dict_factory ==
                            op_copy.oplooplist[i].default_dict_factory)
        # and a reset index
        self.assertTrue(op_copy.master_index == 0)


if __name__ == '__main__':
    unittest.main()
