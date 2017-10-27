# -*- coding: utf-8 -*-

"""
Workflow calculate the elastic constants of structures
"""

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller, Nicolas Mounet."

from aiida.common import aiidalogger
from aiida.orm.workflow import Workflow
from aiida.orm import Calculation, Code, Computer, Data, Group
from aiida.orm.calculation.inline import make_inline, optional_inline
from aiida.common.exceptions import WorkflowInputValidationError
from aiida.orm import CalculationFactory, DataFactory, load_workflow
from aiida.orm import load_node
from aiida.workflows.user.epfl_theos.quantumespresso import helpers
from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow
import numpy as np
from aiida.workflows.user.epfl_theos.quantumespresso import elastic2d_utils
from aiida.workflows.user.epfl_theos.dbimporters.utils import get_standardize_structure_results
import time

from aiida.common.constants import ry_si, ry_to_ev, ang_to_m
from aiida.common import aiidalogger

try:
    import spglib
except ImportError:
    from pyspglib import spglib

logger = aiidalogger.getChild('WorkflowDemo')
ParameterData = DataFactory('parameter')
KpointsData = DataFactory('array.kpoints')
BandsData = DataFactory('array.bands')
ArrayData = DataFactory('array')
StructureData = DataFactory('structure')
PwCalculation = CalculationFactory('quantumespresso.pw')


logger = aiidalogger.getChild('WorkflowElastic')

# Inline calculations
from aiida.workflows.user.epfl_theos.quantumespresso.elastic import best_fit_inline, deformation_inline


@make_inline
def elastic_constants_inline(structure,  **kwargs):
    """
    :param parameters: ParameterData with information on method -> 'stress' or 'energy' and spacegroup
    :param kwargs: dictionary containing best fit ParameterData with 'polynomial_coefficients'
    :return:  dictionary {
        'output_parameters' : ParameterData with dictionary {
    }
    """
    from aiida.workflows.user.epfl_theos.quantumespresso import elastic_utils
    from aiida.common.constants import ry_si, ry_to_ev, ang_to_m

    undeformed_structure = structure
    volume_of_undeformed_structure = undeformed_structure.get_cell_volume()

    space_group = spglib.get_symmetry_dataset(undeformed_structure.get_ase())['number']

    methods = list(set([v.inp.output_parameters.inp.parameters.get_dict()['method'] for v in kwargs.values()]))

    if len(methods) != 1:
        raise ValueError("Mixing energy and stress method is not allowed.")
    else:
        method = methods[0]

    # conversion from eV/A^3 to GPa
    default_energy_conversion = ry_si / ry_to_ev / ang_to_m ** 3 / 10 ** 9 / volume_of_undeformed_structure

    # stresses are in GPa, but QE gives negative sign values
    default_stress_conversion = -1

    default_units = 'GPascal'

    # make it 2D compatible
    if sum(undeformed_structure.pbc) == 2:
        cell = undeformed_structure.cell
        height_of_2D_cell = np.dot([0,0,1], cell[2])

        default_energy_conversion *= height_of_2D_cell * ang_to_m * 10 ** 9
        default_stress_conversion *= height_of_2D_cell * ang_to_m * 10 ** 9

        default_units = 'N/m'

    if method == 'energy':
        derivative = 2

    elif method == 'stress':
        derivative = 1

    else:
        return None

    coefficients = []
    standard_deviations = []

    keys = kwargs.keys()
    name = '_'.join(keys[0].split('_')[:-1])
    sorted_keys = [int(key.split('_')[-1]) for key in keys]
    sorted_keys.sort()

    if method == 'energy':
        for key in sorted_keys:
            poly_coeffs_mean =  kwargs[name + '_' + str(key)].get_dict()['polynomial_coefficients_mean']
            poly_coeffs_std = (kwargs[name + '_' + str(key)].get_dict()['polynomial_coefficients_std'])

            coefficients.append(poly_coeffs_mean[-(derivative+1)])
            standard_deviations.append(poly_coeffs_std[-(derivative+1)])
            default_conversion = default_energy_conversion

    elif method == 'stress':
        for key in sorted_keys:
            for stress_index in range(6):
                poly_coeffs_mean =  kwargs[name + '_' + str(key)].get_dict()['tau_{}'.format(
                                                                    stress_index)]['polynomial_coefficients_mean']
                poly_coeffs_std =  kwargs[name + '_' + str(key)].get_dict()['tau_{}'.format(
                                                                    stress_index)]['polynomial_coefficients_std']

                coefficients.append(poly_coeffs_mean[-(derivative+1)])
                standard_deviations.append(poly_coeffs_std[-(derivative+1)])
                default_conversion = default_stress_conversion
    else:
        # method not implemented
        raise NotImplementedError('Only stress and energy method implemented')

    tension_coefficient_matrix = elastic2d_utils.get_elastic_constants(space_group, coefficients, method)
    standard_deviation_vector = elastic2d_utils.get_standard_deviation_of_elastic_constants(space_group,
                                                                                        standard_deviations, method)

    tension_coefficient_matrix = tension_coefficient_matrix * default_conversion
    std_vector = standard_deviation_vector * abs(default_conversion)

    elastic_properties = elastic2d_utils.Elastic2dProperties(tension_coefficient_matrix)
    stability_test_dict = {}

    stability_test_dict['positive_definite_criterion'] = elastic_properties.test_positive_definite_criterion()

    is_stable =  all(stability_test_dict.values())

    return {'output_parameters': ParameterData(dict={
        'tension_coefficients': tension_coefficient_matrix.tolist(),
        'tension_coefficients_standard_deviation': std_vector.tolist(),
        'tension_coefficients_units': default_units,
        'is_stable': is_stable,
        })}

