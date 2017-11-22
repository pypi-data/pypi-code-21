# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import csv
from string import ascii_uppercase, digits
from StringIO import StringIO
from random import choice
from collections import OrderedDict

class DataHolder:
    """
    For internal use only.

    A helper class for holding arbitrary data in a 2d list, then writing to a CSV in a StringIO buffer.
    """

    delimiter = ','

    def __init__(self):
        self._cols = OrderedDict()

    def add_column(self, name, column):
        """Add a column of data with the specified name to the 2d array.

        :param str name: The name of the column.
        :param list column: The column of data.

        If the name is already used in this instance, the old column will be overwritten.
        """
        if not isinstance(column, list):
            raise Exception("Error in DataHolder.add_column: all input values must be lists, not \"" + str(type(column)) + "\"")

        #if self._cols.has_key(name):
        #    print "Warning in DataHolder.add_column: variable \"" + name + "\" already exists"

        self._cols[name] = column
        self._pad_with_nans()

    def _largest_col_length(self):
        """Return the length of the largest column"""
        return max([0] + [len(self._cols[name]) for name in self._cols])

    def _pad_with_nans(self):
        """Fill all columns with None so they're the same length as the largest column"""
        for name in self._cols.keys():
            self._cols[name] += [None]*(self._largest_col_length() - len(self._cols[name]))

    def get_csv_file(self):
        """
        Translate the accumulated 2d array of data into a CSV file inside a StringIO buffer.

        :return: a StringIO buffer containing the CSV
        :rtype: StringIO
        """
        buf = StringIO()
        csv_writer = csv.writer(buf, delimiter=self.delimiter)
        names = self._cols.keys()
        csv_writer.writerow(names)

        for i in xrange(self._largest_col_length()):
            row = [self._cols[name][i] for name in names]
            csv_writer.writerow(row)
        buf.seek(0)
        # Our API requires a file name ending in csv to accept the file. Attaching this to
        # the file-like object allows the request module to handle this
        buf.name = ''.join(choice(ascii_uppercase + digits) for i in range(10)) + '.csv'
        return buf
