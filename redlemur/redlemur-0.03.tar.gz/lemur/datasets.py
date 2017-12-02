import os
import pandas as pd
import numpy as np
import pickle as pkl
import logging
import json

class DataSet:
    def __init__(self, D, name="default"):
        self.D = D
        self.n, self.d = self.D.shape
        self.name = name

    def getResource(self, index):
        return self.D.iloc[index, :]

    def saveMetaData(self, filepath):
        metadata = dict(d=self.d, n=self.n, name=self.name)
        string = json.dumps(metadata, indent=2)
        with open(filepath, 'w') as f:
            f.write(string)
        return string

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

    def __init__(self, df_path, index_column = None):
        self.D = pd.read_csv(df_path)
        if index_column is not None:
            self.D.index = self.D[index_column]
            self.D.index.name = index_column
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

    def getResourceDS(self, index):
        D = pd.DataFrame(self.getResource(index).T)
        name = self.name + " " + \
               str(index) + " "
        DS = DataSet(D, name)
        return DS

def convertDtype(l):
    try:
        return np.array(l, dtype="float")
    except:
        pass
    l = np.array(l, dtype=str)
    l[l == 'nan'] = 'NA'
    return l

class CSVDataSet(DataSet):
    """ A dataset living locally in a .csv file

    """
    def __init__(self, csv_path, index_column = None,  NA_val = ".", name = "mydataset"):
        self.name = name
        
        # Load the data set
        D = pd.read_csv(csv_path, dtype="unicode")
        self.n, self.d = D.shape
        print("Dataset of size", self.n, "samples", self.d, "dimensions", "Loaded")

        # Convert to numeric all numeric rows
        D = D.replace(NA_val, "nan")
        print("Replacing all", NA_val, "with nan")
        d = []
        for c in D.columns:
            d.append(convertDtype(list(D[c])))
            print("Converting", c, end="\r\r") 
        newcolumns = D.columns
        newindex = D.index
        D = list(d)
        D = pd.DataFrame(dict(zip(newcolumns, D)), index = newindex)


        # Set the index column as specified
        if index_column is not None:
            print("Setting index column as", index_column)
            D.index = D[index_column]
            print("Deleting", index_column, "from dataset")
            del D[index_column]

        self.D = D

        # Remove all columns which have all null values
        keep = []
        allnull = self.D.isnull().all(axis=0)
        for c in self.D.columns[allnull]:
            print("Removing column", c, "because it has all null values")
        keep = self.D.columns[~allnull]
        self.D = self.D[keep]

        # Remove all rows which have all null values
        allnull = self.D.isnull().all(axis=1)
        for r in self.D.index[allnull]:
            print("Removing row", r, "because it has all null values")
        keep = self.D.index[~allnull]
        self.D = self.D.loc[keep]
        n, d = self.D.shape
        print("Dataset of size", n, "samples", d, "dimensions", "Resulting")
        self.N = self.D.shape[0]

    def imputeColumns(self, numeric):
        keep = []
        keep = (self.D.dtypes == "float64").as_matrix()
        for c in self.D.columns[~keep]:
            print("Removing column", c, "because it is not numeric")
        self.D = self.D[self.D.columns[keep]]
        cmean = self.D.mean(axis=0)
        values = dict(list(zip(self.D.columns, cmean.as_matrix())))
        #self.D.fillna(value=values, inplace=True)
        d = self.D.as_matrix()
        for i, c in enumerate(self.D.columns):
            print("Imputing column", c, "with value", values[c])
            d[:, i][np.isnan(d[:, i])] = values[c]
        D = pd.DataFrame(d)
        D.index = self.D.index
        D.index.names = self.D.index.names
        D.columns = self.D.columns
        D.columns.names = self.D.columns.names
        self.D = D
        allzero = np.all(self.D.as_matrix() == 0, axis=0)
        for c in self.D.columns[allzero]:
            print("Removing column", c, "because it has all zero values")
        keep = self.D.columns[~allzero]
        allsame = np.std(self.D.as_matrix(), axis=0) == 0
        for c in self.D.columns[allsame]:
            print("Removing column", c, "because it has all zero standard deviation (all values same)")
        keep = self.D.columns[~allsame]
        self.D = self.D[keep]
        n, d = self.D.shape
        print("Dataset of size", n, "samples", d, "dimensions", "Resulting")
        print("Dataset has", self.D.isnull().sum().sum(), "nans")
        print("Dataset has", np.sum(np.isinf(self.D.as_matrix())), "infs")

    def getResource(self, index):
        """Get a specific data point from the data set.

        Parameters
        ----------
        index : int or string
            The index of the data point in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the data point.

        """
        if type(index) is int:
            return self.D.iloc[index].as_matrix()
        else:
            return self.D.loc[index].as_matrix()

    def getColumn(self, index):
        """Get a column of the dataframe.
 
        Parameters
        ----------
        index : int or string
            The index of the column in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`
            The values in the column.
        """
        if type(index) is int:
            return self.D.iloc[:, index].as_matrix()
        else:
            return self.D[index].as_matrix()

    def getColumnValues(self, index):
        """Get the unique values of a column.

        Parameters
        ----------
        index : int or string
            The index of the column in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`
            A ndarray of the unique values.

        """
        column = self.getColumn(index)
        if column.dtype == "float64":
            column = column[~np.isnan(column)]
        else:
            column = column[np.array([x != "NA" for x in column])]
        return np.unique(column)


    def getColumnDistribution(self, index):
        """Get the distribution of values in a column.

        Parameters
        ----------
        index : int or string
            The index of the column in `D`, either positional or a string.

        Returns
        -------
        :obj:`ndarray`, :obj:`ndarray`
            An array x of the unique labels, and an array y of the count of that label

        """
        x = self.getColumnValues(index)
        column = self.getColumn(index)
        y = [np.sum(column == v) for v in x]
        return x, y

    def getColumnNADist(self, index):
        column = self.getColumn(index)
        if column.dtype == "float64":
            na = np.sum([np.isnan(x) for x in column])
            not_na = len(column) - na
            return na, not_na
        else:
            na = np.sum([x == "NA" for x in column])
            not_na = len(column) - na
            return na, not_na
        return na, not_na

    def getColumnDescription(self, index, sep = "\n"):
        """Get a description of the column.

        """
        desc = []
        if type(index) is int:
            index = self.D.columns.values[index]
        for i, name in enumerate(self.D.columns.names):
            desc.append(name + ": " + index[i])
        return sep.join(desc)

    def getLevelValues(self, index):
        return np.unique(self.D.columns.get_level_values(index))


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

    def __init__(self, dataset, metric, index_level = 0):
        self.dataset = dataset
        self.labels = self.dataset.D.index.get_level_values(index_level)
        self.label_name = self.dataset.D.index.names[index_level]
        self.metric = metric
        self.metric_name = metric.__name__
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
