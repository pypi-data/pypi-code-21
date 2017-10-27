# -*- coding: utf-8 -*-

from aiida.orm.calculation.inline import make_inline,optional_inline
from aiida.common.exceptions import InternalError
from aiida.orm import DataFactory,Node

try:
    from aiida.backends.djsite.db import models
except ImportError:
    from aiida.djsite.db import models

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Marco Gibertini, Andrius Merkys, Nicolas Mounet, Philippe Schwaller."

CifData = DataFactory('cif')
StructureData = DataFactory('structure')

def get_farthest_node(node, aiida_class=Node):
    """
    Get the farthest node from a given node, WITHOUT the use 
    of the transitive closure table.
    :param node: an AiiDA Node object
    :param aiida_class: the class of objects to look for (e.g. 
        StructureData, CifData, etc.)
    :return: a query set with all the farthest nodes 9at the same distance)
        from node.
    """
    from copy import deepcopy
    node_type = aiida_class()._query_type_string
    depth_found = None
    q_found = models.DbNode.aiidaobjects.filter(id=node.pk)
    q_inputs = models.DbNode.aiidaobjects.filter(outputs=node).distinct()
    depth = -1 # to be consistent with the DbPath depth (=0 for direct inputs)
    while q_inputs.count() > 0:
        depth += 1
        q = q_inputs.filter(type__startswith=node_type)
        if (q.count() > 0): 
            q_found = deepcopy(q)
            depth_found = depth
        inputs = list(q_inputs)
        q_inputs = models.DbNode.aiidaobjects.filter(outputs__in=inputs).distinct()
    
    return q_found.distinct().order_by('ctime')


def get_source_id(node, optional_value = None):
    """
    Returns ID of node source in a transparent way to support backwards
    compatibility.

    :param node: an AiiDA node
    :param optional_value: if no attribute value is found, optional_value
        is returned
    :return: node ID in the source database
    """
    source = node.get_extra('original_source', {})
    id = source.get('id', None)
    if id is None:
        id = node.get_extra('icsd_nr', None)
    if id is None:
        cif = get_farthest_node(node,aiida_class=CifData)[0]
        source = cif.get_attrs().get('source',{})
        id = source.get('id',None)
    if id is None:
        id = optional_value
    return id


def get_source_db_name(node, optional_value = None):
    """
    Returns node source database in a transparent way to support backwards
    compatibility.

    :param node: an AiiDA node
    :param optional_value: if no attribute value is found, optional_value
        is returned
    :return: source database name
    """
    source = node.get_extra('original_source', {})
    name = source.get('db_name', None)
    if name is None:
        if 'icsd_nr' in node.extras():
            name = 'Icsd'
    if name is None:
        cif = get_farthest_node(node,aiida_class=CifData)[0]
        source = cif.get_attrs().get('source',{})
        name = source.get('db_name',None)
    if name is None:
        name = optional_value
    return name


def get_info_2D_structure(structure):
    """
    Find the in-plane & out-of-plane indices of the lattice vectors of a 
    2D structure, a unit vector orthogonal to the 2D plane (and such that
    its projection to the out-of-plane lattice vector is positive), and the
    vacuum space and thickness of the structure, by computing the
    maximum empty space between all atomic positions projected on the
    orthogonal axis.
    :param structure: a 2D AiiDA structure (i.e. with one non-periodic
        direction out of three)
    :return: a dictionary of the form:
        {'inplane_indices': in-plane indices of the lattice (cell) vectors,
         'outofplane_index': out-of-plane index of the lattice (cell) vector,
         'ortho_unit_vector': unit vector orthogonal to the layer,
         'vacuum': vacuum space between layers (angstrom),
         'thickness': thickness of the layer(angstrom),
        }
    
    .. note:: the layer does not necessarily have to be along the x-y plane.
    """
    import numpy as np
    
    if sum(structure.pbc)!=2:
        raise ValueError("The structure should have one (and only one) "
                         "non-periodic axis!")

    # in-plane and out-of-plane lattice vectors
    inplane_indices = np.where(structure.pbc)[0]
    outofplane_index = np.where([not _ for _ in structure.pbc])[0][0]
    # orthogonal directions (out-of-plane) (sign is set such that 
    # the projection to the non-periodic axis is positive)
    ortho_dir = np.cross(structure.cell[inplane_indices[0]],
                         structure.cell[inplane_indices[1]])
    ortho_dir /= np.linalg.norm(ortho_dir) \
                * np.sign(np.dot(structure.cell[outofplane_index],ortho_dir))
    
    # build a supercell along the non-periodic direction to compute the
    # vacuum distance
    supercell_size = [1,1,1]-(np.array(structure.pbc)-[1,1,1])
    s_dummy=StructureData(ase=structure.get_ase()*supercell_size)
    vacuum = max(np.diff(sorted([np.dot(si.position,ortho_dir)
                                 for si in s_dummy.sites])))
    thickness = np.dot(structure.cell[outofplane_index],ortho_dir) - vacuum
    if thickness<0:
        if thickness<-1e-5:
            raise ValueError("Negative thickness found for structure {} "
                             "({})".format(structure.pk,thickness))
        else:
            thickness = 0.
    
    return {'inplane_indices': inplane_indices,
            'outofplane_index': outofplane_index,
            'ortho_unit_vector': ortho_dir,
            'vacuum': vacuum,
            'thickness': thickness,
            }


