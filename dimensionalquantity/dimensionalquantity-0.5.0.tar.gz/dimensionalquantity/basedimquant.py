#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
This file defines the class BaseDimQuant.
This class builds the basis for DimQuant:
combining a numerical value with an instance of Dimensional.
"""

from functools import wraps

from . import Dimensional as D

# like compatible_with_operation() for Dimensional but expl. only for __add__ and __sub__
def compatible_with_linear_operation(operation='<undefined>'):
    def decorate_specified_operation(method):
        @wraps(method)
        def decorated(self, other, **kwargs):
            if not isinstance(other, BaseDimQuant):
                raise TypeError(''.join(['unsupported operand type(s) for {}:'.format(operation),
                                         ' \'{}\' and \'{}\''.format(type(self).__name__,
                                                                     type(other).__name__)]))
            elif self.dimensions!=other.dimensions:
                raise ValueError(''.join(['Operation {} requires'.format(operation),
                                          'the two operands to have equal dimensions.']))
            else:
                return method(self, other)
        return decorated
    return decorate_specified_operation

def compatible_with_comparison(comparison_name='<undefined>'):
    def comparison(compare):
        @wraps(compare)
        def decorated(self, other, **kwargs):
            if not isinstance(other, BaseDimQuant):
                if self.is_non_dimensional():
                    # how to access (e.g.) self.numeric.__eq__(other)?
                    # 'return self.numeric.compare(other)' doesn't work
                    # because 'self.numeric' doesn't have a method called 'compare'
                    # this hack works, but looks ugly:
                    return eval('self.numeric.{}(other)'.format(compare.__name__))
                else:
                    raise TypeError(' '.join(['\'{}\' not supported'.format(comparison_name),
                                              'between instances of',
                                              '\'{}\' and \'{}\''.format(type(self).__name__,
                                                                         type(other).__name__)]))
            else:
                if (self.dimensions!=other.dimensions):
                    raise NotImplementedError(' '.join(['Comparison \'{}\' is not defined'.format(comparison_name),
                                                        'for dimensional quantities of different dimension!']))
                else:
                    return compare(self, other)
        return decorated
    return comparison

class BaseDimQuant(object):
    """Base class for working with dimensional quantities.
    
    Args:
        numeric (int, float, complex): A number representing the amount of the dimensional quantity.
        dimensions (dict, Dimensional): The dimensions of the quantity.
        
    .. seealso:: 
        This class isn't an abstract or meta class.
        Nonetheless, this class isn't intended to be be used on its own:
        DimQuant (which is derived from BaseDimQuant) offers a more convenient string based constructor.
        :py:meth: `dimensionalquantity.DimQuant`"""
    def __init__(self, numeric=0, dimensions=D({})):
        self.numeric=numeric
        self.dimensions=dimensions

    @property
    def numeric(self):
        """A number (int, float, complex) representing the amount of the dimensional quantity."""
        return self.__numeric
    @numeric.setter
    def numeric(self, value):
        if isinstance(value, (int, float, complex)) \
                and not isinstance(value, bool): # note: bool is instance of int but that doesn't make sense here!
            self.__numeric = value
        else:
            raise TypeError('Numeric value isn\'t a numeric type but of \'{}\' instead.'.format(type(value).__name__))

    @property
    def dimensions(self):
        """The dimensions (dict, Dimensional) of the quantity in the format of a dict.
        It is e.g. for '1 m': dimensions = {'L': 1}."""
        return self.__dimensions
    @dimensions.setter
    def dimensions(self, dims):
        if isinstance(dims, (D, dict)):
            self.__dimensions = D(dims)
        else:
            raise TypeError('Dimensions aren\'t of type \'Dimensional\' but of \'{}\' instead.'.format(type(dims).__name__))
    
    @compatible_with_linear_operation('+')
    def __add__(self, other):
        return self.__class__(numeric = self.numeric+other.numeric,\
                              dimensions = D(self.dimensions))
    # the __radd__ isn't actually necessary
    # because the compatible_with_linear_operation decorator
    # anyway only accepts other's of BaseDimQuant type
    # hence, the only time __radd__ would come into play would be
    # to throw a TypeError; which we can easily leave for other to throw.
    #@compatible_with_linear_operation('+')
    #def __radd__(self, other):
    #    self.__add__(other)

    @compatible_with_linear_operation('-')
    def __sub__(self, other):
        return self.__class__(numeric = self.numeric-other.numeric,\
                              dimensions = D(self.dimensions))
    # not implementing __rsub__ for same reason as __radd__
    #@compatible_with_linear_operation('-')
    #def __rsub__(self, other):
    #    return -self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, BaseDimQuant):
            #return BaseDimQuant(numeric = self.numeric*other.numeric,\
            #                dimensions = self.dimensions+other.dimensions)
            return self.__class__(numeric = self.numeric*other.numeric,\
                                  dimensions = self.dimensions+other.dimensions)
        else:
            return self.__class__(numeric = self.numeric*other,\
                                  dimensions = D(self.dimensions))
    def __rmul__(self, other):
        return self*other

    def __truediv__(self, other):
        if isinstance(other, BaseDimQuant): 
            return self.__class__(numeric = self.numeric/other.numeric,\
                                  dimensions = self.dimensions-other.dimensions)
        else:
            return self.__class__(numeric = self.numeric/other,\
                                  dimensions = D(self.dimensions))

    def __rtruediv__(self, other):
        # if isinstance(other, BaseDimQuant): this case is covered by __truediv__
        return self.__class__(numeric = other/self.numeric,\
                              dimensions = -1*D(self.dimensions))

    # __pow__ makes sense only if the exponent is either not an instance of BaseDimQuant
    # or if all entries of BaseDimQuant.dimensions are 0
    def __pow__(self, other):
        if not isinstance(other, BaseDimQuant):
            return self.__class__(numeric = self.numeric**other,\
                                  dimensions = self.dimensions*other)
        else:
            if not other.is_non_dimensional():
                raise NotImplementedError(' '.join(['The exponent cannot be a dimensional quantity,',\
                                                    'it has to be a purely numerical value!']))
            else:
                if self.is_non_dimensional():
                    return self.numeric**other.numeric
                else:
                    return self**other.numeric
    def __rpow__(self, other):
        return self.__class__(other)**self

    @compatible_with_comparison('==')
    def __eq__(self, other):
        """according to https://docs.python.org/3/reference/datamodel.html
        __eq__ directly also takes care of __neq__
        """
        return (self.numeric == other.numeric)

    @compatible_with_comparison('>')
    def __gt__(self, other):
        return (self.numeric > other.numeric)

    @compatible_with_comparison('>=')
    def __ge__(self, other):
        return (self.numeric >= other.numeric)

    @compatible_with_comparison('<')
    def __lt__(self, other):
        return (self.numeric < other.numeric)

    @compatible_with_comparison('<=')
    def __le__(self, other):
        return (self.numeric <= other.numeric)

    def is_non_dimensional(self):
        """Method to test whether the dimensional quantity
        is actually dimension-free.
        Dimension-free represents that either
        the length of dimensions declared is 0
        (i.e. no dimensions declared), or
        all declared dimensions are 0.
        A dimensional quantity can be dimension-free,
        i.e. non-dimensional,
        e.g. if a length quantity is divided by another length.
        The start point of such a division is necessarily
        a dimensional quantity
        (or at least, the point of this module is to support such a case)
        but the result is a pure number.

        .. seealso:
            It doesn't make sense to have a dimensional exponent;
            e.g. 2**'1 m' isn't defined.
        """
        return ( (len(self.dimensions)==0) or not any(self.dimensions.values()) )

    def __repr__(self):
        """Example:
        >>> q = BaseDimQuant('1 m/s')
        >>> print(q)
        BaseDimQuant(1, Dimensional({'L':1, 't':-1})"""
        return 'BaseDimQuant({}, {})'.format(self.numeric,self.dimensions)
