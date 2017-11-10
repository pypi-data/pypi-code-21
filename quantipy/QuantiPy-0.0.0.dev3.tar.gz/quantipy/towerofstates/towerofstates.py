# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import itertools
import quantipy.lattice as latt
import quantipy.symmetries as symm
from quantipy.utils import _validunitcell, _map_to_simtorus

def towerofstates(unitcell, structure, lattice=None, local_sym_group=None, Smax=5):
    """
    Compute the tower of states or groundstate sectors of a given structure on a lattice.

    :type unitcell: quantipy.Lattice instance
    :param unitcell: Lattice in the size of the unitcell of the magnetic structure.
    :type structure: list/np.ndarray
    :param structure: Magnetic structure as vectors. 
    :type lattice: quantipy.Lattice instance
    :param lattice: Lattice to put the magnetic structure onto it. Largen than unitcell.
        The symmetry properties of this lattice are used for symmetry reduction. **Optional**
    :type Smax: int
    :param Smax: Maximal S which is considered in the computation. **Optional**. Default: Smax=5
    """

    #check if unitcell fits to lattice
    if lattice is not None:
        if not _validunitcell(unitcell.simulation_torus, lattice.simulation_torus):
            raise ValueError('Cannot fit unitcell onto lattice!')


    if lattice is None:
        #irreps of unitcell
        irreps = symm._get_irreps(unitcell, unitcell.symmetries_torus, twod_to_oned=False)
        #permutations
        perms = unitcell._get_permutations()
    else:
        #irreps of lattice
        irreps = symm._get_irreps(lattice, lattice.symmetries_torus, twod_to_oned=False)
        #permutations
        perms = lattice._get_permutations()

    #set structure for spins
    if type(structure) is list:
        structure = np.array(structure)
    if not type(structure) is np.ndarray:
        raise ValueError('Structure must be a list or numpy.ndarray!')
    if not structure.shape==(unitcell.n_sites,3):
        raise ValueError('Structure must be of shape unitcell.n_sites x 3!')

    #write structure on lattice
    if lattice is not None:
        structurelattice = np.zeros([lattice.n_sites,3])
        coordsinunitcell = _map_to_simtorus(lattice.coordinates, unitcell.simulation_torus) 
        unitcellinunitcell = _map_to_simtorus(unitcell.coordinates, unitcell.simulation_torus) 
        for i, uc in enumerate(unitcellinunitcell):
            idx = np.all(np.isclose(uc, coordsinunitcell), axis=1)
            structurelattice[idx,:] = structure[i,:]
    else:
        structurelattice = structure

    structure = structurelattice

    #get stabilizer
    stab_idx = []
    stab_phis = []
    stab_rs = []
    for idx,perm in enumerate(perms):
        #print 'perm=',perm
        structure_permuted = structure[perm]
        #print 'st=', structure
        #print 'st_perm=',structure_permuted
        
        #find SO(3) rotation
        if np.allclose(np.dot(structure, structure.T), np.dot(structure_permuted, structure_permuted.T)):
            isstab = True
            evU, U = np.linalg.eigh(np.dot(structure, structure.T))
            r = sum(evU>1e-6)
            U = U[:,-r:]
            evU = evU[-r:]
            V1temp = np.dot(np.dot(structure.T,U), np.diag(np.sqrt(1./evU)))
            V2temp = np.dot(np.dot(structure_permuted.T,U), np.diag(np.sqrt(1./evU)))
#            print 'V1', V1temp
#            print 'V2', V2temp
            
            AdA = np.dot(structure.T, structure)
            BdB = np.dot(structure_permuted.T, structure_permuted)
            e1, V1 = np.linalg.eigh(AdA)
            e2, V2 = np.linalg.eigh(BdB)
            V1[:,-r:] = V1temp
            V2[:,-r:] = V2temp
