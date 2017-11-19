""" Utility module for command line script select_images
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import os
import numpy as np
import scipy.linalg as la

from cPickle import load

import cv2

def image_colour_distribution(img):
    """ 
        Extract colour distribution parameters.
        
        Parameters
        ----------

        img: array [height, width]
            The RGB image

        Returns
        -------
        
        array[9]
            colour distribution parameters
    """
    
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    m = np.mean(lab.reshape(-1, 3), axis=0)
    s = la.cholesky(np.cov(lab.reshape(-1, 3).T))
    del lab
    return np.hstack([ m, s[np.triu_indices(3)]])

def check_cleared(images, model_path=None):
    """ 
        Classify images as cleared or un-cleared based on a GMM.
        
        Parameters
        ----------

        images: list
            The RGB images
            
        model_path: str
            Path to the damp of GMM

        Returns
        -------
        
        list
            True if the corresponding image is classified as cleared.
    """
    if model_path is None:
        return np.zeros_like(images, dtype=bool)
        
    if len(images) == 0:
        return []
        
    X = np.asarray([image_colour_distribution(img) for img in images])
    
    assert(os.path.exists(model_path))

    model, mu, sig, gcl = load(open(model_path))
        
    labels = model.predict((X - mu)/sig)
    
    return labels == gcl
            