def rescale(structure1,structure2,print_warnings=False):
    """
    Rescale structures before comparing them, in the case of
    low-dimensional materials (1D or 2D).
    3D and 0D compounds, or compounds that don't have the same
    periodic boundary conditions (pbc), are not rescaled.
    .. note:: There was a bug in this function for 2D structures with
    a non-orthogonal third axis -> fixed on 13/04/2017. Fix does not change
    anything for 2D structures with orthogonal third axis, or non-2D structures.
    """
    import ase
    import numpy as np
    from copy import deepcopy

    s1ase = structure1.get_ase()
    s2ase = structure2.get_ase()
    
    if sum(structure1.pbc) == 2 and sum(structure2.pbc) == 2:
        info_dict1 = get_info_2D_structure(structure1)
        info_dict2 = get_info_2D_structure(structure2)
        
        plane_indices1 = info_dict1['inplane_indices']
        plane_indices2 = info_dict2['inplane_indices']
        ratio = np.linalg.norm(np.cross(structure1.cell[plane_indices1[0]],
                                        structure1.cell[plane_indices1[1]]))/\
                np.linalg.norm(np.cross(structure2.cell[plane_indices2[0]],
                                        structure2.cell[plane_indices2[1]]))
        ratio /= len(structure1.sites)/float(len(structure2.sites))
        cell1 = np.array([np.array(structure1.cell[i])/ratio**0.25 if i in plane_indices1
                           else structure1.cell[i] for i in range(3)])
        cell2 = np.array([np.array(structure2.cell[i])*ratio**0.25 if i in plane_indices2
                           else structure2.cell[i] for i in range(3)])
        # We rescale also the out-of-plane lattice vector
        # by comparing the thicknesses of the two materials.
        # If at least one of the two structures is strictly 2D (within a
        # given precision), NO rescaling is performed
        ortho_index1,ortho_dir1,vacuum1,thickness1 = \
            info_dict1['outofplane_index'],info_dict1['ortho_unit_vector'],\
            info_dict1['vacuum'],info_dict1['thickness']
        ortho_index2,ortho_dir2,vacuum2,thickness2 = \
            info_dict2['outofplane_index'],info_dict2['ortho_unit_vector'],\
            info_dict2['vacuum'],info_dict2['thickness']
        
        # TODO: implement better the case when vacuum is not the same in both
        if print_warnings and abs(vacuum1 - vacuum2)>1e-2 :
            print "WARNING in rescale: vacuum is different for the two "\
                  "2D structures! ({}, {}). For the structure comparison "\
                  "the vacuum is set to the average of the two".format(vacuum1,vacuum2)
        vacuum = (vacuum1 + vacuum2)/2.
        
        # correct the cell only if both materials are not strictly 2D
        if (thickness1 > 2e-2 and thickness2 > 2e-2):
            ortho_ratio = thickness1/thickness2
        else: 
            ortho_ratio = 1.0        
        # The following also re-aligns the layers (i.e. out-of-plane axis becomes 
        # orthogonal to the layer)
        the_cell1 = s1ase.cell
        the_cell2 = s2ase.cell
        #the_cell1[ortho_index1] = (thickness1 + vacuum1) * ortho_dir1
        #the_cell2[ortho_index2] = (thickness2 + vacuum2) * ortho_dir2
        the_cell1[ortho_index1] = (thickness1 + 0 if thickness1>=1e-5 else 1e-5)* ortho_dir1
        the_cell2[ortho_index2] = (thickness2 + 0 if thickness2>=1e-5 else 1e-5)* ortho_dir2
        # the two lines below are useful to get the correct scaled positions
        # later on, when we define the_structure1 & the_structure2
        s1ase.set_cell(the_cell1)
        s2ase.set_cell(the_cell2)
        # now we also rescale the cell according to the thickness ratio
        # (we do NOT apply the changes to s1ase & s2ase yet - done later)
        #cell1[ortho_index1] = (1.0/ortho_ratio**0.5 *thickness1 + vacuum) * ortho_dir1
        #cell2[ortho_index2] = (ortho_ratio**0.5 * thickness2 + vacuum) * ortho_dir2
        cell1[ortho_index1] = (1.0/ortho_ratio**0.5 * thickness1 + 0 if thickness1>=1e-5 else 1e-5) * ortho_dir1
        cell2[ortho_index2] = (ortho_ratio**0.5 * thickness2 + 0 if thickness2>=1e-5 else 1e-5)* ortho_dir2
                
    elif sum(structure1.pbc) == 1 and sum(structure2.pbc) == 1:
        # TODO: here also we should rescale according to the cross section
        # (similarly to thickness rescaling in the 2D case)
        axis_indice1 = np.where(structure1.pbc)[0][0]
        axis_indice2 = np.where(structure2.pbc)[0][0]
        ratio = np.linalg.norm(structure1.cell[axis_indice1])/\
                np.linalg.norm(structure2.cell[axis_indice2])
        ratio /= len(structure1.sites)/float(len(structure2.sites))
        cell1 = np.array([np.array(structure1.cell[i])/ratio**0.5 if i == axis_indice1
                           else structure1.cell[i] for i in range(3)])
        cell2 = np.array([np.array(structure2.cell[i])*ratio**0.5 if i == axis_indice2
                           else structure2.cell[i] for i in range(3)])
    else:
        cell1 = structure1.cell
        cell2 = structure2.cell

    #s1ase.set_cell(cell1)
    the_structure1=StructureData(ase=ase.Atoms(cell=cell1,
                                               scaled_positions=s1ase.get_scaled_positions(),
                                               numbers=s1ase.numbers,
                                               tags=s1ase.get_tags(),
                                               pbc=[True]*3))

    #s2ase.set_cell(cell2)
    the_structure2=StructureData(ase=ase.Atoms(cell=cell2,
                                               scaled_positions=s2ase.get_scaled_positions(),
                                               numbers=s2ase.numbers,
                                               tags=s2ase.get_tags(),
                                               pbc=[True]*3))
                                               
    if sum(structure1.pbc) == 2 and sum(structure2.pbc) == 2:
        # For 2D structures we put back the vacuum (now the cell contains 
        # just the layer) (not sure this is needed)
        asecell1 = the_structure1.get_ase()
        cell1[ortho_index1] += vacuum*ortho_dir1
        asecell1.set_cell(cell1)
        the_structure1 = StructureData(ase=asecell1)
        #
        asecell2 = the_structure2.get_ase()
        cell2[ortho_index2] += vacuum*ortho_dir2
        asecell2.set_cell(cell2)
        the_structure2 = StructureData(ase=asecell2)
    
    return the_structure1, the_structure2


def group_similar_structures(structure_list, ltol=0.2, stol=0.3, angle_tol=5,
    anonymous=False,framework=False,attempt_supercell=False,
    check_full_graph=False,symprecs=[]):
    """
    Given a list of structures, use fit method of StructureMatcher class
    from pymatgen to group them by structural equality.
    Modified version of the group_structure method of StructureMatcher.

    :param structure_list: list of AiiDA structures to be grouped
    :param ltol: (float) Fractional length tolerance. Default is 0.2.
    :param stol: (float) Site tolerance. Defined as the fraction of the
                  average free length per atom := ( V / Nsites ) ** (1/3)
                  Default is 0.3.
    :param angle_tol: (float) Angle tolerance in degrees. Default is 5 degrees.
    :param anonymous: anonymous comparison, i.e. the structures are assumed
                       to have the same set of species (all possible 
                       permutations are checked). Default is False.
    :param framework: use the FrameworkComparator instead of SpeciesComparator
                      i.e. regardless of species. Default is False.
    :param attempt_supercell: (bool) if True it attempts to generate a supercell
                              transformation to map the smaller structure
                              to the larger one 
    :param check_full_graph: if True, check the full graph of similar
                             structures and output the connected groups
                             and matrix of adjacency. Default is False.
    :param symprecs: list of precision parameters to be tested
        to compare also the spacegroups. If empty, no spacegroup 
        comparison. If not empty, comparison criterion is:
        * similarity in the StructureMatcher sense (with sm.fit)
        * AND spacegroup is the same for at least one couple of
        symmetry precisions tested.
 
    :return: A list of lists of matched structure indices
    
    :raise : ImportError if the pymatgen StructureMatcher or spglib is not found
    
    .. note:: Assumption: if s1 == s2 but s1 != s3, then s2 and s3 will be put
    in different groups without comparison. This means that depending
    on the order in which the structures are given, this function
    might give different results (the reference structure will change -
    the similarity relation is not transitive).
    .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
    """
    adjacent_matrix = None
    try:
        import spglib
    except ImportError:
        try:
            from pyspglib import spglib
        except ImportError:
            raise ImportError("spglib required. It can be installed with "
                              "pip install --user spglib")

    try:
        from pymatgen.analysis.structure_matcher import StructureMatcher
    except ImportError:
        raise ImportError("Pymatgen required. It can be installed using pip: "
                          "(sudo) pip install pymatgen")
    
    def compare_structures(structure_1, structure_2,sm,
                           anonymous=False,symprecs=[]):
        """
        Compare two AiiDA structures.
        :param structure_1: first structure
        :param structure_2: second structure
        :param sm: instance of a StructureMatcher class
        :param anonymous: if True, anonymous comparison
        :param symprecs: list of precision parameters to be tested
        .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
        """
        s1,s2 = rescale(structure_1,structure_2)
        s1_ase = s1.get_ase()
        s2_ase = s2.get_ase()
        if symprecs:
            spg_equal = any([any([spglib.get_spacegroup(s1_ase,symprec=p1)==\
                                  spglib.get_spacegroup(s2_ase,symprec=p2)
                            for p2 in symprecs]) for p1 in symprecs])
        else:
            spg_equal = True
        if anonymous:
            return spg_equal and sm.fit_anonymous(
                s1.get_pymatgen_structure(),s2.get_pymatgen_structure())
        else:
            return spg_equal and sm.fit(
                s1.get_pymatgen_structure(),s2.get_pymatgen_structure())
    
    
    # create an instance of StructureMatcher class
    if not framework:
        sm = StructureMatcher(ltol,stol,angle_tol,
                              attempt_supercell=attempt_supercell)
    else:
        from pymatgen.analysis.structure_matcher import FrameworkComparator
        sm = StructureMatcher(ltol,stol,angle_tol,FrameworkComparator,
                              attempt_supercell=attempt_supercell)

    if not check_full_graph:
        all_groups_indices = []
        unmatched = range(len(structure_list))
        while len(unmatched) > 0:
            # Index of the reference structure that will be compared with the others
            ref = unmatched.pop(0)
            matches = [ref]
            # Indices of structures that give a positive result
            inds = [i for i in unmatched \
                    if compare_structures(structure_list[ref],
                        structure_list[i],sm,anonymous=anonymous,
                        symprecs=symprecs)]
            matches.extend(inds)
            # Refine the list of the indices of the structure that are still unmatched
            unmatched = [i for i in unmatched if i not in inds]
            all_groups_indices.append(matches)
            
    else:
        # here we want to get the complete groups that are connected by
        # the StructureMatcher similarity relation
        import numpy as np
        try:
            from scipy.sparse.csgraph import connected_components
        except ImportError:
            raise ImportError('scipy version 0.11 or higher is required'
                              ' with check_full_graph=True')
        # build adjacency matrix
        num_structures = len(structure_list)
        adjacent_matrix = np.eye(num_structures,dtype=int)
        for i in range(num_structures):
            for j in range(i+1,num_structures):
                adjacent_matrix[i,j] = int(compare_structures(
                            structure_list[i],structure_list[j],
                            sm,anonymous=anonymous,symprecs=symprecs))
                adjacent_matrix[j,i] = adjacent_matrix[i,j]
        # get the connected groups
        _,connection = connected_components(adjacent_matrix,directed=False)
        all_groups_indices = [np.where(connection==e)[0].tolist() for e in set(connection)]

    return all_groups_indices, adjacent_matrix


