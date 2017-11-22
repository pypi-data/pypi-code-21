from dataclay.api import init

init("./storage.properties")

from KMeans.model.classes import Board

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


def init_random(dim, k, seed):
    np.random.seed(seed)
    m = np.random.random((k, dim))
    return m


def kmeans_frag(numV, k, dim, epsilon, maxIterations, numFrag):
    size = numV // numFrag  # points per fragment, I assume, and I hope that the division is exact

    startTime = time.time()
    X = Board(dim, size)

    # Initialize locally, make all the fragments persistents, and then persist the board itself
    X.init_random(numV, 5)  # starting seed to match PyCOMPSs original generation
    X.make_persistent()

    mu = list(init_random(dim, k, 5))  # consistency, mu is a list

    print "Points generation Time {} (s)".format(time.time() - startTime)

    oldmu = []
    n = 0
    startTime = time.time()
    while not has_converged(mu, oldmu, epsilon, n, maxIterations):
        oldmu = mu

        partialResult = list()
        # clusters = list()
        for f, frag in enumerate(X.fragments):
            cluster = frag.cluster_points(mu)
            # clusters.append(cluster)
            partialResult.append(frag.partial_sum(cluster))

        mu = mergeReduce(reduceCentersTask, partialResult)
        mu = [mu[c][1] / mu[c][0] for c in mu]
        while len(mu) < k:
            indP = np.random.randint(0, size)
            indF = np.random.randint(0, numFrag)
            # not-so-subtle bug here for dataClay implementation of Board --fixme maybe?
            mu.append(X[indF][indP])
        n += 1

    print "Kmeans Time {} (s)".format(time.time() - startTime)
    return (n, mu)

if __name__ == "__main__":
    import sys
    import time
    from dataclay.api import finish

    numV = int(sys.argv[1])
    dim = int(sys.argv[2])
    k = int(sys.argv[3])
    numFrag = int(sys.argv[4])

    startTime = time.time()
    result = kmeans_frag(numV, k, dim, 1e-4, 10, numFrag)
    print "Ellapsed Time {} (s)".format(time.time() - startTime)
    finish()
