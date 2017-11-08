from .alignment import LEFT, RIGHT, CENTER, ColumnAlignment


class Table(object):
    def __init__(self):
        self.columns = []
        self.entries = []

    def add_column(self, heading, alignment=LEFT):
        if isinstance(alignment, int):
            alignment = ColumnAlignment(alignment)
        if alignment not in [LEFT, CENTER, RIGHT]:
            raise ValueError('Table.addColumn(): invalid alignment given')
        self.columns.append(Column(heading, alignment))

    def append(self, *fields):
        diff = len(self.columns) - len(fields)
        if diff < 0:
            raise ValueError('Table.append(): too many fields given')
        self.entries.append(list(fields) + [None] * diff)

    def format_row(self, fields):
        return ' | '.join([''] + [str(f) for f in fields] + ['']).strip()

    def __str__(self):
        titleRow = '|'
        separatorRow = '|'
        for column in self.columns:
            titleRow += ' {} |'.format(column.heading)
            separatorRow += '{}---{}|'.format(
                ':' if column.alignment.has_flag(LEFT) else ' ',
                ':' if column.alignment.has_flag(RIGHT) else ' '
            )
        result = '{}\n{}\n'.format(titleRow, separatorRow)
        result += '\n'.join(map(self.format_row, self.entries))
        return result + '\n'


class Column(object):
    def __init__(self, heading, alignment=LEFT):
        self.heading = heading
        self.alignment = alignment
