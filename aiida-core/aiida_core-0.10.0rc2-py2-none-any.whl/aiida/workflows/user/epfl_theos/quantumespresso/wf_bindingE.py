# -*- coding: utf-8 -*-
"""
Workflow calculate the binding energy of structures.
"""

from aiida.common import aiidalogger
from aiida.orm.workflow import Workflow
from aiida.orm import Calculation, Code, Computer, Data, Group
from aiida.orm.calculation.inline import make_inline
from aiida.common.exceptions import WorkflowInputValidationError
from aiida.orm import CalculationFactory, DataFactory
from aiida.orm import load_node
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
import numpy as np
import time


__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller, Nicolas Mounet."


class BindingEnergyWfExc(Exception):
    pass


class NoLayerFoundExc(BindingEnergyWfExc):
    """
    Raised when a no layer is found anymore after the vc-relax of the
    3D structure.
    """
    pass

logger = aiidalogger.getChild('WorkflowDemo')
ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
BandsData = DataFactory('array.bands')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')


def get_max_wallclock(structure):
    number_of_sites = int(len(structure.sites) /2)
    max_wallclock = max(min(number_of_sites*3600,43199),7200)

    return max_wallclock

def get_max_wallclock_vc_relax(structure): 
    number_of_sites = len(structure.sites)
    max_wallclock = max(min(number_of_sites*3600,43199),7200)

    return max_wallclock

@make_inline
def binding_energy_inline(parameters_bulk,parameters_layer,structure_layer):
    """
    Inline calculation to compute the binding energy from the output
    of two calculations.
    :param parameters_bulk: output parameters of the bulk calculation
    :param parameters_layer: output parameters of the layer calculation
    :param structure_layer: layer structure (output structure if layer 
        calc. was a relaxation, otherwise input structure)
    :return: a dictionary of the form
            {'output_parameters': ParameterData with the dictionary
                                    {'binding_energy': binding energy per area,
                                     'binding_energy_units': 'eV/ang^2'}
             }
    """
    energy_bulk = parameters_bulk.get_dict()['energy']
    energy_layer = parameters_layer.get_dict()['energy']
    area = np.linalg.norm(np.cross(structure_layer.cell[0], structure_layer.cell[1]))
    binding_energy = (energy_bulk - energy_layer) / area
    
    return {'output_parameters': ParameterData(dict={
                                    'binding_energy': binding_energy,
                                    'binding_energy_units': 'eV/ang^2',
                                    'area': area,
                                    'area_units': 'ang^2',
                                    })
            }

