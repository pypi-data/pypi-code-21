import unittest

from velenxc.funclibs.h import *


class HListItemCounterCase(unittest.TestCase):
    """test h.h_list_item_counter function
    """
    def test_input_null_list_return_null_dict(self):
        self.assertEqual({}, h_list_item_counter([]))

    def test_input_item_list_return_counter(self):
        self.assertEqual({'a': 2, 'b': 1}, h_list_item_counter(['a', 'a', 'b']))


class HChunkListCase(unittest.TestCase):
    """test h.h_chunk_list function
    """
    def test_input_less_size_list_return_self(self):
        self.assertEqual([('1', '2')], list(h_chunk_list(['1', '2'], 2)))

    def test_input_bigger_size_list_return_extend_list(self):
        self.assertEqual([('1', '2', None, None)], list(h_chunk_list(['1', '2'], 4)))

