#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

ods
===

This file contains interfaces to the OpenDocument Spreadsheet file format.

It is split into the following sections

 * shape
 * code
 * attributes
 * row_heights
 * col_widths
 * macros

"""

from src.lib.ODSReader import ODSReader

import src.lib.i18n as i18n

# Use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext

class Ods(object):
    """Interface between code_array and ods file

    The ods file is read from disk with the read method.
    The ods file is written to disk with the write method.

    Parameters
    ----------

    code_array: model.CodeArray object
    \tThe code_array object data structure
    ods_file: file
    \tFile like object in ods format

    """

    def __init__(self, code_array, ods_file):
        self.code_array = code_array
        self.ods_file = ods_file

    def _get_tables(self, ods):
        """Returns list of table nodes from ods object"""

        childnodes = ods.spreadsheet.childNodes
        qname_childnodes = [(s.qname[1], s) for s in childnodes]
        return [node for name, node in qname_childnodes if name == u"table"]

    def _get_rows(self, table):
        """Returns rows from table"""

        childnodes = table.childNodes
        qname_childnodes = [(s.qname[1], s) for s in childnodes]
        return [node for name, node in qname_childnodes
                if name == u'table-row']

    def _get_cells(self, row):
        """Returns rows from row"""

        childnodes = row.childNodes
        qname_childnodes = [(s.qname[1], s) for s in childnodes]
        return [node for name, node in qname_childnodes
                if name == u'table-cell']

    def _ods2code(self):
        """Updates code in code_array"""

        ods = ODSReader(self.ods_file, clonespannedcolumns=True)
        tables = ods.sheets
        for tab_id, table in enumerate(tables):
            for row_id in xrange(len(table)):
                for col_id in xrange(len(table[row_id])):
                    key = row_id, col_id, tab_id
                    text = unicode(table[row_id][col_id])
                    self.code_array[key] = text


    # Access via model.py data
    # ------------------------

    def from_code_array(self):
        """Replaces everything in pys_file from code_array"""

        raise NotImplementedError


    def to_code_array(self):
        """Replaces everything in code_array from pys_file"""

        self._ods2code()