class BindingEnergyWorkflow(Workflow):
    """
    Workflow to find the binding energy of a layered structure by comparing
    the energy of a 3D crystal after a vc-relax with the energy of a layer 
    found in the relaxed parent structure. It can also launch a subworkflow 
    to determine the binding energy curve for a single layer structure. 
    
    In the end the the relaxed structures, their number of atoms and energies
    are given as output. 
    
    .. note:: It does only work for single layer structures.
    
    Input description.
    The input is a dictionary that follows closely the input of the 
    pw workflow:

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
                         }
                     }
    
    General input :

    params = {  'input': {'distance_kpoints_in_mesh': 0.2,
                          'layer_relaxation_scheme': 'vc-relax',
                          'curve': False,
                          'distances': np.arange(0.5,10,0.5).tolist(),
                          },
                'structure':    structure,
                'pseudo_family': pseudo_family,
                'lowdimfinder_parameters': {u'bond_margins': [0.0],
                                            u'lowdim_dict': {u'full_periodicity': False,
                                                             u'orthogonal_axis_2D': True,
                                                             u'radii_source': u'alvarez',
                                                             u'rotation': True,
                                                             u'vacuum_space': 40
                                                             },
                                            u'output': {u'group_data': True,
                                                        u'parent_structure_with_layer_lattice': False,
                                                        u'rotated_parent_structure': True
                                                        },
                                            u'radii_offsets': [-0.75, -0.7, -0.65, -0.6, -0.55],
                                            u'target_dimensionality': 2
                                            },
                'pw_codename' : codename,
                'pw_calculation_set': {'resources':{'num_machines': 2},
                                       'max_wallclock_seconds': max_seconds,
                                        #'custom_scheduler_commands':"#SBATCH -A, --account=theos",
                                        },
                'pw_parameters': pw_input_dict,
                'pw_input':{'volume_convergence_threshold': 5.e-2,
                            'clean_workdir': False,
                            },
    }
    
    """

    _default_distance_kpoints_in_mesh = 0.2
    _default_layer_relaxation_scheme = 'scf'
    _default_curve = False

    def __init__(self,**kwargs):
        super(BindingEnergyWorkflow, self).__init__(**kwargs)

    @Workflow.step
    def start(self):
        """
        Check input parameters
        """

        self.append_to_report("Checking input parameters")
        
        mandatory_keys = [   ('structure',StructureData,"the structure (a previously stored StructureData object)"),
                             ('pseudo_family',basestring,'the pseudopotential family'),
                             ('lowdimfinder_parameters',dict,"the parameters for the lowdimfinder inline calculation (dictionary)"),
#                             ('pw_codename',basestring,'the PW codename'),
#                             ('pw_calculation_set',dict,'A dictionary with resources, walltime, ... for pw calcs.'),
#                             ('pw_parameters',dict,"A dictionary with the PW input parameters"),
                             ]
        
        main_params = self.get_parameters()
        
        # validate pw keys
        helpers.validate_keys(main_params, mandatory_keys)
        
        if 'pw_calculation' not in main_params.keys():
            self.next(self.launch_vc_relax)
        else:
            self.next(self.search_layers)

    @Workflow.step
    def launch_vc_relax(self):
        """
        Run a vc-relax calculation on a 3D structure which contains a layer.
        """

        self.append_to_report("Preparing vc-relax")
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
        kpoints_mesh_spacing = params.get('input',{}).get(
                                    'distance_kpoints_in_mesh',
                                    self._default_distance_kpoints_in_mesh)

        # construct the k-points for the initial structure
        kpoints = KpointsData()
        kpoints.set_cell_from_structure(structure)
        kpoints.set_kpoints_mesh_from_density(kpoints_mesh_spacing,
                                              force_parity=True)
        kpoints.store()
        pw_params['kpoints'] = kpoints

        # force vc-relax calculation
        try:
            pw_params['input']['relaxation_scheme'] = 'vc-relax'
        except KeyError:
            pw_params['input'] = {'relaxation_scheme': 'vc-relax'}

        pw_params['structure'] = structure

        #if pw_params['calculation_set'].get('max_wallclock_seconds', None) is None:
        #    pw_params['calculation_set']['max_wallclock_seconds'] = get_max_wallclock_vc_relax(structure)

        wf = PwWorkflow(params=pw_params)
        wf.start()
        self.append_to_report("vc-relax workflow on 3D  bulk launched (pk: {})".format(wf.pk))
        self.attach_workflow(wf)

        self.next(self.search_layers)

    @Workflow.step
    def search_layers(self):
        """
        Take the relaxed 3D, find the layer again and calculate the 
        energy of the layer in vacuum. 
        """
        from aiida.workflows.user.epfl_theos.dbimporters.utils import get_lowdimfinder_results

        params = self.get_parameters()
        if 'pw_calculation' in params.keys():
            pw_calculation = params.pop('pw_calculation')
        else:
            wf_pw_list = list(self.get_step(self.launch_vc_relax).get_sub_workflows().order_by('ctime'))
            pw_calculation = wf_pw_list[-1].get_result('pw_calculation')
        
        #self.append_to_report("Pw calc pk: {}".format(pw_calculation.pk))

        try:
            structure = pw_calculation.out.output_structure
            self.append_to_report("output structure pk: {}".format(structure.pk))
        except AttributeError:
            structure = pw_calculation.inp.structure
            self.append_to_report("input structure pk: {}".format(structure.pk))

        #lowdimfinder_inline_dict = params['structure'].inp.layerlattice3D_0.inp.lowdim_params.get_dict()
        #lowdimfinder_inline_params = ParameterData(dict=lowdimfinder_inline_dict).store()
        lowdimfinder_inline_params = ParameterData(dict=params['lowdimfinder_parameters'])
        result_dict =  get_lowdimfinder_results(structure=structure,
                                                   parameters=lowdimfinder_inline_params,
                                                   store=True)

        if (params['lowdimfinder_parameters']['target_dimensionality'] in
            result_dict['output_parameters'].get_dict()['all_dimensionalities_found']):
            for key in [k for k in result_dict.keys() if k.startswith('group_data_')]:
                group_data = result_dict[key].get_dict()
                idx = key.split('group_data_')[1]
                if len(group_data['dimensionality']) == 1:
                    break
            dimensionality_list = group_data['dimensionality']
        else:
            self.append_to_report('No layer anymore')
            raise NoLayerFoundExc

