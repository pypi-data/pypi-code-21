from itertools import chain

from six import iteritems

DEFAULT = object()
"Sometimes `None` has its own meaning other than a default, so `DEFAULT` constant can be handy"


def get_method_class_name(method):
    self = method.__self__
    if self:
        return self.__class__.__name__


def get_call_repr(func_or_meth, args=(), kwargs=None):
    kwargs = kwargs or {}

    return '{}({})'.format(
        func_or_meth.__name__,
        ', '.join(chain((repr(arg) for arg in args),
                        ('{}={!r}'.format(k, v) for k, v in iteritems(kwargs))))
    )


def identity_func(x):
    return x
