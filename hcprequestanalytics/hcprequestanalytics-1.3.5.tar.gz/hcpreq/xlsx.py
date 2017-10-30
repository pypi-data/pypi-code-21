# The MIT License (MIT)
#
# Copyright (c) 2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import csv
import xlsxwriter
from time import asctime, localtime, strftime


class Csv(object):
    """
    A class that handles the generation of CSV files.
    """

    def __init__(self, prefix):
        """
        :param prefix:      the prefix per generated filename
        """
        self.prefix = prefix

    def newsheet(self, name, fieldnames, **kwargs):
        """
        Create a new CSV file.

        :param name:        the files base name
        :param fieldnames:  a list of field names
        """
        fname = self.prefix + '-' + name + '.csv'
        try:
            self.hdl = open(fname, 'w')
        except Exception as e:
            sys.exit('open {} failed - {}'.format(fname ,e))

        self.writer = csv.DictWriter(self.hdl, fieldnames=list(fieldnames))
        self.writer.writeheader()

    def writerow(self, row):
        """
        Write a data row.

        :param row:     a data row, matching the header (dict)
        """
        self.writer.writerow(row)

    def closesheet(self, prefix, **kwargs):
        """
        Close the open file.

        :param **kwargs:    just a place-holder
        """
        self.hdl.close()

    def close(self, **kwargs):
        """
        Close the object.
        """

