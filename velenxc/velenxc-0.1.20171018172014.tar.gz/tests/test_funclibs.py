import unittest

from velenxc.funclibs import f, m, r


class RandomGeneratorTestCase(unittest.TestCase):
    def test_f_should_return_itself(self):
        self.assertEqual('me', f.f_('me'))

