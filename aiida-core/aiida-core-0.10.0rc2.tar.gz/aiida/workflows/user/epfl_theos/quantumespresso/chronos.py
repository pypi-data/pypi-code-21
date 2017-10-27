# -*- coding: utf-8 -*-

from aiida.orm.workflow import Workflow
from aiida.orm import JobCalculation, DataFactory, Group, CalculationFactory,\
                      load_node, Code
try:
    from aiida.backends.djsite.db import models
except ImportError:
    from aiida.djsite.db import models
from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow,_default_nspin_from_QE
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos.dbimporters.utils import scalars_are_equal,objects_are_equal
from aiida.common.example_helpers import test_and_get_code
from aiida.orm.calculation.inline import make_inline,optional_inline,InlineCalculation
from random import uniform,randint
import numpy as np
from copy import deepcopy
from aiida.common.exceptions import InternalError

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet."


ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
BandsData = DataFactory('array.bands')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')

_default_QE_etot_conv_thr = 1e-4
_default_QE_conv_thr = 1e-6


def get_pw_mag_wfs_with_parameters(wf_params,ignored_keys=['codename','group_name',
                                'calculation_set','settings','vdw_table',
                                'input|automatic_parallelization',
                                'input|clean_workdir','input|max_restarts',
                                'parameters|ELECTRONS|electron_maxstep',
                                #'parameters|ELECTRONS|mixing_beta',
                                #'parameters|ELECTRONS|mixing_mode',
                                'parameters|ELECTRONS|diagonalization',
                                ]):
    """
    TODO: deal better with the key 'vdw_table' (now it is simply ignored...)
    Find all PwWorkflow already run with the same parameters. Take out the
    one that is non spin-polarized and return it separately
    :param wf_params: a dictionary with all the parameters (can contain
        dictionaries, structure and kpoints)
    :param ignored_keys: list of keys of wf_params that are ignored in the 
        comparison (a '|' means descending into a sub-dictionary)
    :return: a tuple with the list of workflows with magnetization included, 
        and the wf with zero magnetization (None if none could be found).
    """
    the_params = deepcopy(wf_params)
    helpers.take_out_keys_from_dictionary(the_params,ignored_keys)
    _ = the_params['parameters']['SYSTEM'].pop('nspin',None)
    _ = the_params['parameters']['SYSTEM'].pop('starting_magnetization',None)
    structure_ref = the_params.pop('structure')
    kpoints_ref = the_params.pop('kpoints',None)
    if kpoints_ref:
        try:
            kpoints_ref = kpoints_ref.get_kpoints_mesh()
        except AttributeError:
            kpoints_ref = kpoints_ref.get_kpoints()
    
    wfs_pw = helpers.get_wfs_with_parameter(structure_ref,'PwWorkflow')
    zero_mag_wf = None
    mag_wfs = []
    for wf_pw in wfs_pw:
        if 'pw_calculation' in wf_pw.get_results():
            params = wf_pw.get_parameters()
            helpers.take_out_keys_from_dictionary(params,ignored_keys+['structure'])
            kpoints = params.pop('kpoints',None)
            if kpoints:
                try:
                    kpoints = kpoints.get_kpoints_mesh()
                except AttributeError:
                    kpoints = kpoints.get_kpoints()
            
            if objects_are_equal(kpoints,kpoints_ref):
                nspin = params['parameters']['SYSTEM'].pop('nspin',_default_nspin_from_QE)
                start_mag = params['parameters']['SYSTEM'].pop('starting_magnetization',0.)
                
                if objects_are_equal(the_params,params):
                    if nspin==1 and start_mag==0.:
                        zero_mag_wf = wf_pw
                    elif nspin==2 and start_mag:
                        mag_wfs.append(wf_pw)
    
    return mag_wfs, zero_mag_wf


@optional_inline
def prepare_structure_with_all_independent_atoms_inline(structure,parameters):
    """
    OBSOLET.
    Create a structure with different kind names set to all 
    individual atoms. Each structure is a supercell of the initial 
    structure (only the periodic dimensions are increased in the 
    supercell(s) ).
    
    :param structure: the initial structure
    :param parameters: ParameterData with key 'size_supercell'
        which gives the supercell size in each periodic dimension.
    :return: a dictionary of the form
        {'indpt_atoms_structure': the_structure}
    """
    import string
    
    # string with all alphanumeric characters + underscore
    chars = string.digits + string.ascii_letters + '_'
    # construct supercell
    size_supercell = parameters.get_dict()['size_supercell']
    supercell_shape = tuple([size_supercell if _ else 1 for _ in structure.pbc])
    supercell = StructureData(ase=structure.get_ase()*supercell_shape)
    the_structure = StructureData(cell=supercell.cell,pbc=structure.pbc)
    # build dictionary with kinds and numbers of atoms found with each kind 
    kinds_set = set(supercell.get_site_kindnames())
    kinds_dict = dict(zip(kinds_set,[0]*len(kinds_set)))
    for si in supercell.sites:
        new_kind_name = "{}{}".format(si.kind_name,chars[kinds_dict[si.kind_name]])
        the_structure.append_atom(position=si.position,name=new_kind_name,
                            symbols=structure.get_kind(si.kind_name).symbol)
        kinds_dict[si.kind_name] += 1

    return {'indpt_atoms_structure': the_structure}


