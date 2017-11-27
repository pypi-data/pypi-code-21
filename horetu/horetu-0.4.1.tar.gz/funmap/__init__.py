from copy import copy
from functools import partial

def funmap(*keys, name=None):
    _repr = 'funmap(' + ', '.join(map(repr, keys)) + ', name=%s)'
    class Repr(type):
        def __repr__(Class):
            return _repr % repr(Class.__name__)
    class Map(object):
        'This is strange so that :py:func:`isinstance` can work.'
        def __repr__(self):
            return _repr % repr(self.__name__)

        @classmethod
        def from_dict(FM, x):
            return FM(lambda:x)()

        def __new__(Class, func):
            class FunMap(Class, metaclass=Repr):
                __doc__ = func.__doc__
                def __new__(C, *args, **kwargs):
                    return object.__new__(C)
                
                def __repr__(self):
                    out = self.__class__.__name__ + '('
                    out += ', '.join(map(repr, self._args))
                    if self._kwargs:
                        out += ', '.join('%s=%s' % (k, repr(v)) \
                                         for k, v in self._kwargs.items())
                    out += ')'
                    return out

                def __str__(self):
                    tpl = '    %s: %s'
                    title = [repr(self)]
                    data = [(tpl % (k, self.__dict__.get(k,''))) \
                            for k in keys]
                    return '\n'.join(title + data)

                @classmethod
                def from_dict(FM, x):
                    fm = FM.__new__(FM)
                    fm._args = fm._kwargs = tuple()
                    fm._update(x)
                    return fm

                def __init__(self, *args, **kwargs):
                    self._args = tuple(args)
                    self._kwargs = dict(kwargs)
                    out = func(*self._args, **self._kwargs)

                    if not hasattr(out, 'items'):
                        raise ValueError('Function should return a dict.')
                    elif not hasattr(out, '__iter__') or set(out) != set(keys):
                        strk = '", "'.join(keys)
                        raise ValueError('Function should return a dict with "%s".' % strk)
                    self._update(out)

                def _update(self, x):
                    self._evaluated = True
                    for k, v in x.items():
                        if hasattr(self, k):
                            raise ValueError('Key "%s" is not allowed.' % k)
                        self.__dict__[k] = v
                
            FunMap.__name__ = func.__name__
            return FunMap
    if name:
        Map.__name__ = name
    return Map