#            print 'V1', V1
#            print 'V2', V2
            #check if Vi orthogonal
            for V in [V1,V2]:
                assert(np.allclose(np.dot(V,np.conj(V).T),np.eye(3)))

            V = np.dot(V2, np.linalg.inv(V1))
            if np.linalg.det(V)<0:
                if r<3:
                    V2[:,0] = -V2[:,0]
                    V = np.dot(V2, np.linalg.inv(V1))
                    assert(np.abs(np.linalg.det(V)-1)<1e-6)
                else:
                    isstab = False
 
            #Compute angle
            if isstab:
                #print 'V=',V
                phi = np.arccos((np.trace(V) - 1.)/2.)
                # print 'phi=',phi, 'r=',r
                assert(np.allclose(np.dot(structure_permuted, V), structure))
        
                stab_idx.append(idx) 
                stab_phis.append(phi) 
                stab_rs.append(r) 

    stab_idx = np.array(stab_idx)
    stab_phis = np.array(stab_phis)
    stab_rs = np.array(stab_rs)

    #Reduce representation
    def get_chiS(phi,r,S):
        if r==1 and np.abs(phi)<1e-6:
            return 1 #integral over all rotations around axis
        elif np.abs(phi)<1e-6:
            return 2*S+1
        else:
            return np.sin((S+.5)*phi)/np.sin(phi*.5)

    n_irreps = np.zeros([len(irreps),Smax],dtype=int)
    for S in range(Smax):
        chi_S = map(lambda x: get_chiS(x[0],x[1],S), np.vstack([stab_phis,stab_rs]).T)
        #print 'chi_S=',chi_S
        for i,irrep in enumerate(irreps):
            #create phase array, not allowed operators are 0
            phases = np.zeros(len(perms), dtype='complex')
            phases[irreps[irrep]['allowed_ops']] = irreps[irrep]['phases']
            
            #compute occupance of irrep 
            dim_stab = len(np.intersect1d(stab_idx, irreps[irrep]['allowed_ops']))
            n_irrep = np.sum(phases[stab_idx]*chi_S)/dim_stab

            if n_irrep.imag>1e-6:
                raise ValueError('A problem occured when reducing to irreps!')
            n_irrep = np.real(n_irrep)
            if abs(np.around(n_irrep)-n_irrep)>1e-6:
                raise ValueError('A problem occured when reducing to irreps!')
            n_irrep = int(n_irrep)
            if n_irrep<0:
                raise ValueError('A problem occured when reducing to irreps!')

            n_irreps[i,S] = n_irrep 

    # print n_irreps

    #Print irreps
    strings = []
    for S in range(Smax):
        for i,irrep in enumerate(irreps):
            if n_irreps[i,S]==1:
                strings.append('S=%i %s' %(S,irrep))
            elif n_irreps[i,S]>1:
                strings.append('%i x S=%i %s' %(n_irreps[i,S], S, irrep))

    string = 'Representation = ' + ' + '.join(strings)

    print string

    return string





def gs_sectors(structure, lattice):
    """
    Compute the space-group sectors of the ground-state representation on a lattice.
    Especially useful for dimer coverings. For magnetic structures, :func:`towerofstates` should be used.

    :type structure: dict(string/int - np.ndarray)
    :param structure: Structure of the groundstate as dictionary
    :type lattice: quantipy.Lattice
    :param lattice: The lattice on which the representation should be reduced.
    :rtype: str
    :returns: Space group irreps for given representation.
    """

    irreps = symm._get_irreps(lattice, lattice.symmetries_torus, twod_to_oned=False)
    perms = lattice._get_permutations()
    
    if type(structure) is not dict:
        raise ValueError('structure must be a dictionary!')

    #sort structure
    for st in structure:
        stsort = np.sort(structure[st],axis=1)
        stsort = stsort[np.argsort(stsort[:,0]),:]
        structure[st] = stsort

    #get stabilizer
    stab_idx = []
    for idx,perm in enumerate(perms):
        isstab = True
        for st in structure.values():
            newst = perm[st]
            #sort newst
            newstsort = np.sort(newst,axis=1)
            newstsort = newstsort[np.argsort(newstsort[:,0]),:]
            #check whether stabilizer
            if np.all(newstsort==st):
                isstab = isstab and True 
            else:
                isstab = isstab and False
        if isstab:
            stab_idx.append(idx) 

    stab_idx = np.array(stab_idx)

    #Reduce representation
    n_irreps = np.zeros(len(irreps),dtype=int)
    for i,irrep in enumerate(irreps):
        #create phase array, not allowed operators are 0
        phases = np.zeros(len(perms), dtype='complex')
        phases[irreps[irrep]['allowed_ops']] = irreps[irrep]['phases']
        
        #compute occupance of irrep 
        dim_stab = len(np.intersect1d(stab_idx, irreps[irrep]['allowed_ops']))
        n_irrep = np.sum(phases[stab_idx])/dim_stab

        if n_irrep.imag>1e-6:
            raise ValueError('A problem occured when reducing to irreps!')
        n_irrep = np.real(n_irrep)
        if abs(int(n_irrep)-n_irrep)>1e-6:
            raise ValueError('A problem occured when reducing to irreps!')
        n_irrep = int(n_irrep)
        if n_irrep<0:
            raise ValueError('A problem occured when reducing to irreps!')

        n_irreps[i] = n_irrep 

    #Print irreps
    strings = []
    for i,irrep in enumerate(irreps):
        if n_irreps[i]==1:
            strings.append('%s' %irrep)
        elif n_irreps[i]>1:
            strings.append('%i %s' %(n_irreps[i], irrep))

    string = 'Representation = ' + ' + '.join(strings)

    print string

    return string
