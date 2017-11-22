from dataclay import dclayMethod
from dataclay.contrib.collections import SplittableCollectionMixin
from dataclay.contrib.dummy_pycompss import task

from storage.api import StorageObject
import numpy as np


class Fragment(StorageObject):
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


class Board(StorageObject, SplittableCollectionMixin):
    """
    @ClassField fragments list<KMeans.Fragment>
    @ClassField dim int
    @ClassField n_points int
    @ClassField points_per_fragment int
    """

    @dclayMethod(dim=int, points_per_fragment=int)
    def __init__(self, dim, points_per_fragment):
        self.dim = dim
        self.fragments = list()
        self.n_points = 0

        # Model programmer stuff, not application stuff, not sure where to put this
        self.points_per_fragment = points_per_fragment

    @dclayMethod(n_points=int, base_seed=int)
    def init_random(self, n_points, base_seed):
        self.n_points = n_points

        from dataclay import runtime
        from itertools import cycle

        execution_environments = cycle(runtime.get_execution_environments_info().keys())

        i = 0  # Corner-case: single non-full fragment
        for i in range(n_points // self.points_per_fragment):
            np.random.seed(base_seed + i)
            fragment = Fragment(
                dim=self.dim,
                # Misc note about entropy, seeds and PyCOMPSs implementation: #
                ###############################################################
                # PyCOMPSs initializes with the seed and then iterates all the
                # points_per_fragment-like variable in order to build the
                # fragment. This results in several calls to np.random.random
                # (but all of them are "vector" calls).
                #
                # Here I propose a single "matrix" call, resulting in a
                # different seed per call of random.random. It seems that the
                # entropy usage of numpy is consistent and the preliminary
                # tests indicate that the implementation is equivalent
                # (although I am not sure that this is a spec on the
                # numpy.random behaviour).
                points=np.random.random([self.points_per_fragment, self.dim]),
                base_index=i * self.points_per_fragment
            )
            fragment.make_persistent(dest_backend_id=execution_environments.next())
            self.fragments.append(fragment)

        remain = n_points % self.points_per_fragment
        if remain:
            np.random.seed(base_seed + i + 1)
            fragment = Fragment(
                dim=self.dim,
                points=np.random.random([remain, self.dim]),
                base_index=i * self.points_per_fragment
            )
            fragment.make_persistent(dest_backend_id=execution_environments.next())
            self.fragments.append(fragment)
