# -*- coding: utf-8 -*-
"""
    This module will create a seaborn table which acts a dictionary and a list.
    It makes handling some raw data very quick and convenient.

    It can do this by consuming:
        list of list
        list of dictionary
        dictionary of dictionary
        dictionary of lists

    It can consume these from raw python data structures, csv, text, or mark down files.
    It can output to csv, text, or html.
"""
import os
import sys
from collections import OrderedDict
from functools import reduce

if sys.version_info[0] == 2:
    xrange = range


    class by_key(object):
        def __init__(self, keys):
            self.keys = isinstance(keys, list) and keys or [keys]

        def __call__(self, obj1, obj2):
            for key in self.keys:
                if obj1[key] > obj2[key]:
                    return 1
                if obj1[key] < obj2[key]:
                    return -1
            return 0
else:
    basestring = str
    unicode = str


    class by_key(object):
        def __init__(self, keys, comp=None):
            self.keys = isinstance(keys, list) and keys or [keys]
            self.comp = comp or (lambda x: x)

        def __call__(self, obj):
            return [self.comp(obj[k]) for k in self.keys]


class SeabornTable(object):
    MAX_SIZE = 1000
    DELIMINATOR = ' | '

    def __init__(self, table=None, columns=None, row_columns=None, tab='', key_on=None):
        """
        :param table: obj can be list of list or list of dict or any combination
        :param columns: list of str of the columns in the table
        :param row_columns: columns of the list if different then visible columns on output
        :param tab: str to include before every row
        :param key_on: tuple of str if assigned then the table can be accessed as a dict
        """
        if columns:
            columns = list(columns)
        if row_columns:
            row_columns = list(row_columns)

        # normalize table to a list of SeabornRows
        if not table:
            self.row_columns = columns or row_columns or []
            self.table = []
        elif isinstance(table, SeabornTable):
            self.row_columns = table[0]._columns + []
            self.table = [SeabornRow(self.row_columns, list(row))
                          for row in table]
        elif isinstance(table, list) and isinstance(table[0], SeabornRow):
            self.row_columns = table[0]._columns
            self.table = table
        elif isinstance(table, dict):
            temp = SeabornTable.dict_to_obj(table, columns, row_columns, key_on=key_on)
            self.row_columns, self.table = temp.row_columns, temp.table
        elif isinstance(table, list):
            temp = SeabornTable.list_to_obj(table, columns, row_columns, key_on=key_on)
            self.row_columns, self.table = temp.row_columns, temp.table
        elif getattr(table, 'headings', None) is not None and \
                        getattr(table, 'row_columns', None) is not None:
            self.row_columns = row_columns or columns or table.headings
            self.table = [SeabornRow(self.row_columns,
                                     [row[c] for c in self.row_columns])
                          for row in table]
        else:
            raise Exception("Unknown type of table")

        self._parameters = {}
        self.tab = tab
        self.key_on = key_on
        self._columns = columns or self.row_columns

    def __add__(self, other):
        new_row_columns = self.row_columns + [c for c in other.row_columns
                                              if c not in self.row_columns]
        new_table = []
        for row in self.table + other.table:
            new_row = SeabornRow(
                new_row_columns, [row.get(c, None) for c in new_row_columns])
            new_table.append(new_row)

        return SeabornTable(table=new_table,
                            columns=self.columns,
                            row_columns=new_row_columns)

    @staticmethod
    def get_normalized_columns(list_):  # todo this could probably be optimized
        """
        :param list_: list of dict
        :return: list of string of every key in all the dictionaries
        """
        ret = []
        for row in list_:
            if len(row.keys()) > len(ret):
                ret = SeabornTable.ordered_keys(row)

        for row in list_:
            for key in row.keys():
                if not key in ret:
                    ret.append(key)
                    if not isinstance(row, OrderedDict):
                        ret.sort()
        return ret

    @staticmethod
    def ordered_keys(dict_):
        """
        :param dict_: dict of OrderedDict to be processed
        :return: list of str of keys in the original order or in alphabetical order
        """
        return isinstance(dict_, OrderedDict) and dict_.keys() or \
               dict_ and sorted(dict_.keys()) or []

    def map(self, func):
        """
        This will replace every cell in the function with func(cell)
        :param func: func to call
        :return: None
        """
        for row in self.table:
            for i, cell in enumerate(row):
                row[i] = func(cell)

    @classmethod
    def list_to_obj(cls, list_, columns, row_columns, tab='', key_on=None):
        """
        :param list_: list of list or list of dictionary to use as the data source
        :param columns: list of strings to label the columns on print out
        :param row_columns: list of columns in the actually data a super set of columns
        :param tab: str of the tab to use before the row on printout
        :param key_on: str of the column to key each row on
        :return: SeabornTable
        """
        if getattr(list_[0], 'keys', None) and not isinstance(list_[0], dict):
            row_columns = row_columns or columns or list_[0].keys()
            table = [SeabornRow(
                row_columns,
                [getattr(row, col, None) for col in row_columns])
                for row in list_]
        elif isinstance(list_[0], dict):
            row_columns = row_columns or columns or cls.key_on_columns(key_on, cls.get_normalized_columns(list_))
            table = [SeabornRow(row_columns,
                                [row.get(c, None) for c in row_columns])
                     for row in list_]

        elif isinstance(list_[0], (list, tuple)) and len(list_) == 1:
            row_columns = row_columns or columns or cls.key_on_columns(key_on,
                                                                       ['Column %s' % i for i in range(len(list_[0]))])
            table = [SeabornRow(row_columns, row) for row in list_]

        elif isinstance(list_[0], (list, tuple)):
            row_columns = row_columns or columns or list_.pop(0)
            table = [SeabornRow(row_columns, row) for row in list_]

        else:
            row_columns = ['LIST'] or columns
            table = [SeabornRow(row_columns, [row]) for row in list_]

        return cls(table, columns, row_columns, tab, key_on)

    @classmethod
    def dict_to_obj(cls, dict_, columns, row_columns, tab='', key_on=None):
        """
        :param dict_: dict of dict or dict of list
        :param columns: list of strings to label the columns on print out
        :param row_columns: list of columns in the actually data a super set of columns
        :param tab: str of the tab to use before the row on printout
        :param key_on: str of the column to key each row on
        :return: SeabornTable
        """
        if isinstance(list(dict_.values())[0], dict):
            row_columns = row_columns or columns or cls.key_on_columns(key_on, cls.ordered_keys(dict_.values()[0]))
            if key_on is None:
                table = [SeabornRow(row_columns, [row[c] for c in row_columns])
                         for row in dict_.values()]
            else:
                table = [SeabornRow(row_columns, [row.get(c, c == key_on and key or None) for c in row_columns])
                         for key, row in dict_.items()]

        elif isinstance(list(dict_.values())[0], list):  # todo this may need more work
            row_columns = row_columns or columns or cls.key_on_columns(key_on, sorted(dict_.keys()))
            if key_on is None:
                table = [SeabornRow(row_columns, [dict_[c][i] for c in columns])
                         for i in range(len(dict_[columns[0]]))]
            else:
                table = [SeabornRow(row_columns, [dict_[c][i] for c in columns])
                         for i in range(len(dict_[columns[0]]))]

        else:
            row_columns = row_columns or columns or ['KEY', 'VALUE']
            table = [SeabornRow(row_columns, [k, v]) for k, v in
                     dict_.items()]

        return cls(table, columns, row_columns, tab, key_on)

    @classmethod
    def key_on_columns(self, key_on, columns):
        """
        :param key_on: str of column
        :param columns: list of str of columns
        :return: list of str with the key_on in the front of the list
        """
        if key_on is not None:
            if key_on in columns:
                columns.remove(key_on)
            columns = [key_on] + columns
        return columns

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, column_names):
        assert isinstance(column_names, (list, tuple))
        for col in column_names:
            if col not in self.row_columns:
                self.row_columns.append(col)
                for row in self:
                    row.append(None)
        self._columns = column_names

    def naming_convention_columns(self, convention='underscore', remove_empty=True):
        """
        This will change the column names to a particular naming convention.
            underscore: lower case all letters and replaces spaces with _
            title: uppercase first letter and replaces _ with spaces
        :param convention: str enum of "lowercase_underscore"
        :param remove_empty: bool if true will remove column header of value ''
        :return: None
        """
        converter = getattr(self, '_%s_column' % convention, None)
        assert converter is not None, 'Convention "%s" is not a valid convention' % convention
        for i, old_name in enumerate(self.row_columns):
            new_name = converter(old_name)
            self.row_columns[i] = new_name
            if old_name in self._columns:
                self._columns[self._columns.index(old_name)] = new_name
        if remove_empty:
            self.remove_column('')

    @staticmethod
    def _title_column(name):
        return " ".join([word.title() for word in str(name).split('_')])

    @staticmethod
    def _underscore_column(name):
        return name.lower().replace(' ', '_')

    def remove_column(self, name):
        """
        :param name: str of the column to remove from every row in the table
        :return: None
        """
        if name in self.row_columns:
            index = self.row_columns.index(name)
            for row in self.table:
                row.pop(index)
            self.row_columns.pop(index)

        if '' in self._columns:
            self._columns.remove(name)

    def filter_by(self, **kwargs):
        """
        :param kwargs: dict of column == value
        :return: SeabornTable
        """
        ret = SeabornTable(
            columns=self.columns, row_columns=self.row_columns, tab=self.tab,
            key_on=self.key_on)
        for row in self:
            if not False in [row[k] == v for k, v in kwargs.items()]:
                ret.append(row)
        return ret

    def filter(self, column, condition='!=', value=None):
        """
        :param column: str or index of the column
        :param condition: str of the python operator
        :param value: obj of the value to test for
        :return: SeabornTable
        """
        ret = SeabornTable(
            columns=self.columns, row_columns=self.row_columns, tab=self.tab,
            key_on=self.key_on)
        for row in self:
            if getattr(row[column], condition, None):
                if eval('row[column].%s(%s)' % (condition, value)):
                    ret.append(row)
            if eval('row[column] %s value' % condition):
                ret.append(row)
        return ret

    def append(self, row=None):
        """
            This will add a row to the table
        :param row: obj, list, or dictionary
        :return: SeabornRow that was added to the table
        """
        self.table.append(self.normalize_row(row))
        return self.table[-1]

    def remove(self, row):
        assert row in self.table, 'Row %s was not in this table' % row
        self.table.remove(row)

    @classmethod
    def pertibate_to_obj(cls, columns, given=None, when=None, then=None, pertibate_columns=None,
                         filter_func=None, max_size=None):
        """
            This will create and add rows to the table by pertibating the
            parameters for the provided columns
        :param columns: list of str of columns in the table
        :param pertibate_columns: list of str of columns to pertibate
        :param filter_func: func to return False to filter out row
        :param max_size: int of the max size of the table
        :return: SeabornTable
        """
        table = cls(columns=columns)
        table._setup_steps(given, when, then)
        table.pertibate(pertibate_columns, filter_func, max_size)
        return table

    def pertibate(self, pertibate_columns=None, filter_func=None, max_size=None):
        """
        :param pertibate_columns: list of str fo columns to pertibate see DOE
        :param filter_func: func that takes a SeabornRow and return True if this row should be exist
        :param max_size: int of the max size of the table
        :return:  None
        """
        pertibate_columns = pertibate_columns or self.columns
        for c in pertibate_columns:
            assert c in self.columns, 'Column %s was not part of this self' % c

        # noinspection PyTypeChecker
        column_size = [c in pertibate_columns and len(self._parameters[c]) or 1
                       for c in self.columns]

        max_size = min(max_size or reduce(lambda x, y: x * y, column_size),
                       self.MAX_SIZE)

        for indexes in self.index_iterator(column_size, max_size):
            row = SeabornRow(self.row_columns,
                             [self.pertibate_value(indexes.pop(0), c) for
                              c in self.columns])

            kwargs = row.obj_to_dict()
            if filter_func is None or filter_func(_row_index=len(self.table),
                                                  **kwargs):
                self.table.append(row)

        for c in self.columns:  # if the parameter is a dynamic function
            if hasattr(self._parameters[c], '__call__'):
                # noinspection PyTypeChecker
                self.set_column(c, self._parameters[c])

    def _setup_steps(self, given, when, then):
        """
        :param given: dict of list of values
        :param when: dict of list of values
        :param then: dict of list of values
        """
        # todo review
        self.given = given or {}
        self.when = when or {}
        self.then = then or {}

        self._parameters = {'#': lambda _row_index, **kwargs: _row_index}
        self._parameters.update(self.given)
        self._parameters.update(self.when)
        self._parameters.update(self.then)
        self._columns = self.columns or (
            self.ordered_keys(self.given) +
            self.ordered_keys(self.when) +
            self.ordered_keys(self.then))

    def pertibate_value(self, index, column):
        # noinspection PyTypeChecker
        value = self._parameters.get(column, '')
        if isinstance(value, list):
            return value[index]
        return value

    @staticmethod
    def index_iterator(column_size, max_size, mix_index=False):
        """
            This will iterate over the indexes and return a list of indexes
        :param column_size: list of int of the size of each list
        :param max_size: int of the max number of iterations
        :param mix_index: bool if True will go first then last then middle
        :return: list of int of indexes
        """
        # todo implement a proper partial factorial design
        indexes = [0 for c in column_size]

        index_order = [0]
        if mix_index:
            for i in xrange(1, max(column_size)):
                index_order += [-1 * i, i]
        else:
            index_order += xrange(1, max(column_size))

        for i in xrange(max_size):
            yield [index_order[indexes[i]] for i in xrange(len(indexes))]

            for index in xrange(len(column_size)):
                indexes[index] += 1
                if indexes[index] < column_size[index]:
                    break

                indexes[index] = 0
                if index == len(column_size) - 1:
                    raise StopIteration()

    def row_to_str(self, row, width):
        """
            This will return a list as a text in the form of a behave table
        :param row: list of values
        :param width: list of int of the column width
        :return: str of the row in the behave table format | col 1 | col 2 |
        """
        d = self.DELIMINATOR

        def str_(obj):
            return '' if obj is None else safe_str(obj, True)

        try:
            return (d + d.join([str_(row[r]).ljust(width[i]) for i, r in
                                enumerate(self._columns)]) + d).strip()
        except:
            return (d + d.join([str_(row[r]).ljust(width[r]) for r in
                                xrange(len(width))]) + d).strip()
            # todo fix this

    def column_width(self, index=None, name=None, max_width=300):
        """
        :param index: int of the column index
        :param name: str of the name of the column
        :param max_width: int of the max size of characters in the width
        :return: int of the width of this column
        """
        assert name is not None or index is not None
        if name and not name in self.row_columns:
            return min(max_width, name)

        if index is not None:
            name = self.columns[index]
        else:
            index = self.row_columns.index(name)

        values_width = [len(name)]
        if isinstance(self._parameters.get(name, None), list):
            values_width += [len(safe_str(p, True))
                             for p in self._parameters[name]]

        values_width += [len(safe_str(row[index], True)) for row in self.table]

        ret = max(values_width)
        return min(max_width, ret) if max_width else ret

    def __str__(self):
        """
        :return: str of the table
        """
        column_widths = [self.column_width(name=col) for col in self.columns]
        ret = [self.row_to_str(row, column_widths) for row in
               ([self.columns] + self.table)]
        return self.tab + ('\n' + self.tab).join(ret)

    def insert(self, index, column, default_value='', values=None,
               compute_value_func=None, compute_key=None):
        """
            This will insert a new column at index and then set the value
            unless compute_value is provided
        :param index: int index of where to insert the column
        :param column: str of the name of the column
        :param default_value: obj of the default value
        :param values: obj of the column values (should be equal to table length)
        :param compute_value_func: func to compute the value given the current row
        :param compute_key: str of the column to send to computer_value_func instead of row
        :return: None
        """
        self.row_columns.insert(index, column)
        if self.row_columns is not self.columns and column not in self.columns:
            self.columns.insert(index, column)
        for row in self.table:
            if values:
                row.insert(index, values.pop(0))
            else:
                row.insert(index, default_value)
            if compute_value_func is not None:
                row[index] = compute_value_func(row if compute_key is None else row[compute_key])

        self._parameters[column] = list(set(self.get_column(column)))

    def __eq__(self, other):
        if not isinstance(other, SeabornTable):
            other = SeabornTable(other)
        return self.table.__eq__(other.table)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if not isinstance(other, SeabornTable):
            other = SeabornTable(other)
        return self.table.__gt__(other.table)

    def __lt__(self, other):
        if not isinstance(other, SeabornTable):
            other = SeabornTable(other)
        return self.table.__lt__(other.table)

    def __ge__(self, other):
        if not isinstance(other, SeabornTable):
            other = SeabornTable(other)
        return self.table.__ge__(other.table)

    def __le__(self, other):
        if not isinstance(other, SeabornTable):
            other = SeabornTable(other)
        return self.table.__le__(other.table)

    def __len__(self):
        return len(self.table)

    def pop_column(self, column):
        self.columns = [c for c in self.columns if c != column]

    def keys(self):
        return self.columns

    def has_key(self, item):
        return item in self.columns

    def clear(self):
        self.table = []

    def copy(self):
        return self.__class__(self)

    @property
    def key_on(self):
        return self._key_on

    @key_on.setter
    def key_on(self, value):
        """
        :param value: str of which column to key the rows on like a dictionary
        :return: None
        """
        if isinstance(value, basestring):
            value = (value,)
        self._key_on = value

    def set_column(self, item, value=None):
        if hasattr(value, '__call__'):
            value = [value(_row_index=r, **self.table[r].obj_to_dict()) for r
                     in xrange(len(self.table))]
        else:
            value = isinstance(value, list) and value or [value] * len(self)

        if item not in self.row_columns:
            self.row_columns.append(item)
            for row in self.table:
                row.append(None)

        index = self.row_columns.index(item)
        for i, row in enumerate(self.table):
            row[index] = value[i]

    def get_column(self, item):
        index = self.columns.index(item)
        return [row[index] for row in self.table]

    def __contains__(self, value):
        if not isinstance(value, (tuple, list, dict, SeabornRow)) and self.key_on and len(self.key_on) == 1:
            value = [value]

        if isinstance(value, (tuple, list)) and self.key_on and len(value) == len(self.key_on):
            for row in self.table:
                key = [row[k] for k in self.key_on]  # todo better job
                if key == list(value):
                    return True
            return False
        elif isinstance(value, SeabornRow) and value._columns == self.row_columns:
            return value in self.table
        elif isinstance(value, SeabornRow):  # todo better job
            value = [value[k] for k in self.row_columns]
            for row in self.table:
                if [row[k] for k in self.row_columns] == value:
                    return True
            return False

        elif isinstance(value, (tuple, list, dict)):
            return self.normalize_row(value) in self.table

    def __getitem__(self, item):
        """
            This will return a row if item is an int or if key_on is set
            else it will return the column if column if it is in self._columns
        :param item: int or str of the row or column to get
        :return: list
        """
        if isinstance(item, (int, slice)):
            return self.table[item]
        else:
            assert self.key_on
            if not isinstance(item, (tuple, list)):
                item = [item]

            for row in self.table:
                key = [row[k] for k in self.key_on]  # todo better job
                if key == list(item):
                    return row

            row = self.append()
            for i, key in enumerate(self.key_on):
                row[key] = item[i]
            return row

    def __setitem__(self, item, value):
        """
            This will set a row if item is an int or set the values of a column
        :param item: int or str of the row or column to set
        :param value: func or obj or list if it is a list then assign each row
            from this list
        :return: None
        """
        if isinstance(item, int):
            self.table[item] = self.normalize_row(value)
        else:
            assert self.key_on
            if not isinstance(item, (tuple, list)):
                item = [item]

            for i, row in enumerate(self.table):
                key = [row[k] for k in self.key_on]  # todo better job
                if key == list(item):
                    self.table[i] = value
                    return

            row = self.append(value)
            for i, key in enumerate(self.key_on):
                row[key] = item[i]

    def normalize_row(self, row):
        if row is None:
            values = [None for i in range(len(self.row_columns))]
        elif isinstance(row, (dict, SeabornRow)):
            values = [row.get(k, None) for k in self.row_columns]
        elif not isinstance(row, list):
            values = [getattr(row, k, None) for k in self.row_columns]
        else:
            values = (row + [None for i in range(len(row),
                                                 len(self.row_columns))])
        return SeabornRow(self.row_columns, values)

    @classmethod
    def str_to_obj(cls, text, deliminator='|'):
        text = text.strip().split('\n')
        list_of_list = [[cell.strip() for cell in row.split(deliminator)]
                        for row in text]
        if list_of_list[0][0] == '' and list_of_list[0][-1] == '':
            list_of_list = [row[1:-1] for row in list_of_list]
        return cls(list_of_list)

    @property
    def parameters(self):
        return self._parameters

    @staticmethod
    def safe_str(cell):  # todo reconcile this with excel version of safe_str
        if cell is None:
            return ''
        if isinstance(cell, basestring):
            if cell.replace('.', '').isdigit() or '"' in cell or cell in ['False', 'True']:
                cell = '"%s"' % cell

        return str(cell)

    def obj_to_mark_down(self, title_columns=True):
        """
        This will return a str of a mark down text
        :param title_columns: bool if True will title all headers
        :return: str
        """
        md = [[self._title_column(cell) if title_columns else str(cell) for cell in self.columns]]
        md += [[self.safe_str(row[col]) for col in self.columns] for row in self.table]
        widths = []

        for col in range(len(md[0])):
            width = max([len(row[col]) + 1 for row in md])
            widths.append(min(300, width))

        md.insert(1, [":" + '-' * (width - 1) for width in widths])
        md = ['| '.join([row[c].ljust(widths[c])
                         for c in range(len(row))]) for row in md]
        string = '| ' + ' |\n| '.join(md) + ' |'
        return '| ' + ' |\n| '.join(md) + ' |'

    @classmethod
    def objs_to_mark_down(cls, tables, keys=None, pretty_columns=True):
        """
        :param tables: dict of {str <name>:SeabornTable}
        :param keys:   list of str of the order of keys to use
        :return:       str of the converted markdown tables
        """
        keys = keys or tables.keys()
        ret = ['#### ' + key + '\n' + tables[key].obj_to_mark_down(pretty_columns=pretty_columns) for key in keys]
        return '\n\n'.join(ret)

    def obj_to_csv(self, quote_everything=False, space_columns=True):
        """
        This will return a str of a csv text that is friendly to excel
        :param quote_everything: bool if True will quote everything if it needs
            it or not
        :param space_columns: bool if True it will align columns with spaces
        :return: str
        """
        csv = [[self.excel_cell(cell, quote_everything)
                for cell in self.columns]]
        csv += [[self.excel_cell(row[col], quote_everything)
                 for col in self.columns] for row in self.table]

        if space_columns:
            widths = []

            def len_(obj, max_width=300):
                ret = [len(o) for o in safe_str(obj).split('\r')]
                return min(max_width, max(ret))

            for col in range(len(csv[0])):
                widths.append(max([len_(row[col]) for row in csv]))

            csv = [','.join([row[c].ljust(widths[c])
                             for c in range(len(row))]) for row in csv]
        else:
            csv = [','.join(row) for row in csv]

        if os.name == 'posix':
            return '\r\n'.join(csv)
        else:
            return '\n'.join(csv)

    def html_link_cells(self):
        """
        This will return a new table with cell linked with their columns
        that have <Link> in the name
        :return:
        """
        new_table = self.copy()
        for row in new_table:
            for c in new_table.columns:
                link = '%s <Link>' % c
                if row.get(link, None):
                    row[c] = '<a href="%s">%s</a>' % (row[link], row[c])

        new_table.columns = [c for c in self.columns if '<Link>' not in c]
        return new_table

    def html_row_respan(self, row_span):
        row_span = [col for col in (row_span or []) if col in self.columns]
        if not row_span or len(self) < 2:
            return
        i = 0
        while i < len(self):
            for j, row in enumerate(self[i + 1:], i + 1):
                differences = [c for c in row_span if self[i][c] != row[c]]
                if differences:
                    break
                for c in row_span:
                    self[i][c] = HTMLRowRespan(row[c], j - i + 1)
                    row[c] = HTMLRowRespan(row[c])
            i = j if i != j else i + 1

    def obj_to_html(self, tab='', border=1, cell_padding=5, cell_spacing=1,
                    border_color='black', align='center', row_span=None):
        """
        This will return a str of an html table.
        :param tab: str to insert before each line e.g. '    '
        :param border: int of the thickness of the table lines
        :param cell_padding: int of the padding for the cells
        :param cell_spacing: int of the spacing for hte cells
        :param border_color: str of the color for the border
        :param align: str for cell alignment, center, left, right
        :param row_span: list of rows to span
        :return: str of html code
        """
        html_table = self.html_link_cells()
        html_table.html_row_respan(row_span)
        data = [self.html_row(html_table.columns, tab + '  ', '#bcbcbc',
                              align=align)]
        for i, row in enumerate(html_table):
            color = '#dfe7f2' if i % 2 else None
            row = [row[c] for c in html_table.columns]
            data.append(self.html_row(row, tab + '  ', color, align=align))

        ret = '''
            <table border="%s" cellpadding="%s" cellspacing="%s"
                   bordercolor="%s" >
              %s
            </table>'''.strip().replace('\n            ', '\n')

        data = ('\n%s  ' % tab).join(data)
        return (ret % (border, cell_padding, cell_spacing, border_color, data)
                ).replace('\n', '\n%s' % tab)

    @staticmethod
    def html_cell(cell):
        head = '<th'
        if isinstance(cell, HTMLRowRespan):
            if cell.count == 0:
                return ''
            head = '<th rowspan="%s"' % cell.count

        if cell is None:
            return '%s/>' % head
        if '\n' not in safe_str(cell):
            return '%s>%s</th>' % (head, cell)
        return '%s align="left">%s</th>' % (
            head, safe_str(cell).replace('\n', '<br>'))

    def html_row(self, row, tab='  ', background_color=None, header='',
                 align='center'):
        data = [self.html_cell(cell) for cell in row]

        if background_color is not None:
            header = 'bgcolor="%s"' % background_color + header

        header += 'align="%s"' % align
        return '<tr %s>\n%s  %s\n%s</tr>' % (
            header, tab, ('\n%s  ' % tab).join(data), tab)

    def excel_cell(self, cell, quote_everything=False):
        """
        This will return a text that excel interprets correctly when
        importing csv
        :param cell: obj to store in the cell
        :param quote_everything: bool to quote even if not necessary
        :return:
        """
        if cell is None:
            return ''
        if cell is True:
            return 'TRUE'
        if cell is False:
            return 'FALSE'
        if isinstance(cell, unicode):
            cell = cell.replace(u'\u2019', "'").replace(u'\u2018', "'")
            cell = cell.replace(u'\u201c', '"').replace(u'\u201d', '"')

        if isinstance(cell, unicode):
            cell = cell.encode('ascii', errors="replace")

        if sys.version_info[0] == 3 and isinstance(cell, bytes):
            cell = cell.decode('utf-8')

        if quote_everything:
            return '"' + safe_str(cell) + '"'

        if isinstance(cell, str) and cell.replace('.', '').isdigit():
            return '"' + cell + '"'

        ret = safe_str(cell).replace('\r', '\\r').replace('\n', '\r')

        if ret.startswith(' ') or ret.endswith(' '):
            return '"' + ret.replace('"', '""') + '"'

        for special_char in ['\r', '\t', '"', ',']:
            if special_char in ret:
                return '"' + ret.replace('"', '""') + '"'

        return ret

    @classmethod
    def csv_to_obj(cls, file_path='', text='', columns=None,
                   remove_empty_rows=True, key_on=None):
        """
        This will convert a csv file or csv text into a seaborn table and return it
        :param file_path: str of the path to the file
        :param text: str of the csv text
        :param columns: list of str of columns to use
        :param remove_empty_rows: bool if True will remove empty rows which can happen in non-trimmed file
        :param key_on: list of str of columns to key on
        :return: SeabornTable
        """
        if file_path and os.path.exists(file_path):
            text = open(file_path, 'rb').read()
            if sys.version_info[0] == 3:
                text = text.decode('utf-8')
        data = []
        text = text.replace('\xdf', 'B')
        text = text.replace('\xef\xbb\xbf', '')
        if text.find('\r\n') == -1:
            lines = text.replace('""', '\xdf').split('\n')
        else:
            lines = text.replace('""', '\xdf').split('\r\n')

        for i in xrange(len(lines)):
            lines[i] = lines[i].replace('\r', '\n').replace('\\r', '\r').split(',')
        l = 0
        while l < len(lines):
            cells = lines[l]
            l += 1
            i = 0
            row = []
            while i < len(cells):
                cell = cells[i]  # for some reason this is slow in pycharm debug
                i += 1
                while cell.count('"') % 2:
                    if i >= len(cells):  # this shouldn't, but maybe excel is doing it
                        cells += lines[l]
                        cell += "\n" + cells[i]  # add the line break back in
                        l += 1
                    else:
                        cell += ',' + cells[i]
                    i += 1
                cell = cell.strip()
                if cell and cell[0] == '"' and cell[-1] == '"':
                    cell = cell[1:-1].replace('\xdf', '"')
                elif cell.replace('.', '').isdigit():
                    cell = eval(cell)

                row.append(cell)
            if not remove_empty_rows or True in [bool(r) for r in row]:
                data.append(row)

        ret = cls(data, key_on=key_on)
        ret.columns = columns or ret.columns
        return ret

    @classmethod
    def mark_down_to_dict_of_obj(cls, file_path='', text='', columns=None, key_on=None, ignore_code_blocks=True):
        """
        This will read multiple tables separated by a #### Header and return it as a dictionary of headers
        :param file_path: str of the path to the file
        :param text: str of the mark down text
        :param columns: list of str of columns to use
        :param key_on: list of str of columns to key on
        :param ignore_code_blocks: bool if true will filter out any lines between ```
        :return: OrderedDict of {<header>: SeabornTable}
        """
        if file_path and os.path.exists(file_path):
            text = open(file_path, 'r').read()

        ret = OrderedDict()
        paragraphs = text.split('####')
        for paragraph in paragraphs[1:]:
            header, text = paragraph.split('\n', 1)
            ret[header.strip()] = cls.mark_down_to_obj(text=text, columns=columns, key_on=key_on)
        return ret

    @staticmethod
    def clean_cell(text):
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        elif text.replace('.', '').isdigit() or text in ['True', 'False']:
            text = eval(text)
        return text

    @classmethod
    def mark_down_to_obj(cls, file_path='', text='', columns=None, key_on=None, ignore_code_blocks=True):
        """
        This will convert a csv file or csv text into a seaborn table and return it
        :param file_path: str of the path to the file
        :param text: str of the mark down text
        :param columns: list of str of columns to use
        :param key_on: list of str of columns to key on
        :param ignore_code_blocks: bool if true will filter out any lines between ```
        :return: SeabornTable
        """
        if file_path and os.path.exists(file_path):
            text = open(file_path, 'r').read()

        data = []
        text = text.replace('\r\n', '\n').replace('\r', '\n').strip()

        if ignore_code_blocks:
            text = text.split("```")
            for i in xrange(1, len(text), 2):
                text.pop(i)
            text = (''.join(text)).strip()

        assert text.startswith('|') and text.endswith('|'), "Unknown format for markdown table"

        table = []
        for row in text.split('\n'):
            row = row.strip()
            if row == '':
                continue
            assert row[0] == '|' and row[-1] == '|', 'The following line is formatted correctly: %s' % row
            table.append([SeabornTable.clean_cell(cell) for cell in row[1:-1].split('|')])
        return cls(table=table[2:], columns=columns or table[0], key_on=key_on)

    def sort_by_key(self, keys=None):
        keys = keys or self.key_on
        keys = keys if isinstance(keys, (list, tuple)) else [keys]
        if sys.version_info[0] == 2:
            self.table.sort(by_key(keys))
        else:
            self.table.sort(key=by_key(keys))

    def reverse(self):
        self.table.reverse()


