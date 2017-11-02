from strpy.bobo.classification import linearsvm
import numpy as np
import scipy.linalg
import sklearn.decomposition
from strpy.bobo.util import quietprint


def pca(trainset, n_components, features=None, fractionOfImages=1, fractionOfDescriptors=1):
    """Principal component analysis on an RDD, with optional features applied"""
    
    # collect sampled set of training set, compute features, collect locally
    if features is not None:
        data = (trainset.sample(withReplacement=False, fraction=fractionOfImages)  # sample small fraction of images
                        .map(features) # feature extraction within bounding box 
                        .flatMap(lambda x: x)  # explode all descriptors into an RDD of SIFT vectors
                        .sample(withReplacement=False, fraction=fractionOfDescriptors)  # sample small fraction of images
                        .collect())  # Collect locally for in-memory PCA
    else:
        data = trainset.collect()
        
    # Principal Component Analysis
    PCA = sklearn.decomposition.PCA(n_components)
    quietprint('[janus.reduction.pca]: Computing %d-d PCA on training set %d x %d' % (n_components, len(data), len(data[0])))
    PCA.fit(data)  # data = (n_samples x n_features) array 

    # Return PCA object (PCA.transform(x) will project features)
    return PCA



    