class Xlsx(Csv):
    """
    A class that handles the generation of an XLXS file.
    """

    def __init__(self, prefix):
        """
        :param prefix:  the prefix per generated filename
        """
        super().__init__(prefix)
        self.content = {}

        self.wb = xlsxwriter.Workbook('{}-analyzed.xlsx'.format(prefix))
        self.wb.set_properties({'title': 'HCP Request Analytics',
                                'author': 'hcprequestanalytics by Thorsten '
                                          'Simons (sw@snomis.de)',
                                'category': 'analytics',
                                'comments': 'Documentation at '
                                            'https://hcprequestanalytics.'
                                            'readthedocs.io',
                                })
        self.bold = self.wb.add_format({'bold': True})
        self.linkback = self.wb.add_format({'bold': True,
                                          'font_size': 14,
                                          'color': 'blue',
                                          'bg_color': 'yellow'})
        self.title0 = self.wb.add_format({'bold': False,
                                          'font_size': 14,
                                          'bg_color': 'yellow'})
        self.title = self.wb.add_format({'bold': True,
                                         'font_size': 14,
                                         'bg_color': 'yellow',
                                         'bottom': 5})
        self.num = self.wb.add_format({'num_format': '#,##0'})

        # create the Content sheet
        self.contentws = self.wb.add_worksheet(name='CONTENT')
        self.contentws.hide_gridlines(option=2)


    def newsheet(self, name, fieldnames, runtime=0.0, comment=''):
        """
        Create a new worksheet

        :param name:        the files base name
        :param fieldnames:  a list of field names
        :param runtime:     the time it took to run the query (str)
        :param comment:     a comment to be added
        """
        self.fieldnames = fieldnames
        self.content[name] = {'comment': comment,
                              'runtime': '{}'.format(runtime)}
        # record the length of each columns title
        uplift = 1.15  # uplift for bold header line
        self.colw = [len(w)*uplift for w in fieldnames]

        self.ws = self.wb.add_worksheet(name=name)

        # write the comment into the header, plus a link to the CONTENT sheet
        self.ws.set_row(0, 20, self.title0)
        self.ws.merge_range(0, 0, 0, 7, comment)
        self.ws.merge_range(0, 8, 0, 10, '', self.title0)
        self.ws.write_url(0, 8, 'internal:CONTENT!B2', self.linkback,
                          '<<< back to CONTENT <<<')
        # insert a spacer row
        self.ws.set_row(1, 8, self.title0)
        # write the field names
        self.ws.set_row(2, 20, self.title)
        self.ws.write_row(2, 0, fieldnames)
        # insert a spacer row
        self.ws.set_row(3, 8)
        self.row = 4

    def writerow(self, row):
        """
        Write a data row.

        :param row:     a data row, matching the header
        """
        _row = [row[x] for x in self.fieldnames]
        row = _row

        # this is done to properly set the width per column, taking in account
        # thousand-seperators
        clen = []
        for x in range(0, len(self.fieldnames)):
            try:
                _s = '{:,}'.format(int(row[x]))
                _ls = len(_s)
                clen.append(_ls)
            except ValueError:
                clen.append(len(str(row[x])))

        # save the max. length per row to be able to set column width later
        # when we close this sheet
        for x in range(0, len(self.fieldnames)):
            if clen[x] > self.colw[x]:
                self.colw[x] = clen[x]

        self.ws.write_row(self.row, 0, row, self.num)
        self.row += 1

    def closesheet(self, fp=''):
        """
        Close the open file.

        :param fp:  the cell where to split/freeze the pane
        """

        # set column width
        for x in range(0, len(self.fieldnames)):
            self.ws.set_column(x, x, self.colw[x])

        if fp:
            self.ws.freeze_panes(fp)
        return

    def close(self, start='', end=''):
        """
        Create a Content sheez and close the workbook.

        :param start:   the timestamp of the first rec in the DB
        :param end:     the timestamp of the last rec in the DB
        """
        row = 4
        col = 1
        title = self.wb.add_format({'bold': True,
                                    'align': 'center',
                                    'font_size': 14,
                                    'bg_color': 'yellow'})
        hright = self.wb.add_format({'align': 'right',
                                     'font_size': 12,
                                     'font_color': 'lightgrey',
                                     'bottom': True})
        hlink = self.wb.add_format({'align': 'left',
                                    'font_size': 12,
                                    'font_color': 'lightgrey',
                                     'bottom': True})
        hlight = self.wb.add_format({'align': 'right',
                                    'font_size': 12,
                                    'font_color': 'lightgrey',
                                     'bottom': True})
        right = self.wb.add_format({'bold': True,
                                   'align': 'right',
                                   'font_size': 12})
        link = self.wb.add_format({'bold': True,
                                   'align': 'left',
                                   'font_size': 12,
                                   'color': 'blue'})
        light = self.wb.add_format({'bold': False,
                                    'italic': True,
                                    'align': 'right',
                                    'font_size': 12,
                                    'font_color': 'lightgrey'})
        footer = self.wb.add_format({'bold': False,
                                     'align': 'center',
                                     'font_size': 10,
                                     'bg_color': 'yellow'})

        # headline
        self.contentws.merge_range(1, 1, 1, 5, 'Content', title)
        self.contentws.write(row-1, 1, 'query', hright)
        self.contentws.write(row-1, 2, '', hright)
        w_q = len('query')
        self.contentws.write(row-1, 3, 'description', hlink)
        self.contentws.write(row-1, 4, '', hlink)
        w_c = len('description')
        self.contentws.write(row-1, 5, 'runtime (h:m:s.ms)', hlight)
        w_r = len('runtime (h:m:s.ms)')

        for q in sorted(self.content.keys()):
            self.contentws.write(row, col, q, right)
            self.contentws.write_url(row, col+2,
                                     'internal:{}!A1'.format(q),
                                     link, self.content[q]['comment'])
            self.contentws.write(row, col+4, self.content[q]['runtime'], light)
            w_q = len(q) if len(q) > w_q else w_q
            w_c = len(self.content[q]['comment']) if len(
                self.content[q]['comment']) > w_c else w_c
            w_r = len(self.content[q]['runtime']) if len(
                self.content[q]['runtime']) > w_r else w_r
            row += 1

        # set column width for...
        # ...the query
        self.contentws.set_column(col, col, w_c*.6)
        # ...spacer
        self.contentws.set_column(col+1, col+1, 2)
        # ...the comment, linking to the respetive sheet
        self.contentws.set_column(col+2, col+2, w_c*.9)
        # ...spacer
        self.contentws.set_column(col+3, col+3, 2)
        # ...the queries' runtime in seconds
        self.contentws.set_column(col+4, col+4, w_r*.9)

        # footer
        self.contentws.merge_range(row+2, 1, row+2, 5,
                                   'created {} from log records starting at {}, ending at {}'
                                   .format(asctime(),
                                           strftime('%a %b %d %H:%M:%S %Y',
                                                    localtime(start)),
                                           strftime('%a %b %d %H:%M:%S %Y',
                                                    localtime(end))),
                                   footer)

        # Thu Oct  5 20:48:16 2017
        # '%a %b %d %H:%M:%S %Y'

        # make this the visible sheet on workbook open
        self.contentws.set_first_sheet()
        self.contentws.activate()

        self.wb.close()

