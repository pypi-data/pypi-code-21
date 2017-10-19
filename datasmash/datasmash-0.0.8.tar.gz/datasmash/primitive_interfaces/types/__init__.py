from typing import Sequence

try:
    import numpy  # type: ignore
    Sequence.register(numpy.ndarray)
    Sequence.register(numpy.matrix)
except ImportError:
    pass

try:
    import pandas  # type: ignore
    Sequence.register(pandas.DataFrame)
    Sequence.register(pandas.SparseDataFrame)
except ImportError:
    pass
