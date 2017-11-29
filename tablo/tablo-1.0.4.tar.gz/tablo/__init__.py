import re

from tablo.base import BaseTabloColumn, BaseTablo

from tablo.format import Align, Format, joinrow


ROW_PATTERN = re.compile('\s*\|\s*')

NEED_TABLO_INSTANCE_TO_COMPARE = 'Need Tablo instance to compare'


class TabloColumn(BaseTabloColumn):
    """ Моделирует колонку таблицы с разделителями """

    default_align = Align.Left

    def __init__(self, name, rows):
        """
            name: Имя колонки, также является видимым заголовком
            rows: Массив строк таблицы
        """
        super().__init__(name, rows)
        self._format = Format(self.default_align, self.__max_margin(name, self._rows))

    @property
    def format(self):
        return self._format.copy()

    @property
    def margin(self):
        return self._format.margin

    @margin.setter
    def margin(self, value):
        self._format.margin = value

    def __max_margin(self, name, rows):
        """ при вычислении ширины колонки используются значения из всех строк и имя колонки """
        rows.append(name)
        return max(len(str(r)) for r in rows)

    def centred(self):
        self._format.align = Align.Center

    def not_spaced(self):
        self._format.spacer = ''


class Tablo(BaseTablo):

    _Column = TabloColumn

    def __init__(self, headers):
        super().__init__(headers)

    @property
    def headers(self):
        return self._headers

    @property
    def rows(self):
        return self._rows

    def __str__(self):
        return self._get_row_strs()

    def __eq__(self, other):
        if not isinstance(other, Tablo):
            raise TypeError('{} {}'.format(other, NEED_TABLO_INSTANCE_TO_COMPARE))
        result = all([
            self.__are_headers_equal(other),
            self.__are_rows_equal(other)
        ])
        return result

    def __are_headers_equal(self, other):
        if len(self.headers) != len(other.headers):
            return False
        for s, o in zip(self.headers, other.headers):
            if s != o:
                return False
        return True

    def __are_rows_equal(self, other):
        if len(self.rows) != len(other.rows):
            return False
        for s, o in zip(self.rows, other.rows):
            for se, so in zip(s, o):
                if se != so:
                    return False
        return True

    def _get_row_strs(self):
        result = ''
        header_str = joinrow(self.__formatted_header())
        result += header_str + '\n'
        for i, row in enumerate(self.__formatted_rows()):
            row_str = joinrow(row)
            result += row_str + '\n'
        return result

    def print(self):
        header_str = joinrow(self.__formatted_header())
        print(header_str)
        for i, row in enumerate(self.__formatted_rows()):
            row_str = joinrow(row)
            print(row_str)

    def __formatted_header(self):
        return [self.__format_data(h, h) for h in self._headers]

    def __formatted_rows(self):
        return [self.__format_row(row) for row in self._rows]

    def __format_row(self, row):
        result = []
        for h in self._headers:
            data = getattr(row, h)
            result.append(self.__format_data(data, h))
        return result

    def __format_data(self, data, h) -> tuple:
        column = getattr(self, h)
        return (data, column.format)

    @classmethod
    def from_str(cls, text):
        rows = cls.__split_rows(text)
        str_headers = cls.__parse_str_row(rows[0])
        t = Tablo(str_headers)
        for row in rows[1:]:
            t.append_row(cls.__parse_str_row(row))
        return t

    @classmethod
    def __split_rows(cls, text):
        ROW_SEPARATOR = re.compile(r'\|\||\s*\n+\s*')
        rows = re.split(ROW_SEPARATOR, text)
        result = [r.strip() for r in rows if r]
        return result

    @classmethod
    def __parse_str_row(cls, str_row):
        symbols = [s.strip() for s in re.split(ROW_PATTERN, str_row) if s]
        return symbols
