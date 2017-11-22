"""Management of Persistent Objects."""

import lru
import collections

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'


# FIXME un-hardcode this
cached_objects_dict = lru.LRU(500)


class IdentityDict(collections.MutableMapping):
    __slots__ = ("internal_dict",)

    def __init__(self):
        self.internal_dict = dict()

    def __setitem__(self, key, value):
        self.internal_dict[id(key)] = (key, value)

    def __getitem__(self, item):
        return self.internal_dict[id(item)][1]

    def __delitem__(self, key):
        del self.internal_dict[id(key)]

    def __len__(self):
        return len(self.internal_dict)

    def __iter__(self):
        return self.internal_dict.itervalues()

    def __contains__(self, item):
        return id(item) in self.internal_dict
