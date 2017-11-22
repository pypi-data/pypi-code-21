import unittest

from hgicommon.helpers import create_random_string, extract_version_number

_PREFIX = "123"
_POSTFIX = "456"


class TestCreateRandomString(unittest.TestCase):
    """
    Tests for `create_random_string`.
    """
    def test_no_prefix_or_postfix(self):
        string = create_random_string()
        self.assertGreater(len(string), 0)
        self.assertIsInstance(string, str)

    def test_prefix(self):
        string = create_random_string(prefix=_PREFIX)
        self.assertTrue(string.startswith(_PREFIX))

    def test_postfix(self):
        string = create_random_string(postfix=_POSTFIX)
        self.assertTrue(string.endswith(_POSTFIX))

    def test_prefix_and_postfix(self):
        string = create_random_string(prefix=_PREFIX, postfix=_POSTFIX)
        self.assertTrue(string.startswith(_PREFIX))
        self.assertTrue(string.endswith(_POSTFIX))


class TestExtractVersionNumber(unittest.TestCase):
    """
    Tests for `extract_version_number`.
    """
    def test_when_no_version_number(self):
        self.assertRaises(ValueError, extract_version_number, "no_version_number")

    def test_when_major_version_number(self):
        self.assertEqual("1", extract_version_number("test1version"))

    def test_when_major_minor_version_number(self):
        self.assertEqual("1.2", extract_version_number("test1_2version"))

    def test_when_major_minor_patch_version_number(self):
        self.assertEqual("1.2.3", extract_version_number("test1_2_3version"))

    def test_when_multiple_version_numbers(self):
        self.assertEqual("1", extract_version_number("test1or2"))


if __name__ == "__main__":
    unittest.main()
