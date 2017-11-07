from copy import *
import math


def _contains(x, C):
    return x in C


class Set:
    def __init__(self, elems, containsF = _contains):
        self.elems = elems
        self._contains = containsF # It is a function! Not a method!


    def setContainsFunction(self, f):
        self._contains = f


    def __contains__(self, elem):
        return self._contains(elem, self)


    def __mul__(self, b):
        return Set(intersection(self.elems, b.elems, self._contains), self._contains)


    def __add__(self, b):
        return Set(union(self.elems, b.elems, self._contains), self._contains)


    def __sub__(self, b):
        return Set(sub(self.elems, b.elems, self._contains), self._contains)


    def __str__(self):
        return "<{}: {}>".format(Set.__name__, str(list(self.elems)))


def union(a, b, contains = _contains):
    ret = copy(a)
    for elem in b:
        if not contains(elem, ret):
            ret.append(elem)
    return ret


def intersection(a, b, contains = _contains):
    ret = []
    for elem in a:
        if contains(elem, b):
            ret.append(elem)
    return ret


def sub(a, b, contains = _contains):
    ret = []
    for elem in a:
        if not contains(elem, b):
            ret.append(elem)
    return ret


if __name__ == '__main__':
    a = Set([1.1,2.2,3.3], lambda x, C: math.floor(x) in map(math.floor, C))
    b = Set([2.1,3.4,4.5])

    print(a + b)
    print(a * b)
    print(a - b)
    print(b - a)