@optional_inline
def prepare_all_magnetic_structures_inline(parameters,structure):
    """
    Create structures with two different kind names for each kind of atoms, in 
    order to test possible antiferromagnetic (or more generally ferrimagnetic) states.
    Structures are generated with pymatgen and enumlib, with different spin
    signs associated to atoms of the same specie, i.e. duplicating the species.
    The final set of structures depend on an order_parameter (0.5 for antiferromagnetism, 
    but it can be 0.25, or anything between 0 and 1, for ferrimagnetic states).
    Since enumlib cannot generate supercells when more than 2 species are duplicated,
    we limit ourselves to only 2 species. See the class MagOrderingTransformation in
    https://github.com/materialsproject/pymatgen/blob/master/pymatgen/transformations/advanced_transformations.py,
    for more details.
    
    .. note:: requires pymatgen (version 3.3.5) and the enumlib code from 
        https://github.com/msg-byu/enumlib):
        - compile enum.x and makestr.x
        - then you need to change the pymatgen source code (typically in
            /usr/local/lib/python2.7/dist-packages/pymatgen/command_line/enumlib_caller.py):
            line 61, change
            enum_cmd = which('multienum.x')
            into
            enum_cmd = which('enum.x')
    
    .. note:: in non-periodic directions, one does not build a supercell.
    
    .. note:: a previous version (buggy) was called 'prepare_magnetic_structures_inline'
    
    :param parameters: a ParameterData object with a dictionary containing
        {'order_parameter': a number between 0 and 1 (0.5 for antiferromagnetic states),
         'species': list of species names to be duplicated (should not be more than 2),
         'max_supercell_size': the maximum supercell size,
         'max_number_of_structures': the maximum number of structures to be generated
                                     (default: 1000),
         'symprec': the precision of the symmetry refinement for spglib (when used)
                    (default: 5e-3),
         'extract_primitive': True to extract primitive cell after 
                              generation of the new structures (3D only)
                              (default: True),
         'preserve_xy_plane': True to preserve the xy plane within the two
                              first lattice vectors, if possible (3D only)
                              (default: False),
         }
    :param structure: the initial structure
    :return: a dictionary of the form
        {'output_parameters': ParameterData object containing {'warnings': list of warnings},
         'output_fm_structure' (if present): ferromag. structure with the cell of the
                                first afm structure (for better energy comparison).
                                Absent if first afm structure has the same cell
                                as the initial structure (because then the
                                initial structure can be used),
         'output_afm_structure_0': first antiferromag. structure,
         'output_afm_structure_1': second antiferromag. structure,
         etc.}
    """
    from pymatgen.transformations.advanced_transformations import MagOrderingTransformation
    try:
        import spglib
    except ImportError:
        from pyspglib import spglib
    import ase,traceback
    from aiida.workflows.user.epfl_theos.dbimporters.utils import group_similar_structures
    epsilon = 1e-4 # accuracy of the comparisons
    
    def get_refined_structure_with_spins(structure,symprec=5e-3,primitive=True):
        """
        Get a refined structure (optionally primitive) using spglib, 
        from a structure that has various spins
        .. note:: this refinement is useless! (and it changes
        the coordinate system)
        """
        if max(structure.get_ase().numbers)>=93:
            raise ValueError("Case when actinides above U are present in the"
                              " structure is not implemented")
        structure_ase = structure.get_ase()
        # translate ase structure into 'equivalent' structure without tags,
        # replacing species with tags with super heavy actinides
        # (dirty trick to be able to deal with it in spglib)
        numbers_tags_spins = set([(n,t) for n,t in zip(structure_ase.numbers,
                                                   structure_ase.get_tags()) if t!=0])
        artificial_numbers = range(93,93+len(numbers_tags_spins)+1) # to replace species with spin
        numbers_dict = dict([((n,t),a) for (n,t),a in
                             zip(numbers_tags_spins,
                                 artificial_numbers[:len(numbers_tags_spins)])]
                            +[((n,t),n) for (n,t) in zip(structure_ase.numbers,
                                                         structure_ase.get_tags()) if t==0])
        inverse_numbers_dict = dict([(a,(n,t)) for (n,t),a in 
                                     zip(numbers_tags_spins,
                                         artificial_numbers[:len(numbers_tags_spins)])]
                        +[(n,(n,t)) for (n,t) in zip(structure_ase.numbers,
                                                     structure_ase.get_tags()) if t==0])
        the_numbers = [numbers_dict[(n,t)] for n,t in zip(structure_ase.numbers,
                                                          structure_ase.get_tags())]
        the_ase = ase.Atoms(cell=structure_ase.cell,
                            scaled_positions=structure_ase.get_scaled_positions(),
                            pbc=structure_ase.pbc,numbers=the_numbers)
        # refine and get primitive cell
        (refined_cell,refined_pos,refined_atoms)=spglib.refine_cell(the_ase,
                                                                    symprec=symprec)
        refined_structure_ase = ase.Atoms(cell=refined_cell,scaled_positions=refined_pos,
                                        numbers=refined_atoms,pbc=structure_ase.pbc)
        prim_structure_ase = refined_structure_ase
        if primitive:
            (prim_cell,prim_pos,prim_atoms)=spglib.find_primitive(refined_structure_ase,
                                                                  symprec = symprec)
            if not any([e is None for e in (prim_cell,prim_pos,prim_atoms)]):
                prim_structure_ase = ase.Atoms(cell=prim_cell,scaled_positions=prim_pos,
                                         numbers=prim_atoms,pbc=structure_ase.pbc)
                #print structure_ase.get_chemical_formula(), prim_structure_ase.get_chemical_formula()
        # translate back into initial structure with spins
        the_numbers,the_tags = zip(*[inverse_numbers_dict[n] 
                                     for n in prim_structure_ase.numbers])
        the_structure_ase = ase.Atoms(cell=prim_structure_ase.cell,
                                    scaled_positions=prim_structure_ase.get_scaled_positions(),
                                    pbc=prim_structure_ase.pbc,
                                    numbers=the_numbers,tags=the_tags)
        primitive_structure = StructureData(ase=the_structure_ase)
        
        return primitive_structure					

    def order_cell_2D(structure,trans_mat,epsilon=1e-4,force_orthogonal=False):
        """
        Re-order the lattice vectors to put the out-of-plane one in the end
        -> this preserves the xy plane for 2D & layered structures
        """
        #out-of-plane lattice vector
        oop_vector = [row.tolist() for row in trans_mat if abs(row[2])>epsilon]
        oop_vector[0][2] = abs(oop_vector[0][2])
        if force_orthogonal:
            if len(oop_vector)!=1:
                raise InternalError("Cannot force orthogonality if there "
                                     "are several out-of-plane vectors")
            # force orthogonal out-of-plane axis (translate periodic image of 
            # the 2D structure)
            oop_vector[0][:2] = [0., 0.]
        # in-plane lattice vectors
        ip_vectors = [row.tolist() for row in trans_mat if abs(row[2])<=epsilon]
        the_trans_mat = np.array(ip_vectors+oop_vector)
        if the_trans_mat.shape != (3,3):
            raise ValueError("Can't find a proper supercell")
        if np.linalg.det(the_trans_mat) < 0:
            # flip the two in-plane vectors
            the_trans_mat = np.array(ip_vectors[::-1]+oop_vector)
        if abs(np.linalg.det(the_trans_mat)-round(np.linalg.det(the_trans_mat)))>epsilon:
            raise InternalError("Supercell does not contain an integer number of "
                                "the initial cell",np.linalg.det(the_trans_mat))
        structure.reset_cell((the_trans_mat.dot(cell)).tolist())

    params_dict = parameters.get_dict()
    symprec = params_dict.get('symprec',5e-3)
    warnings = []
    if not params_dict['species']:
        warnings.append("There are no species to be assigned spins")
        return {'output_parameters': ParameterData(dict={'warnings': warnings})}
    
    # initial checks on the structure cell and its dimensionality
    cell = np.array(structure.cell)
    pbc = list(structure.pbc)
    if sum(pbc)==1:
        if pbc != [False,False,True] or (not all(np.abs(cell[:2,2])<=epsilon)
            or not all(np.abs(cell[2,:2])<=epsilon)):
            raise ValueError("Initial 1D structure should have its axis along the"
                             " third lattice vector and along z, and the two "
                             "first lattice vectors perpendicular to it")    
    elif sum(pbc)==2:
        if pbc != [True,True,False] or not all(np.abs(cell[:2,2])<=epsilon):
            raise ValueError("Initial 2D structure should have its 2D plane made "
                             "by the first two lattice vectors, and in the x-y "
                             "plane")    
    
    structure_tmp = structure.copy()
    structure_tmp.pbc = [True]*3
    structure_pymatgen = structure_tmp.get_pymatgen_structure()

    species_dict = dict([(sp,1) for sp in params_dict['species']])
    order = params_dict['order_parameter']
    min_cell_size = MagOrderingTransformation.determine_min_cell(
            structure_pymatgen,species_dict,order)
    if min_cell_size > params_dict['max_supercell_size']:
        warnings.append("Cannot run enumlib: max_supercell_size is "
                        "smaller than minimum cell size for enumeration")
        return {'output_parameters': ParameterData(dict={'warnings': warnings,
                                                          'min_cell_size': min_cell_size})}
    mag_order_trans = MagOrderingTransformation(species_dict,max_cell_size=min(
            min_cell_size,params_dict['max_supercell_size']))
    try:
        enum_mag = mag_order_trans.apply_transformation(
            structure_pymatgen,params_dict.get('max_number_of_structures',1000))
    except (TypeError,ValueError) as e:
        warnings.append("enumlib failed (probably because the number of elements "
                        "to be assigned spins is too high)")
        warnings.append(e.message)
        warnings.extend(traceback.format_exc().split('\n'))
        return {'output_parameters': ParameterData(dict={'warnings': warnings,
                                                          'min_cell_size': min_cell_size})}
    
    # generate the structures with spins
    structures = []
    for e in enum_mag:
        structure_tmp=StructureData(pymatgen_structure=e['structure'])
        #print structure_tmp.get_formula(),structure_tmp.cell
        # screen out cells that contain two layers or more -> find them
        # by checking the third column of the transformation matrix between 
        # the initial structure and this one
        # compute transformation matrix between initial cell and the magnetic one
        trans_mat = np.array(structure_tmp.cell).dot(np.linalg.inv(np.array(cell)))
        if sum(pbc)==3:
            # 3D case
            if (not params_dict.get('preserve_xy_plane',False) and 
                params_dict.get('extract_primitive',True)):
                # we take the primitive, although it's not clear it's needed
                # (in a rare cases we get a smaller structure...)
                primitive_structure = get_refined_structure_with_spins(structure_tmp,symprec,primitive=True)
                structures.append(primitive_structure)
            else:#if params_dict.get('preserve_xy_plane',False):
                # we cannot take the primitive cell when we want to keep
                # the xy plane, because it would change the cartesian 
                # coordinates system and mess up the recognition of the
                # z-axis
                # cell refinement is useless!! we suppressed it
                #refined_structure = get_refined_structure_with_spins(structure_tmp,symprec,primitive=False)
                #trans_mat = np.array(refined_structure.cell).dot(np.linalg.inv(np.array(cell)))
                order_cell_2D(structure_tmp,trans_mat,epsilon=epsilon,force_orthogonal=False)
                structures.append(structure_tmp)
            #else:
            #    refined_structure = get_refined_structure_with_spins(structure_tmp,symprec,primitive=False)
            #    structures.append(refined_structure)
            
        elif sum(pbc)==2 and all([abs(e)<=1+epsilon for e in trans_mat[:,2]]):
            # 2D case (structure should not contain more than one cell in
            # out-of-plane direction)
            order_cell_2D(structure_tmp,trans_mat,epsilon=epsilon,force_orthogonal=True)
            structures.append(structure_tmp)
            
        elif sum(pbc)==1:
            # 1D case (structure should not contain more than one cell except
            # in the 1D direction)
            # check that the projection of any two lattice vectors of the new cell
            # onto the x-y plane (perpendicular to the 1D axis) has not changed area
            xy_area_ratio = [abs(np.linalg.det(np.array([row[:2] for i,row 
                                                         in enumerate(trans_mat)
                                                         if i!=j]))) for j in range(3)]
            if all([a<=1+epsilon for a in xy_area_ratio]):
                # vector along the 1D axis
                axis_vector = [row.tolist() for row,a in zip(trans_mat,xy_area_ratio)
                                if abs(a)>epsilon]
                # other perpendicular vectors
                perp_vectors = [row.tolist() for row,a in zip(trans_mat,xy_area_ratio)
                                if abs(a)<=epsilon]
                # force perpendicular vectors to be orthogonal to the 1D axis 
                # (translate periodic image of the 1D structure)
                perp_vectors[0][2] = 0.
                perp_vectors[1][2] = 0.
                the_trans_mat = np.array(perp_vectors+axis_vector)
                if the_trans_mat.shape != (3,3):
                    raise ValueError("Can't find a proper supercell")
                if np.linalg.det(the_trans_mat) < 0:
                    # flip the first two vectors
                    the_trans_mat = np.array(perp_vectors[::-1]+axis_vector)
                if abs(np.linalg.det(the_trans_mat)-round(np.linalg.det(the_trans_mat)))>epsilon:
                    raise InternalError("Supercell does not contain an integer number of "
                                        "the initial cell",np.linalg.det(the_trans_mat))
                structure_tmp.reset_cell((the_trans_mat.dot(cell)).tolist())
                structures.append(structure_tmp)
                
        elif sum(pbc)==0:
            if abs(abs(np.linalg.det(trans_mat))-1)<=epsilon:
                structures.append(structure_tmp)
        #print structure_tmp.get_formula(),structure_tmp.cell,"\n",\
        #      "\n".join([site.__str__() for site in sorted(structure_tmp.sites,
        #            key=lambda x: (structure_tmp.get_kind(x.kind_name).symbol,
        #                           x.position))])
    if not structures:
        warnings.append("No new structures found (probably supercells were all"
                        " along the out-of-plane direction)")
    
    output_params_dict = {'warnings': warnings,'min_cell_size': min_cell_size}
    result_dict = {}
    
    if structures:
        # take away redundant structures
        all_groups_indices, _ = group_similar_structures(structures,epsilon,epsilon,epsilon)
        unique_structures = [structures[i[0]] for i in all_groups_indices]
        for s in unique_structures:
            s.pbc = pbc
        # Take the first afm structure and suppress all the spin 'tags' (to have 
        # the same kpoints grid for a ferromag calc. and a non spin-polarized calc.)
        # We do it only if the initial cell is not the same as any of the
        # afm structures.
        if not any([objects_are_equal(s.cell,structure.cell,epsilon=epsilon)
            for s in unique_structures]):
            s_ase = unique_structures[0].get_ase()
            s_ase.set_tags([0]*s_ase.get_number_of_atoms())
            fm_structure = StructureData(ase=s_ase)
            result_dict['output_fm_structure'] = fm_structure
        else:
            output_params_dict['same_cell_as_fm_structure'] = True
            
        result_dict['output_parameters'] = ParameterData(dict=output_params_dict)
        result_dict.update(dict([("output_afm_structure_{}".format(i),s) for i,s in enumerate(
                        unique_structures)]))
    
    return result_dict

