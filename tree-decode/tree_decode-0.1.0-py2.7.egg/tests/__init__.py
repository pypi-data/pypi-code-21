"""
Top-level directory for all of tree-decode's tests.
This is also the place where any test helpers can be stored.
"""

import pickle
import sys

PY3 = sys.version_info >= (3, 0, 0)
PY2 = sys.version_info >= (2, 0, 0) and not PY3


def pickle_model(model, filename, **kwargs):
    """
    Pickle a decision-tree model that has compatibility with Python 2.x.

    For the pickling to be compatible, we need to generate the files using
    Python 2.x (hopefully we can use Python 3.x in the future).

    Parameters
    ----------
    model : object
        The decision-tree that we are to pickle.
    filename : str
        The filename where the pickled model is stored.
    """

    if not PY2:
        raise TypeError("Must use Python 2.x to generate pickled files")

    with open(filename, "wb") as f:
        pickle.dump(model, f, protocol=0, **kwargs)


def load_model(filename, **kwargs):
    """
    Unpickle a decision-tree model that has compatibility with Python 2.x.

    Parameters
    ----------
    filename : str
        The filename where the pickled model is stored.

    Returns
    -------
    unpickled_model : object
        The decision-tree model pickled and stored at the given filepath.
    """

    # Encoding argument necessary to read the pickled files.
    if PY3:
        kwargs.update(encoding="latin1")

    with open(filename, "rb") as f:
        return pickle.load(f, **kwargs)
