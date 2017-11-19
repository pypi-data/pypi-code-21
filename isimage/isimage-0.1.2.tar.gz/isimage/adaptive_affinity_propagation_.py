""" Algorithm for clustering : Adaptive Affinity propagation 
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: BSD clause 3

import numpy as np
import warnings

from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils import as_float_array
from sklearn.utils import check_random_state
from sklearn.metrics import euclidean_distances

def average_silhouette(I, S):
    """ 
    Computes average Silhouette index 

    Parameters
    ----------

    I: array
        Cluster exemplair indeices

    S: array [n_samples, n_samples]
        Matrix of similarities between points
        
    Returns
    -------
    
    float
        average silhouette index

    """
    
    K = I.size
    
    n_samples = S.shape[0]
    
    D = -S 
    
    if K < 2:
        return 0 
    
    
    a = np.zeros(n_samples)
    b = np.zeros(n_samples)
    b[:] = np.inf
    
    c = np.argmax(S[:, I], axis=1)
    c[I] = np.arange(K)
    for k in range(K):
        ii = np.where(c == k)[0]
        j = np.argmax(np.sum(S[ii[:, np.newaxis], ii], axis=0))
        I[k] = ii[j]
    
    c = np.argmax(S[:, I], axis=1)
    c[I] = np.arange(K)
    
    valid = np.zeros(n_samples, dtype = bool)
    s = np.zeros(n_samples)
    s[:] = 0
    
    for k in range(K):
        ii = np.where(c == k)[0]
        
        a[ii] = 0
        if ii.size > 1:
            a[ii] = (np.sum(D[ii[:, np.newaxis], ii], axis=0) 
                    - np.diag(D[ii[:, np.newaxis], ii]))/(ii.size - 1)
            valid[ii] = True
        
        io = np.where(c != k)[0]
        b[io] = np.minimum(b[io], np.mean(D[ii[:, np.newaxis], io], axis=0))
    
    s[valid] = ((b - a)/np.maximum(a, b))[valid]
    
    return np.average(s)

def adaptive_affinity_propagation(S, convergence_iter=40, delay=10
    , max_iter=50000, max_damping=0.85, add_noise=1.e-4, max_noise=5.e-4
    , Kmin=2, Kmax=None, copy=True, verbose=False, random_state=None):
    """Perform Adaptive Affinity Propagation Clustering of data

    Parameters
    ----------

    S: array [n_samples, n_samples]
        Matrix of similarities between points

    convergence_iter: int, optional, default: 40
        Number of iterations with no change in the exemplairs
        of estimated clusters to assume the convergence.
        
    delay: int, optional, default: 10
        Number of iterations the convergent state should hold before 
        changing the preference value

    max_iter: int, optional, default: 200
        Maximum number of iterations

    max_damping: float, optional, default: 0.85
        The ceiling of the damping factor in adaptive dumping.

    add_noise: float, optional, default: 1.e-4
        The amount of Gaussian noise in units of std.dev. of similarity 
        values to add to S per iteration.

    max_noise: float, optional, default: 5.e-4
        The maximum total amount of Gaussian noise in units of std.dev. 
        of similarity values to add to S.

    Kmin: int, optional, default: 2
        The minimum number of clusters to look for.

    Kmax: int, optional, default: None
        The maximum number of clusters to look for.

    copy: boolean, optional, default: True
        If copy is False, the affinity matrix is modified inplace by the
        algorithm, for memory efficiency

    verbose: boolean, optional, default: False
        The verbosity level

    Returns
    -------

    cluster_centers_indices: array [n_clusters]
        index of clusters centers

    labels : array [n_samples]
        cluster labels for each point

    Notes
    -----
    TODO: add examples in examples/cluster/plot_affinity_propagation.py.

    References
    ----------
    Brendan J. Frey and Delbert Dueck, "Clustering by Passing Messages
    Between Data Points", Science Feb. 2007
    
    K. Wang, J. Zhang, D. Li, X. Zhang and T. Guo. Adaptive Affinity 
    Propagation Clustering. Acta Automatica Sinica, 33(12):1242-1246, 2007 
    """
    S = as_float_array(S, copy=copy)
    n_samples = S.shape[0]
    damping = .5

    if S.shape[0] != S.shape[1]:
        raise ValueError("S must be a square array (shape=%s)" % repr(S.shape))


    A = np.zeros((n_samples, n_samples))
    R = np.zeros((n_samples, n_samples))  # Initialize messages
    
    if Kmax is None:
        Kmax = np.inf

    # Remove degeneracies
    random_state = check_random_state(random_state)
    S += ((np.finfo(np.double).eps * S + np.finfo(np.double).tiny * 100) *
          random_state.randn(n_samples, n_samples))
    
    # Execute parallel affinity propagation updates
    e = np.zeros((n_samples, convergence_iter))

    ind = np.arange(n_samples)
    
    # adaptive init    
    w2 = convergence_iter/8
    Ks = np.zeros(convergence_iter)
    Kb = np.zeros(convergence_iter)
    
    pm = np.median(S)
    ps = 0.01*pm
    p  =.5*pm
    
    b = 0
    nits = 0
    
    best_I = np.array([0])
    best_sil = -1
    
    lastC = -1
    lastK = n_samples
    let_it_pass = 0
    
    nstd = np.std(S[np.triu_indices(S.shape[0], 1)])
    noise_count = 0
    
    for it in range(max_iter):
        # Place preference on the diagonal of S
        S.flat[::(n_samples + 1)] = p
        
        # Compute responsibilities
        Rold = R.copy()
        AS = A + S

        I = np.argmax(AS, axis=1)
        Y = AS[np.arange(n_samples), I]  

        AS[ind, I[ind]] = - np.finfo(np.double).max

        Y2 = np.max(AS, axis=1)
        R = S - Y[:, np.newaxis]

        R[ind, I[ind]] = S[ind, I[ind]] - Y2[ind]

        R = (1 - damping) * R + damping * Rold  # Damping

        # Compute availabilities
        Aold = A
        Rp = np.maximum(R, 0)
        Rp.flat[::n_samples + 1] = R.flat[::n_samples + 1]

        A = np.sum(Rp, axis=0)[np.newaxis, :] - Rp

        dA = np.diag(A)
        A = np.minimum(A, 0)

        A.flat[::n_samples + 1] = dA

        A = (1 - damping) * A + damping * Aold  # Damping

        # Check for convergence
        ri = it % convergence_iter
        
        E = (np.diag(A) + np.diag(R)) > 0
        e[:, ri] = E
        K = np.sum(E, axis=0)

        # Adaptive
        Ks[ri] = K
        
        if it >= w2 + 1:
            Ksw2 = np.hstack([Ks[min(convergence_iter + ri - w2
                        , convergence_iter):], Ks[max(ri - w2, 0):ri]])
            
            ri_1 = (it - 1) % convergence_iter
            Km_1 = np.mean(np.hstack([Ks[max(ri_1 - w2, 0):ri_1]
                    , Ks[min(convergence_iter + ri_1 - w2, convergence_iter):]]))
            
            decrease = (np.mean(Ksw2) - Km_1) < 0
            constant = np.sum(np.abs(Ksw2[:-1] - Ksw2[-1])) == 0
            Kb[ri] = int(decrease or constant)
            
        if it >= convergence_iter:
            se = np.sum(e, axis=1)
            unconverged = (np.sum((se == convergence_iter) + (se == 0))
                           != n_samples)
            # Scanning p
            if not unconverged and (K > 0):
                Hdown = 1
            else:
                Hdown = 0
                b = 0
                nits = 0
                
            nits += 1
            if Hdown == 1 and nits >= delay:
                lastK = K
                I = np.where(np.diag(A + R) > 0)[0]
                sil = average_silhouette(I, S)
                if sil > best_sil and K <= Kmax:
                    best_sil = sil
                    best_I = I
                
                lastC = it
                
                if verbose:
                    print("Converged at %d clusters after %d iterations, sil = %f." % (K, it, sil))
                
                b += 1
                q = .1*np.sqrt(K + 50)
                p += b*ps/q
                nits = 0
                
                if K <= 2:
                    if verbose:
                        print("K <= 2 after %d iterations." % it)

                    break
            if let_it_pass < 0:
                let_it_pass += 1
            vib = (lastC >= 0 and (it - lastC) > 5*(convergence_iter + delay))
            osc = np.sum(Kb) < 2*convergence_iter/3 and let_it_pass == 0
            if osc or vib:
                if verbose:
                    if osc:
                        print("Oscillations at %f clusters after %d iterations, p = %f." % (damping, it, p))
                    else:
                        print("Vibrations at %f clusters after %d iterations, p = %f." % (damping, it, p))
                    
                lastC = it
                
                damping = min(max_damping, damping + 0.05)
                if osc :
                    let_it_pass = -2*convergence_iter/3
                if damping >= max_damping:
                    if vib and nstd > 0 and np.sqrt(noise_count)*add_noise < max_noise : 
                        S += add_noise*nstd*random_state.randn(n_samples, n_samples)
                        noise_count += 1
                    else:
                        p += ps
                
    else:
        if verbose:
            print("max_iter reached.")
            
    I = best_I 
    K = I.size  # Identify exemplars

    if K > 0:
        
        c = np.argmax(S[:, I], axis=1)
        c[I] = np.arange(K)  # Identify clusters
        # Refine the final set of exemplars and clusters and return results
        for k in range(K):
            ii = np.where(c == k)[0]
            j = np.argmax(np.sum(S[ii[:, np.newaxis], ii], axis=0))
            I[k] = ii[j]
        
        c = np.argmax(S[:, I], axis=1)
        c[I] = np.arange(K)
        labels = I[c]
        # Reduce labels to a sorted, gapless, list
        cluster_centers_indices = np.unique(labels)
        labels = np.searchsorted(cluster_centers_indices, labels)
    else:
        labels = np.empty((n_samples, 1))
        cluster_centers_indices = None
        labels.fill(np.nan)

    return cluster_centers_indices, labels


###############################################################################

class AdaptiveAffinityPropagation(BaseEstimator, ClusterMixin):
    """Perform Affinity Propagation Clustering of data

    Parameters
    ----------
    convergence_iter: int, optional, default: 40
        Number of iterations with no change in the exemplairs
        of estimated clusters to assume the convergence.
        
    delay: int, optional, default: 10
        Number of iterations the convergent state should hold before 
        changing the preference value

    max_damping: float, optional, default: 0.85
        The ceiling of the damping factor in adaptive dumping.

    add_noise: float, optional, default: 1.e-4
        The amount of Gaussian noise in units of std.dev. of similarity 
        values to add to S per iteration.

    max_noise: float, optional, default: 5.e-4
        The maximum total amount of Gaussian noise in units of std.dev. 
        of similarity values to add to S.

    max_iter: int, optional, default: 200
        Maximum number of iterations

    min_clusters: int, optional, default: 2
        The minimum number of clusters to look for.

    max_clusters: int, optional, default: None
        The maximum number of clusters to look for.

    copy: boolean, optional, default: True
        If copy is False, the affinity matrix is modified inplace by the
        algorithm, for memory efficiency

    affinity: string, optional, default=``euclidean``
        Which affinity to use. At the moment ``precomputed`` and
        ``euclidean`` are supported. ``euclidean`` uses the
        negative squared euclidean distance between points.

    verbose: boolean, optional, default: False
        Whether to be verbose.


    Attributes
    ----------
    `cluster_centers_indices_` : array, [n_clusters]
        Indices of cluster centers

    `labels_` : array, [n_samples]
        Labels of each point

    `affinity_matrix_` : array-like, [n_samples, n_samples]
        Stores the affinity matrix used in ``fit``.

    Notes
    -----
    TODO: add examples in examples/cluster/plot_affinity_propagation.py.

    The algorithmic complexity of affinity propagation is quadratic
    in the number of points.

    References
    ----------

    Brendan J. Frey and Delbert Dueck, "Clustering by Passing Messages
    Between Data Points", Science Feb. 2007
    
    K. Wang, J. Zhang, D. Li, X. Zhang and T. Guo. Adaptive Affinity 
    Propagation Clustering. Acta Automatica Sinica, 33(12):1242-1246, 2007 
    """

    def __init__(self, convergence_iter=40, delay=10, max_damping=.95
                , add_noise=1.e-4, max_noise=5.e-4, max_iter=50000
                , min_clusters=2, max_clusters=None, copy=True
                , affinity='euclidean', verbose=False, random_state=None):

        self.convergence_iter = convergence_iter
        self.delay = delay
        self.max_damping = max_damping
        self.add_noise = add_noise
        self.max_noise = max_noise
        self.max_iter = max_iter
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.copy = copy
        self.verbose = verbose
        self.affinity = affinity
        self.random_state = random_state

    @property
    def _pairwise(self):
        return self.affinity is "precomputed"

    def fit(self, X):
        """ Create affinity matrix from negative euclidean distances, then
        apply adaptive affinity propagation clustering.

        Parameters
        ----------

        X: array [n_samples, n_features] or [n_samples, n_samples]
            Data matrix or, if affinity is ``precomputed``, matrix of
            similarities / affinities.
        """

        if X.shape[0] == X.shape[1] and not self._pairwise:
            warnings.warn("The API of AffinityPropagation has changed."
                          "Now ``fit`` constructs an affinity matrix from the"
                          " data. To use a custom affinity matrix, set "
                          "``affinity=precomputed``.")
        if self.affinity is "precomputed":
            self.affinity_matrix_ = X
        elif self.affinity is "euclidean":
            self.affinity_matrix_ = -euclidean_distances(X, squared=True)
        else:
            raise ValueError("Affinity must be 'precomputed' or "
                             "'euclidean'. Got %s instead"
                             % str(self.affinity))

        self.cluster_centers_indices_, self.labels_ = adaptive_affinity_propagation(
            self.affinity_matrix_
            , convergence_iter=self.convergence_iter
            , delay=self.delay
            , max_damping=self.max_damping
            , add_noise=self.add_noise
            , max_noise=self.max_noise
            , max_iter=self.max_iter
            , Kmin=self.min_clusters
            , Kmax=self.max_clusters
            , copy=self.copy
            , verbose=self.verbose
            , random_state=self.random_state)
        return self

