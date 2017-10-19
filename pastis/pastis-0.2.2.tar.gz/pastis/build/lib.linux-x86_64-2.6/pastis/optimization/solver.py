import numpy as np
from scipy import sparse

from .optimization_ import Optimizer


class PoissonOptimizer(object):
    """
    """
    def __init__(self):
        self.optimizer = Optimizer(model="poisson")

    def fit(self, counts, lengths, init=None, random_state=None):
        c = sparse.coo_matrix(counts)
        row, col, data = c.row.astype(int), c.col.astype(int), c.data
        if init is None:
            init = np.random.randn((lengths.sum() * 3))
        else:
            init = init.flatten()
        self.init = init
        self.X_ = self.optimizer.fit(
            row, col, data, counts.shape[0], lengths,
            init, dispersion=init)
        return self.X_


class NegativeBinomialOptimizer(object):
    """
    """
    def __init__(self):
        self.optimizer = Optimizer(model="negative_binomial")

    def fit(self, counts, lengths, dispersion, init=None, random_state=None):
        c = sparse.coo_matrix(counts)
        row, col, data = c.row.astype(int), c.col.astype(int), c.data
        if init is None:
            init = np.random.randn((lengths.sum() * 3))
        else:
            init = init.flatten()
        self.init = init

        if len(dispersion) != len(data):
            raise ValueError("Disperson should be of same length as data")
        self.X_ = self.optimizer.fit(
            row, col, data, counts.shape[0], lengths,
            init, dispersion=dispersion.astype(float))
        return self.X_


class MDS(object):
    """
    """
    def __init__(self):
        self.optimizer = Optimizer(model="mds")

    def fit(self, counts, lengths, init=None, random_state=None):
        c = sparse.coo_matrix(counts)
        row, col, data = c.row.astype(int), c.col.astype(int), c.data
        if init is None:
            init = np.random.randn((lengths.sum() * 3))
        else:
            init = init.flatten()
        self.init_ = init.copy()
        self.X_ = self.optimizer.fit(
            row, col, data, counts.shape[0], lengths,
            init, dispersion=init)
        return self.X_
