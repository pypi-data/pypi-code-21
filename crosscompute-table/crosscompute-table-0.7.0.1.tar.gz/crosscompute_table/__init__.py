import pandas as pd
from invisibleroads_macros.disk import get_file_extension
from crosscompute.exceptions import DataTypeError
from crosscompute.scripts.serve import import_upload_from
from crosscompute.types import DataType
from functools import partial
from io import StringIO
from os.path import exists


class TableType(DataType):
    suffixes = 'table',
    formats = 'csv', 'msg', 'json', 'xls', 'xlsx'
    style = 'crosscompute_table:assets/part.min.css'
    script = 'crosscompute_table:assets/part.min.js'
    template = 'crosscompute_table:type.jinja2'
    views = [
        'import_table',
    ]
    requires_value_for_path = False

    @classmethod
    def save(Class, path, table):
        if path.endswith('.csv'):
            table.to_csv(path, encoding='utf-8', index=False)
        elif path.endswith('.msg'):
            table.to_msgpack(path, compress='blosc')
        elif path.endswith('.json'):
            table.to_json(path)
        elif path.endswith('.xls') or path.endswith('.xlsx'):
            table.to_excel(path)
        else:
            raise DataTypeError(
                'file format not supported (%s)' % get_file_extension(path))

    @classmethod
    def load(Class, path):
        if not exists(path):
            raise IOError
        if path.endswith('.csv'):
            table = _load_csv(path)
        elif path.endswith('.msg'):
            table = pd.read_msgpack(path)
        elif path.endswith('.json'):
            table = pd.read_json(path, orient='split')
        elif path.endswith('.xls') or path.endswith('.xlsx'):
            table = pd.read_excel(path)
        else:
            raise DataTypeError(
                'file format not supported (%s)' % get_file_extension(path))
        return table

    @classmethod
    def parse(Class, x, default_value=None):
        if isinstance(x, pd.DataFrame):
            return x
        return pd.read_csv(
            StringIO(x), encoding='utf-8', skipinitialspace=True)

    @classmethod
    def render(Class, table, format_name='csv'):
        if format_name == 'csv':
            return table.to_csv(encoding='utf-8', index=False)
        elif format_name == 'json':
            return table.to_json(orient='split')


def import_table(request):
    return import_upload_from(request, TableType, {'class': 'editable'})


def _load_csv(path):
    f = partial(pd.read_csv, skipinitialspace=True)
    try:
        return f(path, encoding='utf-8')
    except UnicodeDecodeError:
        pass
    try:
        return f(path, encoding='latin-1')
    except UnicodeDecodeError:
        pass
    return f(open(path, errors='replace'))