class SeabornRow(list):
    def __init__(self, columns, values):
        super(SeabornRow, self).__init__(values)
        self._columns = columns

    def __getitem__(self, item):
        try:
            if isinstance(item, int):
                return list.__getitem__(self, item)
            else:
                for i in range(len(self._columns)):
                    if self._columns[i] == item:  # this fixes a special case that didn't work for index
                        return self[i]
                assert KeyError, item

        except Exception as e:
            raise Exception(dict(original_error=str(e),
                                 item=item,
                                 columns=self._columns,
                                 size=len(self)))

    def __setitem__(self, item, value):

        if isinstance(item, int):
            return list.__setitem__(self, item, value)
        elif item in self._columns:
            return list.__setitem__(self, self._columns.index(item), value)

    @property
    def columns(self):
        return self._columns

    def obj_to_dict(self):
        return dict([(self._columns[i], list.__getitem__(self, i))
                     for i in range(len(self))])

    def __repr__(self):
        return super(SeabornRow, self).__repr__()

    def __str(self):
        return super(SeabornRow, self).__str__()

    def get(self, key, default):
        try:
            if key in self._columns:
                return list.__getitem__(self, self._columns.index(key))
            else:
                return default
        except Exception as e:
            raise

    def update(self, dict):
        for k, v in dict.items():
            self[k] = v

    def copy(self):
        return SeabornRow(self._columns, list(self) + [])

    def __nonzero__(self):
        for cell in self:
            if cell:
                return True
        return False


class HTMLRowRespan(object):
    def __init__(self, value, count=0):
        self.value = value
        self.count = count

    def __str__(self):
        return '' if self.value is None else str(self.value)

    def __cmp__(self, other):
        return self.value != other


def safe_str(obj, repr_line_break=False):
    """ This is because non-ascii values can break normal str function """
    try:
        if repr_line_break:
            return str(obj).replace('\n', '\\n')
        else:
            return str(obj)
    except Exception as e:
        return obj.encode('utf-8')


if sys.version_info[0] == 2:
    class by_key(object):
        def __init__(self, keys):
            self.keys = isinstance(keys, list) and keys or [keys]

        def __call__(self, obj1, obj2):
            for key in self.keys:
                if obj1[key] > obj2[key]:
                    return 1
                if obj1[key] < obj2[key]:
                    return -1
            return 0
else:

    class by_key(object):
        def __init__(self, keys, comp=None):
            self.keys = isinstance(keys, list) and keys or [keys]
            self.comp = comp or (lambda x: x)

        def __call__(self, obj):
            return [self.comp(obj[k]) for k in self.keys]
