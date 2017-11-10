# -*- coding: utf-8 -*-
import numpy as np

def getpathdistance(path, points):
    """
    Check if points are on path and give the distance along the path.
    
    :type path: np.ndarray(n x 2)
    :param path: Edge points of the path which should be linearly connected.
    :type points: np.ndarray(N x 2)
    :param points: Point coordinates to be checked if they are on the path. If true, the distance along the path is computed!
    :returns: Bool-array: True for points on path, False else; Array of distances for points which are on the path
    """
    
    #check if path and points are in correct shape
    path = np.array(path)
    points = np.array(points)
    if not path.shape[1]==2:
        raise ValueError('path must be a numpy array of shape N x 2')
    if not points.shape[1]==2:
        raise ValueError('points must be a numpy array of shape N x 2')
        
    #path vectors
    vecs = np.diff(pathgoalpoints,axis=0)
    
    onpatharray = []
    distances = np.array([])
    for p in points:
        for i in range(len(vecs)):
            #check if p is aligned with vecs
            aligned = np.abs(np.cross(p-path[i],vecs[i]))<1e-6
            #check if p is inbetween vecs start and end point by projecting
            projection = np.dot(p-path[i],vecs[i]/np.linalg.norm(vecs[i]))
            inbetween = -1e-6 < projection < np.linalg.norm(vecs[i])+1e-6
            if aligned and inbetween:
                onpath = True
                dist = projection+np.sum(np.linalg.norm(vecs,axis=1)[:i])
                distances = np.append(distances,dist)
                break
            else:
                onpath = False
        onpatharray.append(onpath)
    return onpatharray,distances


def getpath(pathpoints, n=50):
    """
    Get a (segmented) linear path between the pathpoints.
    
    :type pathpoints: np.ndarray(N x dim)
    :param pathpoints: Points defining the path.
    :type n: int
    :param n: Number of points of the path between the pathpoints. **Optional**. Default: 50
    :rtype: (np.ndarray, np.ndarray)
    :returns: points on (segmented) linear path, distances to first point along path (for 2d plotting)
    """
    pathpoints = np.array(pathpoints)
    if pathpoints.shape[0]<2:
        raise ValueError('You must give at least 2 points for pathpoints')
    
    ks = np.zeros([(pathpoints.shape[0]-1)*n, pathpoints.shape[1]])
    
    for i in xrange(pathpoints.shape[0]-1):
        for xyz in xrange(pathpoints.shape[1]):
            ks[i*n:(i+1)*n,xyz] = np.linspace(pathpoints[i][xyz], pathpoints[i+1][xyz], n)

    kdist = np.zeros(len(ks))
    for i in xrange(1,len(ks)):
        kdist[i] = np.linalg.norm(ks[i]-ks[i-1]) + kdist[i-1]

    return ks,kdist
    
