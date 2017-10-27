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
from aiida.workflows.user.epfl_theos.quantumespresso import elastic_utils
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

@make_inline
def deformation_inline(structure, parameters):
    """
    Take a structure, a deformation vector, a maximal Lagrangian strain and
    the number of deformed structures.
    :param structure: undeformed structure
    :param parameters: ParameterData with dictionary {
        'maximal_lagrangian_strain': maximal strain value
        'number_of_strains_per_deformation:
        'strain_vector': Voigt notation
        'normalize_deformation_matrix': default False,

    }

    :return: a dictionary of the form {}
    """
    params = parameters.get_dict()
    lagrangian_strain_max = params['maximal_lagrangian_strain']
    number_of_structures = params['number_of_strains_per_deformation']
    strain_vector = np.array(params['strain_vector'])
    normalize = params.get('normalize_deformation_matrix')
    original_cell = structure.cell

    result_dict = {}

    point_range = int(number_of_structures / 2)
    for index, point in enumerate(range(-point_range, point_range + 1)):
        if point == 0:
            continue

        lagrangian_strain_magnitude = lagrangian_strain_max * float(point) / point_range

        #relative_strain_vector = strain_vector * lagrangian_strain_magnitude

        # Lagrangian to eulerian strain transformation
        epsilon_matrix = elastic_utils.lagrangian_eulerian_strain_transformation(strain_vector,
                                                                                 normalize,
                                                                                 lagrangian_strain_magnitude)

        deformation_matrix = np.identity(3) + epsilon_matrix

        new_cell = np.dot(original_cell, deformation_matrix)

        # create new structure
        ase_structure = structure.get_ase()
        ase_structure.set_cell(new_cell, scale_atoms=True)

        new_structure = StructureData(ase=ase_structure)

        result_dict['deformed_structure_{}'.format(index)] = new_structure
        result_dict['output_parameters_{}'.format(index)] = ParameterData(dict={
            'lagrangian_strain': lagrangian_strain_magnitude,
        })

    return result_dict

