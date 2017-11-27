from tablo.base import BaseTabloColumn, BaseTablo

from tablo.format import Align, Format, joinrow


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

    def print(self):
        header_str = joinrow(self.__formatted_header())
        print(header_str)
        for row in self.__formatted_rows():
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
