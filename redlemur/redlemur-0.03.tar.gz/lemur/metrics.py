import numpy as np
import scipy.signal as signal
import multiprocessing

class FroCorr:
    """An implementation the Frobenius-norm-of-correlation-matricies metric.

    This is not a class to be instantiated, but rather a way to organize and separate the 
    parameterization and comparison steps of the metric calculation to optimize a distance 
    matrix computation (e.g., compute the correlation matrix for each datapoint `once`, then
    just compare correlation matricies).

    """
        
    def parameterize(D):
        """Compute the correlation matrix of a single data point.

        Parameters
        ----------
        D : :obj:`DataSet`
            The lemur data set object to parameterize.

        Returns
        -------
        :obj:`list` of :obj:`ndarray`
            The correlation matrix of each object in the dataset.

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

class DiffAve:
    """A MRI distance. The euclidian distance of the average voxel intensity volumes.

    This is not a class to be instantiated, but rather a way to organize and separate the 
    parameterization and comparison steps of the metric calculation to optimize a distance 
    matrix computation (e.g., compute the correlation matrix for each datapoint `once`, then
    just compare correlation matricies).

    """
        
    def parameterize(D):
        """Compute the correlation matrix of a single data point.

        Parameters
        ----------
        D : :obj:`DataSet`
            The lemur data set object to parameterize.

        Returns
        -------
        :obj:`list` of :obj:`ndarray`
            The average of each object in the dataset.

        """
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            return list(map(lambda j: np.mean(D.getResource(j), axis=3), range(D.N)))

    def compare(x, y):
        """Compute the euclidian distance of two average volumes.

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

class NanNorm:
    """The dot product between two vectors, except nans are just treated as 0.

    """
        
    def parameterize(D):
        """Identity function.

        Parameters
        ----------
        D : :obj:`DataSet`
            A dataset.

        Returns
        -------
        :obj:`list` of :obj:`ndarray`
            The a list of each vector in the dataset.

        """

        return list(map(lambda j: D.getResource(j), range(D.N)))

    def compare(x, y):
        """Compute the euclidian distance of two correlation matricies.

        Parameters
        ----------
        x : :obj:`ndarray`
            The left vector argument.
        y : :obj:`ndarray`
            The left vector argument.

        Returns
        -------
        float
            The distance.

        """
        return np.nansum((x - y) * (x - y))

class VectorDifferenceNorm:
        
    def parameterize(D):
        """Identity function.

        Parameters
        ----------
        D : :obj:`DataSet`
            A dataset.

        Returns
        -------
        :obj:`list` of :obj:`ndarray`
            The a list of each vector in the dataset.

        """

        return list(map(lambda j: D.getResource(j), range(D.N)))

    def compare(x, y):
        """Compute the euclidian distance of two correlation matricies.

        Parameters
        ----------
        x : :obj:`ndarray`
            The left vector argument.
        y : :obj:`ndarray`
            The left vector argument.

        Returns
        -------
        float
            The distance.

        """
        return np.linalg.norm((x - y))

class Coh:
    """An implementation of the coherence metric.
    
    This is not a class to be instantiated, but just a method to calculate the intra-datapoint
    coherence distance.

    """
    
    def parameterize(D):
        """Compute the coherence matrix of a single data point.

        Parameters
        ----------
        D : :obj:`ndarray`
            A data matrix on which to compute the coherence matrix.

        Returns
        -------
        :obj:`ndarray`
            The coherence matrix.

        """
        NUM_WORKERS = multiprocessing.cpu_count() - 1
        dat = D.getResource(0)
    
        coherence = np.zeros((dat.shape[0], dat.shape[0]))
        coherence_pars = [(i, j, dat) for i in range(dat.shape[0]) for j in range(i, dat.shape[0])]

        pool = multiprocessing.Pool(processes=NUM_WORKERS)
        results = pool.map_async(Coh.get_coh, coherence_pars)
        coherence_vals = results.get()

        for ((i, j, dat), val) in zip(coherence_pars, coherence_vals):
            coherence[i, j] = val
            coherence[j, i] = val

        return coherence

    def get_coh(tup):
        i, j, dat = tup[0], tup[1], tup[2]
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            return np.mean(np.nan_to_num(signal.coherence(dat[i, :], dat[j, :], fs=500)[1]))

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

