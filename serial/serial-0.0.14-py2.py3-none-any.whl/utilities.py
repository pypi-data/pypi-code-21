from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, \
    unicode_literals
from future import standard_library
from future.utils import native_str

standard_library.install_aliases()
from builtins import *
#


def qualified_name(t):
    # type: (type) -> str
    if hasattr(t, '__qualname__'):
        return t.__qualname__
    tn = t.__name__
    if t.__module__ not in ('builtins', '__builtin__', '__main__'):
        tn = t.__module__ + '.' + tn
    return tn