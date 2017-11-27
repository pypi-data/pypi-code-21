from pprint import pformat

class Loop(object):
    '''
    This class is written strangely so you can wrap a program and thus
    make nice Python documentation for an Interface.
    '''
    def __init__(self, spec):
        self._spec = spec
        update_wrapper(self, self._spec.setup)
        self.__name__ = setup._spec.__name__

    def __call__(self, *args, **kwargs):
        state = self._spec.setup(*args, **kwargs)
        while True:
            try:
                state = self._spec.loop(state)
            except Exit:
                break

def stream(x):
    '''
    :param x: Anything (returned from the underlying program)
    :rtype: Iterable of bytes
    :returns: Output as bytes
    '''
    if x is None:
        raise StopIteration
    elif isinstance(x, bytes):
        yield x
    elif isinstance(x, str):
        yield x.encode('utf-8')
    elif isinstance(x, dict) or not hasattr(x, '__iter__'):
        yield pformat(x).encode('utf-8')
    else:
        for y in x:
            yield from stream(y)
