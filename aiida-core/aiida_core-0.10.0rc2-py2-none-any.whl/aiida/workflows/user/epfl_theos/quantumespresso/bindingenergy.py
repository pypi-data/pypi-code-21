# -*- coding: utf-8 -*-
"""
Workflow calculate the binding energy of structures.
"""

from aiida.orm.workflow import Workflow
from aiida.orm.calculation.inline import make_inline, optional_inline
from aiida.orm import CalculationFactory, DataFactory, load_node, Group, load_workflow
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
import time

ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
BandsData = DataFactory('array.bands')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')

import numpy as np

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet, Philippe Schwaller."


@optional_inline
def binding_energy_inline(parameters,parameters_bulk,structure_bulk,
                             parameters_filter_duplicate,**kwargs):
    """
    Inline calculation to compute the binding energy from the output
    of one bulk calculation and the output of all its sub-structures calculation.
    :param parameters: a ParameterData object with a dictionary of the form
        {'key_energy': name of the key to get the energy from the parameters_bulk
                           and parameters_sub_<i> dictionaries (default='energy'),
         sub_structure_uuid1: output_parameters_uuid1,
         sub_structure_uuid2: output_parameters_uuid2,
         etc.
         }
        (To the uuid of each non-redundant sub-structure of the bulk, corresponds
        the uuid of the calculation output parameters.)
    :param parameters_bulk: output parameters of the bulk calculation
    :param parameters_filter_duplicate: output of the filter duplicate inline
        calculation that filtered out redundant sub-structures
    :param structure_bulk: output (or input) structure of the bulk calculation
    :param kwargs:
        - parameters_sub_<i> where <i> is an integer: output parameters of the 
            non-redundant sub-structure calculations
        - structure_sub_<i> where <i> is an integer: sub-structures that 
            make up the bulk 
    .. note:: parameters_sub_<i> and structure_sub_<i> with the same i do not 
        correspond to each other (actually there are more structure_sub_* - one 
        for each sub-structure - than parameters_sub_* - one for each calculation
        performed)
    :return: a dictionary of the form
            {'output_parameters': ParameterData with the dictionary
                {'binding_energy_per_substructure': binding energy (divided by the number of highest dimensionality sub-structures in the unit cell),
                 'binding_energy_units': 'eV',
                 'number_of_atoms_in_bulk': number of atoms in the bulk,
                 'number_of_highest_dimensionality_substructures_in_bulk': the number of sub-structures that have the largest number of dimensions, in the bulk unit cell (e.g. the number of layers),
                 'relevant_dimension_of_highest_dimensionality_substructure': relevant dimension to be used to normalize the binding energy,
                 'substructure_dimensionalities': all dimensionalities of the sub-structures,
                 'relevant_dimension_units': unit for sub_structure_relevant_dimension,
                 'warnings': a list of warnings,
                 },
            }
    """
    params_dict = parameters.get_dict()
    key_energy = params_dict.get('key_energy','energy')
    binding_energy = parameters_bulk.get_dict()[key_energy]
    output_dict = {'{}_bulk'.format(key_energy): binding_energy}
    filter_duplicate_dict = parameters_filter_duplicate.get_dict()
    
    warnings = []
    relevant_dimension_sub = []
    dimensionalities_sub = []
    for structure_sub_key,structure_sub in [(k,v) for k,v in kwargs.iteritems()
                                            if k.startswith('structure_sub_')]:
        try:
            parameters_sub_uuid = [params_dict[k] for k,v in 
                                   filter_duplicate_dict.iteritems()
                                   if structure_sub.uuid in v][0]
        except (KeyError,IndexError):
            raise ValueError("Sub-structure {} not in parameters_filter_duplicate"
                             " output parameters, or there exists no calculation "
                             "output corresponding to it".format(structure_sub.pk)) 
        
        try:
            parameters_sub = [v for k,v in kwargs.iteritems() 
                              if (k.startswith('parameters_sub_') and
                              v.uuid==parameters_sub_uuid)][0]
        except IndexError:
            raise ValueError("Parameters with uuid {} are not "
                             "in the inputs".format(parameters_sub_uuid))
        
        energy_sub = parameters_sub.get_dict()[key_energy]
        output_dict["{}_{}".format(key_energy,structure_sub_key)] = energy_sub
        binding_energy -= energy_sub
        
        # now find out the relevant dimension to normalize the binding energy
        # extract periodic axes of the sub-structure
        axes = [v for pbc,v in zip(structure_sub.pbc,structure_sub.cell) if pbc]
        dimensionalities_sub.append(len(axes))
        if len(axes) == 0:
            relevant_dimension_sub.append(0)
        elif len(axes) == 1:
            # 1D sub-structure -> relevant dimension is the norm of the unit cell along its axis 
            relevant_dimension_sub.append(np.linalg.norm(axes[0]))
        elif len(axes) == 2:
            # 2D sub-structure -> relevant dimension is the in-plane area of its unit cell
            relevant_dimension_sub.append(np.linalg.norm(np.cross(axes[0],axes[1])))
        else:
            raise ValueError("Wrong dimensionality of the sub-structure with pk "
                             "{}".format(structure_sub.pk))
        
    the_dimensionality,the_relevant_dimension = max(zip(dimensionalities_sub,
                                    relevant_dimension_sub), key=lambda x: x[0])

    if np.max(np.abs(the_relevant_dimension-np.array([r for d,r in 
                        zip(dimensionalities_sub, relevant_dimension_sub)
                        if d==the_dimensionality]))) > 1e-6:
        warnings.append("Relevant dimension of the sub-structures with dim. "
                        "{} are not all the same: {}".format(the_dimensionality,
                                                            relevant_dimension_sub))
    
    # get the total number of highest dimensionality sub-structures (e.g.
    # the number of layers, for layered materials)
    n_high_dim_substructures = sum([d==the_dimensionality for d in dimensionalities_sub])
    
    output_dict.update({'binding_energy_per_substructure': binding_energy/float(n_high_dim_substructures),
                        'energy_units': 'eV',
                        'number_of_atoms_in_bulk': len(structure_bulk.sites),
                        'number_of_highest_dimensionality_substructures_in_bulk': n_high_dim_substructures,
                        'relevant_dimension_of_highest_dimensionality_substructure': the_relevant_dimension,
                        'substructure_dimensionalities': dimensionalities_sub,
                        'relevant_dimension_units': 'ang^{}'.format(the_dimensionality),
                        'warnings': warnings,
                        })
    return {'output_parameters': ParameterData(dict=output_dict)}

