# -*- coding: utf-8 -*-
"""
Slightly adapted version of Werkzeug's :class:`werkzeug.local.LocalProxy`.

Original code licensed from the Werkzeug Team under the following terms:

    Copyright (c) 2014 by the Werkzeug Team, see AUTHORS for more details.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.

        * Redistributions in binary form must reproduce the above
          copyright notice, this list of conditions and the following
          disclaimer in the documentation and/or other materials provided
          with the distribution.

        * The names of the contributors may not be used to endorse or
          promote products derived from this software without specific
          prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

:copyright: Copyright (c) 2014 by the Werkzeug Team
:authors: See Werkzeug's AUTHORS file
:license: BSD
"""
# flake8: noqa
import copy

from clik.compat import implements_bool, PY2


@implements_bool
class Magic(object):  # pragma: no cover
    def __init__(self, name):
        object.__setattr__(self, '_Magic__context', None)
        object.__setattr__(self, '_Magic__name', name)

    def _get_current_object(self):
        """Return the current object."""
        return self.__context.get(self.__name)

    @property
    def __dict__(self):
        try:
            return self._get_current_object().__dict__
        except RuntimeError:
            raise AttributeError('__dict__')

    def __repr__(self):
        try:
            obj = self._get_current_object()
        except RuntimeError:
            return '<%s unbound>' % self.__class__.__name__
        return repr(obj)

    def __bool__(self):
        try:
            return bool(self._get_current_object())
        except RuntimeError:
            return False

    def __unicode__(self):
        try:
            return unicode(self._get_current_object())
        except RuntimeError:
            return repr(self)

    def __dir__(self):
        try:
            return dir(self._get_current_object())
        except RuntimeError:
            return []

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self._get_current_object())
        return getattr(self._get_current_object(), name)

    def __setitem__(self, key, value):
        self._get_current_object()[key] = value

    def __delitem__(self, key):
        del self._get_current_object()[key]

    if PY2:
        __getslice__ = lambda x, i, j: x._get_current_object()[i:j]

        def __setslice__(self, i, j, seq):
            self._get_current_object()[i:j] = seq

        def __delslice__(self, i, j):
            del self._get_current_object()[i:j]

    def __setattr__(x, n, v): return setattr(x._get_current_object(), n, v)
    def __delattr__(x, n): return delattr(x._get_current_object(), n)
    def __str__(x): return str(x._get_current_object())
    def __lt__(x, o): return x._get_current_object() < o
    def __le__(x, o): return x._get_current_object() <= o
    def __eq__(x, o): return x._get_current_object() == o
    def __ne__(x, o): return x._get_current_object() != o
    def __gt__(x, o): return x._get_current_object() > o
    def __ge__(x, o): return x._get_current_object() >= o
    def __cmp__(x, o): return cmp(x._get_current_object(), o)
    def __hash__(x): return hash(x._get_current_object())
    def __call__(x, *a, **kw): return x._get_current_object()(*a, **kw)
    def __len__(x): return len(x._get_current_object())
    def __getitem__(x, i): return x._get_current_object()[i]
    def __iter__(x): return iter(x._get_current_object())
    def __contains__(x, i): return i in x._get_current_object()
    def __add__(x, o): return x._get_current_object() + o
    def __sub__(x, o): return x._get_current_object() - o
    def __mul__(x, o): return x._get_current_object() * o
    def __floordiv__(x, o): return x._get_current_object() // o
    def __mod__(x, o): return x._get_current_object() % o
    def __divmod__(x, o): return x._get_current_object().__divmod__(o)
    def __pow__(x, o): return x._get_current_object() ** o
    def __lshift__(x, o): return x._get_current_object() << o
    def __rshift__(x, o): return x._get_current_object() >> o
    def __and__(x, o): return x._get_current_object() & o
    def __xor__(x, o): return x._get_current_object() ^ o
    def __or__(x, o): return x._get_current_object() | o
    def __div__(x, o): return x._get_current_object().__div__(o)
    def __truediv__(x, o): return x._get_current_object().__truediv__(o)
    def __neg__(x): return -(x._get_current_object())
    def __pos__(x): return +(x._get_current_object())
    def __abs__(x): return abs(x._get_current_object())
    def __invert__(x): return ~(x._get_current_object())
    def __complex__(x): return complex(x._get_current_object())
    def __int__(x): return int(x._get_current_object())
    def __long__(x): return long(x._get_current_object())
    def __float__(x): return float(x._get_current_object())
    def __oct__(x): return oct(x._get_current_object())
    def __hex__(x): return hex(x._get_current_object())
    def __index__(x): return x._get_current_object().__index__()
    def __coerce__(x, o): return x._get_current_object().__coerce__(x, o)
    def __enter__(x): return x._get_current_object().__enter__()
    def __exit__(x, *a, **kw):
        return x._get_current_object().__exit__(*a, **kw)
    def __radd__(x, o): return o + x._get_current_object()
    def __rsub__(x, o): return o - x._get_current_object()
    def __rmul__(x, o): return o * x._get_current_object()
    def __rdiv__(x, o): return o / x._get_current_object()
    if PY2:
        def __rtruediv__(x, o): return x._get_current_object().__rtruediv__(o)
    else:
        __rtruediv__ = __rdiv__
    def __rfloordiv__(x, o): return o // x._get_current_object()
    def __rmod__(x, o): return o % x._get_current_object()
    def __rdivmod__(x, o): return x._get_current_object().__rdivmod__(o)
    def __copy__(x): return copy.copy(x._get_current_object())
    def __deepcopy__(x, memo):
        return copy.deepcopy(x._get_current_object(), memo)
