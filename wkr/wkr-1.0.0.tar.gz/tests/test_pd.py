#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wkr.pd` package."""

import pandas as pd

from wkr.pd import pandas_memoize


def dataframe_gen():
    """Generate a number of DataFrames."""
    d = {'one': pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
         'two': pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])}
    yield pd.DataFrame(d, index=['d', 'b', 'a'])
    df = pd.DataFrame(d, index=['d', 'b', 'a'],
                      columns=['two', 'three'])
    df['three'] = pd.to_numeric(df['three'])
    yield df
    yield pd.DataFrame({'one': [1., 2., 3., 4.],
                        'two': [4., 3., 2., 1.]},
                       index=['a', 'b', 'c', 'd'])
    yield pd.DataFrame([{'a': 1, 'b': 2},
                        {'a': 5, 'b': 10, 'c': 20}])


def test_memoize_pandas_save(tmpdir):
    """Test that `wkr.pd.memoize_pandas` saves to CSV."""
    for idx, df in enumerate(dataframe_gen()):
        filename = tmpdir.join('data{}.csv'.format(idx))

        @pandas_memoize(filename.strpath)
        def f():
            return df

        assert not filename.exists()
        df2 = f()
        assert df2.equals(df)
        assert filename.exists()
        df3 = pd.read_csv(filename.strpath,
                          encoding='utf-8', index_col=0)
        assert df3.equals(df)


def test_memoize_pandas_load(tmpdir):
    """Test that `wkr.pd.memoize_pandas` loads from CSV."""
    for idx, df in enumerate(dataframe_gen()):
        filename = tmpdir.join('data{}.csv'.format(idx))

        # define a memoized function that returns a known value
        @pandas_memoize(filename.strpath)
        def f():
            return df

        # now write to its CSV file a value that is different
        df2 = pd.DataFrame({'x': list(range(40, 30, -1)),
                            'y': list(range(20, 30))},
                           index=list(range(5, 15)))
        assert not df2.equals(df)
        df2.to_csv(filename.strpath, encoding='utf-8')
        assert filename.exists()

        # show that f() now returns df2, not df
        df3 = f()
        assert not df3.equals(df)
        assert df3.equals(df2)

        # remove the CSV file
        filename.remove()


def test_memoize_pandas_parse_dates(tmpdir):
    """Test `wkr.pd.memoize_pandas` on loading datetimes."""
    filename = tmpdir.join('data.csv')

    @pandas_memoize(filename.strpath)
    def f():
        return pd.DataFrame(
            list(range(72)),
            columns=['count'],
            index=pd.date_range('1/1/2011', periods=72, freq='H'))

    assert not filename.exists()
    df = f()
    assert filename.exists()
    df2 = f()

    # DataFrames are equal even if their types aren't the same
    assert df2.equals(df)
    assert df2.index.dtype != df.index.dtype

    @pandas_memoize(filename.strpath, parse_dates=True)
    def f():
        return pd.DataFrame(
            list(range(72)),
            columns=['count'],
            index=pd.date_range('1/1/2011', periods=72, freq='H'))

    filename.remove()
    assert not filename.exists()
    df = f()
    assert filename.exists()
    df2 = f()

    assert df2.equals(df)
    assert df2.index.dtype == df.index.dtype
