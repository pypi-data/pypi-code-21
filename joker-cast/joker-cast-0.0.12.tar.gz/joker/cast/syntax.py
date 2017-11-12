#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import functools
import inspect
import itertools


def noop(*args, **kwargs):
    pass


def adaptive_call(entry):
    """
    >>> import sys
    >>> entry = [print, ['a', 'b'], {'file': sys.stderr}]
    >>> adaptive_call(entry)

    :param entry: an iterable or a callable
    :return:
    """
    pargs = []
    kwargs = dict()
    if callable(entry):
        return entry()

    items = list(entry)
    if not items:
        return items
    if not callable(items[0]):
        raise TypeError('first item of entry must be a callable')

    for x in items[1:]:
        if isinstance(x, (list, tuple)):
            pargs.extend(x)
        elif isinstance(x, dict):
            kwargs.update(x)
        else:
            raise TypeError('params must be a tuple, list or dict')
    return items[0](*pargs, **kwargs)


def format_class_path(obj):
    if isinstance(obj, type):
        klass = obj
    else:
        klass = type(obj)
    m = getattr(klass, '__module__', None)
    q = getattr(klass, '__qualname__', None)
    n = getattr(klass, '__name__', None)
    name = q or n or ''
    if m:
        return '{}.{}'.format(m, name)
    return name


def format_function_path(func):
    if not inspect.ismethod(func):
        mod = getattr(func, '__module__', None)
        if mod is None:
            return func.__qualname__
        else:
            return '{}.{}'.format(mod, func.__qualname__)
    klass_path = format_class_path(func.__self__)
    return '{}.{}'.format(klass_path, func.__name__)


# compatibility
fmt_class_path = format_class_path
fmt_function_path = format_function_path


def instanciate(cls):
    return cls()


def instanciate_with_foolproof(cls):
    """
    The return class can be called again without error
    """
    if '__call__' not in cls.__dict__:
        cls.__call__ = lambda x: x
    return cls()


class AttrEchoer(object):
    """
    Resembles an enum type
    Reduces typos by using syntax based completion of dev tools
    
    Example:
        
        @instanciate_with_foolproof
        class Event(AttrEchoer):
            _prefix = 'event'
            bad_params = ''  # assign whatever
            unauthorized_access = ''  
            undefined_fault = ''
            ...
       
        # no error: 
        assert Event.unauthoried  == 'event.bad_params'
    """
    _prefix = '_root.'

    def __init__(self):
        pass

    def __getattribute__(self, key):
        kls = type(self)
        if key in kls.__dict__ and key != '_prefix':
            if not kls._prefix:
                return key
            return '{}{}'.format(kls._prefix, key)
        return object.__getattribute__(self, key)


def multilevel_get(d, *keys):
    for k in keys:
        v = d.get(k)
        if v is None:
            return None
        d = v
    return d


def _first_arg(*a):
    return a[0]


class ConstantCallable(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value


_always_return_true = ConstantCallable(True)
_always_return_false = ConstantCallable(False)


class Void(object):
    """
    Act as 0, False, '', [] 
    """
    __bool__ = _always_return_false
    __nonzero__ = _always_return_false
    __add__ = _first_arg
    __sub__ = _first_arg
    __radd__ = _first_arg
    __rsub__ = _first_arg
    __round__ = _first_arg
    __truediv__ = _first_arg
    __floordiv__ = _first_arg
    __rtruediv__ = _first_arg
    __rfloordiv__ = _first_arg
    __rmul__ = _first_arg
    __gt__ = _always_return_false
    __ge__ = _always_return_false
    __lt__ = _always_return_false
    __le__ = _always_return_false
    __len__ = ConstantCallable(0)

    def __init__(self, symbol='-'):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.symbol))

    def __eq__(self, other):
        if isinstance(other, Void):
            return True
        return False


class Universe(object):
    __contains__ = _always_return_true
    __iter__ = ConstantCallable(tuple())


# TODO: suport negative index (castfunc=-1 to get last item)
def castable(func):
    """
    >>> @castable
    ... def myfunc(*args):
    ...     for i in range(*args):
    ...         yield i
    ...
    >>> myfunc(12, castfunc=tuple)
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    >>> myfunc(0, 12, 2, castfunc=2)
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
   
    Purely syntax sugar,
    to make interactive use of some functions easier.
    Cast a generator function to list, set, or select n-th item, etc.

        myfunc(..., castfunc=list)   <=>  list(myfunc(...))
        myfunc(..., castfunc=1)      <=>  list(myfunc(...))[1]
    """
    @functools.wraps(func)
    def _decorated_func(*args, **kwargs):
        castfunc = None
        if 'castfunc' in kwargs:
            castfunc = kwargs['castfunc']
            del kwargs['castfunc']

            # shortcut to pick up nth record
            if isinstance(castfunc, int):
                n = castfunc
                castfunc = lambda r: next(itertools.islice(r, n, None))

        result = func(*args, **kwargs)
        if castfunc:
            result = castfunc(result)
        return result
    return _decorated_func
