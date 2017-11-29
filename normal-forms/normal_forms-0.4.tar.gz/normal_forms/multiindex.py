import numpy as np
import combinatorics


class multiindex(object):
    """A multiindex representation.

    In this implementation, the multiindex :math:`(m_1,\\ldots,m_n)` corresponds to partial derivative :math:`\\frac{\\partial}{\\partial x_{m_1}}\\cdots\\frac{\\partial}{\\partial x_{m_n}}f` and homogenous :math:`n^{th}` degree monomial :math:`x_1^{m_1}\\cdots x_n^{m_n}`. A 'telephone-book' ordering is used and indices within the multiindex are assumed to be non-decreasing. For example, the multiindices with length ``n=2`` and with indices less than ``idx_max=3`` are, in increasing order: (0,0), (0,1), (0,2), (1,1), (1,2), (2,2). The next multiindex is cycled back to the first multiindex.

    Attributes
    ----------
    n : int
        number of indices
    idx_max : int
        upper bound, indices can take nonnegative values less than ``idx_max``
    """

    def __init__(self, n, idx_max):
        """Initialize zero multiindex."""

        self.idx = np.zeros(n, dtype=int)
        self.idx_max = idx_max

    def increment(self):
        """Increment multiindex."""

        n_idx = len(self.idx)
        if all(self.idx >= self.idx_max):
            self.idx = np.zeros(n_idx, dtype=int)
        else:
            i = n_idx - 1
            self.idx[i] += 1
            while self.idx[i] == self.idx_max:
                i -= 1
                self.idx[i] += 1
            self.idx[i:] = self.idx[i]

    def to_polynomial(self, var, x=None):
        """Convert multiindex to corresponding polynomial.

        Parameters
        ----------
        var : tuple of ``sympy.symbol`` objects
            list of variables ``x_0``, ``x_1``, ..., ``x_{n-1}``
        x : tuple of length n, optional
            roots of polynomial

        Returns
        -------
        ``sympy`` expression
            :math:`\\prod_{i=0}^{n}` ``var[i]`` if ``x`` is not supplied, otherwise :math:`\\prod_{i=0}^{n}` ``var[i]-x[i]``
        """

        if x == None:
            return np.product([var[idx] for idx in self.idx])
        else:
            return np.product([var[idx] - x[idx] for idx in self.idx])

    def to_var(self, var):
        """Convert multiindex to list of variables.

        Parameters
        ----------
        var : tuple of ``sympy.symbol`` objects
            list of variables ``x_0``, ``x_1``, ..., ``x_{n-1}``

        Returns
        -------
        list of ``sympy.symbol`` objects
            list of ``var[idx]`` for ``idx`` in ``self.idx``
        """

        return [var[idx] for idx in self.idx]

    def factorial(self):
        """Return multiindex factorial.

        In this implementation, multiindex :math:`m=(m_1,\ldots,m_n)` factorial is defined as :math:`\\alpha_1!\cdots \\alpha_n!` where :math:`\\alpha_i` is the number of occurences of :math:`i` in :math:`m`.

        Returns
        -------
        int
            multiindex factorial
        """

        # record number of occurences of idx in self.idx
        fac_dict = np.zeros(self.idx_max, dtype=int)
        for idx in self.idx:
            fac_dict[idx] += 1

        # list of factorials
        fac = combinatorics.factorial_list(int(np.max(fac_dict)))

        # return multiindex factorial
        return np.product([fac[key] for key in fac_dict])
