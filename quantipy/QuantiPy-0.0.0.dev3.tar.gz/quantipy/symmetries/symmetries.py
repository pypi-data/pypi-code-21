# -*- coding: utf-8 -*-

import numpy as np
import itertools
from quantipy.utils.geometryutils import _map_to_simtorus, _torusdistance
from collections import OrderedDict

def inv_permutation(permutation):
    """
    Invert a permutation
    
    :type permutation: list/np.array (N,)
    :param permutation: Permutation to invert
    :rtype: np.array (N,)
    :returns: Inverse permutation
    """
    return np.argsort(permutation)


def _get_permutations(coordinates, unitcell, simtorus, translations, rotations, sym_center=None):
    """
    Get permutations for symmetry operations

    :type coordinates: np.array(N x dimension)
    :param coordinates: Coordinates of a lattice.
    :type unitcell: np.array(dimension x dimension)
    :param unitcell: Unit cell of the lattice.
    :type simtorus: np.array(dimension x dimension)
    :param simtorus: Simulation torus of the lattice.
    :type translations: np.array(T x dimension)
    :param translations: Translation vectors for permutations.
    :type rotations: np.array(R x dimension x dimension)
    :param rotations: Rotation matrices in units of unitcell for permutations.
    :type sym_center: np.array(dimension)
    :param sym_center: Symmetry center of the lattice. **Optional**. Default: [0]*dimension
    
    :rtype: np.array (TxR, N) 
    :returns: List of permutations
    """
    
    coordinates = np.array(coordinates)
    unitcell = np.array(unitcell)
    simtorus = np.array(simtorus)
    translations = np.array(translations)
    rotations = np.array(rotations)
    dimension = simtorus.shape[0]
   
    if sym_center is None:
        sym_center = np.zeros(dimension)
    sym_center = np.array(sym_center).reshape(1,dimension)

    if not simtorus.shape[1]==dimension:
        raise ValueError('Simulation torus must be dimension x dimension array!')
    if not unitcell.shape[0]==unitcell.shape[1]==dimension:
        raise ValueError('unitcell must be array of shape dimension x dimension!')
    if not coordinates.shape[1]==dimension:
        raise ValueError('Coordinates must be array of shape N x dimension!')
    if not translations.shape[1]==dimension:
        raise ValueError('translations must be array of shape N x dimension!')
    if not rotations.shape[1]==rotations.shape[2]==dimension:
        raise ValueError('rotations must be array of shape N x dimension x dimension!')

    #map coordinates to simtorus
    coordinates = _map_to_simtorus(coordinates,simtorus)
    
    #permutation for coordinates
    coordperm = np.lexsort(tuple(np.round(coordinates.T, decimals=6)))

    permutations = np.zeros([translations.shape[0]*rotations.shape[0],coordinates.shape[0]],dtype=int)
    for idx,(rot,trans) in enumerate(itertools.product(rotations,translations)):
        rot_matrix_nonfrac = np.dot(np.dot(np.linalg.inv(unitcell), rot), unitcell)
        newcoords = np.dot(rot_matrix_nonfrac, coordinates.T - sym_center.T).T + sym_center + trans
        newcoords = _map_to_simtorus(newcoords, simtorus)
        newcoordperm = np.lexsort(tuple(np.round(newcoords.T, decimals=6)))

        perm = coordperm[inv_permutation(newcoordperm)]
        
        assert np.allclose(newcoords,coordinates[perm])
        permutations[idx] = perm

    return permutations


def _get_permutations_OBC(coordinates, rotations, sym_center=None):
    """
    Get permutations for symmetry operations for open clusters

    :type coordinates: np.array(N x dimension)
    :param coordinates: Coordinates of a lattice.
    :type rotations: np.array(R x dimension x dimension)
    :param rotations: Rotation matrices.
    :type sym_center: np.array(dimension)
    :param sym_center: Symmetry center of the lattice. **Optional**. Default: [0]*dimension
    
    :rtype: np.array (R, N) 
    :returns: List of permutations
    """
    
    coordinates = np.array(coordinates)
    rotations = np.array(rotations)
    dimension = coordinates.shape[1]

   
    if sym_center is None:
        sym_center = np.zeros(dimension)
    sym_center = np.array(sym_center).reshape(1,dimension)

    if not coordinates.shape[1]==dimension:
        raise ValueError('Coordinates must be array of shape N x dimension!')
    if not rotations.shape[1]==rotations.shape[2]==dimension:
        raise ValueError('rotations must be array of shape N x dimension x dimension!')

    #permutation for coordinates
    coordperm = np.lexsort(tuple(np.round(coordinates.T, decimals=6)))

    permutations = np.zeros([rotations.shape[0],coordinates.shape[0]],dtype=int)
    for idx,rot in enumerate(rotations):
        newcoords = np.dot(rot, (coordinates - sym_center).T).T + sym_center
        newcoordperm = np.lexsort(tuple(np.round(newcoords.T, decimals=6)))

        perm = coordperm[inv_permutation(newcoordperm)]
        
        assert np.allclose(newcoords,coordinates[perm], atol=1e-5)
        permutations[idx] = perm

    return permutations