@make_inline
def best_fit_inline(parameters, **kwargs):
    """

    :param parameters: ParameterData dictionary containing {
        'fitting_orders':
        'index_lagrangian_strains':
        'method':
        'lagrangian_strain_vector':
        'scoring_function'

    }

    :return: dictionary
    {
        'output_parameters': ParameterData with the dictionary
        {
            'polynomial_coefficients_mean',
            'polynomial_coefficients_variance',
        }
        'cross_validation_analysis_array': ArrayData with cross_validation_errors for different fits..
        {
            # valid for all
            'lagrangian_strains',
            'energies',
            'lagrangian_stresses',
            'maximal_lagrangian_strains'

            # per specific stress
            'plateau', # lagrangian_strain_max_indices, best order
            or 'sigma_1_plateau'


            # per specific order,

            'polynomial_coefficients_order_2' -> list indices corresponding to lagrangian_strain_max_list
            'cross_validation_errors_order_2'
            or
            'tau_1_polynomial_coefficients_order_4'
        }
    }
    """
    import numpy as np
    ArrayData = DataFactory('array')
    fitting_orders = parameters.get_dict()['fitting_orders']
    method = parameters.get_dict()['method']
    scoring_function =  parameters.get_dict()['scoring_function']
    index_lagrangian_strains = parameters.get_dict()['index_lagrangian_strains']
    lagrangian_strain_vector = np.array(parameters.get_dict()['lagrangian_strain_vector'])
    plateau_min_points = parameters.get_dict().get('plateau_min_points', 2)

    normalize = parameters.get_dict().get('normalize_deformation_matrix', True)

    if normalize:
        divider = elastic_utils.get_matrix_norm_from_lagrangian_vector(lagrangian_strain_vector)
    else:
        divider = 1.

    result_dict = {}

    cv_array_data = ArrayData()
    output_parameters_dict = {}

    lagrangian_strains = []
    energies = []
    stresses = []



    for index_string, output_parameters in kwargs.iteritems():
        lagrangian_strain = index_lagrangian_strains[int(index_string.split('_')[-1])]
        energies.append(output_parameters.get_dict()['energy'])

        lagrangian_strains.append(lagrangian_strain/divider)

        stress_matrix = np.array(output_parameters.get_dict().get('stress', None))

        # physical to lagrangian stress
        #relative_lagrangian_strain_vector = lagrangian_strain * lagrangian_strain_vector

        epsilon_matrix = elastic_utils.lagrangian_eulerian_strain_transformation(lagrangian_strain_vector,
                                                                                 normalize=normalize,
                                                                                 magnitude=lagrangian_strain)
        deformation_matrix = np.identity(3) + epsilon_matrix
        inverse_deformation_matrix = np.linalg.inv(deformation_matrix)

        if stress_matrix is not None:
            lagrangian_stress_matrix = np.linalg.det(deformation_matrix) * np.dot(inverse_deformation_matrix,
                                                                np.dot(stress_matrix,inverse_deformation_matrix))

            stresses.append(elastic_utils.symmetric_matrix_to_voigt_vector(lagrangian_stress_matrix))

    sorted_lagrangian_strains, sorted_energies = zip(*sorted(zip(lagrangian_strains, energies)))

    if len(stresses) > 0 :
        sorted_lagrangian_strains,  sorted_stresses = zip(*sorted(zip(lagrangian_strains,  stresses)))

        if not all([_ is None for _ in sorted_stresses]):
            cv_array_data.set_array('lagrangian_stresses', np.array(sorted_stresses))


    cv_array_data.set_array('lagrangian_strains', np.array(sorted_lagrangian_strains))
    cv_array_data.set_array('energies',np.array(sorted_energies))


    if method == 'energy':
        relevant_polynomial_coeff = 2
        mean_polynomial_coefficients, standard_deviation,  cv_error_analysis_dict = find_best_fit(
                                                                        sorted_lagrangian_strains, sorted_energies,
                                                                            relevant_polynomial_coeff,
                                                                            fitting_orders, scoring_function,
                                                                            plateau_min_points)

        output_parameters_dict = {
            'polynomial_coefficients_mean': mean_polynomial_coefficients,
            'polynomial_coefficients_std':standard_deviation ,
        }

        for key, value in cv_error_analysis_dict.iteritems():
            cv_array_data.set_array(key, value)

    elif method == 'stress':

        output_parameters_dict = {}
        relevant_polynomial_coeff = 1

        for stress_index in range(6):

            sorted_stresses_of_index = [stress[stress_index] for stress in sorted_stresses]

            mean_polynomial_coefficients, standard_deviation,  cv_error_analysis_dict = find_best_fit(
                x_values=sorted_lagrangian_strains, y_values=sorted_stresses_of_index,
                relevant_polynomial_coeff=relevant_polynomial_coeff,
                fitting_orders=fitting_orders , scoring_function=scoring_function,
                plateau_min_points=plateau_min_points)

            output_parameters_dict['tau_{}'.format(stress_index)] = {
                'polynomial_coefficients_mean': mean_polynomial_coefficients,
                'polynomial_coefficients_std': standard_deviation
            }

            maximal_lagrangian_strains = cv_error_analysis_dict.pop('maximal_lagrangian_strains')

            for key, value in cv_error_analysis_dict.iteritems():
                cv_array_data.set_array('tau_{}_{}'.format(stress_index,key), value)

        cv_array_data.set_array('maximal_lagrangian_strains', maximal_lagrangian_strains)

    result_dict['output_parameters'] = ParameterData(dict=output_parameters_dict)
    result_dict['cross_validation_analysis_array'] = cv_array_data


    return result_dict

