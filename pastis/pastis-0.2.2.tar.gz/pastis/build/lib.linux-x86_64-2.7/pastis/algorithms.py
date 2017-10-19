import os
import numpy as np
from scipy import sparse
from .optimization import solver

from sklearn.metrics import euclidean_distances
from sklearn.isotonic import IsotonicRegression

from .config import parse


max_iter = 5

CMD_PM = ('%s -o %s -w 8 '
          '-r %d '
          '-k %s '
          '-i %s '
          '-c %s -y 1 -a %f -b %f > %s')


CMD_MDS = ('%s -o %s -w 8 '
           '-r %d '
           '-k %s '
           '-i %s '
           '-c %s -y 1 > %s')


def run_mds(directory):
    print "Running MDS"

    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)

    random_state = np.random.RandomState(seed=options["seed"])

    # XXX That should change !!
    counts = np.load(os.path.join(directory,
                                  options["counts"]))

    wish_distances = compute_wish_distances(counts, alpha=options["alpha"],
                                            beta=options["beta"])
    wish_distances[np.arange(len(counts)), np.arange(len(counts))] = 0
    wish_distances = sparse.coo_matrix(np.triu(wish_distances))

    X = 1. - 2. * random_state.rand(len(counts) * 3)
    lengths = np.array([wish_distances.shape[0]])

    mds = solver.MDS()
    X = mds.fit(wish_distances, lengths, init=X)
    # Save the results
    mask = counts.sum(axis=0) == 0
    X[mask] = np.nan
    np.savetxt(os.path.join(
        directory,
        "MDS." + options["output_name"]) + ".coord", X)

    return X


def compute_wish_distances(counts, alpha=-3, beta=1):
    """
    Computes wish distances from a counts matrix

    Parameters
    ----------
    counts : ndarray
        Interaction counts matrix

    alpha : float, optional, default: -3
        Coefficient of the power law

    beta : float, optional, default: 1
        Scaling factor

    Returns
    -------
    wish_distances
    """
    wish_distances = counts.copy() / beta
    wish_distances[wish_distances != 0] **= 1. / alpha
    # FIXME this doesn't use beta
    return beta * wish_distances


def run_nmds(directory):
    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)
    X = run_mds(directory)

    for i in range(0, max_iter):
        X[np.isnan(X)] = 0

        dis = euclidean_distances(X)
        counts = np.load(
            os.path.join(directory, options["counts"]))
        counts[np.isnan(counts)] = 0

        wish_distances = np.zeros(counts.shape)
        lengths = np.array([wish_distances.shape[0]])

        print "Fitting isotonic regression..."
        ir = IsotonicRegression()
        wish_distances[counts != 0] = ir.fit_transform(
            1. / counts[counts != 0],
            dis[counts != 0])
        wish_distances = sparse.coo_matrix(np.triu(wish_distances))
        mds = solver.MDS()
        X = mds.fit(wish_distances, lengths, init=X)
        # Save the results
        mask = counts.sum(axis=0) == 0
        X[mask] = np.nan
        np.savetxt(os.path.join(
            directory,
            "NMDS.%d." % (i, ) + options["output_name"]) + ".coord", X)

    np.savetxt(os.path.join(
        directory,
        "NMDS." + options["output_name"]) + ".coord", X)
    return X


def run_pm1(directory):
    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)
    X = run_mds(directory)

    counts = np.load(os.path.join(directory, options["counts"]))
    counts[np.arange(len(counts)), np.arange(len(counts))] = 0
    counts = sparse.coo_matrix(np.triu(counts))

    lengths = np.array([counts.shape[0]])

    po = solver.PoissonOptimizer(max_iter=100000,
                                 alpha=options["alpha"],
                                 beta=options["beta"])

    X = po.fit(counts, lengths, init=X)
    np.savetxt(os.path.join(
        directory,
        "PM1." + options["output_name"]) + ".coord", X)
    return X


def run_pm2(directory):
    from .poisson_model_power_law import estimate_alpha_beta
    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)
    alpha, beta = options["alpha"], options["beta"]
    X = run_mds(directory)

    # Save counts in a format the C++ code can use
    counts = np.load(
        os.path.join(directory, options["counts"]))
    counts[np.arange(len(counts)), np.arange(len(counts))] = 0

    counts = sparse.coo_matrix(np.triu(counts))
    lengths = np.array([counts.shape[0]])

    for i in range(0, max_iter):
        X[np.isnan(X)] = 0
        # Fit alpha and beta
        if i != 0:
            alpha, beta = estimate_alpha_beta(
                counts.toarray() + counts.toarray().T,
                X, ini=np.array([alpha]))

        po = solver.PoissonOptimizer(max_iter=100000, alpha=alpha, beta=beta)
        X = po.fit(counts, lengths, init=X)

        # Save the results
        mask = counts.sum(axis=0) == 0
        X[mask] = np.nan
        np.savetxt(os.path.join(
            directory,
            "PM2.%d." % (i, ) + options["output_name"]) + ".coord", X)

    np.savetxt(os.path.join(
        directory,
        "PM2." + options["output_name"]) + ".coord", X)
    return X
