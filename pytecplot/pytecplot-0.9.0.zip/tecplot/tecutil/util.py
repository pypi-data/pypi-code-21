from builtins import super, int

import inspect
import logging

from collections import Iterable, namedtuple
from contextlib import contextmanager
from ctypes import cast, c_int, POINTER
from six import string_types

from .tecutil_connector import _tecutil
from ..constant import Color
from ..exception import TecplotAttributeError, TecplotTypeError

log = logging.getLogger(__name__)

maxint64 = 2**(64 - 1) - 1
minint64 = -maxint64 - 1
maxuint64 = 2**64 - 1

XYPosition = namedtuple('XYPosition', ['x', 'y'])
XYPosition.__new__.__defaults__ = (None, None)

XYZPosition = namedtuple('XYZPosition', ['x', 'y', 'z'])
XYZPosition.__new__.__defaults__ = (None, None)

RectTuple = namedtuple('RectTuple', ['x1', 'y1', 'x2', 'y2'])
RectTuple.__new__.__defaults__ = (None, None, None, None)


class Index(int):
    """Position identifier type.

    This type is used internally to represent a position in a list. It is
    used to indicate that a change between zero-based indexing and one-based
    indexing must occur at the TecUtil boundary.

    This type can be treated exactly like a Python native `int` and is only
    meaningful internally to the tecplot Python module.
    """


IndexRange = namedtuple('IndexRange', ['min', 'max', 'step'])
"""Index range specification along some axis.

This is similar to Python's :class:`slice` object except that ``max`` is included
in the evaluated indexes. Here are some things to note:

    * All indices start with 0 and go to some maximum index ``m``.
    * Negative values represent the indexes starting with the maximum at -1
      and continuing back to the beginning of the range.
    * A step of `None`, 0 and 1 are all equivalent and mean that no elements
      are skipped.
    * A negative step indicates a skip less than the maximum.
"""
IndexRange.__new__.__defaults__ = (None, None, None)


def flatten_args(*args):
    flatargs = []
    for a in args:
        if isinstance(a, Iterable) and not isinstance(a, string_types):
            flatargs += list(a)
        else:
            flatargs.append(a)
    return tuple(flatargs)


def array_to_enums(array_pointer, array_size, enum_type):
    indexes = cast(array_pointer, POINTER(c_int))
    return tuple(enum_type(indexes[i]) for i in range(array_size))


def inherited_property(cls):
    def _copy_property(prop):
        attr = getattr(cls, prop.__name__)
        return property(attr.fget, attr.fset, attr.fdel, prop.__doc__)
    return _copy_property


def lock_attributes(cls):
    """
    As a decorator of a class, this ensures that no new attributes are created
    after __init__() is called.
    """
    def _setattr(self, name, value):
        if __debug__:
            if not name.startswith('_') and name not in dir(self):
                stacknames = [f[0].f_code.co_name for f in inspect.stack()[:3]]
                if '__init__' not in stacknames:
                    msg = 'No attribute: {}.{}'
                    classname = self.__class__.__name__
                    raise TecplotAttributeError(msg.format(classname, name))
        return super(cls, self).__setattr__(name, value)
    cls.__setattr__ = _setattr
    return cls


_VarInfo = namedtuple('VarInfo', ('types', 'values', 'names'))


def check_arglist_argtypes(function_name, *args):
    for arg in args:
        vinfo = _VarInfo(*arg)
        for name, value in zip(vinfo.names, vinfo.values):
            if value is not None:
                if not isinstance(value, tuple(vinfo.types)):
                    errfmt = '{}: Type of  parameter {} must be one of: {}'
                    types = ', '.join(t.__name__ for t in vinfo.types)
                    errmsg = errfmt.format(function_name, name, types)
                    raise TecplotTypeError(errmsg)


