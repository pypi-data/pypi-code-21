#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import itertools
from collections import deque
from itertools import chain, combinations

from six import moves as six_moves


def chunkwize(chunksize, iterable):
    """
    >>> list(chunkwize(5, range(14)))
    [[0, 1, 2, 3, 4], 
     [5, 6, 7, 8, 9], 
     [10, 11, 12, 13]]
     
    :param chunksize: integer
    :param iterable:
    """
    chunksize = int(chunksize)
    chunk = []
    for item in iterable:
        if len(chunk) >= chunksize:
            yield chunk
            chunk = []
        chunk.append(item)
    yield chunk


def chunkwize_parallel(chunksize, *sequences):
    """
    >>> s1 = '1234567890'
    >>> s2 = 'abcdefghijk'
    >>> list(chunkwize_parallel(4, s1, s2))
    [['1234', 'abcd'], ['5678', 'efgh'], ['90', 'ijk']]
    
    :param chunksize: integer
    :param sequences: tuple of strings or lists (must support slicing!)
    """
    chunksize = int(chunksize)
    for i in itertools.count(0):
        r = [s[i * chunksize:(i + 1) * chunksize] for s in sequences]
        if any(r):
            yield r
        else:
            raise StopIteration


def all_combinations(iterable):
    """
    >>> list(all_combinations('abcd'))
    [(),
     ('a',),
     ('b',),
     ('c',),
     ('d',),
     ('a', 'b'),
     ('a', 'c'),
     ('a', 'd'),
     ('b', 'c'),
     ('b', 'd'),
     ('c', 'd'),
     ('a', 'b', 'c'),
     ('a', 'b', 'd'),
     ('a', 'c', 'd'),
     ('b', 'c', 'd'),
     ('a', 'b', 'c', 'd')]
    """
    items = list(iterable)
    return chain.from_iterable(
        combinations(items, i) for i in range(1 + len(items)))


def window_sum(wsize, numbers):
    """
    >>> numbers = [1, 10, 100, 1000, 10000, 100000]
    >>> list(window_sum(3, numbers))
    [111, 1110, 11100, 111000]
    
    :param wsize: integer, size of the moving window
    :param numbers: an iterable of numbers
    """
    queue = deque(maxlen=wsize)
    for num in numbers:
        queue.append(num)
        if len(queue) >= wsize:
            yield sum(queue)


def alternate(*iterables, **kwargs):
    """
    :param iterables:
    :parameter fill:

    >>> ''.join(list(alternate('ABCD', 'abcde')))
    'AaBbCcDde'
    >>> ''.join(list(alternate('ABCD', 'abcde', fill='_')))
    'AaBbCcDd_e' 
    """
    _void = object()
    fill = kwargs.get('fill', _void)
    zip_longest = six_moves.zip_longest
    alt = itertools.chain(*zip_longest(*iterables, fillvalue=fill))
    for item in alt:
        if item is not _void:
            yield item


def flatten(tup):
    if len(tup) == 1:
        return tup[0]
    if len(tup) == 0:
        return None
    return tup
