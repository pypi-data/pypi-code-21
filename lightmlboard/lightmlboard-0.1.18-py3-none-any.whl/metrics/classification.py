"""
@file
@brief Metrics about regressions.
"""
import numpy
import pandas
from sklearn.metrics import roc_auc_score


def is_vector(a):
    """
    Tells if an array is a vector.
    """
    return len(a.shape) == 1 or a.shape[1] == 1


def reshape(exp, val):
    """
    Reshape the expected values and predictions.
    """
    if isinstance(val, list):
        val = numpy.array(val)
    if isinstance(exp, list):
        exp = numpy.array(exp)
    if isinstance(val, pandas.DataFrame):
        val = val.as_matrix()
    if isinstance(exp, pandas.DataFrame):
        exp = exp.as_matrix()
    if not isinstance(val, numpy.ndarray):
        raise TypeError("val is {0} not an array".format(type(val)))
    if not isinstance(exp, numpy.ndarray):
        raise TypeError("exp is {0} not an array".format(type(exp)))
    if is_vector(exp) != is_vector(val):
        if not is_vector(val) and is_vector(exp):
            exp_ = exp
            exp = numpy.zeros((val.shape))
            for i, v in enumerate(exp_.ravel()):
                exp[i, int(v)] = 1
        else:
            exp = exp.ravel()
            val = val.ravel()
    elif is_vector(exp) and is_vector(val):
        exp = exp.ravel()
        val = val.ravel()

    if len(exp.shape) == 2 and exp.shape[1] == 1:
        raise ValueError("exp has two dimensions but one column")
    if len(val.shape) == 2 and val.shape[1] == 1:
        raise ValueError("val has two dimensions but one column")
    return exp, val


def roc_auc_score_micro(exp, val):
    """
    Computes `roc_auc_score <http://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html>`_
    with *average='micro'*.
    """
    exp, val = reshape(exp, val)
    return roc_auc_score(exp, val, average="micro")


def roc_auc_score_macro(exp, val):
    """
    Computes `roc_auc_score <http://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html>`_
    with *average='macro'*.
    """
    exp, val = reshape(exp, val)
    return roc_auc_score(exp, val, average="macro")