def get_prepare_magnetic_structures_results(parameters=None,structure=None,
    check_also_outputs=True):
    """
    Get the results from the prepare_magnetic_structures_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead the output dictionary of the previously
    launched function,
    - otherwise, launches the prepare_magnetic_structures_inline function
    and get its result.
    """    
    result_dict = None
    for ic in InlineCalculation.query(inputs=structure).order_by('ctime'):
        try:
            if ( ic.get_function_name() == 'prepare_all_magnetic_structures_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), parameters.get_dict())
                 and ic.inp.structure.uuid == structure.uuid
                 and 'output_parameters' in ic.get_outputs_dict()):
                if not check_also_outputs:
                    result_dict = ic.get_outputs_dict()
                else:
                    epsilon = 1e-8
                    from aiida.workflows.user.epfl_theos.dbimporters.utils import objects_set
                    ic_result_dict = ic.get_outputs_dict()
                    tmp_result_dict = prepare_all_magnetic_structures_inline(
                        parameters=parameters,structure=structure, store=False)
                    tmp_cells = [v.cell for k,v in tmp_result_dict.items()
                                           if 'structure' in k]
                    ic_cells = [v.cell for k,v in ic_result_dict.items()
                                           if 'structure' in k and k.count('_')==3]
                    tmp_ic_dup_cells = [objects_are_equal(objects_set(tmp_cells,epsilon=epsilon),
                                        objects_set(tmp_cells+[c],epsilon=epsilon),epsilon=epsilon)
                                        for c in ic_cells]
                    ic_tmp_dup_cells = [objects_are_equal(objects_set(ic_cells,epsilon=epsilon),
                                        objects_set(ic_cells+[c],epsilon=epsilon),epsilon=epsilon)
                                        for c in tmp_cells]
                    if (objects_are_equal(tmp_result_dict['output_parameters'].get_dict(),
                        ic.out.output_parameters.get_dict()) and
                        all(tmp_ic_dup_cells) and all(ic_tmp_dup_cells)
                        and len(tmp_cells)==len(ic_cells)):
                        result_dict = ic_result_dict
                        
        except AttributeError:
            pass
    
    #if result_dict is not None:
    #    print "prepare_magnetic_structures_inline already run -> we do not re-run"
    if result_dict is None:
        #print "Launch prepare_magnetic_structures_inline..."
        result_dict = prepare_all_magnetic_structures_inline(
                    parameters=parameters,structure=structure, store=True)
    
    return result_dict

@make_inline
def sort_energy_calcs_inline(parameters,**kwargs):
    """
    Sort a set of energy calcs outputs by increasing energy. When energies are equal
    within a given tolerance, sort by increasing complexity of the input
    structures, i.e. considering first the lowest number atoms, of species and 
    of spins.
    :param parameters: a ParameterData object with a dictionary of the form
        {'epsilon': tolerance in the energy (in eV/atom) for energy differences
                    to be considered significant
         }
    :kwargs: ParameterData objects with the output of the energy (pw) calculations
    :return: a dictionary of the form:
        {'output_parameters': ParameterData object containing the dictionary
                {'minimum_energy_output_uuid': uuid of the output parameters of
                                               the simplest energy calc. 
                                               giving the lowest energy per atom,
                 'sorted_energy_outputs_uuids': uuids of the output parameters, sorted 
                                                according to the energy,
                 'warnings': a list of warnings.
                 }
         }
    """
    epsilon = parameters.get_dict()['epsilon']
    pw_outputs = kwargs.values()
    
    pw_outputs_sorted = sorted(pw_outputs, key = lambda x: 
                                x.dict.energy/x.dict.number_of_atoms )
    pw_output_min = pw_outputs_sorted[0]
    for pw_output in pw_outputs_sorted[1:]:
        if ( scalars_are_equal(pw_outputs_sorted[0].dict.energy/pw_outputs_sorted[0].dict.number_of_atoms,
                        pw_output.dict.energy/pw_output.dict.number_of_atoms,
                        epsilon=epsilon)
            and (pw_output_min.dict.number_of_atoms, 
                 pw_output_min.dict.number_of_species, 
                 pw_output_min.dict.number_of_spin_components)
                > (pw_output.dict.number_of_atoms, 
                   pw_output.dict.number_of_species, 
                   pw_output.dict.number_of_spin_components) ):
            pw_output_min = pw_output

    # a safeguard just in case
    warnings = []
    if ( pw_output_min.dict.number_of_spin_components == 2 
         and (pw_output_min.dict.total_magnetization == 0. and 
         pw_output_min.dict.absolute_magnetization == 0.) ):
        # take anyway the configuration without spin, in this case
        pw_output_min = [pw_output for pw_output in pw_outputs
                         if pw_output.dict.number_of_spin_components==1][0]
        warnings.append("The minimum energy structure was obtained with"
                        "a spin-polarized calculation but is not magnetic"
                        " -> we chose the non-spin polarized calculation")
    
    output_dict = {'minimum_energy_output_uuid': pw_output_min.uuid,
                   'sorted_energy_outputs_uuids': [pw_output.uuid for pw_output in pw_outputs_sorted],
                   'warnings': warnings}
    
    return {'output_parameters': ParameterData(dict=output_dict)}

def get_sort_energy_calcs_results(parameters=None,**kwargs):
    """
    Get the results from the sort_energy_calcs_inline function:
    - if there exists already an inline calculation with the same inputs,
    it does not relaunch it, it gets instead the output dictionary of the previously
    launched function,
    - otherwise, launches the sort_energy_calcs_inline function
    and get its result.
    """
    result_dict = None
    inputs_list = sorted([v.pk for k,v in kwargs.iteritems()])
    
    for ic in InlineCalculation.query(inputs=kwargs.values()[0]).order_by('ctime'):
        ic_inputs_list = sorted([v.pk for k,v in ic.get_inputs_dict().iteritems()
                                 if not k.startswith('parameters')])
        try:
            if ( ic.get_function_name() == 'sort_energy_calcs_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), parameters.get_dict())
                 and ic_inputs_list==inputs_list
                 and 'output_parameters' in ic.get_outputs_dict()):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    #if result_dict is not None:
    #    print "sort_energy_calcs_inline already run -> we do not re-run"
    if result_dict is None:
        #print "Launch sort_energy_calcs_inline..."
        _, result_dict = sort_energy_calcs_inline(parameters=parameters,**kwargs)
    
    return result_dict

