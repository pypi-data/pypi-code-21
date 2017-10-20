import numpy as np
from itertools import product
from sklearn.utils.linear_assignment_ import linear_assignment
from bobo.geometry import sqdist
from bobo.util import ndmin

class kmeans(object):
    def __init__(self):
        self._clusters = None
        
    def __repr__(self):
        if self._istrained():
            c = np.array(self._clusters.centers)
            return '<janus.cluster.kmeans: dim=%d, clusters=%d>' % (c.shape[1], c.shape[0])
        else:
            return '<janus.cluster.kmeans: untrained>'

    def _istrained(self):
        return self._clusters is not None
            
    def train(self, data, clusters=16, maxIterations=20, runs=30, initialization_mode="random", seed=None):
        """Wrapper for Spark MLIB clustering: http://spark.apache.org/docs/latest/mllib-clustering.html"""
    
        # K-Means clustering!
        # assume that the data is an RDD of numpy 1D float arrays defining observations
        from pyspark.mllib.clustering import KMeans
        self._clusters = KMeans.train(data, clusters, maxIterations, runs, initializationMode=initialization_mode, seed=seed)
    
        # Export cluster centers as list of numpy arrays
        return self

    def centers(self):
        """ return numpy array of cluster centers """
        return self._clusters.centers if self._istrained() else None
    
    def assign(self, newdata):
        """ cluster index assignment (data -> cluster) - greedy matching, newdata must be observations x dimensions numpy array"""
        return np.array([self._clusters.predict(x) for x in newdata]).flatten() if self._istrained() else None

    
    def sqnorm(self, newdata):
        """ newdata must be observations x dimensions numpy array"""        
        return np.array([np.square(x - self._clusters.centers[self._clusters.predict(x)]) for x in newdata]) if self._istrained() else None

    def sqdist(self, newdata):
        """ square distance from observations to all clusters"""
        return sqdist(newdata, self.centers())
        
    def clusterassign(self, newdata):
        """ data index assignment (cluster -> data) - Bipartite matching of each cluster center to best data """
        D = sqdist(self.centers(), newdata)
        return linear_assignment(D)[:,1].flatten()   # cluster -> data assignment

    def greedyclusterassign(self, newdata):
        """ data index assignment (cluster -> data) - greedy matching of each cluster center to best data """
        D = sqdist(self.centers(), newdata)
        k_asgn = []
        for i in range(D.shape[0]):
            (u,v) = ndmin(D)
            D[u,:] = np.inf
            D[:,v] = np.inf
            k_asgn.append( (u,v) )
        #k_asgn = sorted(k_asgn, key=lambda x: x[0])
        k_asgn = [x[1] for x in k_asgn]            
        return k_asgn
        
