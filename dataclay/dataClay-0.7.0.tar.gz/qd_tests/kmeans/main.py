import sys

from dataclay.api import is_initialized
import time

assert is_initialized() is True, "This main.py is expected to be executed through COMPSs, " \
                                 "which should initialize the system"

from KMeans import Board
from pycompss.api.task import task
from pycompss.api.parameter import INOUT

import numpy as np

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'


def mergeReduce(function, data):
    """ Apply function cumulatively to the items of data,
        from left to right in binary tree structure, so as to
        reduce the data to a single value.
    :param function: function to apply to reduce data
    :param data: List of items to be reduced
    :return: result of reduce the data to a single value
    """
    from collections import deque
    q = deque(xrange(len(data)))
    while len(q):
        x = q.popleft()
        if len(q):
            y = q.popleft()
            data[x] = function(data[x], data[y])
            q.append(x)
        else:
            return data[x]


@task(returns=dict, priority=True)
def reduceCentersTask(a, b):
    for key in b:
        if key not in a:
            a[key] = b[key]
        else:
            a[key] = (a[key][0] + b[key][0], a[key][1] + b[key][1])
    return a


def has_converged(mu, oldmu, epsilon, iter, maxIterations):
    print "iter: " + str(iter)
    print "maxIterations: " + str(maxIterations)
    if oldmu != []:
        if iter < maxIterations:
            aux = [np.linalg.norm(oldmu[i] - mu[i]) for i in range(len(mu))]
            distancia = sum(aux)
            if distancia < epsilon * epsilon:
                print "Distancia_T: " + str(distancia)
                return True
            else:
                print "Distancia_F: " + str(distancia)
                return False
        else:
            # detencion pq se ha alcanzado el maximo de iteraciones
            return True


@task(returns=dict)
def cluster_points_partial(fragments, mu):
    from collections import defaultdict
    dic = defaultdict(list)

    for XP in fragments:
        frag_cluster = XP.cluster_points(mu)

        for k, v in frag_cluster.iteritems():
            dic[k].extend(v)

    return dic


@task(returns=dict)
def partial_sum(fragments, clusters):
    from collections import defaultdict
    dic = defaultdict(lambda: (0, 0))

    for XP in fragments:
        for i, point_list in clusters.iteritems():
            last_len, last_sum = dic[i]
            dic[i] = (last_len + len(point_list),
                      np.sum(XP[point_list], axis=0))

    # Don't want to serialize the lambda of defaultdict
    return dict(dic)


def init_random(dim, k):
    np.random.seed(5)
    return np.random.random([k, dim])


def kmeans_frag(numV, k, dim, epsilon, maxIterations, numFrag):
    from pycompss.api.api import compss_wait_on
    size = numV // numFrag  # points per fragment, I assume, and I hope that the division is exact

    startTime = time.time()
    X = Board(dim, size)

    # Initialize locally, make all the fragments persistents, and then persist the board itself
    X.init_random(numV, 5)  # starting seed to match PyCOMPSs original generation
    X.make_persistent()

    mu = list(init_random(dim, k))  # consistency, mu is a list

    print "Points generation Time {} (s)".format(time.time() - startTime)

    oldmu = []
    n = 0
    startTime = time.time()
    while not has_converged(mu, oldmu, epsilon, n, maxIterations):
        oldmu = mu

        partialResult = list()

        for block in X.split():
            cluster = cluster_points_partial(block, mu)
            partialResult.append(partial_sum(block, cluster))

        mu = mergeReduce(reduceCentersTask, partialResult)
        mu = compss_wait_on(mu)
        mu = [mu_c[1] / mu_c[0] for mu_c in mu.values()]
        while len(mu) < k:
            indP = np.random.randint(0, size)
            indF = np.random.randint(0, numFrag)
            mu.append(X[indF][indP])
        mu = np.array(mu)
        n += 1
    print "Kmeans Time {} (s)".format(time.time() - startTime)
    return (n, mu)


if __name__ == "__main__":
    print " # Start KMeans main program"

    numV = int(sys.argv[1])
    dim = int(sys.argv[2])
    k = int(sys.argv[3])
    numFrag = int(sys.argv[4])

    print
    print "Parameters:"
    print "###########"
    print "# numV:    %d" % numV
    print "# dim:     %d" % dim
    print "# k:       %d" % k
    print "# numFrag: %d" % numFrag
    print "###########"
    print

    startTime = time.time()
    result = kmeans_frag(numV, k, dim, 1e-4, 10, numFrag)
    print "Elapsed Time {} (s)".format(time.time() - startTime)
    print result

    print "\n ** Finished **"
