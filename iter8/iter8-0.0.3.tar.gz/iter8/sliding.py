from itertools import islice


def sliding(seq, n):
    '''
    Returns a sliding window (of width n) over data from the iterable
        s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...

    From https://docs.python.org/release/2.3.5/lib/itertools-example.html

    >>> list(sliding([1, 2, 3, 4], 2))
    [(1, 2), (2, 3), (3, 4)]
    '''
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def sliding_list(seq, n):
    '''
    Simpler, and works the same as long as the input is a list.

    Returns a list of lists, instead of an iterable of tuples
    '''
    return [seq[i:i + n] for i in xrange(len(seq) + 1 - n)]