def find_similar_structures(structure_ref, structure_list, 
                ltol=0.2, stol=0.3, angle_tol=5,attempt_supercell=False):
    """
    Find all similar structures to a given reference structure, using
    fit method of StructureMatcher class from pymatgen.
    Modified version of the group_structure method of StructureMatcher.

    :param structure_ref: structure to be compared to the other ones.
    :param structure_list: list of AiiDA structures to be compared to.
    :param ltol: (float) Fractional length tolerance. Default is 0.2.
    :param stol: (float) Site tolerance. Defined as the fraction of the
                  average free length per atom := ( V / Nsites ) ** (1/3)
                  Default is 0.3.
    :param angle_tol: (float) Angle tolerance in degrees. Default is 5 degrees.
    :param attempt_supercell: (bool) if True it attempts to generate a supercell
                              transformation to map the smaller structure
                              to the larger one. Default is False
    :return: the indices in structure_list of the matching structures, 
        if any (empty list if none is matching).
    .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
    """
    try:
        from pymatgen.analysis.structure_matcher import StructureMatcher
    except ImportError:
        raise ImportError("Pymatgen required. It can be installed using pip: "
                          "(sudo) pip install pymatgen")

    # create an instance of StructureMatcher class
    sm = StructureMatcher(ltol,stol,angle_tol,
                          attempt_supercell=attempt_supercell)
    # compare ref. structure to all the others
    group_indices = [i for i,structure in enumerate(structure_list) \
            if sm.fit(*[s.get_pymatgen_structure() for s in \
                       rescale(structure_ref,structure)])]
    
    return group_indices


def composition_tuple(structure):
    """
    Get the (sorted) composition tuple of a structure, without the 
    species names, e.g.:
        - (1,2) for MoS2 or Mo2Te4,
        - (2,3) for Bi2Se3 or Bi4Se6,
        - (1,) for C2 or C60,
        etc.
    :param structure: an AiiDA structure
    :return: a sorted tuple of integers without common divider
    """
    from fractions import gcd
    import numpy as np
    num_species = np.array([[structure.get_kind(site.kind_name).get_symbols_string()
                             for site in structure.sites].count(sp)
                            for sp in structure.get_symbols_set()])
    the_gcd = reduce(gcd,num_species)
    return tuple(sorted(num_species/the_gcd))


