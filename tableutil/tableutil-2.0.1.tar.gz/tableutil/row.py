# -*- coding: utf-8 -*-

import logging_helper
from dominate import tags
from collections import OrderedDict
from fdutil.type_check import (is_dictionary,
                               is_list_or_dictionary)
from .cell import Cell

logging = logging_helper.setup_logging()

ROW_NUMBER_HEADING = u'#'


class Row(object):
    def __init__(self,
                 headings,
                 row,
                 row_number=None,
                 classes=None,
                 conversions=None):

        conversions = conversions if conversions else {}
        complex_conversions = [key for key in conversions if is_list_or_dictionary(key)]

        self.headings = headings
        self.classes = classes if classes is not None else []

        if not is_dictionary(row):
            # assume row is iterable.
            # assume it's the whole row in order
            # make a dictionary
            assert len(row) == len(self.headings)

            row = {key: cell if isinstance(cell, Cell) else Cell(value=cell,
                                                                 conversion=conversions.get(key))
                   for key, cell in zip(self.headings, row)}

        else:
            # Got here, so we assume it's a dictionary
            row = {key: value if isinstance(value, Cell) else Cell(value=value,
                                                                   conversion=conversions.get(key))
                   for key, value in iter(row.items())  # Prioritises Py3
                   if key in self.headings}  # Throw away non matching keys

        for complex_conversion in complex_conversions:
            if len([True for key in complex_conversion if key in row]) == len(complex_conversion):
                values = list(
                        conversions[complex_conversion][u'converter'](*[row[key].raw_value
                                                                        for key in complex_conversion]))

                for key in complex_conversion:
                    row[key].value = values.pop(0)

        # Create row dict
        self.row = OrderedDict()

        for heading in self.headings:
            self.row[heading] = (row[heading]
                                 if heading in row.keys()
                                 else Cell(u''))

        if ROW_NUMBER_HEADING in self.headings:
            self.row[ROW_NUMBER_HEADING] = Cell(u'' if row_number is None else row_number)

    def __getitem__(self,
                    item):
        return self.row[item]

    def __setitem__(self,
                    key,
                    value):
        # Todo: Figure out how to add conversion.
        #       Conversions probably need to be
        #       configured per column at table level.
        #       Currently if a value is changed,
        #       the conversion is lost. Could pass
        #       parent table in instead of keys
        self.row[key] = Cell(value)

    def __len__(self):
        return len(self.row)

    @property
    def row_number(self):
        return self.row[ROW_NUMBER_HEADING].raw_value

    @row_number.setter
    def row_number(self,
                   value):
        if ROW_NUMBER_HEADING in self.headings:  # TODO: this does not seem to be the best way to do this...
            self.row[ROW_NUMBER_HEADING].value = value

        else:
            logging.debug(u'Cannot set row number as row numbers are not enabled for this row!')

    @property
    def is_empty(self):
        empty = True

        for cell in self.row.values():
            if u'\n'.join(cell.text()).strip() != u'':
                empty = False
                break

        return empty

    @property
    def width(self):

        """ Get the Cell's text width (including padding) """

        return sum(self.cell_widths)

    @property
    def cell_widths(self):
        return {heading: self[heading].width for heading in self.headings}

    def html(self,
             **kwargs):
        _tr__body_row = tags.tr()

        for heading in self.headings:
            _tr__body_row.add(tags.td(self[heading].html(**kwargs)))

            if self.classes:
                _tr__body_row[u'class'] = u' '.join(self.classes)

        return _tr__body_row

    def jira(self):
        jira_row = u'|'

        for key in self.headings:
            try:
                jira_cell = u'{cell}|'.format(cell=self[key].jira())

            except IndexError:
                jira_cell = u' |'

            jira_row += jira_cell

        return jira_row

    def text(self,
             widths,
             justifications,
             divider):

        cells = [self.row[cell].text(width=widths[idx],
                                     justification=justifications[idx])
                 for idx, cell in enumerate(self.headings)]

        row_height = max(len(row) for row in self.row.values())
        row_lines = []

        for line_idx in range(0, row_height):
            row_line = []

            for col_idx, cell in enumerate(cells):
                row_line.append(u'{string:'
                                u'{fill}{justification}{width}}'.format(string=cell[line_idx]
                                                                        if len(cell) >= line_idx + 1
                                                                        else Cell(u'').text(width=widths[col_idx])[0],
                                                                        fill=u' ',
                                                                        width=widths[col_idx],
                                                                        justification=u'<'))

            row_lines.append(divider.join(row_line))

        return row_lines
