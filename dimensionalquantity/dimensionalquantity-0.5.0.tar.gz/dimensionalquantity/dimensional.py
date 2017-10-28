#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
This file defines the class Dimensional.
This class is at the heart of the concept behind dimensionalquantity:
each dimension -- as a name -- is represented by a dictionary key,
with the corresponding value being the exponent of how often a certain dimension is referred to.
For example, a volume is given by a qubic length.
Hence, the Dimensional of a volume is represented by {'L':3}.
This representation is simple enough and doesn't need its own class.
The class Dimensional provides the functionality
to add, subtract, multiply, etc. instances of Dimensional.
"""

from functools import wraps

# wrapper for Dimensional operations (such as __add__, __sub__) to
# i.   make code more readable by putting reoccuring stuff here,
# ii.  make behavior more intuitive (Dimensional looks like a dict,
#      so it should at least run silently for dicts),
# iii. report sensible error messages
def compatible_with_operation(operation='<undefined>'):
    def decorate_specified_operation(method):
        @wraps(method)
        def decorated(self, other, **kwargs):
            try:
                return method(self, other)
            except (KeyError, AttributeError):
                # while technically an error, for the user there is no real difference
                # between a Dimensional and a dict or ordered_dict or default_dict, etc.
                # hence KeyError is easy to fix:
                # input 'other' has to be converted into Dimensional
                # (if compatible with dict)
                # otherwise the 'KeyError' is actually a TypeError
                # note: isinstance(other, dict) is True also derived instances
                # such as defaultdict or OrderedDict
                if isinstance(other, dict):
                    return method(self, Dimensional(other))
                else:
                    raise TypeError(''.join(['unsupported operand type(s) for {}:'.format(operation),
                                             ' \'{}\' and \'{}\''.format(type(self).__name__,
                                                                         type(other).__name__)]))
        return decorated
    return decorate_specified_operation

class Dimensional(dict):
    """Base class for working with dimensions.
    
    Args:
        Any valid dictionary argument.
        The keys represent the name of the dimension,
        while the values how often said a certain dimension is referred to."""

    def __getitem__(self, key):
        return super(Dimensional, self).get(key,0)
    
    @compatible_with_operation('+')
    def __add__(self, other):
        return Dimensional({key:self[key]+other[key] for key in set(self.keys()).union(other.keys())})

    @compatible_with_operation('+')
    def __radd__(self, other):
        return self.__add__(other)
        
    @compatible_with_operation('-')
    def __sub__(self, other):
        return Dimensional({key:self[key]-other[key] for key in set(self.keys()).union(other.keys())})
    
    @compatible_with_operation('-')
    def __rsub__(self, other):
        return Dimensional({key:other[key]-self[key] for key in set(self.keys()).union(other.keys())})
        
    def __mul__(self, other):
        if isinstance(other, (int, float, complex)):
            return Dimensional({key:other*value for key, value in self.items()})
        else:
            raise TypeError(''.join(['unsupported operand type(s) for /:',
                                     ' \'{}\' and \'{}\''.format(type(self).__name__,
                                                                 type(other).__name__)]))
    def __rmul__(self, other):
        return self*other

    def __repr__(self):
        """default (because derived from dict): {'a':1, 'b':2, ...}"""
        return 'Dimensional({})'.format(super(Dimensional, self).__repr__())
