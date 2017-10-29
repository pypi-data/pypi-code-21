#!/usr/bin/env python
"""Support for simple table drawing.

This is primarily intended for the `Cov` module.
"""
from __future__ import print_function



import sys
from cStringIO import StringIO


class Counters(object):
    """A class to manage named counters.

    This cleans up code that need to count a number of different things and
    also maintain totals of those same things. I wrote it when generating
    coverage statistics. This essentially involves counting "hits", "misses"
    and "lines" for each source file; plus totals for each value across all the
    source files.

    The basic usage is::

        c = Counters()
        c.inc("lines", "misses")  # Increment some counts
        c.inc("lines", "hits")    # Increment some counts
        print(v("lines")          # Will print '2')
        c.reset()                 # Reset counts, but not totals.
        c.inc("lines", "hits")    # Increment some counts again
        print(v("lines")          # Will print('1'))
        print tot("hits")         # Will print '3'

    As a convenience, attribute access is over-ridden so you can get counts and
    totals as attributes prefixed by 'v_' or 't_'. For example::

        c.t_lines == c.tot("lines")
    """
    def __init__(self):
        self._counters = {}
        self._totals = {}

    def inc(self, *names):
        """Increment a selection of counters.

        New counters are created the first time they are seen and immediately
        incremented.

        :Param names:
            You may provide any number of names (as strings).
        """
        for name in names:
            if name not in self._counters:
                self._counters[name] = 0
                self._totals[name] = 0
            self._counters[name] += 1
            self._totals[name] += 1

    def set(self, name, value):
        """Set a counter.

        New counters are created the first time they are seen.

        :Param name:
            The name of the counter.
        :Param value:
            The value of the counter.

        """
        if name not in self._counters:
            self._counters[name] = 0
            self._totals[name] = 0
        self._counters[name] = value
        self._totals[name] += value

    def names(self):
        """Return a list of the defined names."""
        return list(self._counters.keys())

    def reset(self):
        """Reset all value counters, but leave the totals unchanged."""
        for name in self._counters:
            self._counters[name] = 0

    def v(self, name):
        """Return the value of a counter.

        :Return:
            The counter's value. If the counter does not exist then zero is
            returned.
        """
        try:
            return self._counters[name]
        except KeyError:
            return 0

    def tot(self, name):
        """Return the value of a counter's total.

        :Return:
            The counter's total. If the counter does not exist then zero is
            returned.
        """
        try:
            return self._totals[name]
        except KeyError:
            return 0

    def __getattr__(self, name):
        """Read-only attribute access.

        Attributes that start 'v_' or 't_' return values or totals.
        """
        t, name = name[0:2], name[2:]
        if t == "t_":
            return self.tot(name)
        elif t == "v_":
            return self.v(name)
        raise AttributeError(name)


class Table(object):
    """Class to organise tabular data for simple reports."""
    def __init__(self):
        self.columns = []
        self.rows = []

    def addColumn(self, name, fmt, sFmt, uline, ljust):
        """Add a column to the table.

        :Param name:
            The name of the column.
        :Param fmt, sFmt:
            The format to use to represent values in this column. The ``fmt``
            is used if possible and if that fails then ``sFmt`` is used
            instead.
        :Param uline:
            If ``True`` then an underline will be drawn below the column's
            header.
        :Param ljust:
            If ``True`` then the column's content is left justified. Otherwise
            it is right justified.

        """
        self.columns.append((name, fmt, sFmt, uline, ljust))

    def addRow(self, *values):
        """Add a row of values to the table.

        :Param values:
            Each argument is a single value. You may provide fewer arguments
            than there are columns in the table.

        """
        self.rows.append(values)

    def addLine(self):
        """Add an underline to the table, below the current row."""
        self.rows.append(None)

    def draw(self, f=sys.stdout):
        """Draw the table as text.

        :Param f:
            The file to write the table to. This defaults to ``sys.stdout``.

        """
        fmts = [fmt for name, fmt, sFmt, uline, ljust in self.columns]
        sFmts = [sFmt for name, fmt, sFmt, uline, ljust in self.columns]
        ljusts = [ljust for name, fmt, sFmt, uline, ljust in self.columns]

        # Work out the required width for each column, by formattin each value
        # and taking the maximum width found in each column.
        widths = [3] * len(self.columns)
        for row in self.rows:
            if row is None:
                continue
            for i, v in enumerate(row):
                try:
                    s = fmts[i] % v
                except TypeError:
                    s = sFmts[i] % v
                widths[i] = max(widths[i], len(s))

        # Also, allow for the column names, which may increase the width for
        # some columns.
        for i, (name, fmt, sFmt, uline, ljust) in enumerate(self.columns):
            s = sFmt % name
            widths[i] = max(widths[i], len(s))

        # Convert the column widths into format strings (e.g. '%-5.4s') to
        # be used to format column names and underlinings.
        xxx = []
        for i, l in enumerate(widths):
            if ljusts[i]:
                xxx.append("%%-%d.%ds" % (l, l))
            else:
                xxx.append("%%%d.%ds" % (l, l))
        widths = xxx

        # Now draw the column headings, plus underlines.
        s = StringIO()
        for i, (name, fmt, sFmt, uline, ljust) in enumerate(self.columns):
            s.write(widths[i] % name)
            s.write(" ")
        f.write("%s\n" % s.getvalue().rstrip())
        s = StringIO()
        for i, (name, fmt, sFmt, uline, ljust) in enumerate(self.columns):
            if uline:
                s.write(widths[i] % ("=" * 80))
            else:
                s.write(widths[i] % " ")
            s.write(" ")
        f.write("%s\n" % s.getvalue().rstrip())

        # Finally draw the data rows, plus any explicit underlines.
        for row in self.rows:
            if row is None:
                s = StringIO()
                for i, (name, fmt, sFmt, uline, ljust) in enumerate(
                        self.columns):
                    if uline:
                        s.write(widths[i] % ("-" * 80))
                    else:
                        s.write(widths[i] % " ")
                    s.write(" ")
                f.write("%s\n" % s.getvalue().rstrip())
                continue

            s = StringIO()
            for i, v in enumerate(row):
                try:
                    text = fmts[i] % v
                except TypeError:
                    text = sFmts[i] % v
                s.write(widths[i] % text)
                s.write(" ")
            f.write("%s\n" % s.getvalue().rstrip())