@make_inline
def prepare_final_pw_input_inline(parameters,structure,pw_input_min,pw_output_min,
                                  pw_output_scf,bands_output):
    """
    OBSOLET.
    Prepare a new pw input and k-points, selecting the correct smearing and magnetic
    configuration, given the output parameters of a pw calculation,
    and some additional input with the distance between k-points and the  
    smearing scheme to use if smearing is needed
    
    :param parameters: ParameterData object containing a dictionary of the form: 
            {'distance_kpoints_in_mesh': 0.2, 
             'threshold_smearing_energy_per_atom': 1.e-2, 
             'threshold_band_gap': 1.e-2, 
             'conv_thr_per_atom': 1e-12, 
             'etot_conv_thr_per_atom': 1e-6, 
             'forc_conv_thr': 1e-4,
             }
    :param structure: the structure to be calculated
    :param pw_input_min: the input ParameterData of the pw calculation that gave
            the minimum energy configuration (from the magnetic test)
    :param pw_output_min: the output ParameterData from the same pw calculation
    :param pw_output_scf: the output ParameterData from the scf pw calculation
            used to compute the bands
    :param bands_output: ParameterData object containing a dictionary of the form:
            {'is_insulator': True, 
             'band_gap': 1., 
             'band_gap_units': 'eV',
            }
            This is the output from the band-gap calculation on the band 
            structure(s) from the same pw calculation.
    :return: a dictionary of the form
        {'output_pw_input': a ParameterData object with the new pw input,
         'output_kpoints": a KpointsData object with the new kpoints }
             
    """
    params_dict = parameters.get_dict()
    pw_input_dict = pw_input_min.get_dict()
    pw_output_min_dict = pw_output_min.get_dict()
    pw_output_scf_dict = pw_output_scf.get_dict()
    
    # prepare the new kpoints (mesh is forced to be "even")
    final_kpoints=KpointsData()
    final_kpoints.set_cell_from_structure(structure)
    final_kpoints.set_kpoints_mesh_from_density(params_dict['distance_kpoints_in_mesh'],
                                                force_parity=True)

    # prepare the new input
    # baseline input is the pw calculation input
    final_pw_input_dict = pw_input_dict.copy()
    
    # decide if we use smearing or not: check band-gap and smearing energy
    #pw_bands_list = [b for b in kwargs.values() if isinstance(b,BandsData)]
    #if len(pw_bands_list) == 1:
    #    _ = kwargs.popitem()
    #    _, band_gap = is_insulator(pw_bands_list[0],
    #                            n_electrons=pw_output_dict['number_of_electrons']/2.)
    #elif len(pw_bands_list) == 2:
    #    _ = kwargs.popitem()
    #    _ = kwargs.popitem()
    #    band_gap = helpers.get_band_gap_from_2spins_calculation(pw_bands_list[0],
    #                                                            pw_bands_list[1])
    #else:
    #    raise KeyError("Too many, or too few, band structures provided in input")
    #if kwargs:
    #    raise ValueError("Unrecognized kwargs left")
    
    bands_output_dict = bands_output.get_dict()
    band_gap = bands_output_dict['band_gap']
    if band_gap is None:
        band_gap = 0.
    
    n_atoms = pw_output_scf_dict['number_of_atoms']
    is_metal = ( (not bands_output_dict['is_insulator'] or 
                  (abs(pw_output_scf_dict['energy_smearing'])/n_atoms > 
                                params_dict['threshold_smearing_energy_per_atom']))
                  or (band_gap  <= params_dict['threshold_band_gap']) )

    if not is_metal:
        # deactivate the smearing
        final_pw_input_dict['SYSTEM'].pop('occupations',None)
        final_pw_input_dict['SYSTEM'].pop('smearing',None)
        final_pw_input_dict['SYSTEM'].pop('degauss',None)
        if final_pw_input_dict['SYSTEM'].get('nspin',_default_nspin_from_QE) == 2:
            # case of a magnetic material with a band-gap:
            # set the total magnetization in input otherwise QE will fail (it
            # has to be positive and integer)
            final_pw_input_dict['SYSTEM']['tot_magnetization'] = round(abs(pw_output_min_dict['total_magnetization']))
        
    # set some convergence parameters different from the initial pw input
    try:
        final_pw_input_dict['ELECTRONS']['conv_thr'] = params_dict['conv_thr_per_atom']*n_atoms
    except KeyError:
        final_pw_input_dict['ELECTRONS'] = {'conv_thr': params_dict['conv_thr_per_atom']*n_atoms}
    try:
        final_pw_input_dict['CONTROL']['etot_conv_thr'] = params_dict['etot_conv_thr_per_atom']*n_atoms
        final_pw_input_dict['CONTROL']['forc_conv_thr'] = params_dict['forc_conv_thr']
    except KeyError:
        final_pw_input_dict['CONTROL'] = {'etot_conv_thr': params_dict['etot_conv_thr_per_atom']*n_atoms,
                                          'forc_conv_thr': params_dict['forc_conv_thr']}
        
    final_pw_input = ParameterData(dict=final_pw_input_dict)
    
    return {'output_pw_input': final_pw_input,
            'output_kpoints': final_kpoints}

@make_inline
def is_metallic_magnetic_inline(parameters,minimum_energy_calc_output_parameters,
                                **kwargs):
    """
    Collect all information learned about the structure in a single ParameterData
    object: metallic character, number of spins and starting magnetizations to be used.
    
    :param parameters: ParameterData object containing a dictionary of the form: 
            {'threshold_smearing_energy_per_atom': 1.e-2, 
             'threshold_band_gap': 1.e-2, 
             }
    :param minimum_energy_calc_output_parameters: the output ParameterData from
        the energy calculation yielding the minimum energy configuration
    :param minimum_energy_calc_output_array or minimum_energy_calc_output_trajectory:
        the output ArrayData or TrajectoryData
        from the energy calculation yielding the minimum energy configuration
    :param scf_test_calc_output_parameters: the output ParameterData from the 
        scf test calculation (used to compute the bands). Optional: if it is
        not there we use minimum_energy_calc_output_parameters.
    :param bands_output_parameters: ParameterData object containing a dictionary
        of the form:
            {'is_insulator': True, 
             'band_gap': 1., 
             'band_gap_units': 'eV',
            }
        This is the output from the band-gap calculation on the band 
        structure(s).
    
    .. note:: bands_output_parameters can be absent; then we get only 
            the magnetic info.
    
    :return: a dictionary of the form
        {'output_parameters': a ParameterData object with a dictionary of the form:
                 {'is_metallic': True or False,
                  'band_gap': bandgap,
                  'band_gap_units': 'eV',
                  'is_magnetic': True or False,
                  'number_of_spin_components': 1 or more,
                  'number_of_bands': number of Kohn-Sham bands (to be put in SYSTEM->nbnd)
                        (NOTE: for spin-polarized calcs. this number of bands is 
                        still related to num_electrons/2 - QE doubles instead n-kpts),
                  'atomic_magnetic_moments_per_unit_charge': magnetic moment over charge
                                                                 for each atom (only if nspin=2),
                                                                 as computed by QE-PW,
                  'atomic_species_name': species name of each atom, in the same 
                                         order as previous item (only if nspin=2),
                  'atomic_magnetic_moments_per_unit_charge_units': 'Bohrmag/e',
                  'total_magnetization': total magnetization (only if 
                                         is_magnetic=True).
                  }
         }
             
    """
    params_dict = parameters.get_dict()
    mag_output_dict = minimum_energy_calc_output_parameters.get_dict()
    output_dict = {}
    
    try:
        scf_output_dict = kwargs['scf_test_calc_output_parameters'].get_dict()
    except KeyError:
        scf_output_dict = mag_output_dict

    n_atoms = scf_output_dict['number_of_atoms']

    try:
        output_array = kwargs['minimum_energy_calc_output_array']
    except KeyError:
        output_array = kwargs['minimum_energy_calc_output_trajectory']

    try:
        bands_output_dict = kwargs['bands_output_parameters'].get_dict()
        band_gap = bands_output_dict['band_gap']
        if band_gap is None:
            band_gap = 0.
        is_metallic = ( (not bands_output_dict['is_insulator'] or 
                      (abs(scf_output_dict['energy_smearing'])/n_atoms > 
                                    params_dict['threshold_smearing_energy_per_atom']))
                      or (band_gap  <= params_dict['threshold_band_gap']) )
        output_dict = {'is_metallic': is_metallic,
                       'band_gap': band_gap,
                       'band_gap_units': bands_output_dict['band_gap_units'],
                       }
    except KeyError:
        pass
    
    is_magnetic = (mag_output_dict['number_of_spin_components']>1)    
    output_dict.update({'is_magnetic': is_magnetic,
                        'number_of_spin_components': mag_output_dict['number_of_spin_components'],
                        'number_of_bands': scf_output_dict['number_of_bands'],
                        })
    if is_magnetic:
        output_dict['atomic_magnetic_moments_per_unit_charge_units'] = 'Bohrmag/e'
        try:
            output_dict['atomic_magnetic_moments_per_unit_charge'] = \
                (np.array(mag_output_dict['atomic_magnetic_moments'])/
                np.array(mag_output_dict['atomic_charges'])).tolist()
            output_dict['atomic_species_name'] = \
                mag_output_dict['atomic_species_name']
        except KeyError:
            output_dict['atomic_magnetic_moments_per_unit_charge'] = \
                (output_array.get_array('atomic_magnetic_moments')[-1]/
                output_array.get_array('atomic_charges')[-1]).tolist()
            output_dict['atomic_species_name'] = \
                output_array.get_array('atomic_species_name').tolist()
            
        output_dict['total_magnetization'] = mag_output_dict['total_magnetization']
    
    return {'output_parameters': ParameterData(dict=output_dict)}

def get_is_metallic_magnetic_results(parameters,**kwargs):
    """
    Get the results from the is_metallic_magnetic_inline function:
    - if there exists already an inline calculation with the same input parameters,
    it does not relaunch it, it gets instead the output dictionary of the 
    previously launched function,
    - otherwise, launches the single_lowdimfinder_inline function
    and gets its result.
    """
    from aiida.orm.calculation.inline import InlineCalculation
    minimum_energy_calc_output_parameters = kwargs['minimum_energy_calc_output_parameters']
    result_dict = None
    for ic in minimum_energy_calc_output_parameters.get_outputs(InlineCalculation):
        try:
            if ( ic.get_function_name() == 'is_metallic_magnetic_inline'
                 and objects_are_equal(ic.inp.parameters.get_dict(), parameters.get_dict())
                 and objects_are_equal(dict([(k,v.pk) for k,v in ic.get_inputs_dict().iteritems()
                                             if not k.startswith('parameters')]),
                                       dict([(k,v.pk) for k,v in kwargs.iteritems()]))
                 and 'output_parameters' in ic.get_outputs_dict() ):
                result_dict = ic.get_outputs_dict()
        except AttributeError:
            pass
    
    if result_dict is None:
        _,result_dict = is_metallic_magnetic_inline(parameters=parameters,**kwargs)
        
    return result_dict

