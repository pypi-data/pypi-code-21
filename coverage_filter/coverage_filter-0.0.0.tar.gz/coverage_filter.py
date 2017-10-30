"""Manage filters for coverage.

Using coverage filters allows developers to specify which code a specific unit
test is supposed to test, and prevent false coverage.
"""

import functools
import os
import sys


class CoverageFilter(object):
    """A coverage filter.

    A coverage filter prevents certain code executions from being recorded
    as covered. This is done by providing a whitelist of code that should
    be covered.

    For example `mypackage/mymodule.py` will only record coverage of code
    in that file. `mypackage/mymodule.py:foo` will only record coverage of
    functions or methods named `foo` in that file.

    This can be used as a context manager or decorator. For example, these
    two examples are equivalent:

        @FilterCoverage('myfile')
        def myfunc():
            myfile.testedfunc()
        myfunc()

        with FilterCoverage('myfile'):
            myfile.testedfunc()

    Arguments:
        cover_targets: a list of symbols to cover
    """

    def __init__(self, *cover_targets):
        """Create a new filter for coverage.

        Arguments:
            cover_targets: a list of symbols to cover
        """
        self._old_trace = None
        self.is_tracing = False
        self.is_covering = [False]

        self.files = {}
        for target in cover_targets:
            parts = target.split(':', 1)
            if len(parts) == 2:
                filename, symbol = parts
            else:
                filename = parts[0]
                symbol = '*'

            for path in sys.path:
                full_path = os.path.join(path, filename)
                self.files.setdefault(full_path, set()).add(symbol)

    def __call__(self, fn):
        """Use CoverageFilter as decorator."""
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return inner

    def __enter__(self):
        """Use CoverageFilter as context manager."""
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Use CoverageFilter as context manager."""
        self.stop()

    def start(self):
        """Start coverage filter."""
        if not self.is_tracing:
            self._old_trace = sys.gettrace()
            if self._old_trace:
                sys.settrace(self._trace)

        self.is_covering = [False]
        self.is_tracing = True

    def stop(self):
        """Stop coverage filter."""
        if self.is_tracing:
            self.is_tracing = False
            sys.settrace(self._old_trace)

    def _trace(self, frame, event, arg_unused):
        if event == 'call':
            traced_symbols = self.files.get(frame.f_code.co_filename)
            if not traced_symbols:
                should_record = False
            elif '*' in traced_symbols:
                should_record = True
            else:
                should_record = frame.f_code.co_name in traced_symbols

            self.is_covering.append(should_record)
        elif event == 'return':
            self.is_covering.pop()
        elif event == 'exception':
            self.is_covering.pop()

        if self.is_covering[-1]:
            self._old_trace = self._old_trace(frame, event, arg_unused)
        return self._trace