def color_spec(color, plot=None):
    """
        color_spec(Color.Blue, plot)        --> Color.Blue
        color_spec(Color.MultiColor, plot)  --> plot.contour(0)
        color_spec(Color.MultiColor2, plot) --> plot.contour(1)
        color_spec(Color.Blue)              --> Color.Blue
        color_spec(plot.contour(0))         --> Color.MultiColor
        color_spec(plot.contour(1))         --> Color.MultiColor2
    """
    color_spec._indexes = {
        Color.MultiColor: Index(0),
        Color.MultiColor2: Index(1),
        Color.MultiColor3: Index(2),
        Color.MultiColor4: Index(3),
        Color.MultiColor5: Index(4),
        Color.MultiColor6: Index(5),
        Color.MultiColor7: Index(6),
        Color.MultiColor8: Index(7)}
    color_spec._multicolors = {v: k for k, v in color_spec._indexes.items()}
    try:
        if plot:
            return plot.contour(color_spec._indexes[Color(color)])
        else:
            return color_spec._multicolors[Index(color.index)]
    except (AttributeError, KeyError):
        return Color(color)


def filled_slice(slice_, maxlen):
    """Convert start, stop, step in slice to real integers.

    None and negative values are converted to actual default values depending
    on the maxlen given.
    """
    if slice_.start is None:
        start = 0
    elif slice_.start < 0:
        start = maxlen + slice_.start
    else:
        start = slice_.start
    start = min(max(start, 0), maxlen)

    if slice_.stop is None:
        stop = maxlen
    elif slice_.stop < 0:
        stop = maxlen + slice_.stop
    else:
        stop = slice_.stop
    stop = min(max(stop, 0), maxlen)

    if slice_.step is None:
        step = 1
    else:
        step = min(max(slice_.step, 1), maxlen)

    return slice(start, stop, step)


def array_to_str(arr, maxlen=10):
    try:
        itr = iter(arr)
        item = next(itr)
        ret = '[' + str(item)
        for i, item in enumerate(itr, start=2):
            if i > maxlen:
                ret += ' ...'
                break
            ret += ', {}'.format(item)
        return ret + ']'
    except StopIteration:
        return '[]'
    except TypeError:
        return str(arr)


class ListWrapper(object):
    """Converts a list to a wrapped paragraph of items.

    Unline textwrap.TextWrapper, items in the list are not broken over
    multiple lines even if they contain spaces.
    """
    def __init__(self, initial_indent='', subsequent_indent='    ',
                 initial_width=70, subsequent_width=70, delim=',',
                 prefix='', suffix=''):
        assert (len(prefix) + len(initial_indent)) < initial_width
        assert (len(suffix) + len(subsequent_indent)) < subsequent_width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.initial_width = initial_width
        self.subsequent_width = subsequent_width
        self.delim = delim
        self.prefix = prefix
        self.suffix = suffix

    def wrap(self, str_list):
        ret = []
        max_space = self.subsequent_width - len(self.subsequent_indent)

        line = "{}{}".format(self.prefix, self.initial_indent)

        itr = iter(str_list)
        try:
            item = next(itr)
            line += "'{}'".format(item)
        except StopIteration:
            pass  # no items in list

        space_left = self.initial_width - len(line)

        for item in itr:
            s = "{} '{}'".format(self.delim, str(item))
            if len(s) < space_left or max_space <= space_left:
                line += s
                space_left -= len(s)
            else:
                ret.append(line + self.delim)
                line = "{}'{}'".format(self.subsequent_indent, item)
                space_left = self.subsequent_width - len(line)

        if len(self.suffix) <= space_left:
            ret.append(line + self.suffix)
        else:
            ret.append(line)
            ret.append("{}{}".format(self.subsequent_indent, self.suffix))
        return ret

    def fill(self, str_list):
        return '\n'.join(self.wrap(str_list))


@contextmanager
def optional(cls, args):
    """Context for optional arguments that can be None or pass to a class
    constructor.

    In this example, variables is an optional parameter. If not `None`, then
    ``varset`` will be the result of ``IndexSet(*variables)``, if `None`, then
    ``varset`` will be `None`::

        def fn(variables=None):
            with optional(IndexSet, variables) as varset:
                _tecutil.Fn(varset)

    The ``cls`` parameter must be a class and must have the ``__enter__`` and
    ``__exit__`` methods implemented.
    """
    if args is None:
        yield None
    else:
        with cls(*flatten_args(args)) as obj:
            yield obj
