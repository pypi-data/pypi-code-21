
from __future__ import division, print_function, unicode_literals, absolute_import

import unittest

try:
    import context
except ImportError:
    from . import context

import ordered_namespace as ons


"""
Kinds of tests:
    self.assertTrue(value)
    self.assertFalse(value)

    self.assertGreater(first, second, msg=None)
    self.assertGreaterEqual(first, second, msg=None)
    self.assertLess(first, second, msg=None)
    self.assertLessEqual(first, second, msg=None)

    self.assertAlmostEqual(first, second, places=7, msg=None, delta=None)
    self.assertNotAlmostEqual(first, second, places=7, msg=None, delta=None)

    self.assertItemsEqual(actual, expected, msg=None)
    self.assertSequenceEqual(seq1, seq2, msg=None, seq_type=None)
    self.assertListEqual(list1, list2, msg=None)
    self.assertTupleEqual(tuple1, tuple2, msg=None)
    self.assertSetEqual(set1, set2, msg=None)
    self.assertDictEqual(expected, actual, msg=None)

    self.assertRaises(Exception, some_func, arg, arg_nother)

    np.testing.assert_equal(A, B)
    np.testing.assert_allclose(actual, desired, rtol=1e-07, atol=0, err_msg='', verbose=True)
"""

#------------------------------------------------

class TestBasic(unittest.TestCase):
    # def setUp(self):
    #     pass

    # def tearDown(self):
    #     pass

    def test_does_it_run(self):
        info = ons.Struct()

    def test_attributes(self):
        info = ons.Struct()

        item = [1, 2, 3]
        info.AA = item

        self.assertTrue(item == info.AA)

    def test_keys(self):
        info = ons.Struct()

        item = [1, 2, 3]
        info['AA'] = item

        self.assertTrue(item == info['AA'])

    def test_attributes_keys(self):
        info = ons.Struct()

        item = [1, 2, 3]
        info['AA'] = item

        self.assertTrue(item == info.AA)

    def test_order(self):
        keys = ['Z', 'z', 'a', 'B00', 'B1', 'B0']
        values = list(range(len(keys)))

        info_1 = ons.Struct()
        info_2 = ons.Struct()

        for k, v in zip(keys, values):
            info_1[k] = v

        for k, v in zip(keys[::-1], values[::-1]):
            info_2[k] = v

        keys_test_1 = list(info_1.keys())
        keys_test_2 = list(info_2.keys())

        self.assertTrue(keys_test_1 == keys_test_2[::-1])

    def test_nested_dict_converted(self):
        info = ons.Struct()

        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye'}

        info.AA = nuts
        info.AA.BB = corn

        self.assertTrue(type(info.AA) == ons.Struct)
        self.assertTrue(type(info.AA.BB) == ons.Struct)

    def test_as_dict(self):
        info = ons.Struct()

        nuts = {'a': [1, 2], 'X': 'hello'}
        corn = {'b': [6, 9], 'Y': 'bye'}

        info.AA = nuts
        info.AA.BB = corn

        info = info.asdict()

        self.assertTrue(type(info['AA']) == dict)
        self.assertTrue(type(info['AA']['BB']) == dict)


#------------------------------------------------

if __name__ == '__main__':
    unittest.main(verbosity=2)
