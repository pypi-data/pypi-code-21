import numpy as np
import numbers


def _check_squared_array(X):
    """
    Check whether arrays are squared

    Parameters
    ----------
    X : ndarray

    Returns
    -------
    X
    """
    if len(X.shape) != 2:
        raise ValueError(
            "The ndarray has %d dimension. 2D array is expected." %
            len(X.shape))

    if X.shape[0] != X.shape[1]:
        raise ValueError(
            "The ndarray is of shape (%d, %d). Squasev array is expected." %
            (X.shape[0], X.shape[1]))

    return X


def check_random_state(seed):
    """Turn seed into a np.random.RandomState instance

    If seed is None, return the RandomState singleton used by np.random.
    If seed is an int, return a new RandomState instance seeded with seed.
    If seed is already a RandomState instance, return it.
    Otherwise raise ValueError.
    """
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, (numbers.Integral, np.integer)):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError('%r cannot be used to seed a numpy.random.RandomState'
                     ' instance' % seed)
