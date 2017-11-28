from collections import OrderedDict


ERROR_TEMPLATE = "'{}' {}"
INVALID_ROW_INDEX = 'Invalid row index'
INVALID_COLUMN_NAME = 'Invalid column name'
INVALID_PRIMITIVE_TYPE = 'Invalid Primitive type'


class BaseTabloRow:

    data_types = (int, float, str, bool)

    def __init__(self, headers, row_data):
        self._headers = headers
        self.__validate_row_data(row_data)
        self.__row_data = row_data

    def __validate_row_data(self, row_data):
        for d in row_data:
            if not self.__is_supported_type(d):
                raise ValueError(ERROR_TEMPLATE.format(d, INVALID_PRIMITIVE_TYPE))

    def __is_supported_type(self, data):
        result = any([isinstance(data, t) for t in self.data_types])
        return result

    @property
    def data(self):
        return [d for d in self.__row_data]

    def __getattr__(self, item):
        if item not in self._headers and item not in self.__dict__:
            raise AttributeError(ERROR_TEMPLATE.format(item, INVALID_COLUMN_NAME))
        if item in self._headers:
            i = self._headers.index(item)
            if i >= len(self.__row_data):
                return None
            return self.__row_data[i]
        return self.__getattribute__(item)

    def __getitem__(self, item):
        return self.__row_data[item]


class BaseTabloColumn:

    def __init__(self, name, rows):
        self._rows = self.__collect_rows(name, rows)

    def __collect_rows(self, name, rows):
        return [getattr(row, name) for row in rows]

    def __getitem__(self, item):
        validate_item(item, self._rows)
        return self._rows[item]


class BaseTablo:

    _Column = BaseTabloColumn
    _Row = BaseTabloRow

    def __init__(self, headers):
        self._headers = headers
        self._rows = []
        self._columns = OrderedDict()

    def __getattr__(self, item):
        col = self._columns.get(item)
        if col:
            return col
        return self.__getattribute__(item)

    def __getitem__(self, item):
        validate_item(item, self._rows)
        return self._rows[item]

    def append_row(self, row_data):
        new_row = self._Row(self._headers, row_data)
        self._rows.append(new_row)
        self.__recreate_columns()

    def __recreate_columns(self):
        for h in self._headers:
            new_column = self._Column(h, self._rows)
            self._columns[h] = new_column


def validate_item(item, rows):
    if len(rows) <= item:
        raise AttributeError(ERROR_TEMPLATE.format(item, INVALID_ROW_INDEX))
