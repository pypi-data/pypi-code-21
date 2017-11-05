import copy

__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class PassThru(Exception):
    pass


def check_pass_thru():
    raise PassThru
    yield 1


class SetTestBase:

    def setUp(self):
        self.word = word = 'simsalabim'
        self.otherword = 'madagascar'
        self.letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.s = self.type2test(word)
        self.d = dict.fromkeys(word)

    def test_uniquification(self):
        actual = sorted(self.s)
        expected = sorted(self.d)
        self.assertEqual(actual, expected)
        self.assertRaises(PassThru, self.type2test, check_pass_thru())
        self.assertRaises(TypeError, self.type2test, [[]])

    def test_len(self):
        self.assertEqual(len(self.s), len(self.d))

    def test_contains(self):
        for c in self.letters:
            self.assertEqual(c in self.s, c in self.d)
        self.assertRaises(TypeError, self.s.__contains__, [[]])

    def test_isdisjoint(self):
        def f(s1, s2):
            'Pure python equivalent of isdisjoint()'
            return not set(s1).intersection(s2)
        for larg in '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
            s1 = self.type2test(larg)
            for rarg in '', 'a', 'ab', 'abc', 'ababac', 'cdc', 'cc', 'efgfe', 'ccb', 'ef':
                for C in set, frozenset, dict.fromkeys, str, list, tuple:
                    s2 = C(rarg)
                    actual = s1.isdisjoint(s2)
                    expected = f(s1, s2)
                    self.assertEqual(actual, expected)
                    self.assertTrue(actual is True or actual is False)

    def test_or(self):
        i = self.type2test(set(self.word).union(self.otherword))
        self.assertEqual(self.s | self.type2test(self.otherword), i)
        self.assertEqual(self.s | self.otherword, i)

    def test_and(self):
        i = self.type2test(set(self.word).intersection(self.otherword))
        self.assertEqual(self.s & self.type2test(self.otherword), i)
        self.assertEqual(self.s & self.otherword, i)

    def test_sub(self):
        i = self.type2test(set(self.word).difference(self.otherword))
        self.assertEqual(self.s - self.type2test(self.otherword), i)
        self.assertEqual(self.s - self.otherword, i)

    def test_xor(self):
        i = self.type2test(set(self.word).symmetric_difference(self.otherword))
        self.assertEqual(self.s ^ self.type2test(self.otherword), i)
        self.assertEqual(self.s ^ self.otherword, i)

    def test_equality(self):
        self.assertEqual(self.s, self.type2test(self.word))
        self.assertNotEqual(self.s, self.type2test(self.otherword))

    def test_setOfFrozensets(self):
        t = map(frozenset, ['abcdef', 'bcd', 'bdcb', 'fed', 'fedccba'])
        s = self.type2test(t)
        self.assertEqual(len(s), 3)

    def test_sub_and_super(self):
        p, q, r = map(self.type2test, ['ab', 'abcde', 'def'])
        self.assertTrue(p < q)
        self.assertTrue(p <= q)
        self.assertTrue(q <= q)
        self.assertTrue(q > p)
        self.assertTrue(q >= p)
        self.assertFalse(q < r)
        self.assertFalse(q <= r)
        self.assertFalse(q > r)
        self.assertFalse(q >= r)
        self.assertTrue(set('a').issubset('abc'))
        self.assertTrue(set('abc').issuperset('a'))
        self.assertFalse(set('a').issubset('cbs'))
        self.assertFalse(set('cbs').issuperset('a'))

    def test_deepcopy(self):
        class Tracer:
            def __init__(self, value):
                self.value = value
            def __hash__(self):
                return self.value
            def __deepcopy__(self, memo=None):
                return Tracer(self.value + 1)
        t = Tracer(10)
        s = self.type2test([t])
        dup = copy.deepcopy(s)
        self.assertNotEqual(id(s), id(dup))
        for elem in dup:
            newt = elem
        self.assertNotEqual(id(t), id(newt))
        self.assertEqual(t.value + 1, newt.value)
