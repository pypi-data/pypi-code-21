version_number = (1,3,1)
"""Implements functions and classes for working with iterators.

Builds on and extends itertools.

New in (1,3,1):
- minor bug fix in strict_grouper

New in (1,3,0):
- added slide & islide

New in (1,2,0):
- added group_on_separator and separate_on

New in (1,1,0):
- added version number
- added module doc string
- improved strict_grouper: will now be ~10x faster if the last group of
  elements from the input iterable is incomplete
"""

from itertools import zip_longest, groupby

class GroupedIter(object):
    """Base class supporting grouped retrieval of several items from an iterable.

    The iterator protocol defined here for use by subclasses is a wrapper for
    the strict_grouper generator."""
    
    def __init__ (self, iterable, n=1, strict=True):
        self.n = n
        self.it = iterable
        self.strict=strict
        self.i = strict_grouper(self.it, self.n, strict=self.strict)
        
    def __iter__(self):
        return self

    def __next__(self):
        """Returns a tuple of the next n items from the iterable."""

        return next(self.i)

    def __length_hint__(self):
        try:
            return (len(self.it)//self.n)+1
        except TypeError:
            return NotImplemented

class SepIter(object):
    """Base class supporting record retrieval from an iterable.

    The iterator protocol defined here for use by subclasses is a wrapper for
    the group_on_separator generator."""
    
    def __init__ (self, iterable, sep):
        self.separator = sep
        self.it = iterable
        self.i = group_on_separator(self.it, self.separator)
        
    def __iter__(self):
        return self.i

    def __length_hint__(self):
        return NotImplemented
        
def strict_grouper(iterable, size, strict=True):
    """Generator that yields items from iterable in groups of size.

    Similar to the grouper recipe in itertools except that it does
    not try to pad the last group with a fillvalue.
    Instead, if strict is True (the default), raises a ValueError
    if the last group is incomplete (has a length smaller than size).
    If strict is False, it simply returns the truncated group."""
    
    fillvalue = object()
    args = [iter(iterable)]*size
    chunks = zip_longest(*args, fillvalue=fillvalue)
    try:
        prev = next(chunks)
    except StopIteration:
        return

    for chunk in chunks:
        yield prev
        prev = chunk

    if prev[-1] is fillvalue:
        n = len(prev)-1
        while prev[n] is fillvalue:
            n -= 1
        prev=prev[:n+1]
        
        if strict:
            raise ValueError("only %d value(s) left in iterator, expected %d" % (len(prev),size))

    yield prev


def group_on_separator(iterable, separator):
    """Returns start-tagged records - tuple(header, content) - from an iterable.

    Looks for the record separator at the start of each element.
    If the speparator is found, the rest of that element is interpreted
    as the record header. All elements between the header and the next separator
    element are considered the record content which is returned as an iterator.
    Missing content is reported as [], a missing header for the first record
    as None.
    BEWARE: in the generated tuple, the content iterator is only meaningful until
    the next iteration over the generator, and MUST NOT be used afterwards.
    Intended as a building block for higher level classes."""
    
    sep_len=len(separator)
    header_tail = None
    for is_header, item in groupby(iterable, lambda line: line[:sep_len] == separator):
        if is_header:
            header_tails = [h[sep_len:].strip() for h in item]
            for naked_header in header_tails[:-1]:
                yield (naked_header, iter([]))
            header_tail = header_tails[-1]
        else:
            yield (header_tail, item)


def separate_on(iterable, separator):
    """Variation on group_on_separator yielding record content as a list.

    Faster than group_on_separator for small groups and avoiding the caveat of
    possibly invalid content iterators."""
    
    sep_len = len(separator)
    accum = None
    header = None
    for item in iterable:
        item = item.strip()
        if item[:sep_len] == separator:
            if accum is not None:  # Don't bother if there are no accumulated lines.
                yield (header, accum)
            header = item[sep_len:]
            accum = []
        else:
            try:
                accum.append(item)
            except AttributeError:
                accum = [item]
                
    # Don't forget the last group of lines.
    yield (header, accum)


def islide (s, window, step=1):
    """Returns a sliding window iterator over sequence s.

    Typically used on strings to iterate over all substrings of length window."""
    
    return (s[i:i+window] for i in range(0, len(s)-window+1, step))

def slide (s, window, step=1):
    """Returns the result of sliding a window over sequence s as a list.

    Typically used on strings to obtain all substrings of length window."""
    
    return [s[i:i+window] for i in range(0, len(s)-window+1, step)]

def iblock(iterable,bsize,strict=False):
    """Return a list of n items from an iterable.

    Deprecated predecessor of strict_grouper."""
    
    it=iter(iterable)
    i=[it]*(bsize-1)
    while True:
        try:
            result=[next(it)]
        except StopIteration:
            # iterator exhausted, end the generator
            break
        for e in i:
            try:
                result.append(next(e))
            except StopIteration:
                # iterator exhausted after returning at least one item, but before returning n
                if strict:
                    raise ValueError("only %d value(s) left in iterator, expected %d" % (len(result),bsize))
                else:
                    pass
        yield result
