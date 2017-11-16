from __future__ import unicode_literals

import unittest

from tecplot.tecutil import StringList
from tecplot.exception import TecplotTypeError

class TestStringList(unittest.TestCase):

    def test_init(self):
        sl = StringList()
        self.assertEqual(len(sl), 0)
        self.assertEqual(str(sl), str(list()))

        sl = StringList('aa','bb')
        self.assertEqual(len(sl), 2)
        self.assertEqual(str(sl), str(['aa','bb']))

    def test_repr(self):
        sl = StringList('aa', 'bb')
        self.assertEqual(repr(sl), "StringList('aa', 'bb')")

    def test_iter(self):
        data = ['aa','bb','cc']
        sl = StringList(*data)
        for d,s in zip(data,sl):
            self.assertEqual(d,s)

    def test_iadd(self):
        sl = StringList()
        sl += ['aa','bb']
        self.assertEqual(len(sl), 2)
        self.assertEqual(str(sl), str(['aa','bb']))

    def test_eq(self):
        with StringList('ab','cd') as sl1:
            with StringList('ef', 'gh') as sl2:
                self.assertFalse(sl1 == sl2)
                self.assertNotEqual(sl1,sl2)
            with StringList('ij') as sl2:
                self.assertFalse(sl1 == sl2)
                self.assertNotEqual(sl1,sl2)
            with StringList('ab','cd') as sl2:
                self.assertEqual(sl1,sl2)

    def test_context(self):
        with StringList() as sl:
            sl += ['aa','bb']
            self.assertEqual(str(sl), str(['aa','bb']))

    def test_append(self):
        sl = StringList()
        sl.append('aa')
        sl.append('bb')
        self.assertEqual(len(sl), 2)
        self.assertEqual(str(sl), str(['aa','bb']))
        self.assertRaises(TecplotTypeError, sl.append, 1)

    def test_clear(self):
        sl = StringList('aa','bb')
        sl.clear()
        self.assertEqual(len(sl),0)

    def test_long_strings(self):
        sl = StringList('a'*100, 'b'*1024)
        self.assertEqual(sl[0], 'a'*100)
        self.assertEqual(sl[1], 'b'*1024)

        sl = StringList()
        sl.append('a'*100)
        sl.append('b'*1024)
        self.assertEqual(sl[0], 'a'*100)
        self.assertEqual(sl[1], 'b'*1024)

    def test_next(self):
        data = ['aa','bb']
        with StringList(*data) as sl:
            item = iter(sl).next()
            self.assertIn(item, sl)
            self.assertIn(item, data)

if __name__ == '__main__':
    from .. import main
    main()
