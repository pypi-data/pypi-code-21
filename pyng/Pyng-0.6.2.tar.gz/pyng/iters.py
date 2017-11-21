#!/usr/bin/python
"""
    iters.py                         Nat Goodspeed
    Copyright (C) 2010               Nat Goodspeed

NRG 12/01/10
"""

import itertools
# Backwards compatibility: before we had a separate dicts module, we used to
# define subdict() and interdict() here in this module.
from dicts import subdict, interdict

def iterable(obj):
    """Is obj a scalar or a sequence? This is very frequently asked by utility
    functions that might accept either: process either the single object I
    pass, or each item in this sequence.

    But the question has hidden subtleties. isinstance(obj, list) is obviously
    wrong -- what about tuples? Even isinstance(obj, (list, tuple)) isn't
    quite right. What about generators? What about 2.4 generator expressions?
    What about user-defined sequence classes?

    In exasperation we might simply write iter(obj). If it throws, obj is a
    scalar; otherwise it's a sequence. But that's not quite what we (usually)
    want either: you can iterate over the characters in a string...

    This function regards strings as scalars, but supports all other iterables
    as described above. Note that we test against basestring so that we notice
    either an ASCII string or a Unicode string.
    """
    if isinstance(obj, basestring):
        return False
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True

def sequence(obj):
    """Convenience function to support utility functions. If obj is already an
    iterable, return it unchanged; if it's a scalar, return a tuple containing
    that one entry. (We use iterable(), so we treat strings of both kinds as
    scalars.) This permits you to write:

    for item in sequence(obj): ...

    and accept scalars, sequences, generators, whatever.
    """
    if iterable(obj):
        return obj
    else:
        return (obj,)

def empty(iterable):
    """If you want to know whether a sequence is empty, it's common to ask
    whether len(sequence) == 0. But what if the sequence is a generator, and
    it may run indefinitely -- or infinitely?

    This function cheaply tests whether the passed iterable returns no items,
    or at least one item.
    """
    try:
        iter(iterable).next()
        return False
    except StopIteration:
        return True

try:
    any = any
except NameError:
    # Python 2.4 or earlier
    def any(iterable):
        """True if any one bool(item) in the iterable is True. Equivalent to
        reduce(or, iterable) -- except that you can't write reduce(or, ...).
        """
        return not empty(itertools.ifilter(None, iterable))

try:
    all = all
except NameError:
    # Python 2.4 or earlier
    def all(iterable):
        """True if every bool(item) in the iterable is True. Equivalent to
        reduce(and, iterable) -- except that you can't write reduce(and, ...).
        """
        return empty(itertools.ifilterfalse(None, iterable))

def interleave(*iterables):
    """Return the first item from the first iterable, then the first item from
    the second iterable, then the first item from the third iterable, and so
    on for all the iterables. Then return the second item from the first
    iterable, etc. Like itertools.imap(None) except that it returns individual
    items in sequence instead of returning tuples.
    """
    # itertools.imap(None) yields a sequence of tuples. Flatten that sequence
    # of tuples by passing each tuple as a distinct argument to chain().
    # We don't even need to handle each item on its way by.
    return itertools.chain(*itertools.imap(None, *iterables))
