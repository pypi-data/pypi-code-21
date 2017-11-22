from collections import OrderedDict
from enum import Enum, unique
from pandas import DataFrame  # type: ignore
from pandas import Series  # NOQA


@unique
class Stat(Enum):
    """Possible values to pass as `statistic` to column association calls."""
    MI = ('mutual information')
    R2 = ('R squared')
    DATA_R2 = ('data R squared')
    CLASSIC_DEP_PROB = ('classic dep prob')

    def __init__(self, api_value):
        self.api_value = api_value


# TODO(asilvers): This isn't actually getting exposed publicly anywhere
# anymore. It's just used as an intermediate representation before being turned
# into a data frame. But I don't love the data frame representation, so it's
# possible someone will want this. Let it hang around for now.
class ColumnAssociation(object):
    """Provides a reasonable interface to a column association response"""

    def __init__(self, json):
        # Map from column name to index
        self._name_index = OrderedDict([(v, k)
                                        for k, v in enumerate(json['target'])])
        self._elements = json['elements']

    def between(self, colName1, colName2):  # type: (str, str) -> float
        """Returns the value of the column association."""
        colIndex1 = self._name_index[colName1]
        colIndex2 = self._name_index[colName2]
        j1 = min(colIndex1, colIndex2)
        j2 = max(colIndex1, colIndex2)
        return self._elements[_T(j2) + j1]

    def as_series(self):  # type: (...) -> Series
        """Returns the full column association table as a series.

        The returned series has a multi-index of (X, Y) which are the
        column names for that row, and the values of the series at that
        index is the value of the column association between those
        columns.
        """
        columns = list(self._name_index)
        # Building the data frame then returning a series from it is easier
        # than building the multi-index by hand.
        df = DataFrame([(c1, c2, self.between(c1, c2))
                        for c1 in columns
                        for c2 in columns], columns=['X', 'Y', 'I'])
        df = df.set_index(['X', 'Y'])
        return df['I']


def _T(k):  # type: (int) -> int
    """kth triangular number"""
    return (int)(k * (k + 1) / 2)