@make_inline
def rescale_third_axis_inline(parameters,structure):
    """
    Rescale the third axis of a structure cell (rescaling also atomic positions)
    :param structure: the structure to be rescaled
    :param parameters: ParameterData object with a dictionary of the form:
        {'distance_to_be_added': distance (in Angstrom) to be added to the cell
                                 third lattice vector
                                 }
    :return: a dictionary of the form
        {'output_structure': the rescaled structure}
    
    TODO: implement the case when third axis is not orthogonal to x-y!
    """
    distance = parameters.get_dict()['distance_to_be_added']
    cell = structure.cell
    scaling_ratio = (distance+np.linalg.norm(cell[2]))/np.linalg.norm(cell[2])
    the_ase = structure.get_ase().copy()
    the_ase.set_cell(np.dot(np.diag([1,1,scaling_ratio]),the_ase.get_cell()),
                     scale_atoms=True)
    return {'output_structure': StructureData(ase=the_ase)}


class BindingenergyException(Exception):
    pass


class NoSubstructureFoundError(BindingenergyException):
    """
    Raised when no substructure was found on the 3D structure.
    """
    pass


class BindingenergyWorkflow(Workflow):
    """
    Workflow to find the binding energy of a layered structure by comparing
    the energy of a 3D crystal with the energy of a layer 
    found in the relaxed parent structure. It can also launch a subworkflow 
    to determine the binding energy curve for a single layer structure,
    as a function of interlayer distance. 
    
    In the end the relaxed structures, their number of atoms and energies
    are given as output. 
    
    .. note:: for layered materials, be careful how you choose the initial 3D 
        structure: the best is that it has the same lattice as the layers
        (otherwise the in-plane k-points meshes will be different)
    
    Input description.
    The input is a dictionary that follows closely the input of the 
    pw workflow:

    settings = {}

    pw_input_dict = {'CONTROL': {
                         #'tstress': True,
                         },
                      'SYSTEM': {
                         'ecutwfc': 40.,
                         'ecutrho': 320.,
                         #'smearing': 'cold',
                         #'degauss': 0.002,

                         },
                      'ELECTRONS': {
                         #'conv_thr': 1.e-10,
                         #'diagonalization': 'cg',
                         #'mixing_mode': mixing_mode,
                         #'mixing_beta': mixing_beta,
                         }}
    
    General input :
    

    params = {
    'structure':     structure,
    'pseudo_family': pseudo_family,
    
    'input': {'substructure_relaxation_schemes': ['scf'], # for the sub-structures (can be several schemes). If empty, don't launch sub-structure calculations
              'curve_relaxation_scheme': 'relax', # for the curve wf only
              'curve_distances_to_be_added': np.arange(-3.,3.5,0.5).tolist()+[5.,8.,12.], # for the curve wf: distances to be added in the third cell dimension, w.r.t to initial 3D structure 
              'curve_distance_kpoints_in_mesh':  #  dist. between k-pts, for the BE curve wf (to have the same k-points grid for everything). If not present, 'pw_input' -> distance_kpoints_in_mesh is used for each calc.
              },
    .. note:: if there are no input parameter beginning with 'curve', the curve wf is not launched.
        Same for the sub-structure calculation(s) if 'substructure_relaxation_schemes' is an empty list

    'pw_codename': codename,
    'pw_calculation_set': {'resources':{'num_machines': 2},
                           "max_wallclock_seconds": max_seconds,
                           #'custom_scheduler_commands':"#SBATCH -A, --account=theos",
                           },
    'pw_parameters': pw_input_dict,
    'pw_settings': settings,
    'pw_kpoints': kpoints,

    'pw_input':{'volume_convergence_threshold': 5.e-2,
                'clean_workdir': False,
                'relaxation_scheme': 'vc-relax',
                'distance_kpoints_in_mesh': 0.2
                },
                
    'lowdimfinder_parameters': # these are the lowdim_finder inline calculation parameters
        { 'bond_margins': list of bond margins to test,
          'radii_offsets': list of additional offsets applied to the radii,
          'lowdim_dict': # dictionary with lowdimfinder parameters,
              {'rotation': True, # rotation = True puts the layer plane on x-y
               'vacuum_space': 40.,
               'radii_source': 'alvarez',
               'orthogonal_axis_2D': False, # if you don't put this one the curve wf might give nonsense results
               'full_periodicity': False,
               },
          'target_dimensionality': the dimensionality of the reduced structured we want to keep,
          'output': {
                      'parent_structure_with_layer_lattice': True, (True to output the 3D 
                              structure with the same lattice as the layer - 2D only,
                              and requires lowdim_dict['orthogonal_axis_2D'] = False),
                      'rotated_parent_structure': True, (True to output the rotated 3D structure),
                      'group_data': True, (True to output the group_data from the lowdimfinder),
                      },
        
        }
    }
    
    """

    #_default_distance_kpoints_in_mesh = 0.2
    _default_substructure_relaxation_schemes = ['scf']

    def __init__(self,**kwargs):
        super(BindingenergyWorkflow, self).__init__(**kwargs)


    @Workflow.step
    def start(self):
        """
        Check input parameters
        """

        self.append_to_report("Checking input parameters")
        
        mandatory_keys = [   #('structure',StructureData,"the structure (a previously stored StructureData object)"),
                             #('pseudo_family',basestring,"the pseudopotential family"),
                             ('lowdimfinder_parameters',dict,"the parameters for the lowdimfinder inline calculation (dictionary)"),
                             ]
        
        main_params = self.get_parameters()
        if 'distance_kpoints_in_mesh' in main_params.get('input',{}):
            self.append_to_report("WARNING: keyword 'input' -> 'distance_kpoints_in_mesh'"
                                  " is deprecated and will not be used; use "
                                  "'pw_input' -> 'distance_kpoints_in_mesh'"
                                  " instead")
        
        # validate keys
        helpers.validate_keys(main_params, mandatory_keys)
        
        if 'pw_calculation' not in main_params.keys():
            self.next(self.run_bulk)
        else:
            self.next(self.run_substructures)

    @Workflow.step
    def run_bulk(self):
        """
        Run a calculation on a 3D structure which contains a layer.
        """

        self.append_to_report("Preparing bulk calculation")
        from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow

        params = self.get_parameters()

        pw_params = {}

        for k,v in params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:]
                pw_params[new_k] = v
            elif k == 'pseudo_family': 
                pw_params[k] = v

        structure = params['structure']
        pw_params['structure'] = structure
        
        #if 'kpoints' not in pw_params.keys(): # THIS IS OBSOLET (k-pts distance now given in 'pw_input')
            #kpoints_mesh_spacing = params.get('input',{}).get(
            #                            'distance_kpoints_in_mesh',
            #                            self._default_distance_kpoints_in_mesh)
            # construct the k-points mesh for the initial structure
            #kpoints = KpointsData()
            #kpoints.set_cell_from_structure(structure)
            #kpoints.set_kpoints_mesh_from_density(kpoints_mesh_spacing,
            #                                      force_parity=True)
            #kpoints.store()
            #pw_params['kpoints'] = kpoints
        #    self.append_to_report("3D k-points mesh: {} (from k-pts distance: "
        #                        "{})".format(kpoints.get_kpoints_mesh()[0],
        #                                     kpoints_mesh_spacing))

        wf = PwWorkflow(params=pw_params)
        wf.start()

        self.append_to_report("Pw workflow on 3D bulk started, pk {}".format(wf.pk))
        self.attach_workflow(wf)

        self.next(self.run_substructures)


    @Workflow.step
    def run_substructures(self):
        """
        Take the calculated 3D, find the reduced substructure with the
        dimensionality looked for (2 for layers) and calculate the 
        energy of each substructures placed in vacuum. 
        """
        from aiida.workflows.user.epfl_theos.dbimporters.utils import \
            get_lowdimfinder_results, get_single_lowdimfinder_results, \
            get_filter_duplicate_structures_results
        
        params = self.get_parameters()

        if 'pw_calculation' in params.keys():
            pw_calculation = params.pop('pw_calculation')
            self.append_to_report("Pw bulk calculation from input, pk: {}, "
                                  "k-points mesh: {}".format(pw_calculation.pk,
                                pw_calculation.inp.kpoints.get_kpoints_mesh()[0]))
        else:
            wf_pw_list = list(self.get_step(self.run_bulk).get_sub_workflows().order_by('ctime'))
            pw_calculation = wf_pw_list[-1].get_result('pw_calculation')

        try:
            structure = pw_calculation.out.output_structure
        except AttributeError:
            structure = pw_calculation.inp.structure
        self.append_to_report("3D structure: {}".format(structure.pk))

        # parameters for duplicate filtering with super tight tolerances
        filter_duplicate_params = ParameterData(dict={'ltol': 1e-5,
                                                      'stol': 1e-5,
                                                      'angle_tol': 1e-3})
        # launching lowdimfinder to extract the substructures with the 
        # dimensionality looked for
        lowdimfinder_params = ParameterData(dict=params['lowdimfinder_parameters'])
        lowdimfinder_result_dict =  get_lowdimfinder_results(structure=structure,
                                                parameters=lowdimfinder_params,
                                                store=True)
        if 'lowdimfinder_parameters_0' not in lowdimfinder_result_dict.keys():
            raise NoSubstructureFoundError("No substructure with the correct "
                                "dimensionality was found in the computed bulk")
        
        sub_structures_dict = {}
        counter_sub = 0
        # Loop on DISTINCT lowdimfinder parameters to be used to obtain ALL
        # possible reductions into sub-structures.
        # We use the fact that in the lowdimfinder parameters, only the 
        # radii offsets and the bond margins may change
        for idx,(radii_offset,bond_margin) in enumerate(set([(v.get_dict()['radii_offset'],
                                        v.get_dict()['bond_margin'])
                                        for k,v in lowdimfinder_result_dict.iteritems()
                                        if k.startswith('lowdimfinder_parameters_')])):
            lowdim_dict = [v.get_dict() for k,v in lowdimfinder_result_dict.iteritems()
                           if k.startswith('lowdimfinder_parameters_') and
                                (v.get_dict()['radii_offset']==radii_offset and
                                 v.get_dict()['bond_margin']==bond_margin)][0]
            single_lowdimfinder_params = ParameterData(dict={
                'lowdim_dict': lowdim_dict,
                'output': {'parent_structure_with_layer_lattice': True},
                })
            # then launch again a single lowdimfinder to get ALL substructures
            single_lowdimfinder_result_dict = get_single_lowdimfinder_results(
                                                    structure=structure,
                                                    parameters=single_lowdimfinder_params,
                                                    store=True)
            self.append_to_report("Reduction {}: sub-structures dimensionalities: {}".format(
                idx,single_lowdimfinder_result_dict['group_data'].get_dict()['dimensionality']))
            self.add_attribute('single_lowdimfinder_inline_calc_{}'.format(idx),
                               single_lowdimfinder_result_dict['group_data'].inp.group_data)
            
            sub_structures_dict.update(dict( set( [('structure_{}'.format(
                            int(k.split('_')[2])+counter_sub),v)
                            for k,v in single_lowdimfinder_result_dict.iteritems()
                            if k.startswith('reduced_structure_')])))
            counter_sub += len(set([v.pk for k,v in single_lowdimfinder_result_dict.iteritems()
                              if k.startswith('reduced_structure_')]))
        
        # filter duplicates for all sub-structures
        filter_duplicate_result_dict = get_filter_duplicate_structures_results(
                parameters=filter_duplicate_params,store=True,
                **sub_structures_dict)
        
        self.add_attribute('filter_duplicate_output_parameters',
                           filter_duplicate_result_dict['output_parameters'])
        self.append_to_report("Number of distinct sub-structures: {}".format(
            len(filter_duplicate_result_dict['output_parameters'].get_dict().keys())))
            
        for sub_structure_uuid in filter_duplicate_result_dict[
            'output_parameters'].get_dict().keys():
            
            for relaxation_scheme in params.get('input',{}).get(
                    'substructure_relaxation_schemes',
                    self._default_substructure_relaxation_schemes):
                # TODO: re-use the output of each relaxation scheme for the next one
                sub_structure = load_node(sub_structure_uuid)
                pw_params = {'structure': sub_structure}
                for k,v in params.iteritems():
                    if k.startswith('pw_'):
                        new_k = k[3:]
                        pw_params[new_k] = v
                    elif k == 'pseudo_family':
                        pw_params[k] = v
                        
                for key in ['parameters','vdw_table']:
                    if (key not in pw_params.keys() and 
                        key in pw_calculation.get_inputs_dict()):
                        try:
                            pw_params[key] = pw_calculation.get_inputs_dict()[key].get_dict()
                        except AttributeError:
                            pw_params[key] = pw_calculation.get_inputs_dict()[key]
                # re-use the magnetic moments (if magnetic)
                start_mag = helpers.get_starting_magnetization_pw(
                        pw_calculation.out.output_parameters.get_dict())
                # suppress any species in starting_magnetization that is not
                # in the sub_structure, if any
                for k in [k for k in start_mag.get('starting_magnetization',{}) if k not in 
                          pw_params['structure'].get_kind_names()]:
                    start_mag['starting_magnetization'].pop(k)
                if start_mag:
                    pw_params['parameters']['SYSTEM'].update(start_mag)
                else:
                    pw_params['parameters']['SYSTEM'].pop('starting_magnetization',None)
                
                # choose layer relaxation scheme from input
                try:
                    pw_params['input']['relaxation_scheme'] = relaxation_scheme
                except KeyError:
                    pw_params['input'] = {'relaxation_scheme': relaxation_scheme}

                if pw_params['input']['relaxation_scheme'] == 'vc-relax':
                    if sum(sub_structure.pbc) == 2:
                        pw_params['parameters']['CELL'] = pw_params['parameters'].get('CELL',{})
                        pw_params['parameters']['CELL']['cell_dofree'] = '2Dxy'
                        if (abs(np.dot(sub_structure.cell[2],sub_structure.cell[0])) > 1e-8
                            or abs(np.dot(sub_structure.cell[2],sub_structure.cell[1])) > 1e-8):
                            self.append_to_report("WARNING: in sub-structure {}, "
                                                  "third axis is not orthogonal "
                                                  "to the other two".format(sub_structure.pk))
                    elif sum(sub_structure.pbc) == 1:
                        pw_params['parameters']['CELL'] = pw_params['parameters'].get('CELL',{})
                        pw_params['parameters']['CELL']['cell_dofree'] = 'z'
                        if ((abs(np.dot(sub_structure.cell[2],sub_structure.cell[0])) > 1e-8
                            or abs(np.dot(sub_structure.cell[2],sub_structure.cell[1])) > 1e-8)
                            or abs(np.dot(sub_structure.cell[0],sub_structure.cell[1])) > 1e-8):
                            self.append_to_report("WARNING: in sub-structure {}, "
                                                  "all axes are not orthogonal"
                                                  "".format(sub_structure.pk))
                    elif sum(sub_structure.pbc) == 0:
                        pw_params['input']['relaxation_scheme'] = 'relax'
                        self.append_to_report("sub-structure with pk {} is zero "
                                              "dimensional -> switched to relax "
                                              "calculation".format(sub_structure.pk))

                # construct the k-points
                kpoints = KpointsData()
                if all([(np.linalg.norm(np.array(v)-np.array(sub_v))<1e-8 or not pbc)
                        for pbc,sub_v,v in zip(sub_structure.pbc,sub_structure.cell,structure.cell)]):
                    # same dimension(s) along the sub-structure axes ->
                    # the mesh of the 3D calculation is used
                    kpoints_mesh = pw_calculation.inp.kpoints.get_kpoints_mesh()[0]
                    kpoints.set_kpoints_mesh([k if pbc else 1 for pbc,k in zip(
                                            sub_structure.pbc,kpoints_mesh)])
                    kpoints.store()
                    pw_params['kpoints'] = kpoints
                    self.append_to_report("k-points mesh: {} (from 3D calculation: "
                                          "{})".format(kpoints.get_kpoints_mesh()[0],
                                                       kpoints_mesh))
                else:
                    # the k-points mesh is set using the k-points distance provided
                    # in 'pw_input' (or the default one in pw workflow)
                    self.append_to_report("k-points mesh from k-pts distance")
                
                # launch sub-workflow
                wf_sub = PwWorkflow(params=pw_params)
                self.attach_workflow(wf_sub)
                wf_sub.start()
                self.append_to_report("{} Pw workflow launched  (pk: {}) "
                    "on sub-structure {} with pk {} (dim. {})".format(
                    pw_params['input']['relaxation_scheme'],wf_sub.pk,
                    sub_structure.get_formula(),sub_structure.pk,
                    sum(sub_structure.pbc)))

        if any([_.startswith('curve') for _ in params.get('input',{}).keys()]):
            self.next(self.run_curve)
        else: 
            self.next(self.final_step)


    @Workflow.step
    def run_curve(self):
        """
        Only if there are input parameters beginning with 'curve'. 
        Start a subworkflow to calculate the energy of the structure for various
        interlayer distances (actually, we change the cell parameter along the 
        stacking axis).
        .. note:: It works only for layered materials!
        """
        params = self.get_parameters()        
        if 'pw_calculation' in params.keys():
            pw_calculation = params.pop('pw_calculation')
        else:
            wf_pw_list = list(self.get_step(self.run_bulk).get_sub_workflows().order_by('ctime'))
            pw_calculation = wf_pw_list[-1].get_result('pw_calculation')
        curve_params = params
        
        # I choose only one 3D structure (the first one)...
        try:
            structure_3D = self.get_attribute('single_lowdimfinder_inline_calc_0'
                                              ).out.layerlattice3D_structure_0
        except AttributeError:
            structure_3D = self.get_attribute('single_lowdimfinder_inline_calc_0'
                                              ).inp.structure
            self.append_to_report("WARNING: 3D structure with layer lattice not found "
                                  "(probably orthogonal_axis_2D is set to True) "
                                  "-> curve wf might give wrong results if layer "
                                  "not along x-y plane")
        curve_params['structure'] = structure_3D
        self.append_to_report("Input structure pk for curve workflow: {}"
                              "".format(curve_params['structure'].pk))
                    
        if 'curve_distance_kpoints_in_mesh' in params.get('input',{}):
            # construct the k-points (cannot use directly the 3D calc. kpoints
            # as the structure is potentially not the same)
            kpoints = KpointsData()
            # the k-points mesh is set using the k-points distance provided
            kpoints_mesh_spacing = params['input']['curve_distance_kpoints_in_mesh']
            kpoints = KpointsData()
            kpoints.set_cell_from_structure(structure_3D)
            kwargs = {}
            if 'curve_force_parity_kpoints_mesh' in params['input']:
                kwargs = {'force_parity': params['input']['curve_force_parity_kpoints_mesh']}
            kpoints.set_kpoints_mesh_from_density(kpoints_mesh_spacing,
                                                  **kwargs)
            self.append_to_report("k-points mesh for curve wf: {} (from k-pts distance: "
                                  "{})".format(kpoints.get_kpoints_mesh()[0],
                                               kpoints_mesh_spacing))
            kpoints.store()
            curve_params['pw_kpoints'] = kpoints
        # add other parameters from the bulk calculation, if not redefined in params
        for key in ['pw_parameters','pw_vdw_table']:
            if (key not in curve_params.keys() and 
                key[3:] in pw_calculation.get_inputs_dict()):
                try:
                    curve_params[key] = pw_calculation.get_inputs_dict()[key[3:]].get_dict()
                except AttributeError:
                    curve_params[key] = pw_calculation.get_inputs_dict()[key[3:]]

        wf = BindingenergycurveWorkflow(params=curve_params)
        wf.start()
        self.attach_workflow(wf)
        self.append_to_report("Curve workflow launched {} ".format(wf.pk))

        self.next(self.final_step)

    @Workflow.step
    def final_step(self):
        """
        Gather the results.
        """
        params = self.get_parameters()
        group_name = params.get('group_name',None)
        wf_sub_all = list(self.get_step(self.run_substructures).get_sub_workflows())
        
        if any([_.startswith('curve') for _ in params.get('input',{}).keys()]):
            wf_curve = list(self.get_step(self.run_curve).get_sub_workflows().order_by('ctime'))[0]
            self.add_results(wf_curve.get_results())

        if 'pw_calculation' not in params.keys():
            wf_pw_bulk_list = list(self.get_step(self.run_bulk).get_sub_workflows().order_by('ctime'))
            bulk_pw_calculation = wf_pw_bulk_list[-1].get_result('pw_calculation')
        else:
            bulk_pw_calculation = params['pw_calculation']

        try:
            bulk_structure = bulk_pw_calculation.out.output_structure
        except AttributeError:
            bulk_structure = bulk_pw_calculation.inp.structure
        #self.append_to_report("bulk structure pk: {}".format(bulk_structure.pk))
        self.add_result('bulk_pw_calculation', bulk_pw_calculation)
        
        parameters_filter_duplicate = self.get_attribute('filter_duplicate_output_parameters')
        parameters_filter_duplicate_dict = parameters_filter_duplicate.get_dict()
        # output one binding energy per relaxation scheme and per reduction scheme
        for idx,single_lowdimfinder_result_dict in sorted([(k.split('_')[-1],v.get_outputs_dict())
                                for k,v in self.get_attributes().iteritems()
                                if k.startswith('single_lowdimfinder_inline_calc_')]):
        
            for relaxation_scheme in params.get('input',{}).get(
                        'substructure_relaxation_schemes',
                        self._default_substructure_relaxation_schemes):
            
                sub_dict = dict(set([('structure_sub_{}'.format(k.split('_')[2]),v)
                            for k,v in single_lowdimfinder_result_dict.iteritems()
                            if k.startswith('reduced_structure_')]))
                i = 0
                params_dict = {}
                for wf_sub in wf_sub_all:
                    if (wf_sub.get_parameter('input')['relaxation_scheme'] == relaxation_scheme
                        and (wf_sub.get_parameter('structure').uuid in parameters_filter_duplicate_dict
                        and any([v.uuid in parameters_filter_duplicate_dict[wf_sub.get_parameter('structure').uuid]
                                 for v in sub_dict.values()]))):
                        sub_pw_calculation = wf_sub.get_result('pw_calculation')
                        sub_dict['parameters_sub_{}'.format(i)] = \
                                        sub_pw_calculation.out.output_parameters
                        params_dict[wf_sub.get_parameter('structure').uuid] = \
                                sub_pw_calculation.out.output_parameters.uuid
                        self.add_result('substructure_pw_calculation_{}_{}'.format(
                                        relaxation_scheme,i),sub_pw_calculation)
                        i += 1
                
                # make a ParameterData object with the binding energy
                result_dict = binding_energy_inline(
                    parameters=ParameterData(dict=params_dict),
                    parameters_bulk=bulk_pw_calculation.out.output_parameters,
                    structure_bulk=bulk_structure,
                    parameters_filter_duplicate=parameters_filter_duplicate,
                    store=True, **sub_dict)
                
                binding_energy_params = result_dict['output_parameters']
                self.add_result('binding_energy_params_{}_{}'.format(relaxation_scheme,idx),
                                binding_energy_params)
                self.append_to_report("Binding energy for {} scheme (reduction "
                                      "{}) computed, stored in pk {}".format(
                                                        relaxation_scheme,idx,
                                                        binding_energy_params.pk))
                if group_name is not None:
                    # create or get the group
                    group, created = Group.get_or_create(name="{}_{}".format(group_name,
                                                                        relaxation_scheme))
                    if created:
                        self.append_to_report("Created group '{}'".format(group_name))
                    # put the binding energy into the group
                    group.add_nodes([binding_energy_params])
                    self.append_to_report("Adding binding energy with pk {} to "
                                          "group '{}'".format(binding_energy_params.pk,
                                                              group_name))
        
        self.append_to_report("Binding energy workflow completed")
        
        self.next(self.exit)


