import numpy as np
from sklearn.metrics import euclidean_distances


def poisson_model_obj(X, counts, beta=1., alpha=-3, use_zero_counts=False):
    dis = euclidean_distances(X)
    log_likelihood = counts * alpha * np.log(dis) - beta * (dis ** alpha)
    if use_zero_counts:
        val = log_likelihood[
            np.invert(np.isnan(log_likelihood))].sum()
    else:
        val = log_likelihood[
            np.invert(np.isnan(log_likelihood) | (counts == 0))].sum()
    return -val


def negative_binomial_obj(X, counts, beta=1., alpha=-3., d=7.,
                          use_zero_counts=False):
    dis = euclidean_distances(X)
    log_likelihood = (counts * alpha * np.log(dis) -
                      (counts + d) * np.log(d + beta * (dis ** alpha)))
    if use_zero_counts:
        val = -log_likelihood[
            np.invert(np.isnan(log_likelihood))].sum()
    else:
        val = -log_likelihood[
            np.invert(np.isnan(log_likelihood) | (counts == 0))].sum()
    return val
