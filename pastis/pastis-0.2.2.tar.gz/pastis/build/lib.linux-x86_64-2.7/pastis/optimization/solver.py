import numpy as np
from scipy import sparse
from sklearn.utils import check_random_state

from .optimization_ import Optimizer


class PoissonOptimizer(object):
    """
    """
    def __init__(self, max_iter=5000, hessian_approximation=True, tol=1e-1,
                 acceptable_tol=1e-1, mu_strategy="adaptive", nucleus_size=-1,
                 adjacent_beads=-1, alpha=-3, beta=1):

        if mu_strategy == "monotone":
            mu_strategy_type = 0
        elif mu_strategy == "adaptive":
            mu_strategy_type = 1
        else:
            raise ValueError(
                "Unkown mu strategy type")

        self.optimizer = Optimizer(
            model="poisson",
            max_iter=max_iter,
            hessian_approximation=hessian_approximation,
            tol=tol,
            acceptable_tol=acceptable_tol,
            mu_strategy=mu_strategy_type,
            nucleus_size=nucleus_size,
            adjacent_beads=adjacent_beads,
            alpha=alpha,
            beta=beta)

    def fit(self, counts, lengths, init=None, random_state=None, mapping=None,
            bias=None):
        """
        Fitting the poisson model.
        """

        if mapping is not None and (mapping.max() + 1 > len(counts)):
            raise ValueError(
                "Elements from the mapping are outside of the contact "
                "counts'range.")
        if mapping is not None and len(mapping) != lengths.sum():
            raise ValueError(
                "The mapping should be of shape L, where L is the total "
                "lengths of the genome")

        c = sparse.coo_matrix(counts)
        row, col, data = c.row.astype(int), c.col.astype(int), c.data
        random_state = check_random_state(random_state)

        if bias is None:
            bias = np.ones(lengths.sum(), dtype=np.double)
        if init is None:
            init = random_state.randn((lengths.sum() * 3))
        else:
            init = init.flatten()
        self.init = init

        if mapping is None:
            # This is the haploid case. We need to create the mapping by hand.
            mapping_data = np.arange(lengths.sum())
            mapping_num_elements = np.ones(mapping_data.shape)
        else:
            mapping_data = []
            mapping_num_elements = []
            for i in np.unique(mapping):
                mapping_data.append(np.where(mapping == i)[0])
                mapping_num_elements.append(len(np.where(mapping == i)[0]))
            mapping_data = np.concatenate(mapping_data)
            mapping_num_elements = np.array(mapping_num_elements)

        mapping_indptr = np.concatenate(
            [[0],
             mapping_num_elements.cumsum()[:-1]]).astype(np.int32)

        self.X_ = self.optimizer.fit_(
            row, col, data, counts.shape[0], lengths,
            init,
            bias=bias,
            mapping_data=mapping_data.astype(np.int32),
            mapping_num_elements=mapping_num_elements.astype(np.int32),
            mapping_indptr=mapping_indptr.astype(np.int32))

        return self.X_


class NegativeBinomialOptimizer(object):
    """
    """
    def __init__(self, max_iter=5000, hessian_approximation=True, tol=1e-1,
                 acceptable_tol=1e-1,  mu_strategy="adaptive", alpha=-3,
                 beta=1):

        if mu_strategy == "monotone":
            mu_strategy_type = 0
        elif mu_strategy == "adaptive":
            mu_strategy_type = 1
        else:
            raise ValueError(
                "Unkown mu strategy type")

        self.optimizer = Optimizer(
            model="negative_binomial",
            max_iter=max_iter,
            hessian_approximation=hessian_approximation,
            tol=tol,
            acceptable_tol=acceptable_tol,
            mu_strategy=mu_strategy_type,
            alpha=alpha,
            beta=beta)

    def fit(self, counts, lengths, dispersion, init=None, random_state=None,
            bias=None):
        c = sparse.coo_matrix(counts)
        row, col, data = c.row.astype(int), c.col.astype(int), c.data
        random_state = check_random_state(random_state)

        if bias is None:
            bias = np.ones(lengths.sum(), dtype=np.double)

        if init is None:
            init = random_state.randn((lengths.sum() * 3))
        else:
            init = init.flatten()
        self.init = init

        if len(dispersion) != len(data):
            raise ValueError("Disperson should be of same length as data")
        self.X_ = self.optimizer.fit(
            row, col, data, counts.shape[0], lengths,
            init, dispersion=dispersion.astype(float),
            bias=bias)

        return self.X_


class MDS(object):
    """
    """
    def __init__(self, max_iter=5000, hessian_approximation=True, tol=1e-1,
                 acceptable_tol=1e-1, mu_strategy="adaptive", nucleus_size=-1,
                 adjacent_beads=-1):
        if mu_strategy == "monotone":
            mu_strategy_type = 0
        elif mu_strategy == "adaptive":
            mu_strategy_type = 1
        else:
            raise ValueError(
                "Unkown mu strategy type")

        self.optimizer = Optimizer(
            model="mds",
            max_iter=max_iter,
            hessian_approximation=hessian_approximation,
            tol=tol,
            acceptable_tol=acceptable_tol,
            mu_strategy=mu_strategy_type,
            nucleus_size=nucleus_size,
            adjacent_beads=adjacent_beads)

    def fit(self, counts, lengths, init=None, random_state=None):
        """

        """
        # XXX This is not using the random state
        c = sparse.coo_matrix(counts)
        row, col, data = c.row.astype(int), c.col.astype(int), c.data
        random_state = check_random_state(random_state)
        if init is None:
            init = random_state.randn((lengths.sum() * 3))
        else:
            init = init.flatten()
        self.init_ = init.copy()
        self.X_ = self.optimizer.fit(
            row, col, data, counts.shape[0], lengths,
            init, dispersion=init, bias=init)
        return self.X_