def _get_character_table(groupname, symmetries):
    """
    Get the character table for a group.

    :type groupname: str
    :param groupname: Name of the 2d point group.
    :type symmetries: list of str
    :param symmetries: Names of symmetry operations in the group.
    :rtype: Dict
    :returns: Dictionary with name of irreps and their characters for each symmetry operation in the group.
    """
    
    character_table = dict()
    if groupname == "C1":
        assert("C1" in symmetries)
        character_table["A"] = {"C1": 1.0}
    elif groupname == "C2":
        assert("C1" in symmetries and "C2" in symmetries)
        character_table["A"] = {"C1": 1.0, "C2": 1.0}
        character_table["B"] = {"C1": 1.0, "C2": -1.0}   
    elif groupname == "C3":
        assert("C1" in symmetries and "C3" in symmetries and "C3^2" in symmetries)
        e = np.exp(1j*2*np.pi/3)
        character_table["A"] = {"C1": 1.0, "C3": 1.0, "C3^2": 1.0 }
        character_table["Ea"] = {"C1": 1.0, "C3": e, "C3^2": np.conj(e)}
        character_table["Eb"] = {"C1": 1.0, "C3": np.conj(e), "C3^2": e}
    elif groupname == "C4":
        assert("C1" in symmetries and "C4" in symmetries and "C2" in symmetries and "C4^3" in symmetries)
        character_table["A"] = {"C1": 1.0, "C4": 1.0, "C2": 1.0, "C4^3": 1.0 }
        character_table["B"] = {"C1": 1.0, "C4": -1.0, "C2": 1.0, "C4^3": -1.0 }
        character_table["Ea"] = {"C1": 1.0, "C4": 1.0j, "C2": -1.0, "C4^3": -1.0j }
        character_table["Eb"] = {"C1": 1.0, "C4": -1.0j, "C2": -1.0, "C4^3": 1.0j }
    elif groupname == "C6":
        assert("C1" in symmetries and "C6" in symmetries and "C3" in symmetries \
                   and "C2" in symmetries and "C3^2" in symmetries and "C6^5" in symmetries)
        e = np.exp(1j*np.pi/3)
        character_table["A"] = {"C1": 1.0, "C6": 1.0, "C3": 1.0, "C2": 1.0, "C3^2": 1.0, "C6^5": 1.0 }
        character_table["B"] = {"C1": 1.0, "C6": -1.0, "C3": 1.0, "C2": -1.0, "C3^2": 1.0, "C6^5": -1.0 }
        character_table["E1a"] = {"C1": 1.0, "C6": e, "C3": -np.conj(e), "C2": -1.0, "C3^2": -e,\
                                      "C6^5": np.conj(e) }
        character_table["E1b"] = {"C1": 1.0, "C6": np.conj(e), "C3": -e, "C2": -1.0, "C3^2": -np.conj(e),\
                                      "C6^5": e }
        character_table["E2a"] = {"C1": 1.0, "C6": -np.conj(e), "C3": -e, "C2": 1.0, "C3^2": -np.conj(e),\
                                      "C6^5": -e }
        character_table["E2b"] = {"C1": 1.0, "C6": -e, "C3": -np.conj(e), "C2": 1.0, "C3^2": -e,\
                                      "C6^5": -np.conj(e)}
    elif groupname == "D1":
        reflects = [sym for sym in symmetries if "s" in sym]
        assert("C1" in symmetries and len(reflects)==1 )
        character_table["A"] = {"C1": 1.0, reflects[0] : 1.0}
        character_table["B"] = {"C1": 1.0, reflects[0] : -1.0} 
    elif groupname == "D2":
        reflects = [sym for sym in symmetries if "s" in sym]
        assert("C1" in symmetries and "C2" in symmetries and len(reflects)==2 )
        character_table["A1"] = {"C1": 1.0, "C2": 1.0,  reflects[0] : 1.0, reflects[1] : 1.0  }            
        character_table["A2"] = {"C1": 1.0, "C2": 1.0,  reflects[0] : -1.0, reflects[1] : -1.0  }            
        character_table["B1"] = {"C1": 1.0, "C2": -1.0,  reflects[0] : 1.0, reflects[1] : -1.0  }            
        character_table["B2"] = {"C1": 1.0, "C2": -1.0,  reflects[0] : -1.0, reflects[1] : 1.0  } 
    elif groupname == "D3":
        reflects = [sym for sym in symmetries if "s" in sym]
        assert("C1" in symmetries and "C3" in symmetries and "C3^2" in symmetries and len(reflects)==3 )
        character_table["A1"] = {"C1": 1.0, "C3": 1.0, "C3^2": 1.0, reflects[0]: 1.0, reflects[1]: 1.0,\
                                     reflects[2]: 1.0}            
        character_table["A2"] = {"C1": 1.0, "C3": 1.0, "C3^2": 1.0, reflects[0]: -1.0, reflects[1]: -1.0,\
                                     reflects[2]: -1.0}           
        character_table["E"] = {"C1": 2.0, "C3": -1.0, "C3^2": -1.0, reflects[0]: 0.0, reflects[1]: 0.0,\
                                     reflects[2]: 0.0}           
    elif groupname == "D4":
        assert("C1" in symmetries and "C4" in symmetries and "C2" in symmetries and "C4^3" in symmetries \
                   and "C1s" in symmetries and "C4s" in symmetries and "C2s" in symmetries \
                   and "C4^3s" in symmetries)
        character_table["A1"] = {"C1": 1.0, "C4": 1.0, "C2": 1.0, "C4^3": 1.0,\
                                     "C1s": 1.0, "C4s": 1.0, "C2s": 1.0, "C4^3s": 1.0  }
        character_table["A2"] = {"C1": 1.0, "C4": 1.0, "C2": 1.0, "C4^3": 1.0,\
                                     "C1s": -1.0, "C4s": -1.0, "C2s": -1.0, "C4^3s": -1.0  }
        character_table["B1"] = {"C1": 1.0, "C4": -1.0, "C2": 1.0, "C4^3": -1.0,\
                                     "C1s": 1.0, "C4s": -1.0, "C2s": 1.0, "C4^3s": -1.0  }
        character_table["B2"] = {"C1": 1.0, "C4": -1.0, "C2": 1.0, "C4^3": -1.0,\
                                     "C1s": -1.0, "C4s": 1.0, "C2s": -1.0, "C4^3s": 1.0  }
        character_table["E"] = {"C1": 2.0, "C4": 0.0, "C2": -2.0, "C4^3": 0.0,\
                                     "C1s": 0.0, "C4s": 0.0, "C2s": 0.0, "C4^3s": 0.0  }
    elif groupname == "D6":
        assert("C1" in symmetries and "C6" in symmetries and "C3" in symmetries and "C2" in symmetries \
                   and "C3^2" in symmetries and "C6^5" in symmetries and "C1s" in symmetries\
                   and "C6s" in symmetries and "C3s" in symmetries and "C2s" in symmetries \
                   and "C3^2s" in symmetries and "C6^5s" in symmetries)
        character_table["A1"] = {"C1": 1.0, "C6": 1.0, "C3": 1.0, "C2": 1.0, "C3^2": 1.0, "C6^5": 1.0, \
                                     "C1s": 1.0, "C6s": 1.0, "C3s": 1.0, "C2s": 1.0, "C3^2s": 1.0,\
                                     "C6^5s": 1.0 }
        character_table["A2"] = {"C1": 1.0, "C6": 1.0, "C3": 1.0, "C2": 1.0, "C3^2": 1.0, "C6^5": 1.0, \
                                     "C1s": -1.0, "C6s": -1.0, "C3s": -1.0, "C2s": -1.0, "C3^2s": -1.0,\
                                     "C6^5s": -1.0 }
        character_table["B1"] = {"C1": 1.0, "C6": -1.0, "C3": 1.0, "C2": -1.0, "C3^2": 1.0, "C6^5": -1.0, \
                                     "C1s": 1.0, "C6s": -1.0, "C3s": 1.0, "C2s": -1.0, "C3^2s": 1.0,\
                                     "C6^5s": -1.0 }
        character_table["B2"] = {"C1": 1.0, "C6": -1.0, "C3": 1.0, "C2": -1.0, "C3^2": 1.0, "C6^5": -1.0, \
                                     "C1s": -1.0, "C6s": 1.0, "C3s": -1.0, "C2s": 1.0, "C3^2s": -1.0,\
                                     "C6^5s": 1.0 }
        character_table["E1"] = {"C1": 2.0, "C6": 1.0, "C3": -1.0, "C2": -2.0, "C3^2": -1.0, "C6^5": 1.0, \
                                     "C1s": 0.0, "C6s": 0.0, "C3s": 0.0, "C2s": 0.0, "C3^2s": 0.0,\
                                     "C6^5s": 0.0 }
        character_table["E2"] = {"C1": 2.0, "C6": -1.0, "C3": -1.0, "C2": 2.0, "C3^2": -1.0, "C6^5": -1.0, \
                                     "C1s": 0.0, "C6s": 0.0, "C3s": 0.0, "C2s": 0.0, "C3^2s": 0.0,\
                                     "C6^5s": 0.0 }

    else:
        raise ValueError("Invalid Group for Character Table creation!")

    return character_table


