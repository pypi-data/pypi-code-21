# -*- coding: utf-8 -*-

"""Utilities for collections"""


def pretty_dict(dic):
    """Printable string representation of a dictionary

       Items are listed in alphabetical order of their keys,
       to ensure a deterministic representation
       (e.g. for unit tests)

       Examples:

       >>> pretty_dict({1: 2, 3: 4})
       '{1: 2, 3: 4}'

       >>> pretty_dict({'one': 'two', 'three': 'four'})
       '{one: two, three: four}'

       Recursive dictionaries are supported, too:

       >>> pretty_dict({1: 2, 3: {4: 5, 6: 7}})
       '{1: 2, 3: {4: 5, 6: 7}}'
    """
    items = []
    keys = sorted(dic.keys())
    for key in keys:
        val = dic[key]
        if isinstance(val, dict):
            val = pretty_dict(val)
        item_str = '{0}: {1}'.format(key, val)
        items.append(item_str)
    return '{' + ', '.join(items) + '}'
