"""
@file
@brief Metrics about regressions.
"""
from sklearn.metrics import mean_squared_error


def mse(exp, val):
    """
    Computes `mean_squared_error <http://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_error.html>`_.
    """
    return mean_squared_error(exp, val)
