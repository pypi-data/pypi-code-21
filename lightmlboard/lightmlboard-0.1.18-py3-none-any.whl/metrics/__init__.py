"""
@file
@brief Implements metrics.
"""
import sklearn.metrics as metrics
from .classification import roc_auc_score_micro, roc_auc_score_macro, reshape
from .regression import mse


def sklearn_metric(met, exp, val):
    """
    Looks into metrics available in
    :epkg:`scikit-learn:metrics`.

    @param      met     function name
    @param      exp     expected values
    @param      val     values
    @return             number
    """
    if isinstance(val, str):
        raise TypeError("val must be a container of floats")
    if isinstance(exp, str):
        raise TypeError("exp must be a container of floats")
    if hasattr(metrics, met):
        f = getattr(metrics, met)
        exp, val = reshape(exp, val)
        return f(exp, val)
    else:
        raise AttributeError("Unable to find metric '{0}'.".format(met))
