from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, \
    unicode_literals

from unicodedata import normalize

from future import standard_library
from future.utils import native_str

standard_library.install_aliases()
from builtins import *
#

import re
from keyword import iskeyword


def qualified_name(t):
    # type: (type) -> str
    """
    >>> print(qualified_name(qualified_name))
    qualified_name

    >>> from serial import model
    >>> print(qualified_name(model.marshal))
    serial.model.marshal
    """
    if hasattr(t, '__qualname__'):
        tn = t.__qualname__
    else:
        tn = t.__name__
    if t.__module__ not in ('builtins', '__builtin__', '__main__'):
        tn = t.__module__ + '.' + tn
    return tn


def property_name(string):
    # type: (str) -> str
    """
    Converts a "camelCased" attribute/property name, or a name which conflicts with a python keyword, to a
    pep8-compliant property name.

    >>> print(property_name('theBirdsAndTheBees'))
    the_birds_and_the_bees

    >>> print(property_name('FYIThisIsAnAcronym'))
    fyi_this_is_an_acronym

    >>> print(property_name('in'))
    in_
    """
    pn = re.sub(
        r'([a-zA-Z])([0-9])',
        r'\1_\2',
        re.sub(
            r'([0-9])([a-zA-Z])',
            r'\1_\2',
            re.sub(
                r'([A-Z])([A-Z])([a-z])',
                r'\1_\2\3',
                re.sub(
                    r'([a-z])([A-Z])',
                    r'\1_\2',
                    re.sub(
                        r'[^\x20-\x7F]+',
                        '_',
                        normalize('NFKD', string)
                    )
                )
            )
        )
    ).casefold()
    if iskeyword(pn):
        pn += '_'
    return pn


def class_name(string):
    # type: (str) -> str
    """
    Converts a "camelCased", hyphen-ated, or underscore_separated class name, or a name which conflicts
    with a python keyword, to a pep8-compliant class name.

    >>> print(class_name('the birds and the bees'))
    TheBirdsAndTheBees

    >>> print(class_name('the-birds-and-the-bees'))
    TheBirdsAndTheBees

    >>> print(class_name('**the - birds - and - the - bees**'))
    TheBirdsAndTheBees

    >>> print(class_name('FYI is an acronym'))
    FYIIsAnAcronym

    >>> print(class_name('in-you-go'))
    InYouGo

    >>> print(class_name('False'))
    False_

    >>> print(class_name('True'))
    True_
    """
    string = normalize('NFKD', string)
    characters = []
    capitalize_next = True
    for s in string:
        if s in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
            if capitalize_next:
                s = s.upper()
            characters.append(s)
            capitalize_next = False
        else:
            capitalize_next = True
    cn = ''.join(characters)
    if iskeyword(cn):
        cn += '_'
    return cn


if __name__ == '__main__':
    import doctest
    doctest.testmod()