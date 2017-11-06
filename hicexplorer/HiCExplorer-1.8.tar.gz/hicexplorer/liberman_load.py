import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix

def getLibermanBins(filenameList, chrnameList, pandas = True):
        """
        Reads a list of txt file in liberman's format and returns
        cut intervals and matrix. Each file is seperated by chr name
        and contains: locus1,locus2,and contact score seperated by tab.
        """

        data = np.zeros([0,4])
        dim = 0
        ## Create empty row, col, value for the matrix

        row = np.array([]).astype("int")
        col = np.array([]).astype("int")
        value = np.array([])
        cut_intervals = []
        resolution = None

        ## for each chr, append the row, col, value to the first one. Extend the dim
        for i in range(0, len(filenameList)):
            if pandas == True:
                chrd = pd.read_csv(filenameList[i], sep = "\t", header=None)
                chrdata = chrd.as_matrix()
            else:
                print "Pandas unavailable. Reading files using numpy (slower).."
                chrdata = np.loadtxt(filenameList[i])

            # define resolution as the median of the difference of the rows
            # in the data table.
            if resolution is None:
                resolution = np.median(np.diff(np.unique(np.sort(chrdata[:,1])))).astype(int)

            chrcol = (chrdata[:, 1] / resolution).astype(int)
            chrrow = (chrdata[:, 0] / resolution).astype(int)

            chrdim = max(max(chrcol), max(chrrow)) + 1
            row = np.concatenate([row, chrrow + dim])
            col = np.concatenate([col, chrcol + dim])
            value = np.concatenate([value, chrdata[:, 2]])
            dim = dim + chrdim
            import ipdb;ipdb.set_trace()
            for _bin in range(chrdim):
                cut_intervals.append((chrnameList[i], _bin * resolution, (_bin + 1) * resolution))

        final_mat = coo_matrix((value, (row, col)), shape=(dim, dim))

        liberman_data = dict(cut_intervals=cut_intervals, matrix=final_mat)
        return liberman_data



matrix = getLibermanBins(['/data/akhtar/bhardwaj/2016_HiC/test/chr1', '/data/akhtar/bhardwaj/2016_HiC/test/chr2'],
                         ['1', '2'])

import ipdb;ipdb.set_trace()