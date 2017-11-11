import numpy as np
from tabulate import tabulate
from IPython.display import HTML, display


def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


class DataView:
    def __init__(self, cursor, rows):
        self._cols = [col[0] for col in cursor.description]
        self._rows = rows

    def _drow(self, row):
        drow = {}
        for i, col in enumerate(self._cols):
            drow[col] = row[i]
        return drow

    def __iter__(self):
        for row in self._rows:
            yield self._drow(row)

    def __getitem__(self, key):
        if isinstance(key, str):
            # key is colname
            colndx = self._cols.index(key)
            col = [None] * len(self._rows)
            for rowndx, row in enumerate(self._rows):
                col[rowndx] = row[colndx]
            return col
        elif isinstance(key, int):
            # key is rowndx
            return self._drow(self._rows[key])

    def __repr__(self):
        if isnotebook():
            html_tbl = tabulate(self._rows, headers=self._cols, tablefmt='html')
            display(HTML(html_tbl))
            return ''
        else:
            txt_tbl = tabulate(self._rows, headers=self._cols)
            return txt_tbl

    def values(self):
        # Get the "minimum" type in the row
        types = [str, int, float]
        type_to_ndx = dict([(t, i) for i, t in enumerate(types)])
        print(type_to_ndx)
        typendxs = [type_to_ndx[type(cell)] for cell in self._rows[0]]
        print(typendxs)
        typendx = min(typendxs)
        dtype = types[typendx]
        print(dtype)

        num_rows = len(self._rows)
        num_cols = len(self._cols)
        vals = np.zeros((num_rows, num_cols), dtype=dtype)
        for i, row in enumerate(self._rows):
            for j, cell in enumerate(row):
                vals[i, j] = dtype(cell)
                print(type(cell), cell, vals[i, j])
        return vals
