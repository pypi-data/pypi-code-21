# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 18:35:49 2016

@author: danb0b
"""

class Iterable(object):

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.list[index]

        elif isinstance(index, slice):
            return type(self)(*self.list[index])

    def __setitem__(self, index, v):
        if isinstance(index, int):
            self.list[index] = v
            
        elif isinstance(index, slice):
            if isinstance(v,Iterable):
                self.list[index] = v.list
            elif isinstance(v,list):
                self.list[index] = v
            else:
                raise(Exception())

    def __iter__(self):
        for item in self.list:
            yield item

    def __len__(self):
        return len(self.list)