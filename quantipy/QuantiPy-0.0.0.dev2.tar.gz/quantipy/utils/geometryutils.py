# -*- coding: utf-8 -*-
""" 
 Help functions for geometric calculations
  
 :author: Alexander Wietek, Michael Schuler
 
"""
import numpy as np
import itertools
import scipy.spatial
from quantipy.utils import find_rows

def _round_middle_down(arr):
        arrtmp = np.around(arr)
        mv = (arr - np.floor(arr))==.5
        arrtmp[mv] = np.floor(arr[mv])
        return arrtmp
        
def _torusdistance(coord1, coord2, torus):
        """
        Returns distance of two points on the torus.
        
        :type coord1: np.ndarray
        :param coord1: Coordinates of first point.
        :type coord2: np.ndarray
        :param coord2: Coordinates of second point.        
        :param torus: the defining torus. torus[0,:] describes
                      first vector of bounding box, torus[1,:] the second one etc.
        :type torus: np.ndarray
        :rtype: float
        :returns: Distance of coord1, coord2 on the lattice torus.
        """
     
        #first step: move coords in first basis cell spanned by t1,t2
        c1 = np.linalg.solve(torus.T,coord2 - coord1)
        c1 -= _round_middle_down(c1)
        
        return np.linalg.norm(np.dot(torus.T,c1))


def _torusdistancevector(coord1, coord2, torus):
        """
        Returns distance vector of two points on the torus.
        
        :type coord1: np.ndarray
        :param coord1: Coordinates of first point.
        :type coord2: np.ndarray
        :param coord2: Coordinates of second point.        
        :param torus: the defining torus. torus[0,:] describes
                      first vector of bounding box, torus[1,:] the second one etc.
        :type torus: np.ndarray
        :rtype: float
        :returns: Distance of coord1, coord2 on the lattice torus.
        """
     
        #first step: move coords in first basis cell spanned by t1,t2
        c1 = np.linalg.solve(torus.T,coord2 - coord1)
        c1 -= _round_middle_down(c1)
        return np.dot(torus.T,c1)

def _wignerseitz(unitcell):
    """
    Returns wigner-seitz cell edges and faces of given unticell
    
    :type unitcell: np.ndarray
    :param unitcell: unitcell 
    :rtype: np.ndarray, np.ndarray
    :returns: Edges, Faces of wigner seitz cell
    """
            
    if unitcell.shape[0] != unitcell.shape[1] :
        raise ValueError("Canot compute Wigner-Seitz cell, unitcell must be dxd array")

    dimension = unitcell.shape[0]

    # Compute Lattice 
    lattice = np.zeros([5**dimension,dimension])   # TODO: find generic algorithm
    for ctr, i in enumerate(itertools.product([0., 1, 2, -1., -2.],repeat = dimension)):
        lattice[ctr] = np.dot(i, unitcell)
    

    # Compute Voronoi diagram
    if dimension is 1:
        wigner_seitz_edges = np.array([lattice[0]/2.0, lattice[2]/2.0])
    elif dimension > 1:
        vor = scipy.spatial.Voronoi(lattice)
        wigner_seitz_edges_unsort = vor.vertices
        wigner_seitz_faces_unsort = [vertex for i, vertex in enumerate(vor.ridge_vertices) 
                                     if -1 not in vertex and 0 in vor.ridge_points[i]]
        
        # Remove spurios k points, sort edges for 2D 
        if dimension is 2:
            edges = np.unique(np.array(wigner_seitz_faces_unsort).reshape((1,-1)))
            sorted_edges = wigner_seitz_edges_unsort[edges].tolist().sort()
            idx = np.argsort(np.arctan2(wigner_seitz_edges_unsort[edges][:,1],
                                        wigner_seitz_edges_unsort[edges][:,0]))
            wigner_seitz_edges=wigner_seitz_edges_unsort[edges][idx]
        # Remove spurios k points (no sort) in 3D
        else: 
            edges = np.unique(np.array([val for sublist in wigner_seitz_faces_unsort for val in sublist]))
            wigner_seitz_edges=wigner_seitz_edges_unsort[edges]

    # Sort faces corresponing to edges for 2D
    wigner_seitz_faces = []
    for face in wigner_seitz_faces_unsort:
        newface = [int(find_rows(wigner_seitz_edges_unsort[edge], wigner_seitz_edges)[0]) for edge in face]
        wigner_seitz_faces.append(newface)

    return wigner_seitz_edges, wigner_seitz_faces


def _map_to_simtorus(coordinates, simtorus):
    """
    Map coordinates back to simulation torus
    """
    coordinates = np.array(coordinates)
    simtorus = np.array(simtorus)
    dimension = simtorus.shape[0]
    dotrans = False

    if not simtorus.shape[1]==dimension:
        raise ValueError('Simulation torus must be dimension x dimension array!')
    if not coordinates.shape[1]==dimension:
        coordinates = coordinates.T
        dotrans = True
        if not coordinates.shape[1]==dimension:
            raise ValueError('Coordinates must be array of shape N x dimension!')

    c = np.linalg.solve(simtorus.T, coordinates.T)
    c = c%1
    c[c>0.9999999] = 0.
    
    if not dotrans:
        newcoords = np.dot(simtorus.T,c).T
    else:
        newcoords = np.dot(simtorus.T,c)

    return newcoords


def _validunitcell(unitcell,simulation_torus):
    """
    Check if unitcell fits into simulation torus.
    """
    coeffs = np.linalg.solve(unitcell.T, simulation_torus.T)
    return np.allclose(np.around(coeffs), coeffs)




















