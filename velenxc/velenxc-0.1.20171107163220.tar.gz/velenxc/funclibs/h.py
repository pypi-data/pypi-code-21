from itertools import zip_longest
from collections import Counter


def h_list_item_counter(seq):
    """
    get item count in list,
    :param seq: list
    :return: dict {item1: count1, item2: count2}
    """

    return Counter(seq)


def h_chunk_list(one_list, chunk_size):
    """
    extend list length to chunk_size
    :param one_list:  list
    :param chunk_size: int
    :return: chunk_size list, if len(one_list) < chunk_size,fill in None
    """
    return zip_longest(*[iter(one_list)] * chunk_size)

