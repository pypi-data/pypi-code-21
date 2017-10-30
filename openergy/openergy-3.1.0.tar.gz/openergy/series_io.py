import logging
import pandas as pd
from contextlib import contextmanager
from multiprocessing import RLock


logger = logging.getLogger(__name__)


_store_lock = RLock()


@contextmanager
def hdf_get_store(path, **kwargs):
    """
    This function is thread-safe, contrary to pd.get_store
    """
    with _store_lock:
        with pd.HDFStore(path, **kwargs) as store:
            yield store


class IncompleteLocalSeriesIO:
    """
    Equivalent of SingleKeyHDFSeriesIO, but with many missing features.
    """
    def __init__(
        self,
        name,
        data_path
    ):
        """
        complib, complevel: http://pandas.pydata.org/pandas-docs/stable/io.html#compression
        """
        self.name = name
        self.data_path = data_path
        self.hdf_key = "data"

    def _get_pd_store(self):
        #  complib, complevel: http: // pandas.pydata.org / pandas - docs / stable / io.html  # compression
        return hdf_get_store(
            self.data_path,
            complib="zlib",  # blosc fails silently on my lenovo...
            complevel=1)

    def append(self, frame, **kwargs):
        assert len(kwargs) == 0, "incomplete local series io can't manage append kwargs, install otimeframes if needed"

        with self._get_pd_store() as store:
            store.append(self.hdf_key, frame, dropna=False)
            # force write to disk
            # http://pandas.pydata.org/pandas-docs/stable/io.html#notes-caveats
            store.flush(fsync=True)

    def select(self, **kwargs):
        if len(kwargs) != 0:
            logger.error("incomplete local series io can't manage select kwargs, install otimeframes if needed. "
                         "For current select, kwargs will not be used.")

        with self._get_pd_store() as store:
            return store.select("data")
