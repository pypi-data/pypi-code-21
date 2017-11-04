
import unittest

from velenxc.random import RandomGenerator


class RandomGeneratorTestCase(unittest.TestCase):

    def test_random_digits_seed_6(self):
        digits_string = RandomGenerator.get_random_digits()

        self.assertEqual(len(digits_string), 6)

    def test_random_digits_seed_0(self):
        digits_string = RandomGenerator.get_random_digits(seed_cnt=0)

        self.assertEqual(len(digits_string), 0)
        self.assertTrue(isinstance(digits_string, str))
        self.assertTrue(digits_string is '')

    def test_get_identity_with_datetime(self):
        identity = RandomGenerator.get_identity_with_datetime(prefix='FC')

        self.assertEqual(len(identity), 28)
        self.assertTrue(identity.startswith('FC'))

    def test_should_allow_null_prefix(self):
        identity = RandomGenerator.get_identity_with_datetime()

        self.assertEqual(len(identity), 26)
        self.assertTrue(identity.startswith('2'))
