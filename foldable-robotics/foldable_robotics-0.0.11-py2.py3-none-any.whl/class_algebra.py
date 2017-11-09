# -*- coding: utf-8 -*-
"""
Created on Mon May 16 09:55:55 2016

@author: danb0b
"""
class ClassAlgebra(object):
    def __or__(self,other):
        return self.union(other)
        
    def __sub__(self,other):
        return self.difference(other)
        
    def __and__(self,other):
        return self.intersection(other)        

    def __xor__(self,other):
        return self.symmetric_difference(other)

    def __lshift__(self,value):
        return self.dilate(value)

    def __rshift__(self,value):
        return self.erode(value)
        
