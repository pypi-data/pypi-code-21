"""
@file
@brief Metrics about regressions.
"""
import io
import numpy
import pandas


def l1_reg_max(exp, val, max_val=180):
    """
    Implements a :epkg:`L1` scoring function which does not consider
    error above threshold *max_val*.

    @param      exp     list of values or :epkg:`numpy:array`
    @param      val     list of values or :epkg:`numpy:array`
    @return             score

    If ``max_val==180`, the function computes:

    .. math::

        E = \\frac{1}{n} \\sum_{i=1}^n \\frac{\\min \\left| Y_i - \\min(f(X_i), 180) \\right|}{180}

    The computation is faster if :epkg:`numpy:array` are used
    (for *exp* and *val*). *exp and *val* can be filenames or streams.
    In that case, the function expects to find two columns: id, value
    in both files or streams.
    """
    if isinstance(exp, numpy.ndarray) and isinstance(val, numpy.ndarray):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))
        an = numpy.zeros((len(exp),))
        an[:] = max_val
        mv = numpy.minimum(an, val)
        me = numpy.minimum(an, exp)
        df = numpy.abs(mv - me) / max_val
        return df.mean()
    elif isinstance(exp, dict) and isinstance(val, dict):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))
        r = 0.0
        for k, e in exp.items():
            if k in val:
                v = val[k]
                mv = min(v, max_val)
                ev = min(e, max_val)
                d = abs(mv - ev)
                r += 1. * d / max_val
            else:
                raise ValueError("Missing key in prediction {0}".format(k))
        return r / len(exp)
    elif isinstance(exp, (str, io.StringIO)) and isinstance(val, (str, io.StringIO)):
        # We expect filenames.
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
        return l1_reg_max(dd1, dd2, max_val=max_val)
    elif isinstance(exp, list) and isinstance(val, list):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))
        r = 0.0
        for e, v in zip(exp, val):
            mv = min(v, max_val)
            ev = min(e, max_val)
            d = abs(mv - ev)
            r += 1. * d / max_val
        return r / len(exp)
    else:
        raise TypeError(
            "Inconsisten types {0} != {1}".format(type(exp), type(val)))
