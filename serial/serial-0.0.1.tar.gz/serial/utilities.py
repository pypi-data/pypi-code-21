from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals
from future import standard_library
standard_library.install_aliases()

import re
from keyword import iskeyword


def property_name(string):
    # type: (str) -> str
    """
    Converts a "camelCased" attribute/property name to a pep8-compliant property name.

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
                    string
                )
            )
        )
    ).casefold()
    if iskeyword(pn):
        pn = pn + '_'
    return pn