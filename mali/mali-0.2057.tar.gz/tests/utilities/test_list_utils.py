# coding=utf-8
from tests.base import BaseTest
from mali_commands.utilities.list_utils import flatten


class TestListUtils(BaseTest):

    def testFlatten(self):
        iterable = [[1, 2], [3, 4], [5], (6, 7)]
        expected = [1, 2, 3, 4, 5, 6, 7]

        self.assertEqual(flatten(iterable), expected)
