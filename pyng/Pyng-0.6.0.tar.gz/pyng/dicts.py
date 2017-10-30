#!/usr/bin/python
"""
    dicts.py                         Nat Goodspeed
    Copyright (C) 2016               Nat Goodspeed

NRG 2016-03-01
"""

import collections

# ****************************************************************************
#   Dictionary subsets
# ****************************************************************************
def subdict(d, keys):
    """
    Subset of a dict, specified by an iterable of desired keys. If a
    specified key isn't found, you get a KeyError exception. Use interdict()
    if you want softer failure.
    """
    return dict([(key, d[key]) for key in keys])

def interdict(d, keys):
    """
    Set intersection of a dict and an iterable of desired keys. Ignores any
    key in 'keys' not already present in the dict. Use subdict() if you'd
    prefer a KeyError.
    """
    # Guessing that the builtin set intersection operation is more efficient
    # than explicit Python membership tests.
    return subdict(d, set(d.keys()).intersection(keys))

# ****************************************************************************
#   dict search
# ****************************************************************************
def preddict(d, pred, _idxs=()):
    """
    Given a data structure of arbitrary depth -- scalar, iterable, associative
    -- any element of which might be another container -- search for elements
    for which 'pred' (a callable accepting an entry) returns True.

    This function is a generator which will eventually traverse the whole
    structure in depth-first order. It DOES NOT DEFEND against circularity.

    Every time pred(element) returns True, yield a tuple that can be used to
    navigate the data structure back to the found element. The tuple is
    constructed as follows:

    Each element of the tuple steps down to the next level of the data
    structure.

    If the current level of the data structure is a dict, the corresponding
    tuple element is the dict key.

    If the current level of the data structure is a list or tuple, the
    corresponding tuple element is the int index.

    If the entire data structure is a scalar for which pred(d) returns True,
    the tuple will be empty.

    Thus, a loop like this:

    element = d
    for t in yielded_tuple:
        element = element[t]

    should make pred(element) return True.
    """
    if isinstance(d, collections.Mapping):
        for k, v in d.iteritems():
            for tup in preddict(v, pred, _idxs + (k,)):
                yield tup
    elif isinstance(d, collections.Sequence) \
    and not isinstance(d, basestring):
        # This clause is for list, tuple etc. -- NOT strings.
        for i, v in enumerate(d):
            for tup in preddict(v, pred, _idxs + (i,)):
                yield tup
    else:
        # scalar, we hope! or string.
        try:
            # Test this value by calling the passed predicate.
            found = pred(d)
        except (TypeError, AttributeError):
            # Explicitly allow predicates that might not be suitable for all
            # datatypes. For instance, we want to be able to search for all
            # strings containing some substring using the 'in' operator even
            # if not all elements in the data structure are strings.
            pass
        else:
            # pred(d) didn't raise an exception -- did it return True?
            if found:
                yield _idxs

def all_eq_in_dict(d, value):
    """
    Given a data structure of arbitrary depth as described for preddict(),
    generate an index tuple for each element equal to the passed value.
    """
    return preddict(d, lambda v: v == value)

def first_eq_in_dict(d, value):
    """
    Given a data structure of arbitrary depth as described for preddict(),
    return the index tuple for the first element equal to the passed value, or
    None. (Be careful to distinguish None from the empty tuple (). The latter
    is returned when 'd' is a scalar equal to 'value'.)
    """
    try:
        # Obtain the generator-iterator returned by all_in_dict(), then call
        # the iterator's next() method to obtain the first value.
        return iter(all_eq_in_dict(d, value)).next()
    except StopIteration:
        # all_eq_in_dict() traversed the whole structure without yielding
        # anything.
        return None
