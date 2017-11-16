import numpy as np


def unbatch(tensor):
    if isinstance(tensor, np.ndarray):
        return list(map(lambda x: x[0, ...], np.split(tensor, tensor.shape[0])))
    raise TypeError("numpy.ndarray is required, got {}.".format(type(tensor)))
