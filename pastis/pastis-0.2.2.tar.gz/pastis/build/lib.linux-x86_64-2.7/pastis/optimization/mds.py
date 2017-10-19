import numpy as np
from . import solver
from . import utils


def estimate_X(counts, factr=0, init=None, alpha=-3, random_state=None, lengths=None,
                 verbose=None,
                 maxiter=100):
    mds = solver.MDS()
    if lengths is None:
        lengths = np.array([counts.shape[1]])
    wd = utils.compute_wish_distances(counts, alpha=alpha)
    mds.fit(wd, lengths, random_state=random_state, init=init)
    return mds.X_
