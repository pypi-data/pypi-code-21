"""
Uniform kernel alignment puts equal weight to each kernel.

.. math::
    \mathbf{K}_{\mu} = \sum_q \mathbf{K}_{q}

"""

from numpy import ndarray, ones

class UniformAlignment:


    def __init__(self):
        self.trained = False
        self.mu = None
        self.Ks = None
        self.trained = None
        self.Kappa = None

    def fit(self, Ks):
        """
        Learn low-rank approximations and regression line for kernel matrices or Kinterfaces.

        :param Ks: (``list``) of (``numpy.ndarray``) or of (``Kinterface``) to be aligned.

        """
        self.mu = ones((len(Ks), ))
        self.Ks = Ks
        self.trained = True
        self.Kappa = sum([K[:, :] for K in Ks])

    def __call__(self, i, j):
        """
        Access portions of the combined kernel matrix at indices i, j.

        :param i: (``int``) or (``numpy.ndarray``) Index/indices of data points(s).

        :param j: (``int``) or (``numpy.ndarray``) Index/indices of data points(s).

        :return:  (``numpy.ndarray``) Value of the kernel matrix for i, j.
        """
        assert self.trained
        if isinstance(i, ndarray):
            i = i.astype(int).ravel()
        if isinstance(j, ndarray):
            j = j.astype(int).ravel()
        if isinstance(i, int) and isinstance(j, int):
            return self.Kappa[i, j]
        else:
            return self.Kappa[i, :][:, j]

    def __getitem__(self, item):
        """
        Access portions of the kernel matrix generated by ``kernel``.

        :param item: (``tuple``) pair of: indices or list of indices or (``numpy.ndarray``) or (``slice``) to address portions of the kernel matrix.

        :return:  (``numpy.ndarray``) Value of the kernel matrix for item.
        """
        assert self.trained
        return self.Kappa[item]



class UniformAlignmentLowRank(UniformAlignment):
    """
        Uniform kernel alignment when kernels are represented by low-rank
        approximations.
    """

    def __call__(self, i, j):
        """
        Access portions of the combined kernel matrix at indices i, j.

        :param i: (``int``) or (``numpy.ndarray``) Index/indices of data points(s).

        :param j: (``int``) or (``numpy.ndarray``) Index/indices of data points(s).

        :return:  (``numpy.ndarray``) Value of the kernel matrix for i, j.
        """
        assert self.trained
        if isinstance(i, ndarray):
            i = i.astype(int).ravel()
        if isinstance(j, ndarray):
            j = j.astype(int).ravel()
        return sum([G[i, :].dot(G[j, :].T) for G in self.Ks])


    def __getitem__(self, item):
        """
        Access portions of the kernel matrix generated by ``kernel``.

        :param item: (``tuple``) pair of: indices or list of indices or (``numpy.ndarray``) or (``slice``) to address portions of the kernel matrix.

        :return:  (``numpy.ndarray``) Value of the kernel matrix for item.
        """
        assert self.trained
        return sum([G[item[0]].dot(G[item[1]].T) for G in self.Ks])