def _get_irreps(lattice, symmetries, twod_to_oned=True):
    """
    Get all irreps and characters for a system.
    
    :type lattice: quantipy.Lattice instance
    :param lattice: Lattice to compute symmetries
    :type symmetries: dict
    :param symmetries: Symmetry elements computed in Lattice or GenericModel class.
    :type twod_to_oned: Bool
    :param twod_to_oned: If True, 2d irreps are converted to 1d representations. 
                         **Optional**. Default: True
    :rtype: OrderedDict
    :returns: All Irreps, characters and allowed operations of the symmetry group.
    """
    if lattice.dimension==3:
        warnings.warn('Cannot compute PG symmetry phases for 3d yet. Only translations used!')

    #get little groups for model
    little_groups = lattice._get_little_groups(symmetries)
    
    if lattice.trans_sym:
        shifts = lattice.bravaiscoordinates - lattice.bravaiscoordinates[0]
    else:
        shifts = np.zeros((1,lattice.dimension))
    nshifts = shifts.shape[0]

    allirreps = {}
    count_not_high_sym = 0
    
    for lg in little_groups:
        groupname = lg['little_group_name']
        
        #No PG symmetries for 3d yet - Use C1. TODO!
        if lattice.dimension==3:
            lg['little_group']=[np.eye(lattice.dimension)]
            lg['rot_names']=['C1']
            lg['rot_idx']=[0]
            groupname = 'C1'

