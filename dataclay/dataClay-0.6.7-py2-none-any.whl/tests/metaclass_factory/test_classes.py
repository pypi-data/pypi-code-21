from dataclay import dclayMethod
from dataclay.contrib.dummy_pycompss import task

from storage.api import StorageObject
import numpy as np


# Based on Fragment of Kmeans qd_tests
class TestClass(StorageObject):
    """
    @ClassField points anything
    @ClassField dim int
    @ClassField base_index int
    """
    @dclayMethod(dim=int, points="anything", base_index=int)
    def __init__(self, dim, points, base_index):
        self.dim = dim
        self.points = points
        self.base_index = base_index

    @task(returns=dict)
    @dclayMethod(mu="anything", return_="anything")
    def cluster_points(self, mu):
        base_idx = self.base_index
        dic = dict()

        for x in enumerate(self.points):
            bestmukey = min([(i[0], np.linalg.norm(x[1] - mu[i[0]]))
                             for i in enumerate(mu)], key=lambda t: t[1])[0]
            if bestmukey not in dic:
                dic[bestmukey] = [x[0] + base_idx]
            else:
                dic[bestmukey].append(x[0] + base_idx)
        return dic

    @task(returns=dict)
    @dclayMethod(mu="anything", return_="anything")
    def cluster_points_cached(self, mu):
        dic = dict()
        base_idx = self.base_index

        for x in enumerate(self.points):
            bestmukey = min([(i[0], np.linalg.norm(x[1] - mu[i[0]]))
                             for i in enumerate(mu)], key=lambda t: t[1])[0]
            if bestmukey not in dic:
                dic[bestmukey] = [x[0] + base_idx]
            else:
                dic[bestmukey].append(x[0] + base_idx)
        return dic

    @task(returns=dict)
    @dclayMethod(clusters="anything", return_="anything")
    def partial_sum(self, clusters):
        base_idx = self.base_index
        points = self.points
        dic = {}
        for i in clusters:
            p_idx = np.array(clusters[i]) - base_idx
            dic[i] = (len(p_idx), np.sum(points[p_idx], axis=0))
        return dic

    @dclayMethod(idx="anything", return_="anything")
    def __getitem__(self, idx):
        """This class expects `idx` to be a list or an array of indexes.
        Otherwise, performance will suffer *a lot*."""
        return self.points[idx]
