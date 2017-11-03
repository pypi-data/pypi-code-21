# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, absolute_import)
'''
Created on 31 oct. 2017

@author: Jarrige_Pi
'''
import operator
import heapq

#****g* ganessa.sort/About
# PURPOSE
#   The module ganessa.sort provides sorting functions and classes used by the Ganessa tools.
#****
#****g* ganessa.sort/sClasses
#****

#****o* sClasses/HeapSort
# SYNTAX
#   * hs = HeapSort([key]): creates the heap structure. 
#   Instances provide the following methods:
#   * hs.remove(item): removes item - raise KeyError if not found
#   * item, rank = hs.pop(): removes and returns the item of lowest rank.
#   * hs.push(item [, rank]): inserts or replace item with given rank.
#     If the item is already present, its rank and position are updated.
#   * hs.update(item [, rank]): same as push but does nothing if rank unchanged
#   * hs.update_if_lower(item [, rank]): same as push but does nothing if new rank 
#     is higher or equal than the actual rank.
#   * hs.update_if_higher(item [, rank]): same as push but does nothing if new rank 
#     is lower or equal than the actual rank.
#   * count = len(hs): returns the item count in the heap structure
#   
# ARGUMENTS
#   * optional function key: function allowing to compare items being inserted
#   * item: item to be pushed / popped
#   * number rank (optional if key function has been provided to the constructor):
#     defines the ordering of items
# RESULT
#   * hs: HeapSort class member
#   * int count: remaining item count in the heap structure.
# HISTORY
#   Introduced in 1.8.2 (171031)
#****

class HeapSort(object):
    '''Heap sort for a list of objects; makes use of heapq
    hs.push (new or existing item), hs.pop, hs.remove
    hs.update (do not change if equal)
    hs.update_if_higher, hs.update_if_lower'''
    REMOVED = '_<removed-item>_'    # placeholder for a removed item
    
    def __init__(self, key= None):
        self.heap = []              # list of entries arranged in a heap
        self.entry_finder = {}      # mapping of items to entries
        self.counter = 0            # unique sequence count
        self.fun = key
    
    def __len__(self):
        return len(self.entry_finder)
    
    def remove(self, item):
        'Mark an existing item as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(item)
        entry[-1] = HeapSort.REMOVED
        return 
    
    def pop(self):
        'Remove and return the lowest rank item. Raise KeyError if empty.'
        while self.heap:
            rank, _count, item = heapq.heappop(self.heap)
            if item is not HeapSort.REMOVED:
                del self.entry_finder[item]
                return item, rank
        raise KeyError('pop from an empty queue')
        
    def push(self, item, rank= None):
        'Add a new item or update the rank and position of an existing item'
        if rank is None and self.fun is not None:
            rank = self.fun(item)
        if item in self.entry_finder:
            self.remove(item)
        self._add(item, rank)
        
    def update(self, item, rank= None):
        'Add a new item or update the rank if differentk'
        if rank is None and self.fun is not None:
            rank = self.fun(item)
        self._conditional_update(item, rank, operator.__ne__)

    def update_if_lower(self, item, rank= None):
        if rank is None and self.fun is not None:
            rank = self.fun(item)
        self._conditional_update(item, rank, operator.__lt__)

    def update_if_higher(self, item, rank= None):
        if rank is None and self.fun is not None:
            rank = self.fun(item)
        self._conditional_update(item, rank, operator.__gt__)
        
    def _conditional_update(self, item, rank, cond):
        'Add a new item or update the rank of an existing item'
        if item in self.entry_finder:
            entry = self.entry_finder[item]
            # do nothing if rank is the same
            if not cond(rank, entry[0]):
                return
            self.remove(item)
        self._add(item, rank)
    
    def _add(self, item, rank):
        '''Add a non-existing item'''
        self.counter += 1
        entry = [rank, self.counter, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.heap, entry)