#        if dimensionality_list[0] != 2 or len(dimensionality_list) != 1:
#            margin = lowdimfinder_inline_dict['cov_bond_margin']
#
#            for i in np.linspace(0.01,0.1,10):
#                #increase margin
#                lowdimfinder_inline_dict['cov_bond_margin'] = margin + i 
#
#                self.append_to_report("Increasing margin to {}".format(lowdimfinder_inline_dict['cov_bond_margin']))
#
#
#                lowdimfinder_inline_params = ParameterData(dict=lowdimfinder_inline_dict).store()
#
#                calc, result_dict =  lowdimfinder_inline(aiida_struc = structure,lowdim_params=lowdimfinder_inline_params)
#
#                dimensionality_params = result_dict.pop('dimensionality_params')
#
#                dimensionality_list = dimensionality_params.get_dict()['dimensionality']
#
#               if dimensionality_list[0] == 2 and len(dimensionality_list) == 1:
#                    break

        #self.append_to_report("result_dict keys {}".format(result_dict.keys()))
        self.append_to_report("dimensionalities: {}".format(dimensionality_list))
        self.append_to_report("Taking reduced_structure_{} (pk {}) for "
            "the layer".format(idx,result_dict['reduced_structure_{}'.format(idx)].pk))

        if len(dimensionality_list) != 1:
            self.append_to_report('Not a single layer anymore')
            raise NoLayerFoundExc

        aiida_reduced_struc = result_dict.pop('reduced_structure_{}'.format(idx))        
        pw_params = {}
        for k,v in params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:]
                pw_params[new_k] = v
            elif k == 'pseudo_family': 
                pw_params[k] = v

        # choose layer relaxation scheme from input
        try:
            pw_params['input']['relaxation_scheme'] = params.get('input',{}).get(
                'layer_relaxation_scheme',self._default_layer_relaxation_scheme)
        except KeyError:
            pw_params['input'] = {'relaxation_scheme': params.get('input',{}).get(
                'layer_relaxation_scheme',self._default_layer_relaxation_scheme)}

        if pw_params['input']['relaxation_scheme'] == 'vc-relax':
            pw_params['parameters']['CELL'] = {'cell_dofree':'2Dxy'}

        pw_params['structure'] = aiida_reduced_struc

        # construct the k-points (from the kpoints of the 3D vc-relaxed 
        # structure)
        kpoints = KpointsData()
        kpoints_mesh = pw_calculation.inp.kpoints.get_kpoints_mesh()[0]
        kpoints.set_kpoints_mesh([k if pbc else 1 for pbc,k in zip(
                                aiida_reduced_struc.pbc,kpoints_mesh)])
        kpoints.store()
        pw_params['kpoints'] = kpoints

        #if pw_params['calculation_set'].get('max_wallclock_seconds', None) is None:
        #    pw_params['calculation_set']['max_wallclock_seconds'] = get_max_wallclock_vc_relax(structure)

        wf_layer = PwWorkflow(params=pw_params)
        self.attach_workflow(wf_layer)
        wf_layer.start()
        self.append_to_report("{} workflow launched  (pk: {})".format(
                pw_params['input']['relaxation_scheme'],wf_layer.pk))

        if params.get('input',{}).get('curve',self._default_curve):
            self.next(self.launch_curve)
        else: 
            self.next(self.final_step)

    @Workflow.step
    def launch_curve(self):
        """
        Only if the 'curve' input parameter is True. Start a subworkflow to 
        calculate the energy of the layered structure for various 
        interlayer distances.
        """
        params = self.get_parameters()
        wf_pw_list = list(self.get_step(self.search_layers).get_sub_workflows().order_by('ctime'))
        pw_calculation_2D = wf_pw_list[-1].get_result('pw_calculation')
        #self.append_to_report("pw calc pk: {}".format(pw_calculation))
        
        if 'pw_calculation' in params.keys():
            pw_calculation_3D = params.pop('pw_calculation')
        else:
            wf_pw_list = list(self.get_step(self.launch_vc_relax).get_sub_workflows().order_by('ctime'))
            pw_calculation_3D = wf_pw_list[-1].get_result('pw_calculation')

        try:
            structure_2D = pw_calculation_2D.out.output_structure
        except AttributeError:
            structure_2D = pw_calculation_2D.inp.structure
        
        self.append_to_report("Input structure pk for curve workflow: {}"
                              "".format(structure_2D.pk))
        
        curve_params = params
        curve_params['structure'] = structure_2D
        curve_params['pw_kpoints'] = pw_calculation_3D.inp.kpoints

        wf = BindingEnergyCurveWorkflow(params=curve_params)
        wf.start()
        self.attach_workflow(wf)
        self.append_to_report("Curve workflow launched {} ".format(wf.pk))

        self.next(self.final_step)

    @Workflow.step
    def final_step(self):
        """
        Gather the results
        """

        #self.append_to_report("Getting the results")

        params = self.get_parameters()
        wf_pw_layer_list = list(self.get_step(self.search_layers).get_sub_workflows().order_by('ctime'))
        
        if 'pw_calculation' not in params.keys():
            wf_pw_bulk_list = list(self.get_step(self.launch_vc_relax).get_sub_workflows().order_by('ctime'))
            bulk_pw_calculation = wf_pw_bulk_list[-1].get_result('pw_calculation')
        else:
            bulk_pw_calculation = params['pw_calculation']

        try:
            bulk_structure = bulk_pw_calculation.out.output_structure
        except AttributeError:
            bulk_structure = bulk_pw_calculation.inp.structure
        self.append_to_report("bulk structure pk: {}".format(bulk_structure.pk))

        layer_pw_calculation = wf_pw_layer_list[-1].get_result('pw_calculation')
        try:
            layer_structure = layer_pw_calculation.out.output_structure
        except AttributeError:
            layer_structure = layer_pw_calculation.inp.structure
        self.append_to_report("layer structure pk: {}".format(layer_structure.pk))

        area = np.linalg.norm(np.cross(layer_structure.cell[0], layer_structure.cell[1]))

        # make a ParameterData object with the binding energy
        _, result_dict = binding_energy_inline(
            parameters_bulk=bulk_pw_calculation.out.output_parameters,
            parameters_layer=layer_pw_calculation.out.output_parameters,
            structure_layer=layer_structure)
        binding_energy_params = result_dict['output_parameters']
        
        group_name = params.get('group_name',None)
        if group_name is not None:
            # create or get the group
            group, created = Group.get_or_create(name=group_name)
            if created:
                self.append_to_report("Created group '{}'".format(group_name))
            # put the binding energy into the group
            group.add_nodes([binding_energy_params])
            self.append_to_report("Adding binding energy with pk {} to "
                                  "group '{}'".format(binding_energy_params.pk,
                                                      group_name))
        
        binding_energy_dict = {
            #"initial_structure_extras": params['structure'].get_extras(),
            "formula": layer_structure.get_formula(),
            "bulk_relaxed_pk": bulk_structure.pk,
            "bulk_energy": bulk_pw_calculation.res.energy,
            "layer_relaxed_pk": layer_structure.pk,
            "layer_energy": layer_pw_calculation.res.energy,
            "area": area,
            "number_of_atoms": len(bulk_structure.sites),
        }

        self.add_results(binding_energy_dict)
        self.add_result('bulk_pw_calculation', bulk_pw_calculation)
        self.add_result('layer_pw_calculation', layer_pw_calculation)
        self.add_result('binding_energy_params', binding_energy_params)

        if params.get('input',{}).get('curve',self._default_curve):
            wf_curve_list = list(self.get_step(self.launch_curve).get_sub_workflows().order_by('ctime'))
            energy_curve = wf_curve_list[-1].get_result('energy_curve')
            layer_thickness = wf_curve_list[-1].get_result('layer_thickness')
            # OLD VERSION: wrong if third axis not orthogonal to the layer
            # bulk_vacuum_distance = np.linalg.norm(bulk_structure.cell[2]) - layer_thickness
            # CORRECTED VERSION
            bulk_vacuum_distance = np.abs(np.dot(bulk_structure.cell[2],
                np.cross(bulk_structure.cell[0],bulk_structure.cell[1]))/
                np.linalg.norm(np.cross(bulk_structure.cell[0],bulk_structure.cell[1])))\
                - layer_thickness
            energy_curve['distances'].append(bulk_vacuum_distance)
            energy_curve['energies'].append(bulk_pw_calculation.res.energy)
            energy_curve['distances'],energy_curve['energies']=zip(*sorted(zip(energy_curve['distances'],energy_curve['energies'])))
            self.add_result('binding_energy_curve', energy_curve)
            self.add_result('layer_thickness', layer_thickness)

        self.next(self.exit)


