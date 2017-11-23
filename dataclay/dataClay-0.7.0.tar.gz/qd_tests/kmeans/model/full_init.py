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
        dic = dict()

        for x in enumerate(self.points):
            bestmukey = min([(i[0], np.linalg.norm(x[1] - mu[i[0]]))
                             for i in enumerate(mu)], key=lambda t: t[1])[0]
            if bestmukey not in dic:
                dic[bestmukey] = [x[0] + self.base_index]
            else:
                dic[bestmukey].append(x[0] + self.base_index)
        return dic

    @task(returns=dict)
    @dclayMethod(clusters="anything", return_="anything")
    def partial_sum(self, clusters):
        dic = {}
        for i in clusters:
            p_idx = np.array(clusters[i]) - self.base_index
            dic[i] = (len(p_idx), np.sum(self.points[p_idx], axis=0))
        return dic

    @dclayMethod(return_=int)
    def __len__(self):
        return len(self.points)

    @dclayMethod(idx="anything", return_="anything")
    def __getitem__(self, idx):
        """This class expects `idx` to be a list or an array of indexes.
        Otherwise, performance will suffer *a lot*."""
        return self.points[idx]

    @dclayMethod(return_="anything", _local=True)
    def __iter__(self):
        # Note that the following cannot be serialized, hence the `_local` flag.
        return iter(self.points)


# TODO: this may be better to derive from GenericSplit... or maybe not. Think about that
class SplitBoard(StorageObject):
    """
    @ClassField fragments list<KMeans.Fragment>
    @ClassField storage_location anything
    """

    @dclayMethod(fragments="python.list[KMeans.Fragment]", storage_location="anything")
    def __init__(self, fragments, storage_location):
        self.fragments = fragments
        self.storage_location = storage_location

    @task(returns=list)
    @dclayMethod(mu="anything", return_="anything")
    def cluster_points(self, mu):
        ret = list()
        # This has good performance because of the (guaranteed) fragment locality
        for frag in self.fragments:
            dic = dict()
            for x in enumerate(frag.points):
                bestmukey = min([(i[0], np.linalg.norm(x[1] - mu[i[0]]))
                                 for i in enumerate(mu)], key=lambda t: t[1])[0]
                if bestmukey not in dic:
                    dic[bestmukey] = [x[0] + frag.base_index]
                else:
                    dic[bestmukey].append(x[0] + frag.base_index)
            ret.append(dic)
        return ret

    @task(returns=dict)
    @dclayMethod(cluster_list="anything", return_="anything")
    def partial_sum(self, cluster_list):
        dic = {}
        for clusters, fragment in zip(cluster_list, self.fragments):
            for i in clusters:
                p_idx = np.array(clusters[i]) - fragment.base_index

                try:
                    old_idx, old_sum = dic[i]
                except KeyError:
                    # First!
                    dic[i] = (len(p_idx), np.sum(fragment.points[p_idx], axis=0))
                else:
                    # Accumulate
                    dic[i] = (
                        old_idx + len(p_idx),
                        old_sum + np.sum(fragment.points[p_idx], axis=0)
                    )

        return dic

    @dclayMethod(_local=True)
    def enumerate(self):
        """Local-only iteration procedure."""
        from itertools import chain
        idx = chain(
            xrange(f.base_index, f.base_index + len(f))
            for f in self.fragments
        )

        return zip(idx, chain(self.fragments))


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

        exec_envs = cycle(runtime.get_execution_environments_info().keys())

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
            fragment.make_persistent(dest_ee_id=exec_envs.next())
            self.fragments.append(fragment)

        remain = n_points % self.points_per_fragment
        if remain:
            np.random.seed(base_seed + i + 1)
            fragment = Fragment(
                dim=self.dim,
                points=np.random.random([remain, self.dim]),
                base_index=i * self.points_per_fragment
            )
            fragment.make_persistent(dest_ee_id=exec_envs.next())
            self.fragments.append(fragment)

    @dclayMethod(return_="list<storageobject>")
    def get_chunks(self):
        return self.fragments

    @dclayMethod(return_=int)
    def __len__(self):
        return self.n_points

    @dclayMethod(idx=int, return_="anything")
    def __getitem__(self, idx):
        try:
            idx = int(idx)
        except ValueError:
            raise TypeError("Require an integer index")

        if idx >= self.n_points or idx < 0:
            raise IndexError("This board only supports indexes in the range [0, %d)" % self.n_points)

        fragment = idx // self.points_per_fragment
        sub_idx = idx % self.points_per_fragment

        return self.fragments[fragment].points[sub_idx]
