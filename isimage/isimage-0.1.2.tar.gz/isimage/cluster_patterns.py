""" Algorithms for clustring exp[ression patterns
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import numpy as np

import scipy.stats as st
import scipy.linalg as la
import scipy.optimize as opt

import cv2

from adaptive_affinity_propagation_ import AdaptiveAffinityPropagation

import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch

def ssdA_g(param, R, T, x, y, dx, verbose=True):
    """ 
        Compute sum of squared differences between two images under 
        linear-affine transformation and its gradient wrt the transofrmation
        parameters.
        
        Parameters
        ----------
            
        param: array[6]
            Parameters of linear-affine transformation. 
            param[:4] - Linear transform matrix
            param[4:] - Shift vector
            
        R: array [height, width]
            Reference image

        T: array [height, width]
            Template image

        x: array [height, width]
            rescaled x coordiantes

        y: array [height, width]
            rescaled y coordinates
        
        dx: float
            difference in x and y coordinates
        
        verbose: Bool, optional, default: True
            Visualize computation if True.
        
        Returns
        -------
        
        ssd: float
            Sum of squared difference.
            
        penalty: float
            Regularization penalty to avoid degenerate scaling.
        
        D(ssd): array[6] 
            ssd gradient wrt to transformation parameters.
            
        D(penalty): array[6] 
            penalty gradient wrt to transformation parameters.
    """
    alpha = 1.e+0
    
    A = param[:4].reshape(2, 2)
    b = param[4:]

    #transform template
    T_ = cv2.warpAffine(T, np.hstack([A, b.reshape(-1, 1)/dx]), R.shape[::-1])

    #gradient of transformed template wrt x and y
    dTdx = cv2.Scharr(T_, cv2.CV_64F, 1, 0)*(1./(16*2*dx))
    dTdy = cv2.Scharr(T_, cv2.CV_64F, 0, 1)*(1./(16*2*dx))

    diff = T_ - R
    dTdx *= diff
    dTdy *= diff
        
    #penalty    
    DA = la.det(A)
    penalty = np.log(DA**2)
    dP = 4*penalty/DA

    ret = (      np.sum(diff**2)*dx**2
            , alpha*penalty**2
            , -2*np.array([
                  np.sum((dTdx*x)[2:-2, 2:-2]), np.sum((dTdx*y)[2:-2, 2:-2])
                , np.sum((dTdy*x)[2:-2, 2:-2]), np.sum((dTdy*y)[2:-2, 2:-2])
                , np.sum( dTdx[2:-2, 2:-2]),     np.sum( dTdy[2:-2, 2:-2])])*dx**2
            , alpha*np.array([
                   dP*A[1, 1], -dP*A[1, 0]
                 ,-dP*A[0, 1],  dP*A[0, 0]
                 , 0         ,     0        ]))  

    if verbose:
        plt.figure()
        ax = plt.subplot(221)
        ax.imshow(R)
        
        ax = plt.subplot(222)
        ax.imshow(T_)
        
        ax = plt.subplot(223)
        t_ = diff**2
        ax.imshow(1 - np.concatenate([np.minimum(1, R[:, :, np.newaxis]), np.zeros_like(R)[:, :, np.newaxis], np.minimum(1, T_[:, :, np.newaxis])], axis=-1))
        
        ax = plt.subplot(224)
        ax.imshow(t_)
        
        print A, b, ret, alpha * penalty**2

    return ret

def align_images(i1, i2, dry_run=False, verbose=False, x0 = np.array([1, 0, 0, 1, 0, 0], dtype=float)):
    """ 
        Align images by minimizing sum of squared differences under 
        linear-affine transformation.
        
        Parameters
        ----------
            
        i1: array [height1, width1]
            Reference image

        i2: array [height2, width2]
            Template image
            
        dry_run: Bool, optional, default: False
            Do not perform minimization step if True
        
        verbose: Bool, optional, default: False
            Plot alignment result if True
        
        x0: array[6], optional, default: [1, 0, 0, 1, 0, 0]
            Initial linear-affine transformation parameters.
            Default identity linear transform and zero shift.

        
        Returns
        -------
        
        float
            Minimum penalized sum of squared difference acheived.
    """
    
    def obj_fun(param):
        f, fp, g, gp = ssdA_g(param, img, img2, x_, y_, dx, verbose=False)
        return (f + fp, g + gp)
        
    #rescale template image to match reference image size.
    img = np.copy(i1)
    img2 = cv2.warpAffine(i2, np.hstack([np.diag(np.float32(i1.shape[::-1])/np.float32(i2.shape[::-1])), np.zeros((2, 1))]), img.shape[::-1])

    #align in just one step
    max_size = 100
    min_size = 100

    images = []
    if min(img.shape + img2.shape) <= max_size:
        images += [(img.copy(), img2.copy())]
    while min(img.shape + img2.shape) > min_size: # 50:0
        img = cv2.pyrDown(img)
        img2 = cv2.pyrDown(img2)
        if min(img.shape + img2.shape) <= max_size:
            images += [(img.copy(), img2.copy())]
    
    #align rescaled images progressively from min_size to max_size
    res = (x0,)
    for img, img2 in  images[::-1] : 
        x = np.ones((img.shape[0], 1)).dot(np.arange(img.shape[1]).reshape((1, -1)))
        y = np.arange(img.shape[0]).reshape((-1, 1)).dot(np.ones((1, img.shape[1])))

        dx = 1./max([x[-1, -1], y[-1, -1]])

        x_ = x*dx
        y_ = y*dx

        if verbose:
            ssdA_g(x0, img, img2, x_, y_, dx, verbose=True)
        
        if not dry_run:
            repeat = 1
            count = 0
            vals = []
            #run minimization from sligthly different starting points 
            #until valid minimum is found
            while repeat > 0 and count < 100:    
                count += 1    
                res = opt.fmin_l_bfgs_b(  func = obj_fun, x0 = x0 + np.random.randn(6)*.05
                                , fprime=None, approx_grad=False, factr=1.e1, pgtol=1.e-5)
                ok = res[2]['warnflag'] == 0
                repeat -= int(ok)
                if ok:
                    vals += [res[:2]]

            x0 = sorted(vals, key=lambda x_: x_[1])[0][0] 
            
    if verbose:
        plt.figure()
        ax = plt.subplot(221)
        ax = plt.imshow(i1)

        ax = plt.subplot(222)
        ax = plt.imshow(i2)

        ax = plt.subplot(223)
        ax = plt.imshow(img)
        
        A = res[0][:4].reshape(2, 2)
        b = res[0][4:]
        ax = plt.subplot(224)
        ax = plt.imshow(cv2.warpAffine(img2, np.hstack([A, b.reshape(-1, 1)/dx]), img.shape[::-1]))
        
        print res
        print dx
    
    return np.sum(ssdA_g(x0, img, img2, x_, y_, dx, verbose=False)[:2])
    
def pattern_distance(img1, img2, flip=True):
    """ 
        Compute distance between the patterns
        
        Parameters
        ----------
            
        img1: array [height1, width1]
            Expression pattern 1

        img2: array [height2, width2]
            Expression pattern 2
        
        flip: Bool, optional, default: True
            After finding the distance between img1 and img2 from repeat 
            computation with mirror image of img1. 
            
        
        Returns
        -------
        
        distance: float
            Dissimilarity between patterns.
    """

    std1, std2 = np.std(img1), np.std(img2)
    if std1 < 1.e-2 or std2 < 1.e-2:
        return np.min([align_images(img1, img2, dry_run=True)
                     , align_images(img2, img1, dry_run=True)])
    
    imgs = [img1]
    for i in range(3):
        imgs += [cv2.flip(imgs[-1].T, 1)]
        
    d1 = [align_images(img, img2, verbose=False) for img in imgs]
    d2 = [align_images(img2, img, verbose=False) for img in imgs]
    dist = min(d1+d2)
    
    if flip and dist > 0:
        dist = min(dist, pattern_distance(img1.T, img2, flip=False))
    
    return dist
    
def cluster_patterns(patterns, max_clusters=None, compute=None):
    """ 
        Cluster expression patterns on similarity
        
        Parameters
        ----------
            
        patterns: list[N]
            A list of expression patterns to cluster. 

        max_clusters: integer, optional, default: None
            The upper bound on number of clusters
        
        compute: IPython.parallel client, optional, default: None
            Client connected to IPython.parallel cluster to parallelise
            computation of dissimilarities between images
            
        
        Returns
        -------

        labels : array [N]
            cluster labels for each pattern

        D : array[N, N]
            Computed similarity matrix
        
        cluster_centers_indices: array [n_clusters]
            index of clusters centers
    """

    if len(patterns) < 2:
        return np.zeros((1,), dtype=int), np.zeros((1,1)), np.zeros((1,), dtype=int)
        
    D = np.zeros((len(patterns), len(patterns)))
    if compute is None:
        for i, img1 in enumerate(patterns):
            for j, img2 in enumerate(patterns[:i]):
                D[i, j] = pattern_distance(img1, img2)
                
    else:
        clen = 3*len(compute)
        pos = zip(*np.tril_indices(D.shape[0], -1))
        result = np.zeros(len(pos))
        for grp in range(len(pos)/clen + 1):
            if len(pos[grp*clen:(grp + 1)*clen]):
                work = [(patterns[i], patterns[j]) for i, j in pos[grp*clen:(grp + 1)*clen]]
                result[grp*clen:(grp + 1)*clen] = compute.map(lambda par: pattern_distance(par[0], par[1]), work).result
                
        D[np.tril_indices(D.shape[0], -1)] = result

    D += D.T
    D_ = np.copy(np.sqrt(D))
    
    D = -1*np.sqrt(D)

    cluster = AdaptiveAffinityPropagation(affinity='precomputed', max_clusters=max_clusters, convergence_iter=100, delay=20) #
    
    labels = cluster.fit_predict(D)

    pval = 0
    if max(labels) > 0:
        p = 8
            
        W1 = np.sum((p*D[np.tril_indices(D.shape[0])])**2)
        W2 = 0
        for l in set(labels):
            W2 += np.sum((p*D[labels==l][:, labels==l][np.tril_indices(len(labels[labels==l]))])**2)
        
        F = 0
        valid = W2 > 0 and len(labels) > 2
        if valid:
            F = ((W1 - W2)/W2)/(((len(labels) - 1)/(len(labels) - 2))*2.**(2./p) - 1)
        
        if len(labels) > 2:
            pval = st.f(p, (len(labels) - 2)*p).sf(F)
        d = -np.min(D[cluster.cluster_centers_indices_, :][:, cluster.cluster_centers_indices_][np.triu_indices(len(cluster.cluster_centers_indices_), 1)])
        
        if (valid and pval > .1) or (d < np.sqrt(.1) and not valid):
            labels = np.zeros_like(labels)
        
    if max(labels) > 0:
        cluster_centers = cluster.cluster_centers_indices_
    else:
        cluster_centers = np.array([np.argmax(np.sum(D, axis=0))])
    
    return labels, D, cluster_centers