class BindingEnergyCurveWorkflow(Workflow):
    """
    Workflow to get the energy curve vs. interlayer distance for a 
    layered structure.
    """
    def __init__(self,**kwargs):
        super(BindingEnergyCurveWorkflow, self).__init__(**kwargs)

    _default_distance_kpoints_in_mesh = 0.2
    _default_layer_relaxation_scheme = 'scf'
    _default_distances = np.arange(-0.5,6.5,0.5).tolist() + [8, 10, 15] 

    @Workflow.step
    def start(self):
        """
        Check input parameters
        """

        mandatory_keys = [   ('structure',StructureData,"the structure (a previously stored StructureData object)"),
                             ('pseudo_family',basestring,'the pseudopotential family'),
                             ('lowdimfinder_parameters',dict,"the parameters for the lowdimfinder inline calculation (dictionary)"),
#                             ('pw_codename',basestring,'the PW codename'),
#                             ('pw_calculation_set',dict,'A dictionary with resources, walltime, ... for pw calcs.'),
#                             ('pw_parameters',dict,"A dictionary with the PW input parameters"),
                             ]
        
        main_params = self.get_parameters()
        
        # validate pw keys
        helpers.validate_keys(main_params, mandatory_keys)

        self.next(self.interlayer_distance_sweep)

    @Workflow.step
    def interlayer_distance_sweep(self):
        """
        Make a scan in the interlayer distance between layers and calculate 
        the energy for each distance. 
        """
        # maybe the this inline calculation should be put in quantumespresso/helpers
        from aiida.workflows.user.epfl_theos.dbimporters.utils import change_vacuum_space_inline

        params = self.get_parameters()

        structure = params['structure'] # this is a 2D structure 
                                        # (with a lot of vacuum space)
        original_vacuum_space = params['lowdimfinder_parameters']['lowdim_dict']['vacuum_space']
        distances = params.get('input',{}).get('distances',
                                    self._default_distances)

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
            vacuum_parameters = ParameterData(dict={'original_vacuum_space': original_vacuum_space,
                'new_vacuum_space': distance}).store()
            result_dict = change_vacuum_space_inline(structure=structure,parameters=vacuum_parameters,store=True)
            if result_dict['output_structure'] is None:
                self.append_to_report("Thickness {} is too small for "
                                      "distance {}".format(result_dict['output_parameters'].get_dict()['layer_thickness'],
                                                           distance))
            else:
                pw_params['structure'] = result_dict['output_structure']
                # set the relaxation scheme
                try:
                    pw_params['input']['relaxation_scheme'] = params.get(
                        'input',{}).get('layer_relaxation_scheme',
                                        self._default_layer_relaxation_scheme)
                except KeyError:
                    pw_params['input'] = {'relaxation_scheme': params.get(
                        'input',{}).get('layer_relaxation_scheme',
                                        self._default_layer_relaxation_scheme)}

                if pw_params['input']['relaxation_scheme'] == 'vc-relax':
                    pw_params['parameters']['CELL'] = {'cell_dofree':'2Dxy'}

                #if pw_params['calculation_set'].get('max_wallclock_seconds', None) is None:
                #    pw_params['calculation_set']['max_wallclock_seconds'] = get_max_wallclock(pw_params['structure'])
       
                wf_layer = PwWorkflow(params=pw_params)
                self.attach_workflow(wf_layer)
                wf_layer.start()
                wf_layer.add_attribute('distance', distance)

                self.append_to_report("{} workflow launched for distance {} (pk: {})"
                                      "".format(pw_params['input']['relaxation_scheme'],
                                                distance, wf_layer.pk))
                time.sleep(5)
            
        layer_thickness = result_dict['output_parameters'].get_dict()['layer_thickness']
        self.add_result('layer_thickness',layer_thickness)
        
        self.next(self.final_step)

    @Workflow.step
    def final_step(self):
        """
        Get results
        """
        wf_pw_layer_list = list(self.get_step(self.interlayer_distance_sweep
                            ).get_sub_workflows().order_by('ctime'))

        energy_curve = {}
        distances = []
        energies = []
        for wf in wf_pw_layer_list:
            try:
                energies.append(wf.get_results()['pw_calculation'].res.energy)
                distances.append(wf.get_attribute('distance'))
            except (KeyError, AttributeError):
                pass
            
        distances, energies = zip(*sorted(zip(distances, energies)))
        energy_curve['energies'] = energies
        energy_curve['distances'] = distances
        self.add_result("energy_curve", energy_curve)
        self.append_to_report("Binding energy curve workflow completed")

        self.next(self.exit)
