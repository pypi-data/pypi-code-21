#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
This file defines the most important class DimQuant,
which is a child of BaseDimQuant.
The difference with respect to BaseDimQuant is the ability to
initialize a DimQuant instance using a string representation
of a dimensional quantity.
In BaseDimQuant the user has to provide two arguments:
a numerical value, and a Dimensional instance.
In DimQuant the instanciation is simplified.
"""

from . import Dimensional as D
from . import BaseDimQuant
from . import Translator

class DimQuant(BaseDimQuant):
    """Class for working with dimensional quantities.
    
    Args:
        args (string): the usual way to instanciate an object of this class is
            by means of a string such as '1 kg/m2', or '2 m.s'.
        *args (optional): alternatively to the string representation of the quantity
            this class accepts the same arguments as BaseDimQuant.

    .. seealso:: 
        The legal dimensional identifiers for the string representation
        can be found in
        :py:meth: `dimensionalquantity.Translator`"""

    _T = Translator()

    def __init__(self, *args, **kwargs):
        if len(args)==1 and isinstance(args[0], str):
            dq_string = args[0]
            _q, _d = dq_string.split(' ')
            _DQ = self._T.translate(_d)
            self.numeric = _DQ.numeric * float(_q)
            self.dimensions = _DQ.dimensions
        else:
            super(DimQuant, self).__init__(*args, **kwargs)

    def __repr__(self):
        """Example:
        >>> q = DimQuant('1 m/s')
        >>> print(q)
        DimQuant(1, Dimensional({'L':1, 't':-1})"""
        return 'DimQuant({}, {})'.format(self.numeric,self.dimensions)

    def __str__(self):
        """Example:
        >>> q = DimQuant('1 m/s')
        >>> str(q)
        '1 m.s-1'
        Though, the exact result depends on the registered translator.
        .. seealso:: 
            :py:meth: `dimensionalquantity.BasicTranslator`
            :py:meth: `dimensionalquantity.Translator`
        """
        unit_string = self._T.reverse_unit_lookup(self.dimensions)
        return ' '.join([str(self.numeric), unit_string])

    @classmethod
    def register_translator(cls, translator):
        """Thanks to the registered translator we can
        convert a string representation (like '1 m/s') into a `DimQuant`,
        and also a `DimQuant` into a string;
        which is more human readable.
        This is a classmethod,
        which means all DimQuant instances share the same translator.
        Typically, this method is called at the beginning of a script;
        right after registering the corresponding look-up-tables (LUTs)
        needed for the translator.
        Without explicitly registering a translator,
        a default instance of `Translator` is used.

        Args:
            translator (Translator): an instance capable to
                interpret the string representations used in a particular script.

        .. seealso:: 
            :py:meth: `dimensionalquantity.BasicTranslator`
            :py:meth: `dimensionalquantity.Translator`
        """
        cls._T = translator
