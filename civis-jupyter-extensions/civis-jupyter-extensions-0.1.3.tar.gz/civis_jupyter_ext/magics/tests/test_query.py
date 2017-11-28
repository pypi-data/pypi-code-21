import pytest
import pandas as pd
import six

from ..query import magic

if six.PY2:
    import mock
else:
    from unittest import mock


@pytest.mark.parametrize(
    'rows',
    [[('a', 1), ('b', 2)], []])
@mock.patch('civis_jupyter_ext.magics.query.civis')
def test_cell_magic(civis_mock, rows):
    line = 'my-database'
    cell = 'select * from dummy.table'
    civis_mock.io.query_civis.return_value.result.return_value = {
        'result_rows': rows,
        'result_columns': ['c1', 'c2']}
    civis_mock.APIClient.return_value = -1

    df = magic(line, cell)
    if len(rows) > 0:
        test_df = pd.DataFrame({'c1': ['a', 'b'], 'c2': [1, 2]})
        assert df.equals(test_df), "Returned data is wrong!"
    else:
        assert df is None, "Returned data is wrong!"
    civis_mock.io.query_civis.assert_called_with(
        cell, line, client=-1, preview_rows=100)


@pytest.mark.parametrize(
    'sep,database', [
        (' ', 'my-database'),
        ('; ', 'my database'),
        ('; ', 'my-database')])
@pytest.mark.parametrize(
    'cols',
    [(['a', 'b'], [1, 2]), ([], [])])
@mock.patch('civis_jupyter_ext.magics.query.civis')
def test_line_magic(civis_mock, cols, sep, database):
    sql = 'select * from dummy.table'
    line = sep.join([database, sql])
    test_df = pd.DataFrame({'c1': cols[0], 'c2': cols[1]})
    civis_mock.io.read_civis_sql.return_value = test_df
    civis_mock.APIClient.return_value = -1

    df = magic(line)
    if len(cols[0]) > 0:
        assert df.equals(test_df), "Returned data is wrong!"
    else:
        assert df is None, "Returned data is wrong!"
    civis_mock.io.read_civis_sql.assert_called_with(
        sql, database, use_pandas=True, client=-1)
