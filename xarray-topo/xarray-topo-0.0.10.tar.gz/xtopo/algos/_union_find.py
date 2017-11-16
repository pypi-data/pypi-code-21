"""
A numba class representing an union-find data structure.

"""
import numba as nb
import numpy as np


_unionfind_spec = [
    ('_parent', nb.intp[:]),
    ('_rank', nb.intp[:]),
]


@nb.jitclass(_unionfind_spec)
class UnionFind(object):

    def __init__(self, size):
        self._parent = np.arange(0, size, 1, np.intp)
        self._rank = np.zeros(size, np.intp)

    def union(self, x, y):
        xroot = self.find(x)
        yroot = self.find(y)

        if xroot != yroot:
            if self._rank[xroot] < self._rank[yroot]:
                self._parent[xroot] = yroot
            else:
                self._parent[yroot] = xroot
                if self._rank[xroot] == self._rank[yroot]:
                    self._rank[xroot] += 1

    def find(self, x):
        xp = x
        while True:
            xc = xp
            xp = self._parent[xc]
            if xp == xc:
                break
        self._parent[x] = xc
        return xc
