"""
@file
@brief Metrics about regressions.
"""
import io
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


def multi_label_jaccard(exp, val):
    """
    Applies to a multi-label classification problem.
    Computes the average Jaccard index between two sequences
    of sets of labels
    (see `Multi-label classification <https://en.wikipedia.org/wiki/Multi-label_classification>`_).

    @param      exp     list of tuple or list of set or filename or streams (comma separated values) or dict
    @param      val     list of tuple or list of set or filename or streams (comma separated values) or dict
    @return             score

    .. math::

        E = \\frac{1}{n} \\sum_{i=1}^n \\frac{|C_i \\cap P_i|}{|C_i \\cup P_i|}


    """
    def to_set(v):
        if isinstance(v, set):
            return v
        elif isinstance(v, str):
            return set(v.split(','))
        else:
            return set(v)

    if isinstance(exp, (str, io.StringIO)) and isinstance(val, (str, io.StringIO)):
        # Files or streams.
        d1 = pandas.read_csv(exp, header=None, sep=";")
        d2 = pandas.read_csv(val, header=None, sep=";")
        dd1 = {}
        for k, v in d1.itertuples(name=None, index=False):
            if k in dd1:
                raise KeyError("Key '{}' already present".format(k))
            dd1[k] = v
        dd2 = {}
        for k, v in d2.itertuples(name=None, index=False):
            if k in dd2:
                raise KeyError("Key '{}' already present".format(k))
            dd2[k] = v
        return multi_label_jaccard(dd1, dd2)
    elif isinstance(exp, dict) and isinstance(val, dict):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))
        r = 0.0
        for k, e in exp.items():
            if k in val:
                v = val[k]
                es = to_set(e)
                vs = to_set(v)
                r += float(len(es & vs)) / len(es.union(vs))
            else:
                raise ValueError("Missing key in prediction {0}".format(k))
        return r / len(exp)
    elif isinstance(exp, list) and isinstance(val, list):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))

        r = 0.0
        for e, v in zip(exp, val):
            es = to_set(e)
            vs = to_set(v)
            r += float(len(es & vs)) / len(es.union(vs))
        return r / len(exp)
    else:
        raise TypeError(
            "Inconsisten types {0} != {1}".format(type(exp), type(val)))