def find_best_fit(x_values, y_values, relevant_polynomial_coeff,
                  fitting_orders, scoring_function='v10', plateau_min_points=2):
    """

    :param x_values: x values to be fitted
    :param y_values: y values to be fitted
    :param fitting_orders: fittings order to use
    :return mean_polynomial_coefficients: mean values of polynomial over cross validation error plateau
    :return variance: variance of the polynomial coefficients
    :return cross_validation_analysis_dict: {
        'x_max_list'
        'polynomial_coefficients_array_order_[ORDER]'
        'cross_validation_array_order_[ORDER]'
        'plateau'
        'best_order'
    }
    """

    cross_validation_analysis_dict = leave_one_out_cross_validation( x_values, y_values, fitting_orders)
    if scoring_function == 'original':
        best_order, plateau = find_best_plateau_original(cross_validation_analysis_dict, plateau_min_points)
    elif scoring_function == 'v2':
        best_order, plateau = find_best_plateau_v2(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v3':
        best_order, plateau = find_best_plateau_v3(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v4':
        best_order, plateau = find_best_plateau_v4(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v5':
        best_order, plateau = find_best_plateau_v5(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v6':
        best_order, plateau = find_best_plateau_v6(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v7':
        best_order, plateau = find_best_plateau_v7(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v8':
        best_order, plateau = find_best_plateau_v8(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v9':
        best_order, plateau = find_best_plateau_v9(cross_validation_analysis_dict,
                                                   relevant_polynomial_coeff, plateau_min_points)
    elif scoring_function == 'v10':
        best_order, plateau = find_best_plateau_v10(cross_validation_analysis_dict,
                                                    relevant_polynomial_coeff, plateau_min_points)

    mean_polynomial_coefficients = np.mean(np.array(cross_validation_analysis_dict[
        'polynomial_coefficients_order_{}'.format(best_order)][plateau[0]:plateau[1]]), 0).tolist()

    standard_deviation = np.std(np.array(cross_validation_analysis_dict[
        'polynomial_coefficients_order_{}'.format(best_order)][plateau[0]:plateau[1]]), 0).tolist()

    cross_validation_analysis_dict['best_plateau_indices'] = np.array(plateau)
    cross_validation_analysis_dict['best_order'] = np.array(best_order)


    return  mean_polynomial_coefficients, standard_deviation, cross_validation_analysis_dict

def leave_one_out_cross_validation(original_x_values, original_y_values, fitting_orders):
    """
    Calculate the Leave One Out cross validation error for all the polynoms of order
    in fitting_order_list and lagrangian_strain_max for len(x_values) larger then the polynomial order.
    :param fitting_orders:
    :param original_x_values:
    :param original_y_values:
    :return: {
        'cross_validation_errors_order_[ORDER]'
        'polynomial_coefficients_order_[ORDER]'
        'x_max_list'
    }
    """
    import numpy as np

    cross_validation_analysis_dict = {
                                }
    lagrangian_strain_max_set = set([])

    for order in fitting_orders:
        x_values = np.array(original_x_values)
        y_values = np.array(original_y_values)

        cv_error_list = []
        polynomial_coeffs_list = []
        while len(x_values) > order:
            sigma = 0

            lagrangian_strain_max_abs = max(abs(x_values))

            for index, x in enumerate(x_values):
                y = y_values[index]
                # set of values with missing point
                cross_validation_x_values = [value for value in x_values if not value == x]
                cross_validation_y_values = [value for y_index, value in enumerate(y_values) if not index == y_index]

                cross_validation_y = np.polyval(np.polyfit(cross_validation_x_values, cross_validation_y_values, order), x)
                sigma = sigma + (cross_validation_y - y) ** 2

            cross_validation_error = np.sqrt(sigma / len(x_values))

            cv_error_list.append(cross_validation_error)

            lagrangian_strain_max_set.add(lagrangian_strain_max_abs)

            polynomial_coefficients = np.polyfit(x_values, y_values, order).tolist()
            polynomial_coeffs_list.append(polynomial_coefficients)

            # take away the largest values from the list
            y_values = y_values[abs(abs(x_values) - lagrangian_strain_max_abs) > 1.e-7]
            x_values = x_values[abs(abs(x_values) - lagrangian_strain_max_abs) > 1.e-7]

            lagrangian_strain_max_list = list(lagrangian_strain_max_set)
            lagrangian_strain_max_list.sort(reverse=True)

        cross_validation_analysis_dict['cross_validation_errors_order_{}'.format(order)] = np.array(cv_error_list)
        cross_validation_analysis_dict['polynomial_coefficients_order_{}'.format(order)] = np.array(
            polynomial_coeffs_list)

    cross_validation_analysis_dict['maximal_lagrangian_strains'] = np.array(lagrangian_strain_max_list)

    return cross_validation_analysis_dict

def find_best_plateau_original(cross_validation_analysis_dict, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(np.std(cross_validation_error_list[i:j]) / (i - j) ** 2 \
                                    * np.mean(cross_validation_error_list[i:j]))

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v2(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of the polynomial coeffs / plateau_length^2 * max_cv_value
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    # np.std(np.array(cross_validation_analysis_dict[
    #                     'polynomial_coefficients_order_{}'.format(best_order)][plateau[0]:plateau[1]]), 0).tolist()
    #
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            polynomial_coefficients_list = cross_validation_analysis_dict[
                                            'polynomial_coefficients_order_{}'.format(order)]
            number_of_cv_errors = len(cross_validation_error_list)

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(np.std(polynomial_coefficients_list[i:j]) / (i - j) ** 2 \
                                    * np.max(cross_validation_error_list[i:j],0)[-(relevant_polynomial_coeff+1)])

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau


def find_best_plateau_v3(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of the polynomial coeffs / plateau_length^2 * mean_cv_value
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    # np.std(np.array(cross_validation_analysis_dict[
    #                     'polynomial_coefficients_order_{}'.format(best_order)][plateau[0]:plateau[1]]), 0).tolist()
    #
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            polynomial_coefficients_list = cross_validation_analysis_dict[
                                            'polynomial_coefficients_order_{}'.format(order)]
            number_of_cv_errors = len(cross_validation_error_list)

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(np.std(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)]
                                    / (i - j) ** 2 \
                                    * np.mean(cross_validation_error_list[i:j]))

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v4(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of the polynomial coeffs ** 2 / plateau_length^2 * max_cv_value
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    # np.std(np.array(cross_validation_analysis_dict[
    #                     'polynomial_coefficients_order_{}'.format(best_order)][plateau[0]:plateau[1]]), 0).tolist()
    #
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            polynomial_coefficients_list = cross_validation_analysis_dict[
                                            'polynomial_coefficients_order_{}'.format(order)]
            number_of_cv_errors = len(cross_validation_error_list)

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs( np.std(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)]** 2
                                    / (i - j) ** 2
                                    * np.max(cross_validation_error_list[i:j]))

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v5(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)
            polynomial_coefficients_list = cross_validation_analysis_dict[
                'polynomial_coefficients_order_{}'.format(order)]

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(np.std(cross_validation_error_list[i:j]) / (i - j) ** 2 \
                                    * np.mean(cross_validation_error_list[i:j])  \
                                    * np.std(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)])

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v6(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)
            polynomial_coefficients_list = cross_validation_analysis_dict[
                'polynomial_coefficients_order_{}'.format(order)]

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(1. / (i - j) ** 2
                        * np.mean(cross_validation_error_list[i:j])
                        * abs(np.max(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)]
                              -np.min(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)]))

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v7(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)
            polynomial_coefficients_list = cross_validation_analysis_dict[
                'polynomial_coefficients_order_{}'.format(order)]

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = np.mean(cross_validation_error_list[i:j]) \
                        * abs(np.max(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)]
                              -np.min(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)])

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v8(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)
            polynomial_coefficients_list = cross_validation_analysis_dict[
                'polynomial_coefficients_order_{}'.format(order)]

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = np.max(cross_validation_error_list[i:j])  \
                        * abs(np.max(polynomial_coefficients_list[i:j], 0)[-(relevant_polynomial_coeff+1)]
                              -np.min(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)])

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v9(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)
            polynomial_coefficients_list = cross_validation_analysis_dict[
                'polynomial_coefficients_order_{}'.format(order)]

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(np.mean(cross_validation_error_list[i:j]) \
                        * np.std(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)])

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

def find_best_plateau_v10(cross_validation_analysis_dict, relevant_polynomial_coeff, minimal_number_of_points=3):
    """
    Analyse the cross validation errors to find the best plateau and best order, scoring the plateaus using
    score = standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
    :param minimal_length_of_plateau:
    :param cross_validation_analysis_dict: {
        'cross_validation_errors_order_[ORDER]':
        }
    :return: best_fitting_order, best_plateau
    """
    score = None
    best_fitting_order = None
    best_plateau = None

    for key, value in cross_validation_analysis_dict.iteritems():
        if key.startswith('cross_validation_errors_order_'):
            order = int(key.split('_')[-1])

            cross_validation_error_list = value
            number_of_cv_errors = len(cross_validation_error_list)
            polynomial_coefficients_list = cross_validation_analysis_dict[
                'polynomial_coefficients_order_{}'.format(order)]

            for i in range(number_of_cv_errors):
                for j in range(i + minimal_number_of_points, number_of_cv_errors+1):
                    # standard deviation of plateau / plateau_length^2 * mean_value_of_plateau
                    new_score = abs(np.max(cross_validation_error_list[i:j]) \
                                    * np.std(polynomial_coefficients_list[i:j],0)[-(relevant_polynomial_coeff+1)])

                    if score is None or new_score < score:
                        score = new_score
                        best_plateau = [i, j]
                        best_fitting_order = order

    return best_fitting_order, best_plateau

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

    lagrangian_strain_params = kwargs.pop('lagrangian_strain_params')

    lagrangian_strain_vectors = lagrangian_strain_params.get_dict()['lagrangian_strain_vectors']

    forced_space_group = lagrangian_strain_params.get_dict()['force_space_group_for_analysis']

    if forced_space_group:
        space_group = forced_space_group

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
        height_of_2D_cell = np.dot(np.cross(cell[0], cell[1]), cell[2])

        default_energy_conversion *= height_of_2D_cell
        default_stress_conversion *= height_of_2D_cell

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

    elastic_constant_matrix = elastic_utils.get_elastic_constants(space_group, coefficients,
                                            method, custom_strain_list=lagrangian_strain_vectors)
    standard_deviation_vector = elastic_utils.get_standard_deviation_of_elastic_constants(space_group,
                                    standard_deviations, method, custom_strain_list=lagrangian_strain_vectors)

    elastic_constant_matrix = elastic_constant_matrix * default_conversion
    std_vector = standard_deviation_vector * abs(default_conversion)

    stability_test_dict = {}

    elastic_properties = elastic_utils.elastic_properties(elastic_constant_matrix)

    stability_test_dict['bulk_modulus_criterion'] = elastic_properties.test_bulk_modulus_criterion()
    stability_test_dict['shear_modulus_criterion'] = elastic_properties.test_shear_modulus_criterion()
    stability_test_dict['positive_definite_criterion'] = elastic_properties.test_positive_definite_criterion()

    is_stable =  all(stability_test_dict.values())

    return {'output_parameters': ParameterData(dict={
        'elastic_constants': elastic_constant_matrix.tolist(),
        'elastic_constants_standard_deviation': std_vector.tolist(),
        'elastic_constants_units': default_units,
        'stability_criteria': stability_test_dict,
        'is_stable': is_stable,
        'bulk_modulus_voigt': elastic_properties.voigt_bulk_modulus,
        'bulk_modulus_reuss': elastic_properties.reuss_bulk_modulus,
        'shear_modulus_voigt': elastic_properties.voigt_shear_modulus,
        'shear_modulus_reuss': elastic_properties.reuss_shear_modulus,
        'young_modulus_hill': elastic_properties.hill_young_modulus,
        'bulk_modulus_units': default_units,
        'shear_modulus_units': default_units,
        'young_modulus_units': default_units,
        'poisson_ratio_hill': elastic_properties.hill_poisson_ratio,
        'elastic_anisotropy': elastic_properties.elastic_anisotropy,
        })}

# Elastic workflow

class ElasticWorkflow(Workflow):
    """
    lagrangian_strain -> lagrangian strain
    eps/epsilon -> physical strain (eulerian strain)
    """
    _default_distance_kpoints_in_mesh = 0.2
    _default_deformed_structures_relaxation_scheme = 'scf'
    _default_refinement_symprec = 5e-3

    def __init__(self, **kwargs):
        super(ElasticWorkflow, self).__init__(**kwargs)

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

        if 'kpoints' not in pw_params.keys():
            kpoints_mesh_spacing = params.get('input', {}).get(
                'distance_kpoints_in_mesh',
                self._default_distance_kpoints_in_mesh)

            # construct the k-points mesh for the initial structure
            kpoints = KpointsData()
            kpoints.set_cell_from_structure(structure)
            kpoints.set_kpoints_mesh_from_density(kpoints_mesh_spacing,
                                                  force_parity=True)
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

        lagrangian_strains = elastic_params.get('custom_strain_vectors', None)

        if lagrangian_strains is None:
            lagrangian_strains, strain_numbers = elastic_utils.get_strain_list(space_group, method)

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

        # use utils.objects_are_equal compare inputs of pw_calculation upfdata.get_upf_family_names()
        #
        # for key in ['parameters','vdw_table','kpoints', 'pseudofamily']:
        #                     if key in pw_calculation.get_inputs_dict():
        #                         try:
        #                             pw_params[key] = pw_calculation.get_inputs_dict()[key].get_dict()
        #                         except AttributeError:
        #                             pw_params[key] = pw_calculation.get_inputs_dict()[key]

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

        lagrangian_strain_vectors = elastic_params.get('custom_strain_vectors', None)

        if lagrangian_strain_vectors is None:
            lagrangian_strain_vectors, _ = elastic_utils.get_strain_list(space_group, method)

        self.append_to_report('Evaluating {} method'.format(method))
        ordered_best_fit_output_parameters_dict = {}
        deformation_output_parameters = {}

        parameters_dict = {}

        if method == 'energy':
            parameters_dict = {
                'fitting_orders': elastic_params.get('fitting_orders_energy', [2, 4]),
                'method': method,
                'scoring_function': elastic_params.get('scoring_function', 'v10'),
                'plateau_min_points': elastic_params.get('plateau_min_points', 2),
            }

            deformation_output_parameters = deformation_outputparameters_energy
            deformation_index_strain = deformation_energy_index_strain

        elif method == 'stress':
            parameters_dict = {
                        'fitting_orders': elastic_params.get('fitting_orders_stress', [1, 3]),
                        'method': method,
                        'scoring_function': elastic_params.get('scoring_function', 'v10'),
                        'plateau_min_points': elastic_params.get('plateau_min_points', 2),
            }

            deformation_output_parameters = deformation_outputparameters_stress
            deformation_index_strain = deformation_stress_index_strain

        parameters_dict['normalize_deformation_matrix'] = elastic_params.get('normalize_deformation_matrix', True)

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


        lagrangian_strain_params = ParameterData(dict= {
            'lagrangian_strain_vectors': lagrangian_strain_vectors,
            'force_space_group_for_analysis' : elastic_params.get('force_space_group_for_analysis', None)
        })

        ordered_best_fit_output_parameters_dict['lagrangian_strain_params'] = lagrangian_strain_params

        _, elastic_contants_output = elastic_constants_inline(structure=undeformed_structure,
                                                              **ordered_best_fit_output_parameters_dict)

        output_dict = elastic_contants_output['output_parameters'].get_dict()

        elastic_constant_matrix = output_dict['elastic_constants']
        units = output_dict['elastic_constants_units']

        self.append_to_report("Calculated following stiffness matrix "
                              "[{}]: \n[{}, \n{}, \n{}, \n{}, \n{}, \n{}] ".format(
                                units, *elastic_constant_matrix))

        self.add_result('elastic_constants',elastic_contants_output['output_parameters'])

        elastic_constants = elastic_utils.elastic_properties(elastic_constant_matrix)

        if not output_dict['is_stable']:
            for key, value in output_dict['stability_criteria'].iteritems():
                if not value:
                    self.append_to_report('WARNING: Stability criterion {} not passed.'.format(key))

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

        self.append_to_report("Voigt bulk modulus: {:.2f} [{}]".format(elastic_constants.voigt_bulk_modulus, units))
        self.append_to_report("Reuss bulk modulus: {:.2f} [{}]".format(elastic_constants.reuss_bulk_modulus, units))
        self.append_to_report("Voigt shear modulus: {:.2f} [{}]".format(elastic_constants.voigt_shear_modulus, units))
        self.append_to_report("Reuss shear modulus: {:.2f} [{}]".format(elastic_constants.reuss_shear_modulus, units))
        self.append_to_report("Hill Young modulus: {:.2f} [{}]".format(elastic_constants.hill_young_modulus, units))
        self.append_to_report("Hill Poisson ratio: {:.2f}".format(elastic_constants.hill_poisson_ratio))
        self.append_to_report("Universal elastic anisotropy: {}".format(elastic_constants.elastic_anisotropy))

        self.append_to_report("Elastic workflow completed")
        self.append_to_report('Error estimations on constants:')
        self.append_to_report('{}'.format(output_dict['elastic_constants_standard_deviation']))

        self.next(self.exit)



