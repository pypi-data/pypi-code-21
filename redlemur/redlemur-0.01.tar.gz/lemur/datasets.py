import os
import pandas as pd
import numpy as np
import pickle as pkl

class DiskDataSet:
    """A dataset living locally on the hard disk.

    A disk data set is defined by a `.csv` file where entries of the `resource_path` column 
    are paths to local `.pkl` files, and all other columns describe variables of the data point 
    linked to by the `resource_path` variable. 

    Parameters
    ----------
    df_path : str
	Path to the .csv file describing the DiskDataSet.

    Attributes
    ----------
    D : pandas DataFrame
        A DataFrame object describing the dataset.
    N : int
        The number of observations in the dataset.
    name : string
        A descriptive name for the dataset.

    """

    def __init__(self, df_path):
        self.D = pd.read_csv(df_path)
        self.N = self.D.shape[0]
        self.name = df_path.split("/")[-1].split(".")[0].split("_")[0]

    def getResource(self, index):
        """Get a specific data point from the data set.

        Parameters
        ----------
        index : int
            The index of the data point in `D`.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the data point.

        """
        resource_path = self.D["resource_path"].ix[index]
        dim_column = self.D["dim_column"].ix[index]
        with open(resource_path, "rb") as f:
            if dim_column:
                return pkl.load(f).T
            return pkl.load(f)

class DistanceMatrix:
    """A distance matrix computed from a DataSet object.

    Parameters
    ----------
    dataset : :obj:`DiskDataSet`
        A dataset on which to compute the distance matrix
    metric : function
        A distance used to compute the distance matrix.

    Attributes
    ----------
    dataset : :obj:`DiskDataSet`
        A dataset on which to compute the distance matrix
    metric : function
        A distance used to compute the distance matrix.
    N : int
        Number of data points in the dataset.
    matrix : :obj:`ndarray`
        The distance matrix.

    """

    def __init__(self, dataset, metric):
        self.dataset = dataset
        self.metric = metric
        self.N = self.dataset.N
        parameterization = self.metric.parameterize(self.dataset)
        self.matrix = np.zeros([self.N, self.N])
        for i in range(self.N):
            I = parameterization[i]
            for j in range(i + 1):
                J = parameterization[j]
                self.matrix[i, j] = self.metric.compare(I, J)
                self.matrix[j, i] = self.matrix[i, j]

    def getMatrix(self):
        """Get the distance matrix.

        Returns
        -------
        :obj:`ndarray`
            The distance matrix.

        """
        return self.matrix
