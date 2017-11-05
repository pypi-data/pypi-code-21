# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2016 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""I/O with typed tables of uncertain measurements.

The table format is line-oriented text. Hashes denote comments. Initial lines
of the form "colname = value" set a column name that gets the same value for
every item in the table. The header line is prefixed with an @ sign.
Subsequent lines are data rows.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = str ('read').split ()

import six
import numpy as np
from . import Holder, PKError, reraise_context, pktable


# temporary(?) hack: parsing machinery here for now

def _parse_bool (text):
    if not len (text):
        return False
    if text == 'y':
        return True
    raise ValueError ('illegal bool textualization: expect empty or "y"; got "%s"' % text)


def _parse_string (text):
    # Hackity hack so we can use mathlib: numpy object-type array
    if not len (text):
        return np.array (None, dtype=np.object)
    return np.array (six.text_type (text), dtype=np.object)


def _maybe_parse_exact (text, tkind):
    if not len (text):
        return None
    return Textual.from_exact (text, _ttkinds[tkind])


def _maybe_parse_uncert (text, tkind):
    if not len (text):
        return None
    return Textual.parse (text, _ttkinds[tkind])

parsers = {
    # maps 'type tag string' to 'parsing function'.
    'x': None,
    'b': _parse_bool,
    'i': int,
    's': _parse_string,
    'f': lambda t: _maybe_parse_exact (t, ''),
    'Lf': lambda t: _maybe_parse_exact (t, 'L'),
    'Pf': lambda t: _maybe_parse_exact (t, 'P'),
    'u': lambda t: _maybe_parse_uncert (t, ''),
    'Lu': lambda t: _maybe_parse_uncert (t, 'L'),
    'Pu': lambda t: _maybe_parse_uncert (t, 'P'),
}

col_factories = {
    'x': None,
    'b': pktable.ScalarColumn,
    'i': pktable.ScalarColumn,
    's': pktable.StringColumn.new_from_values,
    'f': pktable.ScalarColumn,
    'Lf': pktable.ScalarColumn,
    'Pf': pktable.ScalarColumn,
    'u': pktable.MeasurementColumn,
    'Lu': pktable.MeasurementColumn,
    'Pu': pktable.MeasurementColumn,
}


def _get_parse_info (lname):
    a = lname.rsplit (':', 1)
    if len (a) == 1:
        a.append ('s')
    return a[0], parsers[a[1]], col_factories[a[1]]


def _trimmedlines (path, **kwargs):
    from .io import Path

    for line in Path (path).read_lines (**kwargs):
        line = line[:-1] # trailing newline
        line = line.split ('#', 1)[0]
        if not len (line):
            continue
        if line.isspace ():
            continue
        yield line


def read (path, tabwidth=8, **kwargs):
    """Read a typed tabular text file into a PKTable.

    path
      The path of the file to read.
    tabwidth=8
      The tab width to assume. Please don't monkey with it.
    mode='rt'
      The file open mode (passed to io.open()).
    noexistok=False
      If True and the file is missing, treat it as empty.
    ``**kwargs``
      Passed to io.open ().

    Returns a :class:`pwkit.pktable.PKTable`.

    """
    from .pktable import PKTable
    from .mathlib import append, broadcast_to, empty_like, reshape
    datamode = False
    fixedcols = {}
    columns = {}
    rownum = 0
    alloced = -1

    for text in _trimmedlines (path, **kwargs):
        text = text.expandtabs (tabwidth)

        if datamode:
            # table row
            if rownum == 0:
                for name, cslice, parser, cfactory in info:
                    try:
                        columns[name] = reshape (parser (text[cslice].strip ()), (1,))
                    except:
                        reraise_context ('while parsing "%s"', text[cslice].strip ())
                alloced = 1
            else:
                if rownum >= alloced:
                    for name, cslice, parser, cfactory in info:
                        c = columns[name]
                        columns[name] = append (c, empty_like (c, shape=(64,)))
                    alloced = c.shape[0]

                for name, cslice, parser, cfactory in info:
                    try:
                        columns[name][rownum:rownum+1] = parser (text[cslice].strip ())
                    except:
                        reraise_context ('while parsing "%s"', text[cslice].strip ())

            rownum += 1
        elif text[0] != '@':
            # fixed column
            padnamekind, padval = text.split ('=', 1)
            name, parser, cfactory = _get_parse_info (padnamekind.strip ())
            fixedcols[name] = cfactory, parser (padval.strip ())
        else:
            # column specification
            n = len (text)
            assert n > 1
            start = 0
            info = []

            while start < n:
                end = start + 1
                while end < n and (not text[end].isspace ()):
                    end += 1

                if start == 0:
                    namekind = text[start+1:end] # eat leading @
                else:
                    namekind = text[start:end]

                while end < n and text[end].isspace ():
                    end += 1

                name, parser, cfactory = _get_parse_info (namekind)
                if parser is None: # allow columns to be ignored
                    skippedlast = True
                else:
                    skippedlast = False
                    info.append ((name, slice (start, end), parser, cfactory))
                start = end

            datamode = True

            if not skippedlast:
                # make our last column go as long as the line goes
                # (e.g. for "comments" columns)
                # but if the real last column is ":x"-type, then info[-1]
                # doesn't run up to the end of the line, so do nothing in that case.
                lname, lslice, lparser, lcfactory = info[-1]
                info[-1] = lname, slice (lslice.start, None), lparser, lcfactory

    # we've now read in all of the data

    table = PKTable ()

    for name, cslice, parser, cfactory in info:
        table[name] = cfactory (columns[name][:rownum])

    for name, (cfactory, value) in six.viewitems (fixedcols):
        table[name] = cfactory (broadcast_to (value, (rownum,)))

    return table
