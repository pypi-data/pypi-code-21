
import inspect
import pdb
import sys

from .sql import debug_sql


class TraceEvent(object):

    def __init__(self, *args, **kwargs):
        self.stack = inspect.stack()[2]
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return ", ".join(
            [self.stack[1],
             str(self.stack[2]),
             self.stack[3],
             str(self.args),
             str(self.kwargs)])


class Trace(object):
    sql = debug_sql
    debug = False
    pdb = pdb
    _called = ()

    def __call__(self, *args, **kwargs):
        self._called += (TraceEvent(*args, **kwargs), )

    def __iter__(self):
        for event in self._called:
            yield event
        self._called = ()

    def __str__(self):
        return "\n".join(str(item) for item in self._called)


def trace_debug(builtin="_trace"):
    sys.modules["__builtin__"].__dict__[builtin] = Trace()
