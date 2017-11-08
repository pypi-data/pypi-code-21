import os
import sys
sys.path.append('../../')
import copy
import unittest

from batchcompute.utils.canonicalization import remap 
from batchcompute.core.exceptions import JsonError

class TestCanonical(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_remap(self):
        s = "This is not a json string"
        self.assertRaises(JsonError, remap, s)

if __name__ == '__main__':
    unittest.main()
