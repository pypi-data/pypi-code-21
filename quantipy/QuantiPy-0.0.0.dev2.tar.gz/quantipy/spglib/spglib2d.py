# -*- coding: utf-8 -*-
"""
Spglib implementation for two dimensional lattices
"""

import _spglib as _spg
import numpy as np
from scipy import linalg
from collections import OrderedDict
import math

import spglib


def get_symmetry(unitcell, basiscoordinates, sym_center=np.array([0., 0.]), maxpg=None,
                 symprec=1e-5, angle_tolerance=-1.0):
    """
    Return symmetry operations as hash.
    Hash key 'rotations' gives the numpy integer array
    of the rotation matrices for scaled positions
    Hash key 'translations' gives the numpy double array
    of the translation vectors in scaled positions
    """

    if np.abs(unitcell[0,0]) > 1e-6: 
        alpha = np.arctan(unitcell[0,1]/unitcell[0,0])
    else:
        alpha = np.pi/2
    pg_syms_2d = OrderedDict([("C1", _rot_matrix(0)), ("C6",  _rot_matrix(np.pi/3)), 
                              ("C4",  _rot_matrix(np.pi/2)), ("C3", _rot_matrix(2*np.pi/3)), 
                              ("C2", _rot_matrix(np.pi)), ("C3^2",  _rot_matrix(4*np.pi/3)), 
                              ("C4^3",  _rot_matrix(3*np.pi/2)), ("C6^5",  _rot_matrix(5*np.pi/3)), 
                              ("C1s", np.dot(_rot_matrix(0),_refl_matrix(alpha))), 
                              ("C6s", np.dot(_rot_matrix(np.pi/3),_refl_matrix(alpha))), 
                              ("C4s", np.dot(_rot_matrix(np.pi/2),_refl_matrix(alpha))), 
                              ("C3s", np.dot(_rot_matrix(2*np.pi/3),_refl_matrix(alpha))), 
                              ("C2s", np.dot(_rot_matrix(np.pi),_refl_matrix(alpha))), 
                              ("C3^2s", np.dot(_rot_matrix(4*np.pi/3),_refl_matrix(alpha))), 
                              ("C4^3s",  np.dot(_rot_matrix(3*np.pi/2),_refl_matrix(alpha))), 
                              ("C6^5s",  np.dot(_rot_matrix(5*np.pi/3),_refl_matrix(alpha)))])

    # Filter syms to only use maxpg
    if maxpg != None:
        tmp = OrderedDict([(sym, pg_syms_2d[sym]) for sym in pg_syms_2d if sym in maxpg])
        pg_syms_2d = tmp

    # TODO: extend to non symmorphic wallpaper groups
    allowed_syms_by_unitcell = []
    A = np.transpose(unitcell)

    for name, matrix in pg_syms_2d.iteritems():
        a1new = np.dot(matrix, unitcell[0,:])
        a2new = np.dot(matrix, unitcell[1,:])
        c1 = linalg.solve(A, a1new)
        c2 = linalg.solve(A, a2new)
        
        if np.all(np.abs(c1 - np.round(c1)) < symprec) and np.all(np.abs(c2 - np.round(c2)) < symprec):
            allowed_syms_by_unitcell.append(name)


    # Check whether basis coordinates are mapped
    allowed_syms_by_basiscoordinates = []
    for name in allowed_syms_by_unitcell:
        allmapped = True
        for basiscoord in basiscoordinates:
            newbasiscoord = np.dot(pg_syms_2d[name], basiscoord - sym_center) + sym_center
            ismapped = False
            for basiscoord2 in basiscoordinates:
                c = linalg.solve(A, newbasiscoord - basiscoord2)
                # check if c is integer
                if np.all(np.abs(c - np.round(c))< 1e-6):
                    ismapped = True
                    break
            allmapped = allmapped and ismapped
        if allmapped:
            allowed_syms_by_basiscoordinates.append(name)

    rotations = []
    rotationnames = []
    translations = []


    for name in allowed_syms_by_basiscoordinates:
        rot_mat_frac =  np.around(np.array(np.dot(np.dot(unitcell, pg_syms_2d[name]),\
                                                      np.linalg.inv(unitcell)))).astype('intc')
        rotations.append(rot_mat_frac)
        rotationnames.append(name)
        translations.append([0., 0.])


    return {'rotations': np.array(rotations, dtype='intc', order='C'),
            'translations': np.array(translations, dtype='double', order='C'), 'names':rotationnames}




def get_spacegroup(unitcell, basiscoordinates, sym_center=np.array([0., 0.]), maxpg=None,
                   symprec=1e-5, angle_tolerance=-1.0):
    """
    Return space group (momentarily only point group) symbol and number
    as a string.
    """
    symmetries = get_symmetry(unitcell, basiscoordinates, sym_center=sym_center, maxpg=maxpg,
                              symprec=symprec, angle_tolerance=angle_tolerance)
    return get_pointgroup(symmetries["rotations"])
  