class BindingenergycurveWorkflow(Workflow):
    """
    Workflow to get the energy curve vs. cell third dimension for a 
    layered structure.\
    .. note:: Works only for a layered structure.
    .. note:: All atomic positions are scaled according to the change of the 
        cell 3rd dimension. Therefore, a 'relax' relaxation scheme is the best
        option. vc-relax is also possible (then the 3rd direction is not relaxed).
    """
    def __init__(self,**kwargs):
        super(BindingenergycurveWorkflow, self).__init__(**kwargs)

    _default_curve_relaxation_scheme = 'relax'
    _default_curve_distances_to_be_added = np.arange(-3.,3.5,0.5).tolist() + [5., 8., 12.] 

    @Workflow.step
    def start(self):
        """
        Check input parameters
        """

        mandatory_keys = [   ('structure',StructureData,"the structure (a previously stored StructureData object)"),
                             ('pseudo_family',basestring,'the pseudopotential family'),
#                             ('pw_codename',basestring,'the PW codename'),
#                             ('pw_calculation_set',dict,'A dictionary with resources, walltime, ... for pw calcs.'),
#                             ('pw_parameters',dict,"A dictionary with the PW input parameters"),
                             ]
        
        main_params = self.get_parameters()
        
        # validate keys
        helpers.validate_keys(main_params, mandatory_keys)
        self.next(self.run_cell_scan)

    @Workflow.step
    def run_cell_scan(self):
        """
        Make a scan in the third cell dimension and calculate the energy. 
        """
        params = self.get_parameters()

        structure = params['structure'] # this is a 3D bulk structure
        distances = params.get('input',{}).get('curve_distances_to_be_added',
                                    self._default_curve_distances_to_be_added)

        for distance in distances:
            # build pw wf parameters
            pw_params = {}
            for k,v in params.iteritems():
                if k.startswith('pw_'):
                    new_k = k[3:]
                    pw_params[new_k] = v
                elif k == 'pseudo_family': 
                    pw_params[k] = v
            # Note: k-points are inherited from the pw_kpoints key in params 
            # modify the structure, changing the distance between layers
            rescale_parameters = ParameterData(dict={'distance_to_be_added': distance}).store()
            _, result_dict = rescale_third_axis_inline(structure=structure,
                                                       parameters=rescale_parameters)
            if result_dict['output_structure'] is None:
                self.append_to_report("Third cell dimension {} is too small for "
                                      "distance {}".format(np.linalg.norm(structure.cell[2]),
                                                           distance))
            else:
                pw_params['structure'] = result_dict['output_structure']
                # set the relaxation scheme
                try:
                    pw_params['input']['relaxation_scheme'] = params.get(
                        'input',{}).get('curve_relaxation_scheme',
                                        self._default_curve_relaxation_scheme)
                except KeyError:
                    pw_params['input'] = {'relaxation_scheme': params.get(
                        'input',{}).get('curve_relaxation_scheme',
                                        self._default_curve_relaxation_scheme)}

                if pw_params['input']['relaxation_scheme'] == 'vc-relax':
                    pw_params['parameters']['CELL'] = pw_params['parameters'].get('CELL',{})
                    pw_params['parameters']['CELL']['cell_dofree'] = '2Dxy'
                    if (abs(np.dot(pw_params['structure'].cell[2],
                                   pw_params['structure'].cell[0])) > 1e-8
                        or abs(np.dot(pw_params['structure'].cell[2],
                                      pw_params['structure'].cell[1])) > 1e-8):
                        self.append_to_report("WARNING: in structure {}, third "
                                              "axis is not orthogonal to the "
                                              "other two".format(pw_params['structure'].pk))

                # suppress any species in starting_magnetization that is not
                # in the sub_structure, if any
                start_mag = pw_params['parameters'].get('SYSTEM',{}).get('starting_magnetization',{})
                for k in [k for k in start_mag if k not in 
                          pw_params['structure'].get_kind_names()]:
                    start_mag.pop(k)
                if start_mag:
                    pw_params['parameters']['SYSTEM']['starting_magnetization'] = start_mag

                wf_pw = PwWorkflow(params=pw_params)
                self.attach_workflow(wf_pw)
                wf_pw.start()
                wf_pw.add_attribute('distance', distance)
                self.append_to_report("{} Pw workflow launched for distance {} (pk: {})"
                                      "".format(pw_params['input']['relaxation_scheme'],
                                                distance, wf_pw.pk))
                time.sleep(5)
            
        self.next(self.final_step)

    @Workflow.step
    def final_step(self):
        """
        Get results.
        """
        wf_pw_list = list(self.get_step(self.run_cell_scan
                            ).get_sub_workflows().order_by('ctime'))

        energy_curve = {}
        distances = []
        energies = []
        for wf in wf_pw_list:
            try:
                energies.append(wf.get_results()['pw_calculation'].res.energy)
                distances.append(wf.get_attribute('distance'))
            except (KeyError, ValueError):
                pass
        
        distances, energies = zip(*sorted(zip(distances, energies)))
        energy_curve['energies'] = energies
        energy_curve['distances'] = distances
        self.add_result("energy_curve", energy_curve)
        self.append_to_report("Binding energy curve workflow completed")

        self.next(self.exit)
