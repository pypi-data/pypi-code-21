import math

from cobweb.defaults import MAX_FILTER_SIZE


class BloomFilter:

    def __init__(self, max_elements=MAX_FILTER_SIZE):
        self.maximum = max_elements
        self.size = 0
        self.items = 0

    def __contains__(self, item: str):
        _hash = hash(item)
        return _hash & self.items == _hash

    def __len__(self):
        return self.size

    def count_error_probability(self):
        return 2 ** - math.log(self.maximum / self.size) if self.size else 0

    def add(self, item: str):
        _hash = hash(item)
        self.size += 1
        self.items |= _hash

    def clear(self):
        self.items = 0
        self.size = 0