def get_pointgroup(rotations):
    """
    Return point group name for given symmetries
    """
    # check if reflections are present
    if len([sym for sym in rotations if np.abs(np.linalg.det(sym) + 1) < 1e-6]) != 0:
        return "D%i" %(len(rotations)/2)
    else:
        return "C%i" %len(rotations)



def find_primitive(cell, coordinates, symprec=1e-5, angle_tolerance=-1.0):
    """
    A primitive cell in the input cell is searched and returned
    If no primitive cell is found, (None, None) is returned.
    for this the 3d spglib is used ( misused :-) )
    """
    
    
    # Atomic positions have to be specified by scaled positions for spglib.
    lattice = np.array(np.vstack((np.hstack((cell.T, np.zeros((2,1)))), np.array([0., 0., 2.]))), 
                       dtype='double', order='C')
    coordinates = np.vstack((np.hstack((coordinates, np.zeros((coordinates.shape[0],1)))),
                             (np.hstack((coordinates, np.ones((coordinates.shape[0],1))))))) 
    positions = np.array(linalg.solve(lattice, coordinates.T).T, dtype='double', order='C')
    numbers = np.zeros(len(positions), dtype='intc', order='C')


    # lattice is transposed with respect to the definition of Atoms class
    num_atom_prim = _spg.primitive(lattice,
                                   positions,
                                   numbers,
                                   symprec,
                                   angle_tolerance)
    lattice = lattice[0:2,0:2]
    positions = positions[:,0:2]
    if num_atom_prim > 0:
        return (np.array(-lattice.T, dtype='double', order='C'),
                np.array(positions[:num_atom_prim], dtype='double', order='C'),
                np.array(numbers[:num_atom_prim], dtype='intc'))
    else:
        return None, None, None


  
        
def _rot_matrix(phi):
    return np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]])

def _refl_matrix(alpha):
    return np.array([[np.cos(2*alpha),np.sin(2*alpha)],[np.sin(2*alpha),-np.cos(2*alpha)]])





def get_symmetry_OBC(coordinates, sym_center=np.array([0., 0.]), refl_angle=np.pi/2.,
        maxpg=None, symprec=1e-5, angle_tolerance=-1.0):
    """
    Return symmetry operations as hash.
    Hash key 'rotations' gives the numpy integer array
    of the rotation matrices for scaled positions
    """
    alpha = refl_angle

    pg_syms_2d = OrderedDict([("C1", _rot_matrix(0)), ("C6",  _rot_matrix(np.pi/3)), 
                              ("C4",  _rot_matrix(np.pi/2)), ("C3", _rot_matrix(2*np.pi/3)), 
                              ("C2", _rot_matrix(np.pi)), ("C3^2",  _rot_matrix(4*np.pi/3)), 
                              ("C4^3",  _rot_matrix(3*np.pi/2)), ("C6^5",  _rot_matrix(5*np.pi/3)), 
                              ("C1s", np.dot(_rot_matrix(0),_refl_matrix(alpha))), 
                              ("C6s", np.dot(_rot_matrix(np.pi/3),_refl_matrix(alpha))), 
                              ("C4s", np.dot(_rot_matrix(np.pi/2),_refl_matrix(alpha))), 
                              ("C3s", np.dot(_rot_matrix(2*np.pi/3),_refl_matrix(alpha))), 
                              ("C2s", np.dot(_rot_matrix(np.pi),_refl_matrix(alpha))), 
                              ("C3^2s", np.dot(_rot_matrix(4*np.pi/3),_refl_matrix(alpha))), 
                              ("C4^3s",  np.dot(_rot_matrix(3*np.pi/2),_refl_matrix(alpha))), 
                              ("C6^5s",  np.dot(_rot_matrix(5*np.pi/3),_refl_matrix(alpha)))])

    # Filter syms to only use maxpg
    if maxpg != None:
        tmp = OrderedDict([(sym, pg_syms_2d[sym]) for sym in pg_syms_2d if sym in maxpg])
        pg_syms_2d = tmp

    coordinates = np.array(coordinates)

    allowed_syms = []
    for name in pg_syms_2d:
        newcoords = np.dot(pg_syms_2d[name], (coordinates - sym_center).T).T + sym_center

        allclose = True
        for nc in newcoords:
            if np.any(np.all(np.abs(coordinates-nc)<1e-6,axis=1)):
                allclose = allclose and True
            else:
                allclose = allclose and False
                break
        if allclose:
            allowed_syms.append(name)


    rotations = []
    rotationnames = []
    translations = []

    for name in allowed_syms:
        rotmatrix = pg_syms_2d[name]
        rotations.append(rotmatrix)
        rotationnames.append(name)
        translations.append([0., 0.])


    return {'rotations': np.array(rotations),
            'translations': np.array(translations, dtype='double', order='C'), 'names':rotationnames}