class ChronosWorkflow(Workflow):
    """
    Workflow to make first tests on a unknown structure and get a vc-relaxed
    one. It tests several magnetic and non-magnetic starting configurations,
    and tests also metallicity.
    
    In the end a final vc-relax is done and the band structure computed.
    
    .. note:: We DO NOT test non-collinear magnetism.
    
    Input description.
    The input is a dictionary that follows closely the input of the 
    pw workflow:
    
    General input (here default values are indicated):
    
    'input': {'clean_workdir': False,
              'number_of_random_magnetization_fm': 3,         # number of random starting magnetization states to test ferromagnetism for the initial structure
                                                              # Note: this is a maximum: if other magnetic Pw workflows where already sent in the past,
                                                              # the workflow will find them and launch other Pw wfs ONLY if those found do not make up that number. 
              'number_of_random_magnetization': 2,            # number of random starting magnetization states to test magnetism for each possible magnetic structure
                                                              # Note: this is a maximum: if other magnetic Pw workflows where already sent in the past,
                                                              # the workflow will find them and launch other Pw wfs ONLY if those found do not make up that number. 
              'order_parameters': [0.5],                      # order parameters to test ferrimagnetic states (0.5 for antiferro, but can be anything 
                                                              # between 0 and 1 - see pymatgen and enumlib for details)
              'max_size_supercell': 2,                        # maximum size of supercells (in each periodic dimension) to test for magnetization
              'max_number_of_structures': 10,                 # maximum number of afm structures to be generated,
              'symprec': 5e-3,                                # precision used in the symmetry finder of spglib
              'min_abs_magnetization_to_launch_afm_tests':0.01# minimum absolute magnetization (QE units) to be obtained in ferromagnetic test 
                                                              # to proceed further with antiferro(ferri)magnetic tests
              'min_atomic_mag_moment_for_afm_tests': 0.01     # minimum atomic moment (QE units) to be obtained in ferromagnetic test for a species to be 
                                                              # considered magnetic in antiferro(ferri)magnetic tests
              'min_relative_atomic_mag_moment_for_afm_tests':0.05 # minimum atomic moment relative to the maximum magnetic moment of the structure
                                                              # to be obtained in ferromagnetic test for a species to be 
                                                              # considered magnetic in antiferro(ferri)magnetic tests
              'distance_kpoints_in_mesh': 0.4,                # the distance (in A^-1) between k-points in the mesh for the test calculations
              'offset_kpoints_mesh': [0.5 if pbc else 0. for pbc in structure.pbc]# offset added to the regular k-points mesh created (crystal coord.)
              'scf_test_smearing': cold,                      # type of smearing used for the test scf+bands calculation
              'scf_test_degauss': 0.02,                       # smearing parameter used for the test scf+bands calculation
              'significant_energy_difference_per_atom': 2.e-4,# the minimum energy difference (eV/atom) that is considered significant,
                                                              # when selecting the lowest energy structure
              'threshold_smearing_energy_per_atom': 100.,     # threshold above which we consider the material is metallic (in abs. value; eV/atom)
                                                              # NOTE: default value is arbitrarily large; this means we DO NOT use this criterion by default.
                                                              # It has a meaning only if Gaussian smearing is used, and it gives anyway WRONG
                                                              # metallic character for compounds with small band-gap when the bands lie close to each other.
              'threshold_band_gap': 1.e-2,                    # threshold below which we consider the material is metallic (in abs. value; eV)
              'extract_primitive_in_magnetic_structures':True,# True to extract primitive cell after generation of the afm structures (3D only).
              'preserve_xy_plane_in_magnetic_structures':False,# True to preserve the xy plane within the two first lattice vectors, if possible (3D only).
              'continue_upon_bands_failure': False,           # True to continue even if the scf+bands calculation failed (we get then only the magnetism informatino).
              },
              
    'info_group_name': name of the group where to put the Parameterdata with the
                       magnetic/metallic character information,
    'structure_group_name': name of the group where to put the lowest energy 
                            structure (vc-relaxed),
    
    then, standard pw workflow input for the initial magnetic tests, adding
    'pw_' to every key that concerns the pw scf or relax or vc-relax (not bands)
    calculation (see PwWorkflow):
    
    'structure': structure,
    'pseudo_family': pseudo_family,    
    'pw_codename': pw_codename,
    'pw_settings': settings,
    'pw_parameters': pw_input_dict, # you should probably use RELAXED convergence thresholds here!
    'pw_calculation_set': {'resources':{'num_machines': 1},
                             "max_wallclock_seconds":3600,
                             },
    'pw_input':{'volume_convergence_threshold': 5.e-2,
                'clean_workdir': True,
                },
                
    then, standard band input (see PwWorkflow) to compute bands:
    
    'band_input':{'distance_kpoints_in_dispersion': 0.05,
                  'kpoints_path': [],
                  'clean_workdir': True,
                  },
    'band_parameters_update': {'ELECTRONS': {'diagonalization': 'cg'}},
    'band_group_name': 'test',
    'band_calculation_set': {'resources':{'num_machines': 1},
                             "max_wallclock_seconds":1000,
                             },
    'band_settings': band_settings,
    
    
    """

    _clean_workdir = False
    _max_num_atoms_to_spindisorder = 10 # the maxmimum number of atoms on a single species, that one can 'spin-disorder'
    _default_order_parameters = [0.5]
    _default_number_of_random_magnetizations_fm = 3
    _default_number_of_random_magnetizations = 2
    _default_max_size_supercell = 2
    _default_max_number_of_structures = 20
    _default_symprec = 5e-3
    _default_min_abs_magnetization_to_launch_afm_tests = 0.01
    _default_min_atomic_mag_moment_for_afm_tests = 0.01
    _default_min_relative_atomic_mag_moment_for_afm_tests = 0.05
    _default_distance_kpoints_in_mesh = 0.4
    _default_offset_kpoints_mesh = 0.5
    _default_significant_energy_difference_per_atom = 2.e-4
    _default_threshold_band_gap = 1.e-2
    _default_threshold_smearing_energy_per_atom = 100.
    _default_scf_test_smearing = 'cold'
    _default_scf_test_degauss = 0.02
    
    def __init__(self,**kwargs):
        super(ChronosWorkflow, self).__init__(**kwargs)
    
    @Workflow.step
    def start(self):
        """
        Checks the parameters
        """
        self.append_to_report("Checking input parameters")
        
        mandatory_keys = [   ('structure',StructureData,"the structure (a previously stored StructureData object)"),
                             ('pseudo_family',basestring,'the pseudopotential family'),
                             ('pw_codename',basestring,'the PW codename'),
                             #('pw_calculation_set',dict,'A dictionary with resources, walltime, ... for pw calcs.'),
                             ('pw_parameters',dict,"A dictionary with the PW input parameters"),
                             ('band_calculation_set',dict,'A dictionary with resources, walltime, ...for band calcs.'),
                             ]
        
        main_params = self.get_parameters()
        
        # validate pw keys
        helpers.validate_keys(main_params, mandatory_keys)
        
        # check the pw code
        test_and_get_code(main_params['pw_codename'], 'quantumespresso.pw',
                          use_exceptions=True)

        self.next(self.run_pw_ferromag)
    
    @Workflow.step
    def run_pw_ferromag(self):
        """
        Launch the PwWorkflow with random starting magnetizations, keeping all
        the species the same as in the initial structure (i.e only ferromagetism
        is tested)
        """
        main_params = self.get_parameters()
        
        # take the parameters needed for the PW computation
        pw_params = {}
        for k,v in main_params.iteritems():
            # we do not put these calcs into a group
            if (k.startswith('pw_') and not k.endswith('group_name')):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            elif k == 'pseudo_family': 
                pw_params[k] = v
            
        initial_structure = main_params['structure']
        pw_params['structure'] = initial_structure

        # construct the k-points mesh
        distance_kpoints = main_params.get('input',{}).get(
                                        'distance_kpoints_in_mesh',
                                        self._default_distance_kpoints_in_mesh)
        offset = main_params.get('input',{}).get('offset_kpoints_mesh',
            [self._default_offset_kpoints_mesh if pbc else 0. for pbc in initial_structure.pbc])
        kpoints = KpointsData()
        kpoints.set_cell_from_structure(initial_structure)
        kpoints.set_kpoints_mesh_from_density(distance_kpoints,offset=offset)
        kpoints.store()
        pw_params['kpoints'] = kpoints
        
        # force vc-relax calculations
        try:
            pw_params['input']['relaxation_scheme'] = 'vc-relax'
        except KeyError:
            pw_params['input'] = {'relaxation_scheme': 'vc-relax'}
        
        pw_params['parameters']['SYSTEM'].pop('nspin',None)
        pw_params['parameters']['SYSTEM'].pop('starting_magnetization',None)
        
        # find older PW workflows run on the same structure with the same parameters
        old_mag_wfs,old_zero_mag_wf = get_pw_mag_wfs_with_parameters(pw_params)
        self.add_attribute('ferromag_old_pw_wfs',
                           [_.pk for _ in old_mag_wfs+[old_zero_mag_wf] if _])
        if self.get_attribute('ferromag_old_pw_wfs'):
            self.append_to_report("Found {} previous PW sub-workflow{} "
                                  "on initial structure {} with pk {}".format(
                    len(self.get_attribute('ferromag_old_pw_wfs')),
                    "s" if len(self.get_attribute('ferromag_old_pw_wfs'))>1 else "",
                    initial_structure.get_formula(),initial_structure.pk))
        
        if old_zero_mag_wf is None:
            # non spin-polarized workflow
            pw_params['parameters']['SYSTEM']['nspin'] = 1
            pw_params['parameters']['SYSTEM']['starting_magnetization'] = 0.
            wf_pw = PwWorkflow(params=pw_params)
            wf_pw.store()
            self.append_to_report("Launching PW sub-workflow (pk: {}) "
                                  " on initial structure {}, with"
                                  " nspin=1 and no starting magnetization"
                                  "".format(wf_pw.pk,initial_structure.get_formula()))
            self.attach_workflow(wf_pw)
            wf_pw.start()
         
        # loop to test several starting magnetizations
        nspin = 2
        pw_params['parameters']['SYSTEM']['nspin'] = nspin
        for _ in range(len(old_mag_wfs),main_params.get('input',{}).get(
                            'number_of_random_magnetizations_fm',
                            self._default_number_of_random_magnetizations_fm)):
            
            # start mag between 0.1 and 1 in absolute value, with random sign,
            # for each species
            start_mag = dict([(k.name,round((randint(0,1)*2-1)*uniform(0.1,1),2))
                              for k in initial_structure.kinds])
            pw_params['parameters']['SYSTEM']['starting_magnetization'] = start_mag
            # check if there is a similar workflow that has already run
            # on this structure. Only the starting mag. can be different.
            
            wf_pw = PwWorkflow(params=pw_params)
            wf_pw.store()
            self.append_to_report("Launching PW sub-workflow (pk: {}) "
                                  " on initial structure {}, with"
                                  " nspin={} and starting magnetization={}"
                                  "".format(wf_pw.pk,initial_structure.get_formula(),
                                            nspin,start_mag))
            self.attach_workflow(wf_pw)
            wf_pw.start()
               
        self.next(self.run_pw_general_mag)
        
    @Workflow.step
    def run_pw_general_mag(self):
        """
        If structure is potentially magnetic, launch the PwWorkflow with random 
        starting magnetizations, this time WITH duplication of species to test 
        antiferromagnetic or ferrimagnetic orderings.
        """
        from itertools import chain
        
        main_params = self.get_parameters()
        input_dict = main_params.get('input',{})
        max_num_structures = input_dict.get('max_number_of_structures',
                                        self._default_max_number_of_structures)
        max_sup_size = input_dict.get('max_size_supercell',
                                    self._default_max_size_supercell)
        inline_params_dict = {
                'symprec': input_dict.get('symprec',self._default_symprec),
                }
        if 'preserve_xy_plane_in_magnetic_structures' in input_dict:
            inline_params_dict['preserve_xy_plane'] = \
                    input_dict['preserve_xy_plane_in_magnetic_structures']
        if 'extract_primitive_in_magnetic_structures' in input_dict:
            inline_params_dict['extract_primitive'] = \
                    input_dict['extract_primitive_in_magnetic_structures']
        
        # check magnetism in the previous calculations, then decide if we need to 
        # push the magnetic tests further
        wfs = list(self.get_step(self.run_pw_ferromag).get_sub_workflows()) + \
              list(Workflow.query(pk__in=self.get_attribute('ferromag_old_pw_wfs')))
        pw_mag_calcs = [wf.get_result('pw_calculation') for wf in wfs
                        if ('pw_calculation' in wf.get_results() and 
                            wf.get_result('pw_calculation').inp.parameters.get_dict(
                                )['SYSTEM'].get('nspin',_default_nspin_from_QE)==2)]
        pw_nospin_calcs = [wf.get_result('pw_calculation') for wf in wfs
                        if ('pw_calculation' in wf.get_results() and 
                            wf.get_result('pw_calculation').inp.parameters.get_dict(
                                )['SYSTEM'].get('nspin',_default_nspin_from_QE)==1)]
        if not pw_mag_calcs:
            raise InternalError("All magnetic calculations failed -> the Chronos"
                                " workflow cannot continue")
        if not pw_nospin_calcs:
            raise InternalError("Non spin-polarized calculation failed -> the Chronos"
                                " workflow cannot continue")
                
        max_abs_mag = max([pw.out.output_parameters.get_dict().get(
                            'absolute_magnetization',0) for pw in pw_mag_calcs])
        # get the list of species to "duplicate" (i.e. assign different spins)
        if max_abs_mag >= input_dict.get('min_abs_magnetization_to_launch_afm_tests',
                            self._default_min_abs_magnetization_to_launch_afm_tests):
            # list of calculations with max possible magnetization
            pw_fm_calcs = [c for c in pw_mag_calcs if abs(c.out.output_parameters.get_dict(
                    ).get('absolute_magnetization',0)-max_abs_mag)<=0.01]
            # find lowest energy calc among these
            pw_fm_energy_min = min([pw.out.output_parameters.dict.energy/pw.out.output_parameters.dict.number_of_atoms
                                    for pw in pw_fm_calcs])
            pw_fm_calc_min = min([pw for pw in pw_fm_calcs
                if abs(pw.out.output_parameters.dict.energy/pw.out.output_parameters.dict.number_of_atoms-pw_fm_energy_min)<=
                    input_dict.get('significant_energy_difference',
                    self._default_significant_energy_difference_per_atom)],
                key=lambda x: x.ctime)
            # select species with high enough atomic magnetic moment
            try:
                atomic_species_name = pw_fm_calc_min.out.output_parameters.get_dict()['atomic_species_name']
                atomic_magnetic_moments = pw_fm_calc_min.out.output_parameters.get_dict()['atomic_magnetic_moments']
            except KeyError:
                output_array = pw_fm_calc_min.get_outputs_dict().get('output_trajectory',
                                pw_fm_calc_min.get_outputs_dict().get('output_array'))
                atomic_species_name = output_array.get_array('atomic_species_name')
                atomic_magnetic_moments = output_array.get_array('atomic_magnetic_moments')[-1]
            species_mag = list(chain.from_iterable([[(c.inp.structure.get_kind(k).symbols[0],m)
                for k,m in zip(atomic_species_name,atomic_magnetic_moments)
                if abs(m)>=input_dict.get('min_atomic_mag_moment_for_afm_tests',
                    self._default_min_atomic_mag_moment_for_afm_tests)]
                for c in pw_fm_calcs]))
            
            # additional criterion: atomic magnetic moment of species to be 
            # assigned different spins, should be more than 5% of the maximum 
            # atomic magnetic moment
            if species_mag:
                max_atomic_moment = max([abs(_[1]) for _ in species_mag])
                species_mag = [(k,m) for k,m in species_mag if abs(m)>=input_dict.get(
                        'min_relative_atomic_mag_moment_for_afm_tests',
                        self._default_min_relative_atomic_mag_moment_for_afm_tests)*max_atomic_moment]
                inline_params_dict['species'] = list(set([k for k,m in species_mag
                    if c.inp.structure.get_site_kindnames().count(k)
                                    <= self._max_num_atoms_to_spindisorder]))
                if set([_[0] for _ in species_mag]) != set(inline_params_dict['species']):
                    self.append_to_report("Magnetic species found were {}, but "
                                          "too high number of atoms for some of "
                                          " them, so only {} were retained"
                                          "".format(set([_[0] for _ in species_mag]),
                                                    set(inline_params_dict['species'])))
                else:
                    self.append_to_report("Magnetic species found: {}".format(
                                                inline_params_dict['species']))
        
        old_wf_pks = []
        if inline_params_dict.get('species',[]):
            # launch antiferro(ferri)magnetic tests
            
            # take the parameters needed for the PW computation
            pw_params = {}
            for k,v in main_params.iteritems():
                # we do not put these calcs into a group
                if (k.startswith('pw_') and not k.endswith('group_name')):
                    new_k = k[3:] # remove pw_
                    pw_params[new_k] = v
                elif k == 'pseudo_family': 
                    pw_params[k] = v
                
            # initial_structure = main_params['structure']
            # replace the above by the vc-relaxed structure of the first step
            try:
                initial_structure = pw_fm_calc_min.out.output_structure
            except AttributeError:
                initial_structure = pw_fm_calc_min.inp.structure
            
            distance_kpoints = main_params.get('input',{}).get(
                                        'distance_kpoints_in_mesh',
                                        self._default_distance_kpoints_in_mesh)
            offset = main_params.get('input',{}).get('offset_kpoints_mesh',
                [self._default_offset_kpoints_mesh if pbc else 0. for pbc in initial_structure.pbc])
            
            # extract convergence parameters that are extensive
            etot_conv_thr = pw_params['parameters'].get('CONTROL',{}).get(
                                        'etot_conv_thr',_default_QE_etot_conv_thr)
            conv_thr = pw_params['parameters']['ELECTRONS'].get('conv_thr',
                                                                _default_QE_conv_thr)
            # force vc-relax calculations
            try:
                pw_params['input']['relaxation_scheme'] = 'vc-relax'
            except KeyError:
                pw_params['input'] = {'relaxation_scheme': 'vc-relax'}
            
            # launch PW workflow on several structures and several random 
            # starting magnetizations
            for order_parameter in input_dict.get('order_parameters',
                                                  self._default_order_parameters):
                inline_params_dict['order_parameter'] = order_parameter
                result_dict = {}
                while ((not result_dict) or len([k for k in result_dict.keys() if '_structure' in k])
                    >max_num_structures) and max_sup_size>=1:
                    inline_params_dict['max_supercell_size'] = max_sup_size
                    inline_params = ParameterData(dict=inline_params_dict)
                    # build set of spin ordered structures with duplicated atoms
                    result_dict = get_prepare_magnetic_structures_results(
                                                parameters=inline_params,
                                                structure=initial_structure)
                    if not [k for k in result_dict.keys() if '_structure' in k]:
                        self.append_to_report("For max supercell_size {}, "
                                              "prepare_magnetic_structures_inline "
                                              "failed ".format(max_sup_size))
                                              #"with the following warnings:\n"
                                              #"{}".format(max_sup_size,"\n".join(
                            #result_dict['output_parameters'].get_dict()['warnings'])))
                    else:
                        the_result_dict = result_dict
                        if (len(set([v.pk for k,v in result_dict.iteritems()
                                 if '_structure' in k]))>max_num_structures):
                            self.append_to_report("For max supercell_size {}, "
                                                  "prepare_magnetic_structures_inline "
                                                  "found too many structures: {}".format(
                                                  max_sup_size,len(set([v.pk
                                                    for k,v in result_dict.iteritems()
                                                    if '_structure' in k]))))
                    max_sup_size -= 1
                self.add_result('prepare_magnetic_structures_output',
                                the_result_dict['output_parameters'])
                structures_afm = [load_node(pk) for pk in set([v.pk
                                    for k,v in the_result_dict.iteritems() 
                                       if '_structure' in k])]
                self.add_result("number_of_structures_for_order_{}"
                                   "".format(str(order_parameter).replace('.','p')),
                                   len(structures_afm))
                for structure in structures_afm[:max_num_structures]:
                    struc_link_name = [k for k,v in the_result_dict.iteritems()
                                       if v.pk==structure.pk][0]
                    pw_params['structure'] = structure
                    # construct the k-points
                    kpoints = KpointsData()
                    kpoints.set_cell_from_structure(structure)
                    kpoints.set_kpoints_mesh_from_density(distance_kpoints,
                                                          offset=offset)
                    kpoints.store()
                    pw_params['kpoints'] = kpoints
                    # change the convergence thresholds that are extensive
                    size_ratio = len(structure.sites)/float(len(initial_structure.sites))
                    try:                  
                        pw_params['parameters']['ELECTRONS']['conv_thr'] = conv_thr*size_ratio
                    except KeyError:
                        pw_params['parameters']['ELECTRONS'] = {'conv_thr': conv_thr*size_ratio}
                    try:                  
                        pw_params['parameters']['CONTROL']['etot_conv_thr'] = etot_conv_thr*size_ratio
                    except KeyError:
                        pw_params['parameters']['CONTROL'] = {'etot_conv_thr': etot_conv_thr*size_ratio}
                    
                    # find older PW workflows run on the same structure with the same parameters
                    old_mag_wfs,old_zero_mag_wf = get_pw_mag_wfs_with_parameters(pw_params)
                    old_tmp_wf_pks = [_.pk for _ in old_mag_wfs+[old_zero_mag_wf] if _]
                    if old_tmp_wf_pks:
                        self.append_to_report("Found {} previous PW sub-workflow{} "
                                              "on structure {} with pk {}".format(
                                                len(old_tmp_wf_pks),
                                                "s" if len(old_tmp_wf_pks)>1 else "",
                                                structure.get_formula(),structure.pk))
                    old_wf_pks.extend(old_tmp_wf_pks)

                    # loop to test several starting magnetizations (if enough have not
                    # already been done)
                    # Note: we do only one magnetic configuration for the fm structure.
                    num_random_mag = 1 if struc_link_name.startswith('output_fm_structure')\
                            else input_dict.get('number_of_random_magnetizations',
                                    self._default_number_of_random_magnetizations)
                    for _ in range(len(old_mag_wfs),num_random_mag):
                        # start mag between 0.1 and 1 in absolute value, with random sign,
                        # for each species selected as magnetic (otherwise we set it to 0.)
                        nbnd = None
                        if struc_link_name.startswith('output_fm_structure'):
                            # this is the structure with the same supercell as
                            # the first afm structure, but without the different
                            # kind names -> re-use the same magnetization as 
                            # in the first step
                            start_mag = helpers.get_starting_magnetization_pw(
                                pw_fm_calc_min.out.output_parameters.get_dict())
                            if not start_mag:
                                output_array = pw_fm_calc_min.get_outputs_dict().get('output_trajectory',
                                                pw_fm_calc_min.get_outputs_dict().get('output_array',None))
                                mag_dict = {
                                    'atomic_magnetic_moments': 
                                            output_array.get_array('atomic_magnetic_moments')[-1].tolist(),
                                    'atomic_charges': output_array.get_array('atomic_charges')[-1].tolist(),
                                    'atomic_species_name': output_array.get_array('atomic_species_name').tolist()
                                    }
                                start_mag = helpers.get_starting_magnetization_pw(mag_dict)
                            start_mag = start_mag['starting_magnetization']
                            nbnd = pw_fm_calc_min.inp.parameters.dict.SYSTEM.get('nbnd',None)
                        else:
                            start_mag = dict([(k.name,round((randint(0,1)*2-1)*uniform(0.1,1),2)
                                           if k.symbol in inline_params_dict['species'] else 0.)
                                          for k in structure.kinds])
                            if order_parameter == 0.5:
                                # special case of antiferromagetism: we enforce 
                                # opposite spins for species with same symbol
                                for sp in inline_params_dict['species']:
                                    start_mag['{}2'.format(sp)] = -start_mag['{}1'.format(sp)]
                        
                        pw_params['parameters']['SYSTEM']['nspin'] = 2
                        pw_params['parameters']['SYSTEM']['starting_magnetization'] = start_mag
                        if nbnd:
                            pw_params['parameters']['SYSTEM']['nbnd'] = nbnd
                        wf_pw = PwWorkflow(params=pw_params)
                        wf_pw.store()
                        self.append_to_report("Launching PW sub-workflow (pk: {}) "
                                              " on structure {} with pk {}, with"
                                              " starting magnetization={}"
                                              "".format(wf_pw.pk,structure.get_formula(),
                                                        structure.pk,start_mag))
                        self.attach_workflow(wf_pw)
                        wf_pw.start()
                        
                    if struc_link_name.startswith('output_fm_structure') and not old_zero_mag_wf:
                        # do again a non-spin polarized calculation for this structure
                        pw_params['parameters']['SYSTEM']['nspin'] = 1
                        pw_params['parameters']['SYSTEM']['starting_magnetization'] = 0.
                        nbnd = pw_nospin_calcs[0].inp.parameters.dict.SYSTEM.get('nbnd',None)
                        if nbnd:
                            pw_params['parameters']['SYSTEM']['nbnd'] = nbnd
                        wf_pw = PwWorkflow(params=pw_params)
                        wf_pw.store()
                        self.append_to_report("Launching PW sub-workflow (pk: {}) "
                                              " on structure {} with pk {}, "
                                              " without spin-polarization"
                                              "".format(wf_pw.pk,structure.get_formula(),
                                                        structure.pk))
                        self.attach_workflow(wf_pw)
                        wf_pw.start()
            
        else:
            self.append_to_report("No magnetic species found -> general magnetic"
                                  " screening does not have to be performed")
        
        self.add_attribute('general_mag_old_pw_wfs',old_wf_pks)
        self.next(self.run_scf_bands)

    @Workflow.step
    def run_scf_bands(self):
        """
        Find lowest energy state, put the corresponding calculation in
        the results, together with its structure, and run an scf + bands 
        calc. (by default with Gaussian smearing)
        """
        from datetime import datetime
        main_params = self.get_parameters()
        initial_structure = main_params['structure']
        
        # Retrieve the sub-workflows
        # first try to get the general mag. tests, if not present (or if
        # structure cell is the same between afm and fm tests), then 
        # add the ferromag. tests.
        wfs = list(self.get_step(self.run_pw_general_mag).get_sub_workflows()) + \
              list(Workflow.query(pk__in=self.get_attribute('general_mag_old_pw_wfs')))
        wfs_ferromag = list(self.get_step(self.run_pw_ferromag).get_sub_workflows()) + \
                   list(Workflow.query(pk__in=self.get_attribute('ferromag_old_pw_wfs')))
        if (not wfs or self.get_result('prepare_magnetic_structures_output'
            ).get_dict().get('same_cell_as_fm_structure',False)):
            wfs += wfs_ferromag
        
        pw_calcs = [wf.get_results().get('pw_calculation',None) for wf in wfs]
        structures_computed_pks = set([wf.get_parameter('structure').pk
                for wf in wfs if 'pw_calculation' in wf.get_results()])
        n_failed_wfs = pw_calcs.count(None)
        
        if n_failed_wfs == len(wfs):
            raise ValueError("All pw workflows failed during the magnetic "
                             "tests -> we cannot continue")
        
        if  n_failed_wfs> 0:
            self.append_to_report("WARNING: {} pw wf{} failed during the magnetic"
                                  " test; we will continue ignoring {}"
                                  "".format(n_failed_wfs,
                                            "" if n_failed_wfs<=1 else "s",
                                            "it" if n_failed_wfs<=1 else "them"))
            while None in pw_calcs:
                pw_calcs.remove(None)
        
        self.add_result("number_of_completed_calcs",len(pw_calcs))
        self.add_result("number_of_structures_computed",len(structures_computed_pks))
        # sort the calculations according to the energy and the 
        # simplicity of the structure calculated (with energy differences
        # significant only above the 'epsilon_energy' level)
        epsilon = main_params.get('input',{}).get('significant_energy_difference_per_atom',
                                                  self._default_significant_energy_difference_per_atom)
        inline_params = ParameterData(dict={'epsilon': epsilon})
        inline_input_dict = dict([('energy_calc_output_parameters_{}'.format(i),
                                   pw_calc.out.output_parameters)
                                  for i,pw_calc in enumerate(pw_calcs)])
        result_dict = get_sort_energy_calcs_results(parameters=inline_params,
                                                    **inline_input_dict)
        pw_calc_min = load_node(result_dict['output_parameters'].get_dict(
                                )['minimum_energy_output_uuid']).inp.output_parameters
                
        if (len(pw_calc_min.out.output_parameters.get_dict()['starting_magnetization'])
                                        <=len(initial_structure.kinds)
            and len(set([wf.pk for wf in wfs_ferromag])-set([wf.pk for wf in wfs]))>0):
            # case when the general mag. tests were performed but the
            # lowest energy configuration is not an afm structure -> 
            # we rather take the minimum configuration from
            # the ferromag. tests
            # store first in the results the output_parameters
            # of the previous inline function to sort calcs. (to keep
            # track of it)
            self.add_result('general_mag_sort_energy_calcs_output',
                            result_dict['output_parameters'])
            # sort the fm and non-spin polarized calcs
            pw_calcs = [wf.get_result('pw_calculation') for wf in wfs_ferromag
                        if 'pw_calculation' in wf.get_results()]            
            inline_input_dict = dict([('energy_calc_output_parameters_{}'.format(i),
                                       pw_calc.out.output_parameters)
                                      for i,pw_calc in enumerate(pw_calcs)])
            result_dict = get_sort_energy_calcs_results(parameters=inline_params,
                                                        **inline_input_dict)
            pw_calc_min = load_node(result_dict['output_parameters'].get_dict(
                                    )['minimum_energy_output_uuid']).inp.output_parameters

        self.add_result('sort_energy_calcs_output',result_dict['output_parameters'])
        self.add_result('lowest_energy_pw_calculation',pw_calc_min)
        try:
            self.add_result('lowest_energy_structure',pw_calc_min.out.output_structure)
        except AttributeError as e:
            if not main_params.get('pw_input',{}).get('finish_with_scf',
                                                      PwWorkflow._finish_with_scf):
                # last calc. was a vc-relax -> there should be an output structure,
                # so we raise an error
                raise e
            self.add_result('lowest_energy_structure',pw_calc_min.inp.structure)
                
        # build pw workflow parameters
        pw_params = {}
        for k,v in main_params.iteritems():
            if k.startswith('band_'):
                pw_params[k] = v
            elif k.startswith('pw_'):
                new_k = k[3:] # remove pw_
                pw_params[new_k] = v
            elif k == 'pseudo_family': 
                pw_params[k] = v

        # force scf calculation
        try:
            pw_params['input']['relaxation_scheme'] = 'scf'
            pw_params['input']['finish_with_scf'] = False
        except KeyError:
            pw_params['input'] = {'relaxation_scheme': 'scf',
                                  'finish_with_scf': False}
        
        pw_params['structure'] = self.get_result('lowest_energy_structure')
        # use the minimum energy configuration found in the previous step
        # for the remaining inputs        
        old_wfs_pw = []
        # try to find previous pw wfs launched with pw_calc_min in input,
        # when it makes sense
        if (main_params.get('input',{}).get('scf_test_smearing',
            self._default_scf_test_smearing)==pw_calc_min.inp.parameters.dict.SYSTEM['smearing']
            and main_params.get('input',{}).get('scf_test_degauss',
                self._default_scf_test_degauss)==pw_calc_min.inp.parameters.dict.SYSTEM['degauss']):
            pw_params['pw_calculation'] = pw_calc_min
            old_wfs_pw = helpers.get_pw_wfs_with_parameters(pw_params,also_bands=True,
                ignored_keys=['codename','group_name','band_group_name',
                'calculation_set','settings','band_calculation_set','band_settings',
                'input|automatic_parallelization','input|clean_workdir',
                'input|max_restarts','parameters','kpoints',
                'band_input|automatic_parallelization','band_input|clean_workdir',
                'band_parameters_update|ELECTRONS|diagonalization'])
        # now try to find those without pw_calc_min in input
        pw_params['kpoints'] = pw_calc_min.inp.kpoints
        pw_params['settings'] = pw_calc_min.inp.settings.get_dict()
        pw_params['parameters'] = pw_calc_min.inp.parameters.get_dict()
        pw_params.pop('pw_calculation',None)
        # re-use the magnetic moments (if magnetic)
        start_mag = helpers.get_starting_magnetization_pw(
                            pw_calc_min.out.output_parameters.get_dict())
        if start_mag:
            pw_params['parameters']['SYSTEM'].update(start_mag)
        # delete relaxation namelists
        for namelist in ['IONS', 'CELL']:
            pw_params['parameters'].pop(namelist,None)
        # force smearing
        pw_params['parameters']['SYSTEM']['occupations'] = 'smearing'
        pw_params['parameters']['SYSTEM']['smearing'] = main_params.get(
                                    'input',{}).get('scf_test_smearing',
                                    self._default_scf_test_smearing)
        pw_params['parameters']['SYSTEM']['degauss'] = main_params.get(
                                    'input',{}).get('scf_test_degauss',
                                    self._default_scf_test_degauss)
        old_wfs_pw.extend(helpers.get_pw_wfs_with_parameters(pw_params,also_bands=True,
            ignored_keys=['codename','group_name','band_group_name',
                    'calculation_set','settings','band_calculation_set','band_settings',
                    'input|automatic_parallelization','input|clean_workdir','input|max_restarts',
                    'parameters|SYSTEM|use_all_frac',
                    'parameters|ELECTRONS|electron_maxstep',
                    'parameters|ELECTRONS|diagonalization',
                    'band_input|automatic_parallelization','band_input|clean_workdir',
                    'band_parameters_update|ELECTRONS|diagonalization']))
        old_wfs_pw = [load_node(pk) for pk in set([_.pk for _ in old_wfs_pw])]
        self.add_attribute('scf_bands_old_pw_wfs',[_.pk for _ in old_wfs_pw])
        
        if old_wfs_pw:
            self.append_to_report("Found {} previous PW scf+bands sub-workflow{} "
                                  "on structure {} with pk {}".format(
                                len(old_wfs_pw),"s" if len(old_wfs_pw)>1 else "",
                                pw_params['structure'].get_formula(),
                                pw_params['structure'].pk))
        
        else:
            if (main_params.get('input',{}).get('scf_test_smearing',
                    self._default_scf_test_smearing)==pw_calc_min.inp.parameters.dict.SYSTEM['smearing']
                and main_params.get('input',{}).get('scf_test_degauss',
                    self._default_scf_test_degauss)==pw_calc_min.inp.parameters.dict.SYSTEM['degauss']
                and Code.get_from_string(pw_params['codename']).get_computer().pk==pw_calc_min.get_computer().pk
                and (datetime.now(tz=pw_calc_min.ctime.tzinfo)-pw_calc_min.ctime).days<=7):
                # recent enough pw_calc_min that can be used here -> 
                # we avoid recomputing the scf
                pw_params['pw_calculation'] = pw_calc_min
                
            wf_pw = PwWorkflow(params=pw_params)
            wf_pw.store()
            self.append_to_report("Launching PW sub-workflow (pk: {}) "
                                  "with {} smearing".format(wf_pw.pk,
                                pw_params['parameters']['SYSTEM']['smearing']))
            self.attach_workflow(wf_pw)
            wf_pw.start()
        
        self.next(self.final_step)
        
    @Workflow.step
    def final_step(self):

        main_params = self.get_parameters()
        input_dict = main_params.get('input',{})
        
        # Retrieve the lowest energy initial pw calc. and its output structure
        pw_calc_min = self.get_result('lowest_energy_pw_calculation')
        pw_output_min = pw_calc_min.out.output_parameters

        # retrieve the scf calculation and its output parameters, and the
        # bands, from the previous step
        wf = (list(Workflow.query(pk__in=self.get_attribute('scf_bands_old_pw_wfs'))) +
              list(self.get_step(self.run_scf_bands).get_sub_workflows()))[0]
        inline_input_dict = {}
        kwargs = {}
            
        try:
            try:
                pw_calc_scf = wf.get_result('pw_calculation')
            except ValueError:
                pw_calc_scf = wf.get_parameter('pw_calculation')
            pw_output_scf = pw_calc_scf.out.output_parameters
            bands_output = wf.get_result('band_structure').out.bands.out.output_parameters
        
        except (ValueError, AttributeError):
            if input_dict.get('continue_upon_bands_failure',False):
                self.append_to_report("WARNING: PW scf + bands wf failed "
                    "or did not provide any result; we will still continue "
                    "to get the magnetic info only")
            else:
                raise ValueError("PW scf + bands wf failed or did not provide any result")
        
        else:
            self.add_result('scf_pw_calculation',pw_calc_scf)
            self.add_result('band_structure_after_scf',wf.get_result('band_structure'))
            self.add_result('band_structure_after_scf_info',bands_output)
            
            # input parameters for is_metallic_magnetic_inline
            list_keys = ['threshold_smearing_energy_per_atom',
                         'threshold_band_gap',
                         ]
            for k in list_keys:
                inline_input_dict[k] = input_dict.get(k,getattr(self,"_default_{}".format(k)))
            
            kwargs = {'bands_output_parameters': bands_output}
            if pw_output_scf.pk != pw_output_min.pk:
                kwargs['scf_test_calc_output_parameters'] = pw_output_scf
        
        if 'output_trajectory' in pw_calc_min.get_outputs_dict():
            kwargs['minimum_energy_calc_output_trajectory'] = pw_calc_min.out.output_trajectory
        else:
            kwargs['minimum_energy_calc_output_array'] = pw_calc_min.out.output_array
        
        # build the new pw input parameters and kpoints
        result_dict = get_is_metallic_magnetic_results(parameters=ParameterData(
                                                        dict=inline_input_dict),
                    minimum_energy_calc_output_parameters=pw_output_min,**kwargs)
        
        self.add_result('is_metallic_magnetic_info',result_dict['output_parameters'])
        
        info_group_name = main_params.get('info_group_name',None)
        if info_group_name is not None:
            group, created = Group.get_or_create(name=info_group_name)
            if created:
                self.append_to_report("Created group '{}'".format(info_group_name))
            # put the resulting calc. into the group
            group.add_nodes([result_dict['output_parameters']])
            self.append_to_report("Adding parameters with pk {} to group '{}'"
                                  "".format(result_dict['output_parameters'].pk,
                                            info_group_name))
        
        struc_group_name = main_params.get('structure_group_name',None)
        if struc_group_name is not None:
            group, created = Group.get_or_create(name=struc_group_name)
            if created:
                self.append_to_report("Created group '{}'".format(struc_group_name))
            # put the resulting calc. into the group
            group.add_nodes([self.get_result('lowest_energy_structure')])
            self.append_to_report("Adding structure with pk {} to group '{}'"
                                  "".format(self.get_result('lowest_energy_structure').pk,
                                            struc_group_name))
        
        self.append_to_report("Chronos workflow completed, all results appended")
        
        # clean scratch leftovers, if requested
        if main_params.get('input',{}).get('clean_workdir',self._clean_workdir):
            self.append_to_report("Cleaning scratch directories")
            save_calcs = [c for c in self.get_results().values() if isinstance(c,JobCalculation)]
            helpers.wipe_all_scratch(self, save_calcs)
        
        self.next(self.exit)