# Elastic workflow

class Elastic2dWorkflow(Workflow):
    """
    lagrangian_strain -> lagrangian strain
    eps/epsilon -> physical strain (eulerian strain)
    """
    _default_distance_kpoints_in_mesh = 0.2
    _default_deformed_structures_relaxation_scheme = 'scf'
    _default_refinement_symprec = 5e-3

    def __init__(self, **kwargs):
        super(Elastic2dWorkflow, self).__init__(**kwargs)

    @Workflow.step
    def start(self):
        """
        Check input parameters
        :return:
        """

        self.append_to_report("Checking input parameters")

        mandatory_keys = [  # ('structure', StructureData, "the structure (a previously stored StructureData object)"),
            # ('pseudo_family', basestring, 'the pseudopotential family'),
            ('input', dict, "parameters to calculate the elastic constants"),
            # ('pw_codename',basestring,'the PW codename'),
            # ('pw_calculation_set',dict,'A dictionary with resources, walltime, ... for pw calcs.'),
            # ('pw_parameters',dict,"A dictionary with the PW input parameters"),
        ]

        mandatory_keys_elastic_params = [
            ('method',basestring, "list of methods to execute, ['energy', 'stress'] or one of both options"),
            ('number_of_strains_per_deformation', int, "number of pw calculations to be done per deformation, " \
                "the calculation of the undeformed structure is added automatically"),
            ]

        main_params = self.get_parameters()
        elastic_params = main_params['input']
        method = elastic_params['method']



        mandatory_keys_elastic_params.append(('maximal_lagrangian_strain_{}'.format(method), float,
                                              "lagrangian_strain max for {} calculation".format(method)))
        # validate pw keys
        helpers.validate_keys(main_params, mandatory_keys)

        if 'pw_calculation' in main_params.keys():
            helpers.validate_keys(elastic_params, mandatory_keys_elastic_params)
            self.append_to_report('Found pw_calculation with pk {} in input params, -> run_deformed_structures'.format(
                                                                                        main_params['pw_calculation']))
            self.next(self.run_deformed_structures)
        elif 'elastic_wf' in main_params.keys():
            self.append_to_report('Found ElasticWorkflow with pk {} in input params, -> analysis'.format(
                                                                                        main_params['elastic_wf']))
            self.next(self.analysis)
        else:
            helpers.validate_keys(elastic_params, mandatory_keys_elastic_params)
            structure = main_params['structure']
            if sum(structure.pbc) != 2:
                ValueError('Check periodic boundary conditions of structure, not 2D...')
            self.next(self.run_input_structure)

    @Workflow.step
    def run_input_structure(self):
        """
        Run a calculation on a undeformed structure
        """

        self.append_to_report("Preparing bulk calculation")
        from aiida.workflows.user.epfl_theos.quantumespresso.pw import PwWorkflow

        params = self.get_parameters()
        pw_params = {}

        for k, v in params.iteritems():
            if k.startswith('pw_'):
                new_k = k[3:]
                pw_params[new_k] = v
            elif k == 'pseudo_family':
                pw_params[k] = v

        structure = params['structure']
        pw_params['structure'] = structure

        if pw_params['input']['relaxation_scheme'] == 'vc-relax':
            if sum(structure.pbc) == 2:
                pw_params['parameters']['CELL'] = pw_params['parameters'].get('CELL',{})
                pw_params['parameters']['CELL']['cell_dofree'] = '2Dxy'
                if (abs(np.dot(structure.cell[2],structure.cell[0])) > 1e-8
                    or abs(np.dot(structure.cell[2],structure.cell[1])) > 1e-8):
                    self.append_to_report("WARNING: in sub-structure {}, "
                                          "third axis is not orthogonal "
                                          "to the other two".format(structure.pk))

        if 'kpoints' not in pw_params.keys():
            kpoints_mesh_spacing = params.get('input', {}).get(
                'distance_kpoints_in_mesh',
                self._default_distance_kpoints_in_mesh)

            # construct the k-points mesh for the initial structure
            kpoints_dummy = KpointsData()
            kpoints_dummy.set_cell_from_structure(structure)
            kpointsmesh_ini = [max(int(np.ceil(round(np.linalg.norm(b) / kpoints_mesh_spacing, 5))), 1)
                               if structure.pbc[i] else 1 for i, b in enumerate(kpoints_dummy.reciprocal_cell)]
            kpointsmesh_ini = [k + (k % 2) if pbc else 1 for pbc, k in zip(structure.pbc, kpointsmesh_ini)]

            kpoints = KpointsData()
            kpoints.set_kpoints_mesh(kpointsmesh_ini)
            kpoints.store()
            pw_params['kpoints'] = kpoints
            self.append_to_report("3D k-points mesh: {} (from k-pts distance: "
                                  "{})".format(kpoints.get_kpoints_mesh()[0], kpoints_mesh_spacing))

        wf = PwWorkflow(params=pw_params)
        wf.start()

        self.append_to_report("Pw workflow on undeformed structure started, pk {}".format(wf.pk))
        self.attach_workflow(wf)

        self.next(self.run_deformed_structures)

    @Workflow.step
    def run_deformed_structures(self):
        """
        Take the input structure, perform deformations and run energy/stress calculations.
        """
        params = self.get_parameters()

        if 'pw_calculation' in params.keys():
            pw_calculation = params.pop('pw_calculation')
            self.append_to_report("Pw bulk calculation from input, pk: {}, k-points mesh: {}".format(pw_calculation.pk,
                                                            pw_calculation.inp.kpoints.get_kpoints_mesh()[0]))
        else:
            wf_pw_list = list(self.get_step(self.run_input_structure).get_sub_workflows().order_by('ctime'))
            pw_calculation = wf_pw_list[-1].get_result('pw_calculation')

        try:
            structure = pw_calculation.out.output_structure
        except AttributeError:
            structure = pw_calculation.inp.structure

        space_group = spglib.get_symmetry_dataset(structure.get_ase())['number']

        symprec = params['input'].get('refinement_symprec', self._default_refinement_symprec)

        if symprec != 0.:
            refine_parameters = ParameterData(dict={
                'symprec': symprec,
            })

            refine_structure_output = get_standardize_structure_results(parameters=refine_parameters,
                                                                   structure=structure)
            structure = refine_structure_output['standardized_structure']

            new_space_group = spglib.get_symmetry_dataset(structure.get_ase())['number']

            if new_space_group != space_group:
                self.append_to_report('Refined structure symmetry from space group {} to {}'.format(
                    space_group, new_space_group
                ))

                space_group = new_space_group

        self.add_attribute('undeformed_structure', structure)

        self.append_to_report("Undeformed structure: {} Space group {}".format(structure.pk, space_group))

        # Get the deformations
        elastic_params = params['input']

        method = elastic_params['method']
        lagrangian_strains, strain_numbers = elastic2d_utils.get_strain_list(space_group, method)

        for deformation_index, strain_vector in enumerate(lagrangian_strains):
            deformation_inline_params = ParameterData(dict={
                'maximal_lagrangian_strain': elastic_params['maximal_lagrangian_strain_{}'.format(method)],
                'number_of_strains_per_deformation': elastic_params['number_of_strains_per_deformation'],
                'strain_vector': strain_vector,
                'normalize_deformation_matrix': elastic_params.get('normalize_deformation_matrix', True),
            })
            self.append_to_report('Deforming original structure with a Lagrangian strain vector of'
                                  '{}, maximal_lagrangian_strain = {}, using {} deformed structures'.format(strain_vector,
                                                                      elastic_params['maximal_lagrangian_strain_{}'.format(method)],
                                                                      elastic_params[
                                                                          'number_of_strains_per_deformation']))

            if elastic_params['number_of_strains_per_deformation']%2 ==1:
                self.append_to_report("WARNING: The number of deformed structures is odd -> will be decreased by one")

            _, deformation_result_dict = deformation_inline(structure=structure, parameters=deformation_inline_params)

            pw_params = {}

            # take inputs from previous pw calculation
            for key in ['vdw_table','kpoints', 'parameters']:
                    if key in pw_calculation.get_inputs_dict():
                        try:
                            pw_params[key] = pw_calculation.get_inputs_dict()[key].get_dict()
                        except AttributeError:
                            pw_params[key] = pw_calculation.get_inputs_dict()[key]

            # if defined in parameters of elastic inputs overwrite
            for k, v in params.iteritems():
                if k.startswith('pw_'):
                    new_k = k[3:]
                    pw_params[new_k] = v
                elif k == 'pseudo_family':
                    pw_params[k] = v

                # choose deformed structure relaxation scheme from input
                relaxation_scheme = params.get('input', {}).get('deformed_structures_relaxation_scheme',
                            self._default_deformed_structures_relaxation_scheme)
                try:
                    pw_params['input']['relaxation_scheme'] = relaxation_scheme
                except KeyError:
                    pw_params['input'] = {'relaxation_scheme': relaxation_scheme}

            for result_key, result_value in deformation_result_dict.iteritems():
                if result_key.startswith('deformed_structure_'):
                    number = result_key.split('_')[-1]
                    lagrangian_strain = deformation_result_dict['output_parameters_{}'.format(number)].get_dict(
                    )['lagrangian_strain']

                    deformed_structure = result_value
                    pw_params['structure'] = deformed_structure

                    # launch sub-workflow
                    wf_sub = PwWorkflow(params=pw_params)

                    self.attach_workflow(wf_sub)
                    wf_sub.start()
                    wf_sub.add_attribute('deformation_dict', {
                        'index': deformation_index,
                        'lagrangian_strain': lagrangian_strain,
                    })
                    self.append_to_report("{} Pw workflow launched  (pk: {}) "
                                          "on deformed structure with pk {}, Lagrangian strain {}".format(
                        pw_params['input']['relaxation_scheme'], wf_sub.pk, deformed_structure.pk, lagrangian_strain
                    ))


        if not elastic_params.get('ignore_undeformed', False):
            pw_params['structure'] = structure

            wf_sub = PwWorkflow(params=pw_params)
            self.attach_workflow(wf_sub)
            wf_sub.start()
            wf_sub.add_attribute('deformation_dict', {
                'index': 'undeformed',
                'lagrangian_strain': 0,
            })
            self.append_to_report("{} Pw workflow launched  (pk: {}) "
                                  "on undeformed structure {} with pk {}".format(
                pw_params['input']['relaxation_scheme'], wf_sub.pk,
                structure.get_formula(), structure.pk,
            ))

        self.next(self.analysis)

    @Workflow.step
    def analysis(self):
        """


        """
        params = self.get_parameters()
        elastic_params = params['input']
        method = elastic_params['method']

        # re-do the analysis on a previously run workflow
        if 'elastic_wf' in params.keys():
            wf_sub = load_workflow(params['elastic_wf'])

            wf_pw_list_deformed_structures = list(wf_sub.get_step(wf_sub.run_deformed_structures
                                          ).get_sub_workflows().order_by('ctime'))

            undeformed_structure = wf_sub.get_attribute('undeformed_structure')

        else:
            wf_pw_list_deformed_structures = list(self.get_step(self.run_deformed_structures
                                                ).get_sub_workflows().order_by('ctime'))

            undeformed_structure = self.get_attribute('undeformed_structure')

        self.append_to_report("Undeformed structure: pk {}, formula {}".format(
                                undeformed_structure.pk,undeformed_structure.get_formula()))

        # create a {deformation_index : { lagrangian_strain : outputparameters}} dictionary
        deformation_outputparameters_energy = {}
        deformation_outputparameters_stress = {}

        # to keep track of the strains..
        deformation_energy_index_strain = {}
        deformation_stress_index_strain = {}

        undeformed_output_parameters = None
        failed_calculations = 0

        # fill the deformation_outputparameters dictionaries
        for wf_sub in wf_pw_list_deformed_structures:

            deformation_attributes = wf_sub.get_attribute('deformation_dict')
            index = deformation_attributes['index']
            try:
                pw_calculation = wf_sub.get_result('pw_calculation')
            except (KeyError, ValueError):
                failed_calculations += 1
                continue

            if index == 'undeformed':
                if not elastic_params.get('ignore_undeformed', False):
                    undeformed_output_parameters = pw_calculation.out.output_parameters

                #self.append_to_report('Volume: {}'.format(undeformed_structure.get_cell_volume()))

            elif method == 'energy':
                if not deformation_outputparameters_energy.has_key(index):
                    deformation_outputparameters_energy[index] = {}
                    deformation_energy_index_strain[index] = {}

                deformation_outputparameters_energy[index]['lagrangian_strain_{}'.format(
                        len(deformation_energy_index_strain[index]))] = pw_calculation.out.output_parameters

                deformation_energy_index_strain[index][
                    len(deformation_energy_index_strain[index])] = deformation_attributes['lagrangian_strain']

            elif method == 'stress':
                if not deformation_outputparameters_stress.has_key(index):
                    deformation_outputparameters_stress[index] = {}
                    deformation_stress_index_strain[index] = {}

                deformation_outputparameters_stress[index]['lagrangian_strain_{}'.format(
                        len(deformation_stress_index_strain[index]))] = pw_calculation.out.output_parameters

                deformation_stress_index_strain[index][
                    len(deformation_stress_index_strain[index])] = deformation_attributes['lagrangian_strain']

        self.append_to_report('Reporting {} failed calculations.'.format(failed_calculations))

        space_group = spglib.get_symmetry_dataset(undeformed_structure.get_ase())['number']

        lagrangian_strain_vectors, _ = elastic2d_utils.get_strain_list(space_group, method)

        self.append_to_report('Evaluating {} method'.format(method))
        ordered_best_fit_output_parameters_dict = {}
        deformation_output_parameters = {}

        if method == 'energy':
            parameters_dict = {
                'fitting_orders': elastic_params.get('fitting_orders_energy', [2, 4, 6, 8]),
                'method': method,
            }

            deformation_output_parameters = deformation_outputparameters_energy
            deformation_index_strain = deformation_energy_index_strain

        elif method == 'stress':
            parameters_dict = {
                        'fitting_orders': elastic_params.get('fitting_orders_stress', [1, 3, 5]),
                        'method': method,
            }

            deformation_output_parameters = deformation_outputparameters_stress
            deformation_index_strain = deformation_stress_index_strain

        for deformation_index, deformation_output_parameters_dict in deformation_output_parameters.iteritems():

            if undeformed_output_parameters is not None:
                deformation_output_parameters_dict['lagrangian_strain_{}'.format(
                        len(deformation_index_strain[deformation_index]))] = undeformed_output_parameters

                deformation_index_strain[deformation_index][len(deformation_index_strain[deformation_index])] = 0.
            else:
                self.append_to_report('WARNING: Undeformed output parameters not found.')

            indices, lagrangian_strains = zip(*sorted(zip(deformation_index_strain[deformation_index].keys(),
                                                          deformation_index_strain[deformation_index].values())))

            parameters_dict['index_lagrangian_strains'] = lagrangian_strains
            parameters_dict['lagrangian_strain_vector'] = lagrangian_strain_vectors[deformation_index]

            fitting_parameters = ParameterData(dict=parameters_dict)

            _, best_fit_output = best_fit_inline(parameters=fitting_parameters,
                                                 **deformation_output_parameters_dict)

            ordered_best_fit_output_parameters_dict['bestfit_{}'.format(deformation_index)] = \
                best_fit_output['output_parameters']

        _, elastic_contants_output = elastic_constants_inline(structure=undeformed_structure,
                                                              **ordered_best_fit_output_parameters_dict)

        output_dict = elastic_contants_output['output_parameters'].get_dict()

        elastic_constant_matrix = output_dict['tension_coefficients']
        units = output_dict['tension_coefficients_units']

        self.append_to_report("Calculated following tension matrix "
                              "[{}]: \n[{}, \n{}, \n{}] ".format(
                                units, *elastic_constant_matrix))

        self.add_result('tension_coefficients',elastic_contants_output['output_parameters'])

        elastic_constants = elastic2d_utils.Elastic2dProperties(elastic_constant_matrix)

        if not output_dict['is_stable']:
            
            self.append_to_report('WARNING: Stability criterion {} not passed.'.format('positive definite'))

        group_name = elastic_params.get('group_name', None)

        if group_name is not None:
            # create or get the group
            group, created = Group.get_or_create(name="{}".format(group_name))
            if created:
                self.append_to_report("Created group '{}'".format(group_name))

            # put the elastic contants into the group
            group.add_nodes([elastic_contants_output['output_parameters']])
            self.append_to_report("Adding elastic constants with pk {} to "
                                  "group '{}'".format(elastic_contants_output['output_parameters'].pk,
                                                      group_name))
        else:
            self.append_to_report("Elastic constants with pk {}".format(elastic_contants_output['output_parameters'].pk))


        self.append_to_report("Elastic workflow completed")
        self.append_to_report('Error estimations on constants:')
        self.append_to_report('{}'.format(output_dict['tension_coefficients_standard_deviation']))

        self.next(self.exit)



