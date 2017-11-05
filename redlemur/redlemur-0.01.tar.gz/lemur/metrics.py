import numpy as np

class FroCorr:
    """An implementation the Frobenius-norm-of-correlation-matricies metric.

    This is not a class to be instantiated, but rather a way to organize and separate the 
    parameterization and comparison steps of the metric calculation to optimize a distance 
    matrix computation (e.g., compute the correlation matrix for each datapoint `once`, then
    just compare correlation matricies.

    """
        
    def parameterize(D):
        """Compute the correlation matrix of a single data point.

        Parameters
        ----------
        D : :obj:`ndarray`
            A data matrix on which to compute the correlation matrix.

        Returns
        -------
        :obj:`ndarray`
            The correlation matrix.

        """
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            return list(map(lambda j: np.nan_to_num(np.corrcoef(D.getResource(j))), range(D.N)))

    def compare(x, y):
        """Compute the euclidian distance of two correlation matricies.

        Parameters
        ----------
        x : :obj:`ndarray`
            The left correlation matrix argument.
        y : :obj:`ndarray`
            The left correlation matrix argument.

        Returns
        -------
        float
            The distance.

        """
        return np.linalg.norm(x - y)
