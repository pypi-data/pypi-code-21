import numpy as np

def factorial_list(n):
    """Return a list of factorials.

    Parameters
    ----------
    n : int
        maximum index of factorial list

    Returns
    -------
    ``numpy.array(n+1,1)`` of ``dtype`` ``int``
        list of factorials :math:`0!, \\ldots, n!`
    """
    res = np.empty(n + 1, dtype=int)
    res[0] = 1
    for i in range(1, n + 1):
        res[i] = res[i - 1] * i
    return res


def simplicial_list(n, k):
    """
    Return a list of simplicial numbers.

    The simplicial number :math:`{n+j-1 \\choose j}` is the number of :math:`j^{th}` degree partial derivatives of a function :math:`f` with domain of dimension :math:`n`, i.e. the number of homogenous :math:`j^{th}` degree monoomials with unitary coefficient.

    Parameters
    ----------
    n : int
        dimension of domain of :math:`f`
    k : int
        maximum derivative degree

    Returns
    -------
    ``numpy.array(k+1,1)`` of ``dtype`` ``int``
        list of :math:`{n+j-1 \\choose j}` for :math:`j=0,\\ldots,k`
    """
    seq = np.empty(k + 1, dtype=int)
    seq[0] = 1
    for i in range(1, k + 1):
        seq[i] = seq[i - 1] * (n + i - 1) / i
    return seq
