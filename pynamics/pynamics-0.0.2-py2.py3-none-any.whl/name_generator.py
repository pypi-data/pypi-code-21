# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 17:35:06 2017

@author: danaukes
"""

class NameGenerator(object):

    @classmethod
    def generate_name(cls):
        try:
            name = cls._generate_name()
        except AttributeError:
            cls._ii = 0
            name = cls._generate_name()
        return name
    
    @classmethod
    def _generate_name(cls):
        try:
            typestring = cls.typestring
        except AttributeError:
            typestring = cls.__name__
            typestring = typestring.lower()
        
        try:
            typeformat = cls.typeformat
        except AttributeError:
            typeformat = '{0}_{1:04d}'
        
        name = typeformat.format(typestring,cls._ii)
        cls._ii+=1
        return name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
    