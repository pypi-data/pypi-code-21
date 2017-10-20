#
#  tsne.py
#
# Implementation of t-SNE in Python. The implementation was tested on Python 2.7.10, and it requires a working
# installation of NumPy. The implementation comes with an example on the MNIST dataset. In order to plot the
# results of this example, a working installation of matplotlib is required.
#
# The example can be run by executing: `ipython tsne.py`
#
#
#  Created by Laurens van der Maaten on 20-12-08.
#  Copyright (c) 2008 Tilburg University. All rights reserved.

import numpy as np
import scipy.spatial


def Hbeta(D=np.array([]), beta=1.0):
    """Compute the perplexity and the P-row for a specific value of the precision of a Gaussian distribution."""

    # Compute P-row and corresponding perplexity
    P=np.exp(-D.copy() * beta)
    sumP=sum(P)
    H=np.log(sumP) + beta * np.sum(D * P) / sumP
    P=P / sumP
    return H, P


def x2p(X=np.array([]), tol=1e-5, perplexity=30.0):
    """Performs a binary search to get P-values in such a way that each conditional Gaussian has the same perplexity."""

    # Initialize some variables
    print "Computing pairwise distances..."
    (n, d)=X.shape
    #sum_X=np.sum(np.square(X), 1)
    #D=np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
    D=scipy.spatial.distance.squareform(scipy.spatial.distance.pdist(X))
    D /= D.max()
    P=np.zeros((n, n))
    beta=np.ones((n, 1))
    logU=np.log(perplexity)

    # Loop over all datapoints
    for i in range(n):

        # Print progress
        if i % 500 == 0:
            print "Computing P-values for point ", i, " of ", n, "..."

        # Compute the Gaussian kernel and entropy for the current precision
        betamin=-np.inf
        betamax= np.inf
        Di=D[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))]
        (H, thisP)=Hbeta(Di, beta[i])

        # Evaluate whether the perplexity is within tolerance
        Hdiff=H - logU
        tries=0
        while np.abs(Hdiff) > tol and tries < 50:

            # If not, increase or decrease precision
            if Hdiff > 0:
                betamin=beta[i].copy()
                if betamax == np.inf or betamax == -np.inf:
                    beta[i]=beta[i] * 2
                else:
                    beta[i]=(beta[i] + betamax) / 2
            else:
                betamax=beta[i].copy()
                if betamin == np.inf or betamin == -np.inf:
                    beta[i]=beta[i] / 2
                else:
                    beta[i]=(beta[i] + betamin) / 2

            # Recompute the values
            (H, thisP)=Hbeta(Di, beta[i])
            Hdiff=H - logU
            tries=tries + 1

        # Set the final row of P
        P[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))]=thisP

    # Return final P-matrix
    print "Mean value of sigma: ", np.mean(np.sqrt(1 / beta))
    return P


def tsne_from_P(P, no_dims=2, max_iter=1000):
    n = P.shape[0]
    print('P.shape = ' + str(P.shape))
    print('n = ' + str(n))
    initial_momentum=0.5
    final_momentum=0.8
    eta=500
    min_gain=0.01
    Y=np.random.randn(n, no_dims).astype(np.float32)

    dY=np.zeros((n, no_dims)).astype(np.float32)
    iY=np.zeros((n, no_dims)).astype(np.float32)
    gains=np.ones((n, no_dims)).astype(np.float32)

    P=P + np.transpose(P)
    P=P / np.sum(P)
    P=P * 4  # early exaggeration
    P=np.maximum(P, 1e-12)

    # Run iterations
    for iter in range(max_iter):
        # Compute pairwise affinities
        sum_Y=np.sum(np.square(Y), 1)
        num=1 / (1 + np.add(np.add(-2 * np.dot(Y, Y.T), sum_Y).T, sum_Y))
        num[range(n), range(n)]=0
        Q=num / np.sum(num)
        Q=np.maximum(Q, 1e-12)

        # Compute gradient
        PQ=P - Q
        for i in range(n):
            dY[i,:]=np.sum(np.tile(PQ[:,i] * num[:,i], (no_dims, 1)).T * (Y[i,:] - Y), 0)

        # Perform the update
        if iter < 20:
            momentum=initial_momentum
        else:
            momentum=final_momentum
        gains=(gains + 0.2) * ((dY > 0) != (iY > 0)) + (gains * 0.8) * ((dY > 0) == (iY > 0))
        gains[gains < min_gain]=min_gain
        iY=momentum * iY - eta * (gains * dY)
        Y=Y + iY
        Y=Y - np.tile(np.mean(Y, 0), (n, 1))

        # Compute current value of cost function
        if (iter + 1) % 10 == 0:
            C=np.sum(P * np.log(P / Q))
            print "Iteration ", (iter + 1), ": error is ", C

        if iter == 100:
            P = P / 4  # stop lying about P

    # Return solution
    return Y


def tsne(X=np.array([]), no_dims=2, perplexity=30.0, max_iter=1000):
    """Runs t-SNE on the dataset in the NxD array X to reduce its dimensionality to no_dims dimensions.
    The syntaxis of the function is Y=tsne.tsne(X, no_dims, perplexity), where X is an NxD NumPy array."""

    # Check inputs
    if isinstance(no_dims, float):
        print "Error: array X should have type float."
        return -1
    if round(no_dims) != no_dims:
        print "Error: number of dimensions should be an integer."
        return -1

    # Compute P-values
    P=x2p(X, 1e-5, perplexity)
    return tsne_from_P(P, no_dims, max_iter)