#        allowed_ops = np.array([np.arange(0,len(shifts)) + 
#            ri*len(lattice.bravaiscoordinates) for ri in lg['rot_idx']]).flatten()
        allowed_ops = np.array([np.arange(0,nshifts) + 
            ri*nshifts for ri in lg['rot_idx']]).flatten()
        
        character_table = _get_character_table(groupname, lg['rot_names'])
        
        #Name of k point
        if lg['high_sym_point']==None or lg['high_sym_point']=='None':
            high_sym_name = str(count_not_high_sym)
            count_not_high_sym +=1
        else:
            high_sym_name = lg['high_sym_point']

        for irrep in character_table:
            #Name of irrep
            if lattice.trans_sym:
                irrepname = "{0}.{1}.{2}".format(high_sym_name.replace('_',''),
                        groupname, irrep)
            else:
                irrepname = "{0}.{1}".format(groupname, irrep)
            
            # Handle 2dim irreducible representations
            if twod_to_oned:
                if (groupname=='D3' and irrep=='E') or (groupname=='D4' and irrep=='E') or (groupname=='D6' and (irrep=='E1' or irrep=='E2')):
                    final_character_table = _get_character_table(lg['little_group_name'].replace('D','C'),
                            lg['rot_names'])
                    final_irrep = irrep + 'a'
                    final_allowed_ops = np.array([np.arange(0,nshifts) + 
                        #lg['rot_idx'][i]*len(lattice.bravaiscoordinates) for i in range(len(lg['rot_idx']))
                        lg['rot_idx'][i]*nshifts for i in range(len(lg['rot_idx']))
                        if not 's' in lg['rot_names'][i] ]).flatten()
                else:
                    final_character_table = character_table
                    final_irrep = irrep
                    final_allowed_ops = allowed_ops
            else:
                final_character_table = character_table
                final_irrep = irrep
                final_allowed_ops = allowed_ops
      
            #Get phases
            phases = np.zeros(len(final_allowed_ops),dtype='complex')
            for i,op in enumerate(final_allowed_ops):
                shift = shifts[op%(shifts.shape[0])]
                symelement = symmetries['names'][op/shifts.shape[0]]
                if symelement==None:
                    symelement='C1'
                pgchar = final_character_table[final_irrep][symelement]
                if lg['k'] is None:
                    momentum = np.zeros(lattice.dimension)
                else:
                    momentum = lg['k']
                phases[i] = np.exp(1j*np.dot(momentum,shift)) * pgchar 
            
            allirreps[irrepname] = {'k': lg['k'], 'allowed_ops': final_allowed_ops, 'phases': phases}

    #Sorting irreps
    def sortfunc(x):
        try:
            int(x[0][0])
            return '2'+x[0]
        except ValueError:
            if 'Gamma' in x[0]:
                return '0'+x[0]
            else:
                return '1'+x[0]

    allirreps = OrderedDict(sorted(allirreps.items(), key=sortfunc))

    return allirreps