def composition_string(structure):
    """
    Given a structure it returns a unique string
    corresponding to its composition
    :param structure: aiida structure object or dictionary with element,
        occurrence pairs
    .. note:: makes sense only for structures without partial occupations!
    """
    from aiida.common.constants import elements
    import ase
    import collections
    import fractions

    if isinstance(structure,StructureData):
        atomic_number_list = [ase.atom.atomic_numbers[structure.get_kind(s.kind_name).get_symbols_string()]
                              for s in structure.sites]
        counter = dict(collections.Counter(atomic_number_list))
    elif isinstance(structure,dict):
        counter = structure

    # The greatest common divisor of the occurrences of each element
    the_gcd = reduce(fractions.gcd,counter.values())

    # Sort elements by atomic number Z and divide occurrence by GCD
    sorted_counter = sorted((k,v//the_gcd) for k, v in counter.iteritems())

    # We now create the string
    string_id = "".join("{}{}".format(elements[_[0]]['symbol'],_[1])
                        for _ in sorted_counter)
    return string_id


@optional_inline
def filter_duplicate_structures_inline(parameters,**kwargs):
    """
    Check for duplicates the structures given in input and 
    provides in output the set of distinct structures and 
    a parameter data to reconstruct the provenance. 
    To compare structures a (modified) algorithm from pymatgen is adopted.
    :param parameters: a dictionary with the parameters for structure comparison:
                       ltol (float): Fractional length tolerance. 
                       stol (float): Site tolerance. Defined as the fraction of the
                                     average free length per atom := ( V / Nsites ) ** (1/3)
                       angle_tol (float): Angle tolerance in degrees.
                       anonymous (optional): True to compare structures 
                                             regardless of the exact species
                                             but taking into account the
                                             arrangement of species (default=False).
                       framework (optional): True to compare structures 
                                             regardless of the species
                                             (default=False)
                       attempt_supercell (optional: (bool) if True it attempts 
                                                    to generate a supercell
                                                    transformation to map the 
                                                    smaller structure
                                                    to the larger one 
                                                    (default=False)
                       check_full_graph (optional): True to check the 
                                                    full graph of similar
                                                    structures and output
                                                    the connected groups
                                                    (default=False).
                        symprecs (optional): list of precisions for 
                            spacegroup finding; this is to add a criterion
                            to the structure comparison: structures are
                            assumed to be equal if StructureMatcher
                            matches them AND one can find a common
                            spacegroup for the two structures, using one
                            of these precisions (can use a different 
                            precision for each structure). If this 
                            parameter is not there or is empty, 
                            spacegroups are not compared.
    :param kwargs: structures to be compared
    :return: {'output_parameters': ParameterData with a dictionary of the form
                    { uuid_ref_1 : [list of uuids],
                      uuid_ref_2 : [list of uuids],
                      etc.
                      },
              'output_array' : (optional, if check_full_graph=True)
                               ArrayData with the 'adjacent_matrix' array,
                               representing the full matrix of
                               adjacent structures  (M[i,j] = 1 if 
                               structures i,j are similar, 0 otherwise).
                               The ArrayData also contains 'structures_uuid'
                               with the uuids of the structures corresponding
                               to the indices of the adjacency matrix.
             }
             where uuid_ref_1, uuid_ref_2, etc. are the uuids of the
             non-redundant structures with the lowest number of atoms 
             and highest number of symmetries in each group, and where 
             the corresponding list of uuids represents the full group 
             of similar structures (the first element in each list being
             the reference structure).
             
    :raise: ValueError if anonymous and framework are both True
    .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
    """
    import numpy as np
    from fractions import gcd
    
    def plural(value):
        """
        :param value: a numerical value
        :return: string 's' if value > 1, '' otherwise
        """
        return 's' if value > 1 else ''

    ParameterData = DataFactory('parameter')

    try:
        import spglib
    except ImportError:
        try:
            from pyspglib import spglib
        except ImportError:
            raise ImportError("spglib required. It can be installed with "
                              "pip install --user spglib")

    # Get structures from input 
    structures = kwargs.values()
    num_structures = len(structures)

    # Check that we indeed have in input a list of structures with length>0
    if num_structures < 1:
        raise ValueError("Number of structures to be compared is less than zero!")

    # We first check that indeed all the structures given
    # have the same string identifier
    # Not strictly necessary, can be removed
    #string_id = None
    #for structure in structures:
    #    if string_id:
    #        if composition_string(structure) != string_id:
    #            raise ValueError("Structures to be compared for filtering "
    #                             "should have the same composition string id")
    #    else:
    #        string_id = composition_string(structure)
    params_dict = parameters.get_dict()
    ltol = params_dict['ltol']
    stol = params_dict['stol']
    angle_tol = params_dict['angle_tol']
    anonymous = params_dict.get('anonymous',False)
    framework = params_dict.get('framework',False)
    attempt_supercell = params_dict.get('attempt_supercell',False)
    symprecs = params_dict.get('symprecs',[])
    check_full_graph = params_dict.get('check_full_graph',False)
    if anonymous and framework:
        raise ValueError("One cannot set both anonymous and framework to True")    

    if not anonymous and not framework:
        string_id = structures[0].get_formula(mode='hill_compact')
    elif not framework:
        num_species = np.array([[structures[0].get_kind(site.kind_name).get_symbols_string()
                                for site in structures[0].sites].count(sp)
                                for sp in structures[0].get_symbols_set()])
        the_gcd = reduce(gcd,num_species)
        num_species = tuple(sorted(num_species/the_gcd))
        string_id = "number of species {}".format(num_species)
    else:
        string_id = "all"

    # If the length == 1, we can directly return the list as it is.
    if num_structures == 1:
        print "{}: only 1 structure".format(string_id)
        result_dict = {'output_parameters' : ParameterData(dict={structures[0].uuid:[structures[0].uuid]})} # Trivially we just have one group with the first and only structure
        if check_full_graph:
            output_array = DataFactory('array')()
            output_array.set_array('adjacent_matrix',np.array([1],dtype=int))
            output_array.set_array('structures_uuid',np.array([structures[0].uuid]))
            result_dict['output_array'] = output_array
        return result_dict
    
    # Convert structures to pymatgen form
    #structures_mg = [ structure.get_pymatgen_structure() for structure in structures]
    
    # We already know from the initial check that we have more than one structure in the list
    result_dict = {}
    all_groups_indices, adjacent_matrix = group_similar_structures(
                    structures,ltol=ltol,stol=stol,angle_tol=angle_tol,
                    anonymous=anonymous,framework=framework, attempt_supercell=attempt_supercell,
                    check_full_graph=check_full_graph,symprecs=symprecs)
    if adjacent_matrix is not None:
        output_array = DataFactory('array')()
        output_array.set_array('adjacent_matrix',adjacent_matrix)
        output_array.set_array('structures_uuid',np.array([s.uuid for s in structures]))
        result_dict['output_array'] = output_array
    
    num_groups = len(all_groups_indices)
    spacegroups = [ spglib.get_symmetry_dataset(structure.get_ase())['number']
                    for structure  in structures ]
    num_spacegroups = len(np.unique(spacegroups))
    if num_groups == num_structures:
        print "\033[31m{}: {} distinct structure{} out of {} ({} spacegroup{})\033[0m".format(
            string_id, num_groups, plural(num_groups),
            num_structures, num_spacegroups, plural(num_spacegroups))
    else:
        print "\033[32m{}: {} distinct structure{} out of {} ({} spacegroup{})\033[0m".format(
            string_id, num_groups, plural(num_groups),
            num_structures, num_spacegroups, plural(num_spacegroups))
            
    if num_groups < num_spacegroups:
        print "\033[1;91mWARNING: {}, number of distinct structures ({}) lower than the number of spacegroups ({})!\033[0m".format(string_id,num_groups,num_spacegroups)
        
    # Order structures so that the reference (first) one in each group has the smallest number of atoms 
    # and the largest number of point-group operations
    output_dict = {}
    for i in range(num_groups):
        group_indices = all_groups_indices[i]
        if len(group_indices)>1:
            # Sort the elements of this group of structures according to the number of atoms
            group_indices = sorted(group_indices, key=lambda k: len(structures[k].sites))
            # The index of the current reference structure with smallest number of atoms
            ref = group_indices[0]
            # I select the indices of the structures with the same number of atoms as the reference one
            min_atoms_indices = [ j for j in group_indices
                                  if len(structures[ref].sites) == len(structures[j].sites)]
            # Sort this subset of structures inversely to the number of symmetry operations
            # (preferring more symmetries)
            min_atoms_indices = sorted(min_atoms_indices, key=lambda k:
                len(spglib.get_symmetry_dataset(structures[k].get_ase())['rotations']),
                reverse = True)

            # Since the structures in each group are ordered with increasing number of atoms
            # we need to reorder just the first structures in the group
            for j in range(len(min_atoms_indices)):
                group_indices[j] = min_atoms_indices[j]
    
        output_dict[structures[group_indices[0]].uuid] = [ structures[j].uuid for j in group_indices]
    
    result_dict['output_parameters'] = ParameterData(dict=output_dict)
    
    return result_dict


def get_filter_duplicate_structures_results(parameters=None,store=True,**kwargs):
    """
    Get the results from the filter_duplicate_structures_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead the output dictionary of the previously
    launched function,
    - otherwise, launches the filter_duplicate_structures_inline function
    and get its result.
    .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    
    inputs_list = sorted([v.pk for k,v in kwargs.iteritems()
                          if k.startswith('structure')])
    result_dict = None
    for ic in InlineCalculation.query(inputs=kwargs.values()[0]).order_by('ctime'):
        ic_inputs_list = sorted([v.pk for k,v in ic.get_inputs_dict().iteritems()
                                 if k.startswith('structure')])
        try:
            if ( ic.get_function_name() == 'filter_duplicate_structures_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), parameters.get_dict())
                 and 'output_parameters' in ic.get_outputs_dict()
                 and ic_inputs_list==inputs_list):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    if result_dict is not None:
        print " filter_duplicate already run -> we do not re-run"
    else:
        print "Launch filtering of duplicates..."
        result_dict = filter_duplicate_structures_inline(parameters=parameters,
                                                         store=store,**kwargs)
    
    return result_dict

@optional_inline
def is_structure_duplicate_inline(parameters,structure_ref,**kwargs):
    """
    Check if structure_ref is a duplicate of any of the other structures
    given in input and provides in output the set of distinct structures and 
    a parameter data to reconstruct the provenance. 
    To compare structures a (modified) algorithm from pymatgen is adopted.
    :param parameters: a dictionary with the parameters for structure comparison:
                       ltol (float): Fractional length tolerance. 
                       stol (float): Site tolerance. Defined as the fraction of the
                       average free length per atom := ( V / Nsites ) ** (1/3)
                       angle_tol (float): Angle tolerance in degrees. 
    :param structure_ref: reference structure to which all the other
                          structures have to be compared.
    :param kwargs: structures to be compared with.
    :return: {'output_parameters': ParameterData with a dictionary of the form
                    { 'is_duplicate': True if structure_ref is a duplicate
                        of one of the other structures, False otherwise,
                      uuid_ref : [list of uuids],
                      }
             }
             where uuid_ref, is the uuid of the structure in the group
             of structures similar to structure_ref, with the lowest 
             number of atoms and highest number of symmetries,
             and where the corresponding list of uuids represents the full group 
             of similar structures (the first element in each list being
             the reference structure).
             NOTE: structure_ref is part of [list of uuids] and can be 
             uuid_ref.
    .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
    """
    ParameterData = DataFactory('parameter')

    try:
        import spglib
    except ImportError:
        try:
            from pyspglib import spglib
        except ImportError:
            raise ImportError("spglib required. It can be installed with "
                              "pip install --user spglib")

    # Get structures from input 
    structures = kwargs.values()
    num_structures = len(structures)
    string_id = structure_ref.get_formula(mode='hill_compact') 

    # If the length == 0, we can directly return the list as it is.
    if num_structures == 0:
        print "{}: only 1 structure".format(string_id)
        return {'output_parameters' : ParameterData(dict={'is_duplicate': False,
                            structure_ref.uuid:[structure_ref.uuid]})} # Trivially we just have one group with the first and only structure

    ltol = parameters.get_dict()['ltol']
    stol = parameters.get_dict()['stol']
    angle_tol = parameters.get_dict()['angle_tol']

    # Group the structures similar to the ref. one
    group_indices = find_similar_structures(structure_ref,structures,ltol,stol,angle_tol)
    is_duplicate = (len(group_indices) > 0)
            
    # Add the reference structure to the list of structures and to the group indices
    group_indices =  group_indices + [len(structures)]
    structures = structures + [structure_ref]
    # Order structures so that the reference (first) one in each group has the smallest number of atoms 
    # and the largest number of point-group operations
    group_indices = sorted(group_indices, key=lambda k: len(structures[k].sites))
    # The index of the current reference structure with smallest number of atoms
    ref = group_indices[0]
    # I select the indices of the structures with the same number of atoms as the reference one
    min_atoms_indices = [ j for j in group_indices
                          if len(structures[ref].sites) == len(structures[j].sites)]
    # Sort this subset of structures inversely to the number of symmetry operations
    # (preferring more symmetries)
    min_atoms_indices = sorted(min_atoms_indices, key=lambda k:
        len(spglib.get_symmetry_dataset(structures[k].get_ase())['rotations']),
        reverse = True)

    # Since the structures in each group are ordered with increasing number of atoms
    # we need to reorder just the first structures in the group
    for j in range(len(min_atoms_indices)):
        group_indices[j] = min_atoms_indices[j]

    output_dict = {'is_duplicate': is_duplicate,
                   structures[group_indices[0]].uuid:
                            [ structures[j].uuid for j in group_indices],
                   }
    
    return { 'output_parameters': ParameterData(dict=output_dict) }


def get_is_structure_duplicate_results(parameters=None,structure_ref=None,
                                            store=True,**kwargs):
    """
    Get the results from the is_structure_duplicate_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead the output dictionary of the previously
    launched function,
    - otherwise, launches the is_structure_duplicate_inline function
    and get its result.
    .. note:: (see rescale function) bug fixed in rescale function on 13/04/2017.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    
    inputs_list = sorted([v.pk for k,v in kwargs.iteritems()
                          if k.startswith('structure')])
    result_dict = None
    for ic in InlineCalculation.query(inputs=structure_ref).order_by('ctime'):
        ic_inputs_list = sorted([v.pk for k,v in ic.get_inputs_dict().iteritems()
                                 if k.startswith('structure') and not k.startswith('structure_ref')])
        try:
            if ( ic.get_function_name() == 'is_structure_duplicate_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), parameters.get_dict())
                 and ic.inp.structure_ref.pk == structure_ref.pk
                 and 'output_parameters' in ic.get_outputs_dict()
                 and ic_inputs_list==inputs_list):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    if result_dict is not None:
        print " is_structure_duplicate already run -> we do not re-run"
    else:
        print "Launch is_structure_duplicate_inline..."
        result_dict = is_structure_duplicate_inline(parameters=parameters,
                                                    structure_ref=structure_ref,
                                                    store=store,**kwargs)
    
    return result_dict

@optional_inline
def standardize_structure_inline(parameters, **kwargs):
    """
    Use the spglib python module to standardize a structure or a cif.

    :param parameters: a dictionary of the form
        {'symprec': the precision used to refine the symmetries of the
                    structure (float). Default=5e-3,
         'to_primitive': output primitive cell. Default=True,
         'no_idealize': disables to idealize lengths and angles of 
                        basis vectors and positions of atoms according
                        to crystal symmetry. Default=False,
         'converter': converter to get the structure from the cif, if
                      needed ('ase' or 'pymatgen'). Default='pymatgen'.
         }
    :param structure: the structure (StructureData) to analyse
    OR
    :param cif: the cif (CifData) to analyse

    .. note:: requires spglib with version >= 1.8.2.1
        (pip install --user spglib --upgrade)

    :return: {'standardized_structure': standardized primitive_structure}

    """
    try:
        structure = kwargs.pop('structure')
        if not isinstance(structure,StructureData):
            raise ValueError('input structure must of a StructureData')
        if 'cif' in kwargs:
            raise ValueError('cannot provide both a cif and a structure')
    except KeyError:
        structure = kwargs['cif']._get_aiida_structure(
            converter=parameters.get_dict().get('converter','pymatgen'),
            store=False)
    
    if sum(structure.pbc)==1:
        raise NotImplementedError("1D case not implemented")
    if sum(structure.pbc)==2 and structure.pbc[2]:
        raise NotImplementedError("2D case where 3rd axis is periodic is "
                                  "not implemented")
    
    try:
        import spglib
    except ImportError:
        from pyspglib import spglib
    import ase
    symprec = parameters.get_dict().get('symprec', 5e-3)
    to_primitive = int(parameters.get_dict().get('to_primitive', True))
    no_idealize = int(parameters.get_dict().get('no_idealize', False))

    structure_ase = structure.get_ase()

    try:
		(refined_cell,refined_pos,refined_atoms) = spglib.standardize_cell(
						structure_ase, to_primitive=to_primitive,
						no_idealize=no_idealize, symprec=symprec)
    except TypeError:
		# the spglib function returned None -> return a warning
		ParameterData = DataFactory('parameter')
		return {'output_parameters': ParameterData(dict={
			'warnings': ['spglib failed to return a standardized structure']
			})}

    # refine the cell
    standardized_structure_ase = ase.Atoms(cell=refined_cell,scaled_positions=refined_pos,
                                    numbers=refined_atoms,pbc=structure_ase.pbc)

    if (sum(structure_ase.pbc)==2 and
        abs(structure_ase.get_volume()-standardized_structure_ase.get_volume())<1e-2):
        # In that case we typically need to re-order the cell and sometimes rotate
        # the coordinate system to align the non-periodic axis with z
        
        # TODO: the case when the volume changes between primitive and initial,
        # in 2D, has to be implemented.
        import numpy as np
        try:
            from pymatgen.analysis.structure_matcher import StructureMatcher
        except ImportError:
            raise ImportError("For 2D case, pymatgen required. It can be"
                              " installed using pip: "
                              "(sudo) pip install pymatgen")
        sm = StructureMatcher(primitive_cell=False)
        std_structure = StructureData(ase=standardized_structure_ase)
        std_structure.pbc = [True]*3
        std_structure_pymat = std_structure.get_pymatgen_structure()
        structure_ase.set_pbc([True]*3)
        structure_pymat = StructureData(ase=structure_ase).get_pymatgen_structure()
        if not sm.fit(structure_pymat,std_structure_pymat):
            raise InternalError("Pb: initial and std structures should be identical!")
        the_std_structure_pymat = sm.get_s2_like_s1(structure_pymat,std_structure_pymat)
        standardized_structure_ase = StructureData(pymatgen=the_std_structure_pymat).get_ase()
        # if needed, rotate the coordinate system
        standardized_structure_ase.rotate(v=standardized_structure_ase.cell[2],
                                          a=[0,0,1],rotate_cell=True)
        # orient the axes to get a positive determinant
        if np.linalg.det(standardized_structure_ase.cell)<0:
            cell = standardized_structure_ase.cell
            the_cell = [-row if (i==2 and cell[2,2]<0) or 
                        (i==0 and cell[2,2]>0 and cell[0,0]<0) or
                        (i==1 and cell[2,2]>0 and cell[0,0]>0) else row
                            for i,row in enumerate(cell)]
            standardized_structure_ase.set_cell(the_cell)
        standardized_structure_ase.set_pbc([True,True,False])

    standardized_structure = StructureData(ase=standardized_structure_ase)

    return {'standardized_structure': standardized_structure}


def get_standardize_structure_results(parameters=None,store=True,
                                      print_progress=True,**kwargs):

    """
    Get the results from the standardize_structure_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead the output dictionary of the previously
    launched function,
    - otherwise, launches the standardize structure function
    and get its result.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    
    if 'structure' in kwargs:
        if 'cif' in kwargs:
            raise ValueError('cannot have both cif and structure as inputs')
        input_node = kwargs['structure']
        input_key = 'structure'
    if 'cif' in kwargs:
        input_node = kwargs['cif']
        input_key = 'cif'

    result_dict = None
    for ic in InlineCalculation.query(inputs=input_node).order_by('ctime'):
        try:
            if ( ic.get_function_name() == 'standardize_structure_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), parameters.get_dict())
                 and ic.get_inputs_dict().get(input_key,Node()).pk == input_node.pk
                 and ('standardized_structure' in ic.get_outputs_dict()
					  or 'output_parameters' in ic.get_outputs_dict())):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass

    if result_dict is not None:
        if print_progress:
			print " standardize_structure_inline already run for {} -> "\
				   "we do not re-run".format(input_node.pk)
    else:
        if print_progress:
			print "Launch standardize_structure_inline for {}...".format(input_node.pk)
        result_dict = standardize_structure_inline(parameters=parameters,
                                                   store=store,**kwargs)
    return result_dict


@make_inline
def primitive_structure_inline(parameters,cif):
    """
    OBSOLET (replaced by standardize_structure_inline)
    Use the spglib python module to find the primitive structure. 

    :param parameters: a dictionary of the form
        {'symprec': the precision used to refine the symmetries of the
                    structure (float),
         'converter': converter used to read the cif ('ase' or 'pymatgen')
         } 
    :param structure: the structure to analyse
    
    .. note:: requires spglib with version >= 1.8.2.1
        (pip install --user spglib --upgrade)
    
    :return: {'primitive_structure_spg': primitive_structure}

    """
    try:
        import spglib
    except ImportError:
        from pyspglib import spglib

    import ase
    symprec = parameters.get_dict()['symprec']
    converter = parameters.get_dict()['converter']

    structure_ase = cif._get_aiida_structure(converter=converter,
                                             store=False).get_ase()

    (refined_cell,refined_pos,refined_atoms)=spglib.refine_cell(structure_ase,
                                                                symprec=symprec)

    # refine the cell
    refined_structure_ase=ase.Atoms(cell=refined_cell,scaled_positions=refined_pos,
                                    numbers=refined_atoms,pbc=structure_ase.pbc)

    # get the primitive cell
    (prim_cell,prim_pos,prim_atoms)=spglib.find_primitive(refined_structure_ase,symprec = symprec)

    if not any([e is None for e in (prim_cell,prim_pos,prim_atoms)]):

        prim_structure_ase=ase.Atoms(cell=prim_cell,scaled_positions=prim_pos,
                                     numbers=prim_atoms,pbc=structure_ase.pbc)
        #print structure_ase.get_chemical_formula(), prim_structure_ase.get_chemical_formula()
    else:
        prim_structure_ase= refined_structure_ase

    primitive_structure = StructureData(ase=prim_structure_ase)
    
    return {'primitive_structure_spg': primitive_structure}


@optional_inline
def lowdimfinder_inline(structure, parameters):
    """
    Take an AiiDA structure and parameter for the LowDimFinder as 
    input and return the reduced structures and the group_data
    as output (default). Only reduced structure of the correct dimensionality 
    (from the 'target_dimensionality' parameter, see below) are output.
    More diverse and customized outputs can be 
    generated by setting the right parameter in the 'output' dictionary 
    to True (see below).
    List of supported parameters (with their default when applicable):: 
        { 'bond_margins': list of bond margins to test,
          'radii_offsets': list of additional offsets applied to the radii,
          'lowdim_dict': dictionary with lowdimfinder parameters,
          'target_dimensionality': the dimensionality of the reduced structured we want to keep,
          'output': {
                      'parent_structure_with_layer_lattice': True, (True to store the 3D 
                              structure with the same lattice as the layer - 2D only,
                              and requires lowdim_dict['orthogonal_axis_2D'] = False),
                      'rotated_parent_structure': True, (True to store the rotated 3D structure),
                      'group_data': True, (True to output the group_data from the lowdimfinder),
                      },
        
        }
    In output, all required structures are given, depending on the parameters
    set in the 'output' dictionary (see above). The resulting dictionary looks
    like:
        {'output_parameters': ParameterData with dictionary of the form
                    {'successful_bond_margins_and_radii_offsets': list of 
                                               tuples (margin,radii_offset) 
                                               that provided reduced structures 
                                               of the dimensionality looked for,
                     'all_dimensionalities_found': list of all dimensionalities
                                                   found in the process,
                     }
         'reduced_structure_[i]': i-th reduced structure found,
         'lowdimfinder_parameters_[i]': the lowdimfinder parameters used to find
                                        the 'reduced_structure_[i]',
         'group_data_[i]': (optional) ParameterData with group_data dictionary 
                           returned by the lowdimfinder corresponding 
                           to 'reduced_structure_[i]',
         'rotated_parent_structure_[i]': (optional) initial 3D structure rotated
                                         in the same way as 'reduced_structure_[i]'
                                         (e.g. with layer in x-y plane, for 2D),
         'layerlattice3D_structure_[i]': (optional) initial 3D structure cast into
                                         the same lattice as the 2D 'reduced_structure_[i]' found
        }
    .. note:: group_data is a dictionary with all data needed to reconstruct the reduced 
        dimensionality structures with any atomic representation tool.
        (positions, chemical symbols, cell, dimensionality). To reconstruct the 
        structure from group_data with ASE, you need to convert all unicode 
        chemical symbols into simple strings (with str function).
        
    """
    from aiida.tools.lowdimfinder import LowDimFinder
    try:
        import spglib
    except ImportError:
        from pyspglib import spglib
    from pymatgen.analysis.structure_matcher import StructureMatcher
    from aiida.common.exceptions import InternalError

    ParameterData = DataFactory('parameter')

    params_dict = parameters.get_dict()
    output_dict = params_dict.get('output', {
                        'parent_structure_with_layer_lattice': False,
                        'rotated_parent_structure': True,
                        'group_data': True,
                        })
    lowdim_dict = params_dict.get('lowdim_dict',{})
    bond_margins = params_dict['bond_margins']
    radii_offsets = params_dict['radii_offsets']
    target_dimensionality = params_dict['target_dimensionality']
    
    layered_2D_list = []
    output_reduced_structures = []
    output_rotated_3D_structures = []
    output_layer_lattice_3D_structures = []
    output_group_data = []
    output_lowdim_params = []
    output_parameters = {'successful_bond_margins_and_radii_offsets': [],
                         'all_dimensionalities_found': [],
                         }

    for bond_margin in bond_margins:
        for radii_offset in radii_offsets:

            low_dim_finder = LowDimFinder(
                                        aiida_structure=structure,
                                        bond_margin=bond_margin,
                                        radii_offset=radii_offset,
                                        max_supercell=3, min_supercell=3,
                                        **lowdim_dict)

            dimensionalities = low_dim_finder.get_group_data()['dimensionality']
            output_parameters['all_dimensionalities_found'] = list(
                set(output_parameters['all_dimensionalities_found'] + dimensionalities))
            
            reduced_structures = low_dim_finder.get_reduced_aiida_structures()
            layer_lattice_3D_structures = low_dim_finder._get_3D_structures_with_layer_lattice()
            rotated_3D_structures = low_dim_finder._get_rotated_structures()
        
            sm = StructureMatcher(1e-8,1e-8,1e-8,scale=False)
            if set(structure.pbc)!=set([True]):
                structure_tmp = structure.copy()
                structure_tmp.pbc=[True]*3
                pymatgen_structure = structure_tmp.get_pymatgen_structure()
            else:
                pymatgen_structure = structure.get_pymatgen_structure()
            
            for srot in rotated_3D_structures:
                if not sm.fit(srot.get_pymatgen_structure(),pymatgen_structure):
                    raise InternalError("Rotated 3D structure and initial "
                                        "structure do not match! (initial "
                                        "structure pk: {})".format(structure.pk))
            for slay in layer_lattice_3D_structures:
                if not sm.fit(slay.get_pymatgen_structure(),pymatgen_structure):
                    raise InternalError("3D structure with layer lattice and "
                                        "initial structure do not match! "
                                        "(initial structure pk: {})".format(structure.pk))
            
            layer_counter = 0
            for dimensionality, reduced_structure, rotated_structure in zip(
                    dimensionalities,reduced_structures,rotated_3D_structures):
                # re-order the sites (that's to avoid color differences
                # between 3D and 2D in vmd...)
                #reduced_structure._set_attr('sites',sorted(reduced_structure.get_attr('sites'),
                #                                           reverse=True))

                if dimensionality == target_dimensionality:
                    structure.label ="3D_with_{}D_substructure".format(dimensionality)
                    if ((bond_margin,radii_offset) not in 
                        output_parameters['successful_bond_margins_and_radii_offsets']):
                        output_parameters['successful_bond_margins_and_radii_offsets'].append(
                            (bond_margin,radii_offset))
                    
                    spacegroup = spglib.get_symmetry_dataset(
                            reduced_structure.get_ase())['number']
                            
                    if ( "{}_{}_{}".format(reduced_structure.get_formula(),
                        spacegroup,structure.pk) not in layered_2D_list ):

                        layered_2D_list.append("{}_{}_{}".format(
                            reduced_structure.get_formula(),spacegroup,
                            structure.pk))
                        reduced_structure.label = "{}D".format(dimensionality)
                        rotated_structure.label = "3D_rotated_with_{}D_substructure".format(dimensionality)
                        
                        output_reduced_structures.append(reduced_structure)
                        output_rotated_3D_structures.append(rotated_structure)
                        output_group_data.append(ParameterData(
                                    dict=low_dim_finder.get_group_data()))
                        output_lowdim_params.append(ParameterData(
                                    dict=low_dim_finder.params))

                        if dimensionality == 2 and layer_lattice_3D_structures:
                            layer_lattice_3D_structure = layer_lattice_3D_structures[layer_counter]
                            layer_lattice_3D_structure.label = "3D_with_2D_lattice"
                            output_layer_lattice_3D_structures.append(layer_lattice_3D_structure)
                            layer_counter += 1
    
    result_dict = {'output_parameters': ParameterData(dict=output_parameters)}
    
    for idx, lowdim_params in enumerate(output_lowdim_params):
        result_dict['lowdimfinder_parameters_{}'.format(idx)] = lowdim_params

    for idx, reduced_structure in enumerate(output_reduced_structures):
        result_dict['reduced_structure_{}'.format(str(idx))] = reduced_structure

    if output_dict.get('rotated_parent_structure',True):
        for idx, rotated_structure in enumerate(output_rotated_3D_structures):
            result_dict['rotated3D_structure_{}'.format(idx)] = rotated_structure

    if output_dict.get('parent_structure_with_layer_lattice', False):
        for idx, layer_lattice_structure in enumerate(output_layer_lattice_3D_structures):
            result_dict['layerlattice3D_structure_{}'.format(idx)] = layer_lattice_structure

    if output_dict.get('group_data', True):
        for idx, group_data in enumerate(output_group_data):
            result_dict['group_data_{}'.format(idx)] = group_data

    return result_dict


def get_lowdimfinder_results(structure=None,parameters=None,store=True):
    """
    Get the results from the lowdimfinder_inline function:
    - if there exists already an inline calculation with the same input structure
    and the same input parameters, it does not relaunch it, it gets instead 
    the output dictionary of the previously launched function,
    - otherwise, launches the lowdimfinder_inline function
    and gets its result.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    params_dict = parameters.get_dict()
    result_dict = None
    for ic in structure.get_outputs(InlineCalculation):
        try:
            if ( ic.get_function_name() == 'lowdimfinder_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), params_dict)
                 and 'output_parameters' in ic.get_outputs_dict() ):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    if result_dict is not None:
        print " lowdimfinder already run for structure {} with pk {} -> " \
              "we do not re-run".format(structure.get_formula(),structure.pk)
    else:
        print "Launch lowdimfinder for structure {} with pk {} ... " \
              "".format(structure.get_formula(),structure.pk)
        result_dict = lowdimfinder_inline(structure=structure,
                                          parameters=parameters,
                                          store=store)
    return result_dict


@optional_inline
def single_lowdimfinder_inline(structure, parameters):
    """
    Take an AiiDA structure and parameter for the LowDimFinder as 
    input and return the reduced structures and the group_data
    as output (default). Contrary to lowdimfinder_inline, a single
    lowdimfinder calculation is launched (no scan) and ALL reduced structures
    (including all dimensionalities) are returned.
    More diverse and customized outputs can be 
    generated by setting the right parameter in the 'output' dictionary 
    to True (see below).
    List of supported parameters (with their default when present):: 
        { 'lowdim_dict': dictionary with lowdimfinder parameters,
          'output': {
                      'parent_structure_with_layer_lattice': True, (True to store the 3D 
                              structure with the same lattice as the layer - 2D only,
                              and requires lowdim_dict['orthogonal_axis_2D'] = False),
                      'rotated_parent_structure': True, (True to store the rotated 3D structure),
                      },
        
        }
    In output, all required structures are given, depending on the parameters
    set in the 'output' dictionary (see above). The resulting dictionary looks
    like:
        {'group_data': ParameterData with group_data dictionary 
                        returned by the lowdimfinder,
         'reduced_structure_[i]': i-th reduced structure found,
         'rotated_parent_structure_[i]': (optional) initial 3D structure rotated
                                         in the same way as 'reduced_structure_[i]'
                                         (e.g. with layer in x-y plane, for 2D),
         'layerlattice3D_structure_[i]': (optional) initial 3D structure cast into
                                         the same lattice as the 2D 'reduced_structure_[i]' found
        }
    .. note:: group_data is a dictionary with all data needed to reconstruct the reduced 
        dimensionality structures with any atomic representation tool.
        (positions, chemical symbols, cell, dimensionality). To reconstruct the 
        structure from group_data with ASE, you need to convert all unicode 
        chemical symbols into simple strings (with str function).
        
    """
    from aiida.tools.lowdimfinder import LowDimFinder
    from pymatgen.analysis.structure_matcher import StructureMatcher
    from aiida.common.exceptions import InternalError

    ParameterData = DataFactory('parameter')
    sm = StructureMatcher(1e-8,1e-8,1e-8,scale=False)
    if set(structure.pbc)!=set([True]):
        structure_tmp = structure.copy()
        structure_tmp.pbc=[True]*3
        pymatgen_structure = structure_tmp.get_pymatgen_structure()
    else:
        pymatgen_structure = structure.get_pymatgen_structure()
    
    params_dict = parameters.get_dict()
    lowdim_dict = params_dict.get('lowdim_dict',{})
    output_dict = params_dict.get('output', {
                        'parent_structure_with_layer_lattice': False,
                        'rotated_parent_structure': False,
                        })
    
    low_dim_finder = LowDimFinder(
                                aiida_structure=structure,
                                **lowdim_dict)
    
    group_data = low_dim_finder.get_group_data()
    reduced_structures = low_dim_finder.get_reduced_aiida_structures()

    result_dict = {'group_data': ParameterData(dict=group_data)}
    
    for idx, reduced_structure in enumerate(reduced_structures):
        result_dict['reduced_structure_{}'.format(str(idx))] = reduced_structure

    if output_dict.get('rotated_parent_structure',False):
        rotated_3D_structures = low_dim_finder._get_rotated_structures()
        for idx, rotated_structure in enumerate(rotated_3D_structures):
            if not sm.fit(rotated_structure.get_pymatgen_structure(),pymatgen_structure):
                raise InternalError("Rotated 3D structure and initial "
                                    "structure do not match! (initial "
                                    "structure pk: {})".format(structure.pk))
            result_dict['rotated3D_structure_{}'.format(idx)] = rotated_structure

    if output_dict.get('parent_structure_with_layer_lattice', False):
        layer_lattice_3D_structures = low_dim_finder._get_3D_structures_with_layer_lattice()
        for idx, layer_lattice_structure in enumerate(layer_lattice_3D_structures):
            if not sm.fit(layer_lattice_structure.get_pymatgen_structure(),pymatgen_structure):
                raise InternalError("3D structure with layer lattice and "
                                    "initial structure do not match! "
                                    "(initial structure pk: {})".format(structure.pk))
            result_dict['layerlattice3D_structure_{}'.format(idx)] = layer_lattice_structure

    return result_dict


def get_single_lowdimfinder_results(structure=None,parameters=None,store=True):
    """
    Get the results from the single_lowdimfinder_inline function:
    - if there exists already an inline calculation with the same input structure
    and the same input parameters, it does not relaunch it, it gets instead 
    the output dictionary of the previously launched function,
    - otherwise, launches the single_lowdimfinder_inline function
    and gets its result.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    params_dict = parameters.get_dict()
    result_dict = None
    for ic in structure.get_outputs(InlineCalculation):
        try:
            if ( ic.get_function_name() == 'single_lowdimfinder_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), params_dict)
                 and 'group_data' in ic.get_outputs_dict() ):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    if result_dict is not None:
        print " single_lowdimfinder already run for structure {} with pk {} -> " \
              "we do not re-run".format(structure.get_formula(),structure.pk)
    else:
        print "Launch single_lowdimfinder for structure {} with pk {} ... " \
              "".format(structure.get_formula(),structure.pk)
        result_dict = single_lowdimfinder_inline(structure=structure,
                                                 parameters=parameters,
                                                 store=store)
    return result_dict


@optional_inline
def change_vacuum_space_inline(structure,parameters):
    """
    Take a 2D structure with a certain vacuum_space and change
    it to another length.
    :param structure: 2D structure
    :param parameters: ParameterData containing a dictionary with
        'original_vacuum_space' and 'new_vacuum_space' 
    :return: dictionary of the form
        {'output_structure': 2D structure with 'new_vacuum_space',
         'output_parameters': ParameterData giving the thickness of the layer
         }

    .. note:: As long as the vacuum_space is positive the atoms won't 
        be scaled. Simply a certain distance between the layers, defined
        by the vacuum_space, is set between the layers. If the 
        vacuum_space is negative, the output layer will be thinner
        than the original layer and the atoms will be scaled 
        respectively. 

    """
    import numpy as np
    ParameterData = DataFactory('parameter')

    original_vacuum_space = parameters.get_dict()['original_vacuum_space']
    new_vacuum_space =  parameters.get_dict()['new_vacuum_space']
    cell = structure.cell

    # get vector orthogonal to layer
    normal_vec = np.cross(cell[0], cell[1])
    unit_normal_vec = normal_vec/np.linalg.norm(normal_vec)

    # height of cell (normal to the layer)
    height = abs(np.dot(unit_normal_vec, cell[2]))

    # thickness of original layer
    thickness = height - original_vacuum_space

    # new height of the unit cell (normal to the layer)
    new_height = thickness + new_vacuum_space
    if new_height <= 0.:
        # cannot build a valid structure in that case
        return {'output_structure': None,
                'output_parameters': ParameterData(dict={
                        'layer_thickness': thickness,
                        'layer_thickness_units': 'angstrom',        
                        }),
                }

    # normalize vector 
    n_3 = cell[2]/np.linalg.norm(cell[2])
    
    # absolute cosine between third cell vector and normal vector
    # (1 only if third axis is orthogonal to the layer)
    cosine = abs(np.dot(n_3, unit_normal_vec))
    new_length_of_3rd_vector = new_height / cosine

    new_structure = structure.copy()
    new_cell = [cell[0], cell[1], new_length_of_3rd_vector  * n_3]
    positions = structure.get_ase().positions #should be simpler?
    
    if new_vacuum_space > 0:
        # do not change the distance between the atoms
        # put atoms back in the middle of the cell 
        new_positions = positions - (original_vacuum_space-new_vacuum_space) / (cosine*2.) *n_3
    else:
        # new cell smaller than original cell --> scale atoms 
        asestruc = structure.get_ase()
        positions = asestruc.get_positions()
        original_cell = [cell[0], cell[1], n_3 * thickness / cosine]
        # set cell back to original thickness
        asestruc.set_cell(original_cell)
        asestruc.set_positions(positions - original_vacuum_space / (cosine*2.) *n_3)
        # scale atoms depending on the size of the original cell
        asestruc.set_cell(new_cell, scale_atoms=True)
        new_positions = asestruc.get_positions()

    new_structure.set_cell(new_cell)
    new_structure.reset_sites_positions(new_positions)

    result_dict = {'output_structure': new_structure,
                   'output_parameters': ParameterData(dict={
                        'layer_thickness': thickness,
                        'layer_thickness_units': 'angstrom',        
                        }),
                   }

    return result_dict


def numbers_are_equal(a,b,epsilon=1e-14):
    """
    Compare two numbers a and b within epsilon.
    :param a: float, int or any scalar
    :param b: float, int or any scalar
    :param epsilon: threshold above which a is considered different from b
    :return: boolean
    """
    return abs(a-b) < epsilon


def scalars_are_equal(a,b,**kwargs):
    """
    Compare two objects of any type, except list, arrays or dictionaries.
    Numbers are compared thanks to the ``numbers_are_equal`` function.
    :param a: any scalar object
    :param b: any scalar object
    :param kwargs: parameters passed to the function numbers_are_equal
    :return: boolean
    :raise: NonscalarError if either a or b is a list, an array or a dictionary
    """
    from numpy import isscalar
    from numbers import Number
    if isscalar(a) and isscalar(b):
        if isinstance(a,Number):
            return isinstance(b,Number) and numbers_are_equal(a,b,**kwargs)
        else:
            return a==b
    elif (a is None) or (b is None):
        return a==b
    else:
        raise TypeError("a and b must be scalars")


def objects_are_equal(obj1,obj2,**kwargs):
    """
    Recursive function.
    Return True if obj1 is the same as obj2. Scalars are
    compared using the function ``scalars_are_equal``.
    Handles strings, floats, ints, booleans, as well as lists, arrays and
    dictionaries containing such objects (possibly nested).
    :param obj1: any object
    :param obj2: any object
    :param kwargs: parameters passed to the function scalars_are_equal
    :return: boolean
    """
    import numpy as np
    
    if isinstance(obj1,dict):
        if not isinstance(obj2,dict):
            return False
        obj1_keys = sorted(obj1.keys())
        obj2_keys = sorted(obj2.keys())
        if not objects_are_equal(obj1_keys,obj2_keys,**kwargs):
            return False
        if not objects_are_equal([obj1[k] for k in obj1_keys],
                                 [obj2[k] for k in obj2_keys],**kwargs):
            return False
        return True
        
    elif isinstance(obj1,list) or (isinstance(obj1,np.ndarray)
                                   or isinstance(obj1,tuple)):
        if not (isinstance(obj2,list) or (isinstance(obj2,np.ndarray) 
                                          or isinstance(obj2,tuple))):
            return False
        if len(obj1) != len(obj2):
            return False
        for e1,e2 in zip(obj1,obj2):
            if np.isscalar(e1):
                if not np.isscalar(e2):
                    return False
                elif not scalars_are_equal(e1,e2,**kwargs):
                    return False
            else:
                if not objects_are_equal(e1,e2,**kwargs):
                    return False
        return True

    else:
        try:
            return scalars_are_equal(obj1,obj2,**kwargs)
        except TypeError:
            raise TypeError("Type of obj1 and obj2 not recognized")


def objects_set(objects,**kwargs):
    """
    Return a set made of objects compared between them using the
    'objects_are_equal' function
    :param objects: an iterable containing any kind of objects that can
        be compared using the 'objects_are_equal' function (list, dict, etc.)
    :param kwargs: additional keyword arguments to be passed to the
        'objects_are_equal' function (e.g. precision for floating point number)
    :return: a set of non-equal objects
    """
    the_set = []
    for obj in objects:
        if len([o for o in the_set if objects_are_equal(obj,o,**kwargs)])==0:
            the_set.append(obj)
    
    return the_set
    

def calculation_inputs_contain_kwargs(calculation, **kwargs):
    """
    Compare the input of a stored calculation with a list of DataNodes
    :param calculation: A stored calculation
    :param kwargs: dictionary of StructureData, KpointsData, ParameterData
        and pseudo family names
    :return: boolean
    """
    KpointsData = DataFactory('kpoints')
    ParameterData = DataFactory('parameter')
    UpfData = DataFactory('upf')

    for kwarg in kwargs:
        data_type = type(kwarg)
        calculation_inputs = calculation.get_inputs(data_type)

        # structure -> simply compare pks
        if data_type == StructureData:
            uuids = [calc_input.uuid for calc_input in calculation_inputs]
            if kwarg.uuid not in uuids:
                return False

        elif data_type == KpointsData:
            try:
                kpoints = kwarg.get_kpoints_mesh()
            except AttributeError:
                kpoints = kwarg.get_kpoints()
                
            try:
                calc_input_kpoints = calculation_inputs[0].get_kpoints_mesh()
            except AttributeError:
                calc_input_kpoints = calculation_inputs[0].get_kpoints()

            is_equal = objects_are_equal(kpoints, calc_input_kpoints)
            if not is_equal:
                return False

        elif data_type == ParameterData:
            params_dict = kwarg.get_dict()
            is_equal = False
            for input in calculation_inputs:
                input_dict = input.get_dict()
                is_equal = objects_are_equal(params_dict, input_dict)
                if is_equal:
                    break
            if not is_equal:
                return False
                
        # check pseudofamily
        elif data_type == basestring:
            calculation_inputs = calculation.get_inputs(UpfData)
            for calculation_input in calculation_inputs:
                if not kwarg in calculation_input.get_upf_family_names():
                    return False

        else:
            return False

    return True
