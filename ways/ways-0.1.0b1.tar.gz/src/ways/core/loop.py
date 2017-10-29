#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''For-loop helper methods.'''


def last_iter(iterable):
    '''Wrap a loop to determine when the last value of a loop is found.

    Reference:
        https://stackoverflow.com/questions/1630320

    Args:
        iterable (iterable): The objects to move through

    '''
    # Get an iterator and pull the first value.

    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).

    for val in it:
        # Report the *previous* value (more to come).
        yield False, last
        last = val
    # Report the last value.
    yield True, last
# end last_iter


if __name__ == '__main__':
    print(__doc__)
