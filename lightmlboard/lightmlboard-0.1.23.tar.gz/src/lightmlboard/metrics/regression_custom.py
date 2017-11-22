"""
@file
@brief Metrics about regressions.
"""
import numpy


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
    (for *exp* and *val*).
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
    else:
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
