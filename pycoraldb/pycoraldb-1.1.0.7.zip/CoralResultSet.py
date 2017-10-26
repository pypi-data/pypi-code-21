#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class CoralResultSet(object):
    """
    Coral Result Set
    Usage:
    >>> import pandas as pd
    >>> pd.DataFrame(rs.values, rs.columns)
    """
    def __init__(self, columns=[], values=[]):
        self.columns = columns
        self.values = values
        
    def items(self):
        return [dict(zip(self.columns, v)) for v in self.values]

    def toDataFrame(self):
        """
        toDataFrame: 转换为pandas.DataFrame对象
        :return: DataFrame对象
        """
        import pandas as pd
        df = pd.DataFrame(self.values, columns=self.columns)
        if self.columns and self.columns[0] == 'timestamp':
            df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y%m%d%H%M%S%f")
            df = df.set_index(df['timestamp'])
        return df
    
    def __len__(self):
        # if isinstance(self.values, numpy.ndarray):
        #     return self.values.shape[0]
        return len(self.values) if self.values else 0
        
    def __iter__(self):
        return CoralResultSetIterator(self)

    def __str__(self, *args, **kwargs):
        return 'CoralResultSet{columns: %s, values: %s}' % (self.columns, self.values)


class CoralResultSetIterator(object):
    def __init__(self, rs):
        self.rs = rs
        self.i = 0
        self.n = len(rs.values)

    def __iter__(self):
        return self

    def next(self):
        if self.i < self.n:
            i = self.i
            self.i += 1
            return dict(zip(self.rs.columns, self.rs.values[i]))
        else:
            raise StopIteration()   


if __name__ == '__main__':
    print CoralResultSet([], [])
    rs = CoralResultSet(['code', 'name'], [['60000.SH', u'浦发银行'], ['000001.SZ', u'平安银行']])
    print rs
    for item in rs:
        print item
