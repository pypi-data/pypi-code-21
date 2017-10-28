#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""This `translator.py` provides the classes `BasicTranslator`, and `Translator`.
These two classes enable the functionality
to initialize a `DimQuant` with a string representation of a dimensional quantity,
e.g. '1 m.s',
instead of the more cumbersome `BaseDimQuant` init
with a numeric and a Dimensional argument."""

import re # https://docs.python.org/3/library/re.html#writing-a-tokenizer
from collections import namedtuple

from . import Dimensional as D
from . import BaseDimQuant as DQ


# https://docs.python.org/3/library/re.html#writing-a-tokenizer
Token = namedtuple('Token', ['typ', 'value'])

SI_unit_LUT = {'m': DQ(1, {'L':1}),
               's': DQ(1, {'t':1}),
               'K': DQ(1, {'T':1}),
               'A': DQ(1, {'i':1}),
               'mol': DQ(1, {'N':1}),
               'cd': DQ(1, {'J':1}),
               # SI uses 'kg' as base unit, i.e. '1e3 g',
               # but instead of creating a special case,
               # initalizing 'g' as basic seems to be cleaner.
               'g': DQ(1e-3, {'M':1}), 
               }

SI_prefix_LUT = {'Y': 1e24,
                 'Z': 1e21,
                 'E': 1e18,
                 'P': 1e15,
                 'T': 1e12,
                 'G': 1e9,
                 'M': 1e6,
                 'k': 1e3,
                 'h': 1e2,
                 #'da': 1e1, # TBD: this is the only prefix needing more than one character
                 '': 1e0,
                 'd': 1e-1,
                 'c': 1e-2,
                 'm': 1e-3,
                 'u': 1e-6,
                 'n': 1e-9,
                 'p': 1e-12,
                 'f': 1e-15,
                 'a': 1e-18,
                 'z': 1e-21,
                 'y': 1e-24,
                 }

class BasicTranslator(object):
    """Class that is able to convert a string representation of a dimensional quantity, e.g. '1 m.s', into a Dimensional object.
    This class further allows to convert back, from a Dimensional to a string.
    
    Args:
        The init of this class takes no arguments.
        The main use of this class is through the two methods `translate()` and `reverse_unit_lookup()`.
        However, before you can use those two methods (e.g. to hand it the above example of '1 m.s'),
        you have to register (`register_*_LUT()`) a look-up-table.
        
    .. seealso:
        If you're interested to work with pre-registered LUTs (corresponding to default SI support) use `Translator()` instead.
        This is a child of `BasicTranslator`, and the recomended way of using `BasicTranslator`;
        because `BasicTranslator` provides only a naked infrastructure.
        :py:meth: `dimensionalquantity.Translator`
    """

    # the following protected entries are available (and identical)
    # for all instances of Translator()
    # https://docs.python.org/3/library/re.html#writing-a-tokenizer
    _token_specification = [
        ('UNIT',  r'[A-Za-z]+'), # any collection of letters...
        ('HOWOFTEN', r'(\-)?(\d+(\.\d+)?)'), # a (possibly negative) (float) number
        ('SEP',r'\.'),            # '.' is a separator, has no real functionality except to help understand from where to where a unit goes
        ('NEGSEP',r'\/'),            # m/s should be the same as m.s-1; NEGSEP makes sure we don't miss the '-1'
        ('GROUPOPEN', r'\('), # stuff between (...) should both apply to '/' inverting the sign of the exponents as well as exponents overall
        ('GROUPCLOSE', r'\)'),
        ]
    _token_grammar = '|'.join('(?P<%s>%s)' % pair for pair in _token_specification)
    _token_program = re.compile(_token_grammar)

    def __init__(self):
        self._unit_LUT = {}
        self._prefix_LUT = {}

    @classmethod
    def _tokenize(cls, string):
        yield Token('GROUPOPEN','^')
        for match in cls._token_program.finditer(string):
            kind = match.lastgroup
            value = match.group(kind)
            if kind=='UNIT':
                yield Token('GROUPOPEN','(')
                yield Token('UNIT', value)
                yield Token('GROUPCLOSE', ')')
            else:
                yield Token(kind, value)
        yield Token('GROUPCLOSE','$')

    def _process_tokens(self, tokens, sign=1, parens_ineq=-1):
        # parens_ineq starts at -1 because tokenizer wraps everything within ^...$,
        # so that an equal parens has still one left (from ^);
        # hence either weassume equal==1 (which looks unintuitive)
        # or we start with a -1 offset
        _collection = []
        _D = D()
        conversion_factor = 1
        for token in tokens:
            if token.typ=='GROUPCLOSE':
                _collection.append( _D )
                parens_ineq -= 1
                return _collection, conversion_factor, parens_ineq # this return will be seen only by recursive call from GROUPOPEN
            if token.typ=='NEGSEP':
                if parens_ineq==0:
                    sign = -1
                else:
                    sign *= -1
            if token.typ=='GROUPOPEN':
                parens_ineq += 1
                lower_coll, _cf, parens_ineq = self._process_tokens(tokens, sign, parens_ineq)
                conversion_factor *= _cf
                lower_coll[-1] *= sign
                _lower = D() 
                for _d in lower_coll:
                    _lower += _d
                _collection.append( _lower )
            if token.typ=='UNIT':
                _DQ = self._process_unit(token.value)
                _D += _DQ.dimensions
                conversion_factor *= _DQ.numeric
            if token.typ=='SEP':
                if parens_ineq==0:
                    sign = (-1)**parens_ineq
                else:
                    pass
            if token.typ=='HOWOFTEN':
                _collection[-1] *= float(token.value)
        return DQ(conversion_factor, _collection[-1])

    def _process_unit(self, unit_value):
        if unit_value in self._unit_LUT.keys():
            return self._unit_LUT[unit_value]
        if len(unit_value)>=2:
            prefix = unit_value[0]
            unit_value = unit_value[1:]
            if unit_value not in self._unit_LUT.keys(): 
                raise KeyError(' '.join(['{} doesn\'t recognize'.format(type(self).__name__),
                                         'symbol {}'.format(unit_value),
                                         'and can thus not translate it into a DimQuant.']))
            if prefix not in self._prefix_LUT.keys():
                raise KeyError(' '.join(['{} doesn\'t recognize'.format(type(self).__name__),
                                         'prefix \'{}\''.format(prefix),
                                         'of unit \'{}\'.'.format(unit_value)]))
            return self._unit_LUT[unit_value]*self._prefix_LUT[prefix]
        else:
            raise ValueError(' '.join(['Cannot recognize a registered unit pattern',
                                        'in \'{}\'.'.format(unit_value),
                                        'to translate into a DimQuant']))

    def translate(self, string):
        """Translates (aka converts) a string representation of the dimension
        into a DimQuant instance.
        Example (this of course depends on what look-up-tables (LUTs) are registered):
        >>> q = self.translate('m/s2')
        >>> print(q)
        DimQuant(1, Dimensional({'L':1, 't':-2})
        >>> q = self.translate('cm.s-2')
        >>> print(q)
        DimQuant(0.01, Dimensional({'L':1, 't':-2})

        Args:
            string (str): String of units to be found in registered LUTs,
                separated by either a dot '.', or a divisor '/',
                as shown in the above examples.

        Return:
            DimQuant representing conversion factor and dimensions according to LUT.

        .. seealso:: 
            :py:meth: `dimensionalquantity.BasicTranslator.register_unit_LUT`
            :py:meth: `dimensionalquantity.BasicTranslator.register_prefix_LUT`
        """
        tokens = self._tokenize(string)
        return self._process_tokens(tokens)

    def reverse_unit_lookup(self, dimensions):
        """Translates (aka converts) a Dimensional instance into a string representation.
        Example (this of course depends on what look-up-tables (LUTs) are registered):
        >>> d = Dimensional({'L':1, 't':-2'})
        >>> s = self.reverse_unit_lookup(d)
        >>> print(s)
        'm.s-2'
        
        Args:
            dimensions (Dimensional, dict): the dimensions you want to convert into a string.

        Return:
            string representation of the Dimensional input argument.
            
        .. seealso:: 
            :py:meth: `dimensionalquantity.BasicTranslator.register_unit_LUT`
            :py:meth: `dimensionalquantity.BasicTranslator.register_prefix_LUT`
        """
        #TODO: clean up the code, yes the tests pass, but its ugly!
        if not isinstance(dimensions, (dict,D)):
            raise TypeError('Cannot lookup {}, which is of type {}'.format(
                            dimensions, type(dimensions).__name__))
        output = []
        for dimension,value in dimensions.items():
            if value==0: continue
            for unit,dq in self._unit_LUT.items():
                for _dim in dq.dimensions:
                    if len(_dim)>1: continue # the reverse look up works only with atomic base dimensions
                    _key = list(_dim)[0]
                    if _key==dimension:
                        output.append(unit)
                        if value!=1:
                            output[-1] += str(value)
        return '.'.join(output)

    def register_unit_LUT(self, unit_LUT, override=False):
        """The Translator converts string representations of a dimensional quantity
        into a DimQuant.
        The rules how to do this conversion is stored
        in two look-up-tables (LUTs):
        one LUT describing the units (like 'm' for meter),
        one LUT describing the unit prefixes (like 'k' for kilo).
        This method registers such a unit LUT to a Translator.
        >>> example_LUT = {'m': BaseDimQuant(1, Dimensional({'L': 1}))}
        >>> translator = BasicTranslator()
        >>> translator.register_unit_LUT(example_LUT)
        
        Args:
            unit_LUT (dict): a dictionary whose keys state the string to translate
                and whose values are a BaseDimQuant
                in which said string is supposed to be translated
            override (Bool=False): indicate whether a previously registered LUT
                is supposed to be overridden (True) or not (False, default).
                If False, the keys of the new (additional) LUT have to be
                unique with respect to previously registered keys.
                Otherwise a ValueError is raised.
                
        Return:
            None or ValueError if the present LUT is not overridden and
            a key of the new LUT is already present in the current LUT.
            
        .. seealso:: 
            :py:meth: `dimensionalquantity.BaseDimQuant`
            :py:meth: `dimensionalquantity.DimQuant`"""
        if override:
            self._unit_LUT = dict(unit_LUT) #copy to have different pointer to avoid spooky action from a distance
        else:
            for (symbol, dimension) in unit_LUT.items():
                if symbol in self._unit_LUT.keys():
                    raise ValueError(' '.join(['Cannot register rule to translate',
                                               'symbol \'{}\' into dimension \'{}\''.format(symbol, dimension),
                                               'because this symbol is already registered with',
                                               'dimension \'{}\'.'.format(symbol)]))
                else:
                    self._unit_LUT[symbol] = dimension

    def register_prefix_LUT(self, prefix_LUT, override=False):
        """The Translator converts string representations of a dimensional quantity
        into a DimQuant.
        The rules how to do this conversion is stored
        in two look-up-tables (LUTs):
        one LUT describing the units (like 'm' for meter),
        one LUT describing the unit prefixes (like 'k' for kilo, i.e. 1e3).
        This method registers such a unit prefix LUT to a Translator.
        >>> example_prefix_LUT = {'k': 1e3}
        >>> translator = BasicTranslator()
        >>> translator.register_prefix_LUT(example_prefix_LUT)
        
        Args:
            prefix_LUT (dict): a dictionary whose keys state the string to translate
                (currently only single letter prefixes are supported)
                and whose values are a float which states the relative value
                compared to a certain baseline
                (e.g. for regular SI units, 'k' would typically signify '1e3')
            override (Bool=False): indicate whether a previously registered LUT
                is supposed to be overridden (True) or not (False, default).
                If False, the keys of the new (additional) LUT (i.e. the prefixes)
                have to be unique with respect to previously registered keys.
                Otherwise a ValueError is raised.
                
        Return:
            None or ValueError if the present LUT is not overridden and
            a key of the new LUT is already present in the current LUT.
            NotImplementedError if the prefix_LUT contains keys whose string
            is more than 1 letter (0 letter (empty string)) is allowed
            and typically signifies unity 1e0.
            
        .. seealso:: 
            :py:meth: `dimensionalquantity.BaseDimQuant`
            :py:meth: `dimensionalquantity.DimQuant`"""
        for symbol in prefix_LUT.keys():
            if len(symbol)>1:
                raise NotImplementedError('Prefixes have to have only 1 (one) letter,'\
                                          + ' other string sizes are currently not supported.'\
                                          + ' The erroneous symbol ({}) contains {} letters.'.format(
                                              symbol, len(symbol)))
        if override:
            self._prefix_LUT = dict(prefix_LUT) #copy to have different pointer to avoid spooky action from a distance
        else:
            for (symbol, value) in prefix_LUT.items():
                if symbol in self._prefix_LUT.keys():
                    raise ValueError(' '.join(['Cannot register prefix \'{}\''.format(symbol),
                                               'because this symbol is already used.']))
                else:
                    self._prefix_LUT[symbol] = value

class Translator(BasicTranslator):
    """Class child of BasicTranslator.
    This means, instances of this class manage out of the box to convert back and forth,
    from a Dimensional to a string.
    
    Args:
        The init of this class takes no arguments.
        The main use of this class is through the two methods `translate()` and `reverse_unit_lookup()`.
        However, before you can use those two methods, you have to register `register_*_LUT()` a look-up-table.
        By default SI LUTs are registered (hence the 'manage out of the box' statement above.)
        
    .. seealso:
        An instance of `Translator` is used in `DimQuant`.
        This allows users to initialize a DimQuant using a string
        rather than a numeric and a Dimensional argument,
        as required by `BaseDimQuant`.
        In fact, the `Translator` instance --
        and with it the pre-registered SI LUTs --
        is the key difference between `BaseDimQuant` and `DimQuant`.
        :py:meth: `dimensionalquantity.DimQuant`
    """
    def __init__(self):
        super(Translator, self).__init__()
        self.register_unit_LUT(SI_unit_LUT)
        self.register_prefix_LUT(SI_prefix_LUT)


