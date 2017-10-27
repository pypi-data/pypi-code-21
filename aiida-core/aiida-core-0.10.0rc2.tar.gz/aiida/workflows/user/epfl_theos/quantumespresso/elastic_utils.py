# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller."


class NotImplementedExc(Exception):
    pass


class SpaceGroupOutOfRangeExc(Exception):
    pass

class CustomVectorMatrixSingularExc(Exception):
    pass

# non null components of tensors for the different symmetries
triclinic_matrix = [
    [1.,1.,1.,1.,1.,1.],
    [1.,1.,1.,1.,1.,1.],
    [1.,1.,1.,1.,1.,1.],
    [1.,1.,1.,1.,1.,1.],
    [1.,1.,1.,1.,1.,1.],
    [1.,1.,1.,1.,1.,1.],
]

monoclinic_II_matrix = [
    [1.,1.,1.,0.,1.,0.],
    [1.,1.,1.,0.,1.,0.],
    [1.,1.,1.,0.,1.,0.],
    [0.,0.,0.,1.,0.,1.],
    [1.,1.,1.,0.,1.,0.],
    [0.,0.,0.,1.,0.,1.]
]

monoclinic_III_matrix = [
    [1.,1.,1.,0.,0.,1.],
    [1.,1.,1.,0.,0.,1.],
    [1.,1.,1.,0.,0.,1.],
    [0.,0.,0.,1.,1.,0.],
    [0.,0.,0.,1.,1.,0.],
    [1.,1.,1.,0.,0.,1.]
]

cubic_matrix = [
    [1.,1.,1.,0.,0.,0.],
    [1.,1.,1.,0.,0.,0.],
    [1.,1.,1.,0.,0.,0.],
    [0.,0.,0.,1.,0.,0.],
    [0.,0.,0.,0.,1.,0.],
    [0.,0.,0.,0.,0.,1.]
]

orthorhombic_matrix = cubic_matrix
hexagonal_matrix = cubic_matrix
tetragonal_I_matrix = cubic_matrix

tetragonal_II_matrix = [
    [1.,1.,1.,0.,0.,1.],
    [1.,1.,1.,0.,0.,1.],
    [1.,1.,1.,0.,0.,0.],
    [0.,0.,0.,1.,0.,0.],
    [0.,0.,0.,0.,1.,0.],
    [1.,1.,0.,0.,0.,1.]
]

rhombohedral_I_matrix = [
    [1.,1.,1.,1.,0.,0.],
    [1.,1.,1.,1.,0.,0.],
    [1.,1.,1.,0.,0.,0.],
    [1.,1.,0.,1.,0.,0.],
    [0.,0.,0.,0.,1.,1.],
    [0.,0.,0.,0.,1.,1.]
]

rhombohedral_II_matrix = [
    [1.,1.,1.,1.,1.,0.],
    [1.,1.,1.,1.,1.,0.],
    [1.,1.,1.,0.,0.,0.],
    [1.,1.,0.,1.,0.,1.],
    [1.,1.,0.,0.,1.,1.],
    [0.,0.,0.,1.,1.,1.]
]


# mapping matrix elements to independent elastic constants
cubic_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 1,
    '11': 0,
    '12': 1,
    '22': 0,
    '33': 2,
    '44': 2,
    '55': 2
}

triclinic_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '03': 3,
    '04': 4,
    '05': 5,
    '11': 6,
    '12': 7,
    '13': 8,
    '14': 9,
    '15': 10,
    '22': 11,
    '23': 12,
    '24': 13,
    '25': 14,
    '33': 15,
    '34': 16,
    '35': 17,
    '44': 18,
    '45': 19,
    '55': 20,
}


monoclinic_II_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '04': 3,
    '11': 4,
    '12': 5,
    '14': 6,
    '22': 7,
    '24': 8,
    '33': 9,
    '35': 10,
    '44': 11,
    '55': 12
}

monoclinic_III_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '05': 3,
    '11': 4,
    '12': 5,
    '15': 6,
    '22': 7,
    '25': 8,
    '33': 9,
    '34': 10,
    '44': 11,
    '55': 12
}

orthorhombic_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '11': 3,
    '12': 4,
    '22': 5,
    '33': 6,
    '44': 7,
    '55': 8
}

tetragonal_I_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '11': 0,
    '12': 2,
    '22': 3,
    '33': 4,
    '44': 4,
    '55': 5
}

tetragonal_II_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '05': 3,
    '11': 0,
    '12': 2,
    '15': -3,
    '22': 4,
    '33': 5,
    '44': 5,
    '55': 6
}

rhombohedral_I_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '03': 3,
    '11': 0,
    '12': 2,
    '13': -3,
    '22': 4,
    '33': 5,
    '44': 5,
    '45': 3,
    '55': [0,-1]
}

rhombohedral_II_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '03': 3,
    '04': 4,
    '11': 0,
    '12': 2,
    '13': -3,
    '14': -4,
    '22': 5,
    '33': 6,
    '35': -4,
    '44': 6,
    '45': 3,
    '55': [0,-1]
}

hexagonal_rules_dict = {
    '00': 0,
    '01': 1,
    '02': 2,
    '11': 0,
    '12': 2,
    '22': 3,
    '33': 4,
    '44': 4,
    '55': [0,-1]
}


# Lagrangian strain vectors, extended the list of
# Rostam Golesorkhtabar
# r.golesorkhtabar@gmail.com
# http://exciting-code.org/elastic
lagrangian_strain_float_dict = {
    '01': [1., 1., 1., 0., 0., 0.],
    '02': [1., 0., 0., 0., 0., 0.],
    '03': [0., 1., 0., 0., 0., 0.],
    '04': [0., 0., 1., 0., 0., 0.],
    '05': [0., 0., 0., 2., 0., 0.],
    '06': [0., 0., 0., 0., 2., 0.],
    '07': [0., 0., 0., 0., 0., 2.],
    '08': [1., 1., 0., 0., 0., 0.],
    '09': [1., 0., 1., 0., 0., 0.],
    '10': [1., 0., 0., 2., 0., 0.],
    '11': [1., 0., 0., 0., 2., 0.],
    '12': [1., 0., 0., 0., 0., 2.],
    '13': [0., 1., 1., 0., 0., 0.],
    '14': [0., 1., 0., 2., 0., 0.],
    '15': [0., 1., 0., 0., 2., 0.],
    '16': [0., 1., 0., 0., 0., 2.],
    '17': [0., 0., 1., 2., 0., 0.],
    '18': [0., 0., 1., 0., 2., 0.],
    '19': [0., 0., 1., 0., 0., 2.],
    '20': [0., 0., 0., 2., 2., 0.],
    '21': [0., 0., 0., 2., 0., 2.],
    '22': [0., 0., 0., 0., 2., 2.],
    '23': [0., 0., 0., 2., 2., 2.],
    '24': [-1., .5, .5, 0., 0., 0.],
    '25': [.5, -1., .5, 0., 0., 0.],
    '26': [.5, .5, -1., 0., 0., 0.],
    '27': [1., -1., 0., 0., 0., 0.],
    '28': [1., -1., 0., 0., 0., 2.],
    '29': [0., 1., -1., 0., 0., 2.],
    '30': [.5, .5, -1., 0., 0., 2.],
    '31': [1., 0., 0., 2., 2., 0.],
    '32': [1., 1., -1., 0., 0., 0.],
    '33': [1., 1., 1., -2., -2., -2.],
    '34': [.5, .5, -1., 2., 2., 2.],
    '35': [0., 0., 0., 2., 2., 4.],
    '36': [1., 2., 3., 4., 5., 6.],
    '37': [-2., 1., 4., -3., 6., -5.],
    '38': [3., -5., -1., 6., 2., -4.],
    '39': [-4., -6., 5., 1., -3., 2.],
    '40': [5., 4., 6., -2., -1., -3.],
    '41': [-6., 3., -2., 5., -4., 1.],
    '42': [-1., 0., 1., 0., 2., 0.],
    '43': [1., -1., 0., 0., 2., 0.],
    '44': [0., 0., 1., 2., 2., 0.],
}

# laue classifications written out
laue_classification_dict = {
    'CI': 'Cubic I',
    'CII': 'Cubic II',
    'HI': 'Hexagonal I',
    'HII': 'Hexagonal II',
    'RI': 'Rhombohedral I',
    'RII': 'Rhombohedral II',
    'TI': 'Tetragonal I',
    'TII': 'Tetragonal II',
    'O': 'Orthorhombic',
    'MIII': 'Monoclinic Diad||x3',
    'MII' 'Monoclinic Diad||x2'
    'N': 'Triclinic'}


def get_laue_classification(space_group_number):
    """
    Return laue classification from space group number
    :param space_group_number:
    :return: laue classification
    """

    if 1 <= space_group_number <= 2:  # Triclinic
        return 'N'
    elif 3 <= space_group_number <= 15:  # Monoclinic
        return 'MII'
    elif 16 <= space_group_number <= 74:  # Orthorhombic
        return 'O'
    elif 75 <= space_group_number <= 88:  # Tetragonal II
        return 'TII'
    elif 89 <= space_group_number <= 142:  # Tetragonal I
        return 'TI'
    elif 143 <= space_group_number <= 148:  # Rhombohedral II
        return 'RII'
    elif 149 <= space_group_number <= 167:  # Rhombohedral I
        return 'RI'
    elif 168 <= space_group_number <= 176:  # Hexagonal II
        return 'HII'
    elif 177 <= space_group_number <= 194:  # Hexagonal I
        return 'HI'
    elif 195 <= space_group_number <= 206:  # Cubic II
        return 'CII'
    elif 207 <= space_group_number <= 230:  # Cubic I
        return 'CI'
    else:
        raise SpaceGroupOutOfRangeExc


def get_number_of_elastic_constants(space_group_number):
    """
    Return number of independent elastic constants for a specific space group number
    :param space_group_number:
    :return: Number of independent elastic constants
    """
    if 1 <= space_group_number <= 2:  # Triclinic
        return 21
    elif 3 <= space_group_number <= 15:  # Monoclinic
        return 13
    elif 16 <= space_group_number <= 74:  # Orthorhombic
        return 9
    elif 75 <= space_group_number <= 88:  # Tetragonal II
        return 7
    elif 89 <= space_group_number <= 142:  # Tetragonal I
        return 6
    elif 143 <= space_group_number <= 148:  # Rhombohedral II
        return 7
    elif 149 <= space_group_number <= 167:  # Rhombohedral I
        return 6
    elif 168 <= space_group_number <= 176:  # Hexagonal II
        return 5
    elif 177 <= space_group_number <= 194:  # Hexagonal I
        return 5
    elif 195 <= space_group_number <= 206:  # Cubic II
        return 3
    elif 207 <= space_group_number <= 230:  # Cubic I
        return 3
    else:
        raise SpaceGroupOutOfRangeExc


def get_lagrangian_strain_list_from_laue(laue_classification,
                                         method):
    """
    Return the list of strain numbers corresponding to strain vectors used to
    calculated the elastic constants for a specific laue class, method and order.

    :param laue_classification: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :param method: 'energy' or 'stress'
    :return: List of strain numbers
    """
    if method == 'energy':
        return _get_strain_list_2nd_order_energy(laue_classification)
    elif method == 'stress':
        return _get_strain_list_2nd_order_stress(laue_classification)
    else:
        raise NotImplementedError

def _get_strain_list_2nd_order_stress_simple(laue_classification):
    if laue_classification in ['HI', 'HII', 'RI', 'RII']:
        return ['02', '04', '06']
    if laue_classification in ['TI', 'TII']:
        return ['02', '04', '06', '07']
    else:
        raise NotImplementedError

def _get_strain_list_2nd_order_stress_simple_v2(laue_classification):
    if laue_classification in ['HI', 'HII', 'RI', 'RII']:
        return ['02', '04', '20']
    if laue_classification in ['TI', 'TII']:
        return ['02', '04', '06', '07']
    else:
        raise NotImplementedError

def _get_strain_list_2nd_order_stress_efficient(laue_classification):
    if laue_classification in ['HI', 'HII', 'RI', 'RII']:
        return ['02', '18']
    if laue_classification in ['TI', 'TII']:
        return ['02', '18', '07', ]
    if laue_classification in ['O']:
        return ['08', '28', '44']
    else:
        raise NotImplementedError

def _get_strain_list_2nd_order_stress_ulics(laue_classification):
    """
    Predefined strain vector list to calculate 2nd order elastic constants using the stress approach
    :param laue_classification: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :return: strain_list
    """
    if laue_classification == 'CI' or laue_classification == 'CII':
        return ['36']
    if laue_classification == 'HI' or laue_classification == 'HII':
        return ['36', '37']
    if laue_classification == 'RI' or laue_classification == 'RII':
        return ['36', '37']
    if laue_classification == 'TI' or laue_classification == 'TII':
        return ['36', '37']
    if laue_classification == 'O':
        return ['36', '37', '38']
    if laue_classification == 'MII' or laue_classification == 'MIII':
        return ['36', '37', '38', '39', '40']
    if laue_classification == 'N':
        return ['36', '37', '38', '39', '40', '41']


def _get_strain_list_2nd_order_energy(laue_classification):
    """
    Predefined strain vector list to calculate 2nd order elastic constants using the energy approach
    :param laue_classification: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :return: strain list
    """
    if laue_classification == 'CI' or laue_classification == 'CII':
        return ['01', '08', '23']
    if laue_classification == 'HI' or laue_classification == 'HII':
        return ['01', '26', '04', '03', '17']
    if laue_classification == 'RI':
        return ['01', '08', '04', '02', '05', '10']
    if laue_classification == 'RII':
        return ['01', '08', '04', '02', '05', '10', '11']
    if laue_classification == 'TI':
        return ['01', '26', '27', '04', '05', '07']
    if laue_classification == 'TII':
        return ['01', '26', '27', '28', '04', '05', '07']
    if laue_classification == 'O':
        return ['01', '26', '25', '27', '03', '04', '05', '06', '07']
    if laue_classification == 'MII':
        return ['01', '25', '24', '28', '29', '27', '20', '12', '42', '43', '05', '21', '15']
    if laue_classification == 'MIII':
        return ['01', '25', '24', '28', '29', '27', '20', '12', '03', '04', '05', '06', '07']
    if laue_classification == 'N':
        return ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']


def _get_strain_list_2nd_order_stress(laue_classification):
    """
    Predefined strain vector list to calculate 2nd order elastic constants using the stress approach
    :param laue_classification: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :return: strain_list
    """
    if laue_classification == 'CI' or laue_classification == 'CII':
        return ['36']
    if laue_classification == 'HI' or laue_classification == 'HII':
        return ['36', '38']
    if laue_classification == 'RI' or laue_classification == 'RII':
        return ['36', '38']
    if laue_classification == 'TI' or laue_classification == 'TII':
        return ['36', '38']
    if laue_classification == 'O':
        return ['36', '38', '40']
    if laue_classification == 'MII' or laue_classification == 'MIII':
        return ['36', '37', '38', '39', '40']
    if laue_classification == 'N':
        return ['36', '37', '38', '39', '40', '41']

def _get_rules_dict_from_laue_class(laue_classification):
    """
    Return the mapping dictionary from independent constants vector to matrix elements
    :param laue_classification:
    :return: mapping rules dictionary
    """
    if laue_classification == 'CI' or laue_classification == 'CII':
        return cubic_rules_dict
    if laue_classification == 'HI' or laue_classification == 'HII':
        return hexagonal_rules_dict
    if laue_classification == 'RI':
        return rhombohedral_I_rules_dict
    if laue_classification == 'RII':
        return rhombohedral_II_rules_dict
    if laue_classification == 'TI':
        return tetragonal_I_rules_dict
    if laue_classification == 'TII':
        return tetragonal_II_rules_dict
    if laue_classification == 'O':
        return orthorhombic_rules_dict
    if laue_classification == 'MII':
        return monoclinic_II_rules_dict
    if laue_classification == 'MIII':
        return monoclinic_III_rules_dict
    if laue_classification == 'N':
        return triclinic_rules_dict

def _get_symmetry_matrix_from_laue_class(laue_classification):
    """
    Return matrix with non null elastic constant elements for specific laue class
    :param laue_classification:
    :return:
    """
    if laue_classification == 'CI' or laue_classification == 'CII':
        return cubic_matrix
    if laue_classification == 'HI' or laue_classification == 'HII':
        return hexagonal_matrix
    if laue_classification == 'RI':
        return rhombohedral_I_matrix
    if laue_classification == 'RII':
        return rhombohedral_II_matrix
    if laue_classification == 'TI':
        return tetragonal_I_matrix
    if laue_classification == 'TII':
        return tetragonal_II_matrix
    if laue_classification == 'O':
        return orthorhombic_matrix
    if laue_classification == 'MII':
        return monoclinic_II_matrix
    if laue_classification == 'MIII':
        return monoclinic_III_matrix
    if laue_classification == 'N':
        return triclinic_matrix

def _get_linear_equations_matrix(method, laue_class, strain_list):
    """
    Return linear equation matrix for specific method, laue classification and strain list
    :param method: 'energy' or 'stress'
    :param laue_class: abbreviation of laue classification
    :param strain_list: list of strain vectors
    :return: a matrix containing the coefficients of the linear equation that has to be solved in order to compute
        the independent elastic constants
    """
    import numpy as np
    def _get_linear_matrix_row_energy(strain_vector, laue_class):
        """
        Generate a matrix row for the energy method, corresponding to one deformation
        :param strain_vector:
        :param laue_class:
        :return:
        """
        import numpy as np
        strain_vector = np.array(strain_vector)
        rules_dict = _get_rules_dict_from_laue_class(laue_class)
        strain_matrix = np.outer(strain_vector, strain_vector)
        number_of_independent_constants = len(set([abs(value)
                                           for value
                                           in rules_dict.values()
                                           if type(value) == int]))

        row = np.zeros(number_of_independent_constants)

        for [x, y], element in np.ndenumerate(strain_matrix):
            rules_dict_key = '{}{}'.format(*sorted([x,y]))
            try:
                index_of_constant = rules_dict[rules_dict_key]
                if type(index_of_constant) == list:
                    for index in index_of_constant:
                        if index >= 0:
                          row[index] += element / len(index_of_constant)
                        else:
                            row[abs(index)] -= element / len(index_of_constant)
                else:
                    if index_of_constant >= 0:
                        row[index_of_constant] += element
                    else:
                        row[abs(index_of_constant)] -= element
            except KeyError:
                continue
        return row / 2

    def _get_linear_matrix_rows_stress(strain_vector, laue_class):
        """
        Generate six matrix rows for the stress method, corresponding to one deformation
        :param strain_vector:
        :param laue_class:
        :return:
        """
        import numpy as np
        rules_dict = _get_rules_dict_from_laue_class(laue_class)
        symmetry_matrix = _get_symmetry_matrix_from_laue_class(laue_class)

        strain_matrix = np.dot(np.array(symmetry_matrix), np.diag(strain_vector))
        number_of_independent_constants = len(set([abs(value)
                                           for value
                                           in rules_dict.values()
                                           if type(value) == int]))
        number_of_stress_directions = 6

        matrix = np.zeros((number_of_stress_directions, number_of_independent_constants))

        for [x, y], element in np.ndenumerate(strain_matrix):
            rules_dict_key = '{}{}'.format(*sorted([x,y]))
            try:
                index_of_constant = rules_dict[rules_dict_key]
                if type(index_of_constant) == list:
                    for index in index_of_constant:
                        if index >= 0:
                            matrix[x][index] += element / len(index_of_constant)
                        else:
                            matrix[x][abs(index)] -= element / len(index_of_constant)
                else:
                    if index_of_constant >= 0:
                        matrix[x][index_of_constant] += element
                    else:
                        matrix[x][abs(index_of_constant)] -= element
            except KeyError:
                continue
        return matrix

    final_matrix = None



    for strain_vector in strain_list:
        if method == 'energy':
            row = _get_linear_matrix_row_energy(strain_vector, laue_class)
            if final_matrix is None:
                final_matrix = row
            else:
                final_matrix = np.vstack((final_matrix, row))
        elif method == 'stress':
            rows = _get_linear_matrix_rows_stress(strain_vector, laue_class)
            if final_matrix is None:
                final_matrix = rows
            else:
                final_matrix = np.vstack((final_matrix, rows))

    return final_matrix


def get_standard_deviation_of_elastic_constants(space_group, standard_deviation_array, method, custom_strain_list=None):
    """
    Transform standard deviation of relevant polynomial coefficients to standard deviation of independent
    elastic constants.
    :param space_group: space_group of structure
    :param standard_deviation_array: Vector containing standard deviation of the relevant polynomial coefficients
    :param method: 'energy' or 'stress'
    :param custom_strain_list: (optional) only if a custom strain list instead of the predefined has been used
        to deform the structure
    :return: Vector with standard deviation on independent elastic constants.
    """
    import numpy as np
    laue_class = get_laue_classification(space_group)
    variance_vector = np.array(standard_deviation_array)**2
    if custom_strain_list is None:
        strain_list, _ = get_strain_list(space_group, method)
    else:
        strain_list = custom_strain_list

    matrix = np.matrix(_get_linear_equations_matrix(method, laue_class, strain_list))
    try:
        linear_transformation_matrix = np.linalg.inv(matrix.T * matrix) * matrix.T
    except np.linalg.LinAlgError:
        raise CustomVectorMatrixSingularExc('The (matrix.T * matrix) formed by the custom '
                                            'strain vectors is not invertible. Please define '
                                            'other strain vectors. ')

    absolute_linear_transformation_matrix = np.square(linear_transformation_matrix)
    variance_vector_after_absolute_linear_transformation = np.dot(absolute_linear_transformation_matrix, variance_vector)
    standard_deviation_absolute_linear_transformation = np.array(variance_vector_after_absolute_linear_transformation[0])**0.5

    #just for comparison
    # diagonal_variance_matrix = np.diag(variance_vector)
    # transformed_covariance_matrix = np.dot(np.dot(linear_transformation_matrix, diagonal_variance_matrix),linear_transformation_matrix.T)
    # transformed_variance_vector = np.diagonal(transformed_covariance_matrix)
    # print transformed_variance_vector**0.5, standard_deviation_absolute_linear_transformation[0] # same

    return  standard_deviation_absolute_linear_transformation[0]

def get_elastic_constants(space_group, polynomial_coeffs_array, method, custom_strain_list=None):
    """
    Return 6x6 elastic constants matrix calculated from the slopes of the strain-stress fits or the curvature
    of the strain-energy fits.
    :param space_group: space_group of structure
    :param polynomial_coeffs_array: relevant polynomial coefficients, slope of strain-stress fit for stress and
        curvature of strain-energy fit for energy method
    :param method: 'energy' or 'stress'
    :param custom_strain_list: (optional) only if a custom strain list instead of the predefined has been used
        to deform the structure
    :return: A symmetric 6x6 matrix containing elastic constants
    """
    import numpy as np
    laue_class = get_laue_classification(space_group)

    if custom_strain_list is None:
        strain_list, _ = get_strain_list(space_group, method)
    else:
        strain_list = custom_strain_list

    matrix = _get_linear_equations_matrix(method, laue_class, strain_list)

    polynomial_coefficients = np.array(polynomial_coeffs_array)
    ci = np.linalg.lstsq(matrix, polynomial_coefficients)

    elastic_constants_matrix = _get_matrix_from_independent_constants(ci[0], laue_class)
    return elastic_constants_matrix

def _get_matrix_from_independent_constants(constants_vector, laue_class, standard_deviation=False):
    """
    Return 6x6 elastic constants matrix from vector with independent elastic constants. The upper triangle
    of the elastic constants matrix is read line by line, and the first independent element, corresponds to
    the first element in the vector, the second element of the vector to the second independent in the matrix,
    ignoring all elements, which are 0.
    :param constants_vector:
    :param laue_class:
    :return: Return 6x6 elastic constants matrix
    """
    import numpy as np
    C = np.zeros((6, 6))
    if laue_class == 'CI' or laue_class == 'CII':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[3, 3] =constants_vector[2]
        C[1, 1] = C[0, 0]
        C[2, 2] = C[0, 0]
        C[0, 2] = C[0, 1]
        C[1, 2] = C[0, 1]
        C[4, 4] = C[3, 3]
        C[5, 5] = C[3, 3]
    elif laue_class == 'HI' or laue_class == 'HII':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[2, 2] =constants_vector[3]
        C[3, 3] =constants_vector[4]
        C[1, 1] = C[0, 0]
        C[1, 2] = C[0, 2]
        C[4, 4] = C[3, 3]
        if standard_deviation is False:
            C[5, 5] = 0.5 * (C[0, 0] - C[0, 1])
        else:
            C[5, 5] = 0.5 * (C[0, 0] + C[0, 1])
    elif laue_class == 'RI':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[0, 3] =constants_vector[3]
        C[2, 2] =constants_vector[4]
        C[3, 3] =constants_vector[5]
        C[1, 1] = C[0, 0]
        C[1, 2] = C[0, 2]
        C[1, 3] = -C[0, 3]
        C[4, 5] = C[0, 3]
        C[4, 4] = C[3, 3]
        if standard_deviation is False:
            C[5, 5] = 0.5 * (C[0, 0] - C[0, 1])
        else:
            C[5, 5] = 0.5 * (C[0, 0] + C[0, 1])
    elif laue_class == 'RII':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[0, 3] =constants_vector[3]
        C[0, 4] =constants_vector[4]
        C[2, 2] =constants_vector[5]
        C[3, 3] =constants_vector[6]
        C[1, 1] = C[0, 0]
        C[1, 2] = C[0, 2]
        C[1, 3] = -C[0, 3]
        C[4, 5] = C[0, 3]
        C[1, 4] = -C[0, 4]
        C[3, 5] = -C[0, 4]
        C[4, 4] = C[3, 3]
        if standard_deviation is False:
            C[5, 5] = 0.5 * (C[0, 0] - C[0, 1])
        else:
            C[5, 5] = 0.5 * (C[0, 0] + C[0, 1])
    elif laue_class == 'TI':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[2, 2] =constants_vector[3]
        C[3, 3] =constants_vector[4]
        C[5, 5] =constants_vector[5]
        C[1, 1] = C[0, 0]
        C[1, 2] = C[0, 2]
        C[4, 4] = C[3, 3]
    elif laue_class == 'TII':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[0, 5] =constants_vector[3]
        C[2, 2] =constants_vector[4]
        C[3, 3] =constants_vector[5]
        C[5, 5] =constants_vector[6]
        C[1, 1] = C[0, 0]
        C[1, 2] = C[0, 2]
        C[1, 5] = -C[0, 5]
        C[4, 4] = C[3, 3]
    elif laue_class == 'O':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[1, 1] =constants_vector[3]
        C[1, 2] =constants_vector[4]
        C[2, 2] =constants_vector[5]
        C[3, 3] =constants_vector[6]
        C[4, 4] =constants_vector[7]
        C[5, 5] =constants_vector[8]
    elif laue_class == 'MII':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[0, 4] =constants_vector[3]
        C[1, 1] =constants_vector[4]
        C[1, 2] =constants_vector[5]
        C[1, 4] =constants_vector[6]
        C[2, 2] =constants_vector[7]
        C[2, 4] =constants_vector[8]
        C[3, 3] =constants_vector[9]
        C[3, 5] =constants_vector[10]
        C[4, 4] =constants_vector[11]
        C[5, 5] =constants_vector[12]
    elif laue_class == 'MIII':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[0, 5] =constants_vector[3]
        C[1, 1] =constants_vector[4]
        C[1, 2] =constants_vector[5]
        C[1, 5] =constants_vector[6]
        C[2, 2] =constants_vector[7]
        C[2, 5] =constants_vector[8]
        C[3, 3] =constants_vector[9]
        C[3, 4] =constants_vector[10]
        C[4, 4] =constants_vector[11]
        C[5, 5] =constants_vector[12]
    elif laue_class == 'N':
        C[0, 0] =constants_vector[0]
        C[0, 1] =constants_vector[1]
        C[0, 2] =constants_vector[2]
        C[0, 3] =constants_vector[3]
        C[0, 4] =constants_vector[4]
        C[0, 5] =constants_vector[5]
        C[1, 1] =constants_vector[6]
        C[1, 2] =constants_vector[7]
        C[1, 3] =constants_vector[8]
        C[1, 4] =constants_vector[9]
        C[1, 5] =constants_vector[10]
        C[2, 2] =constants_vector[11]
        C[2, 3] =constants_vector[12]
        C[2, 4] =constants_vector[13]
        C[2, 5] =constants_vector[14]
        C[3, 3] =constants_vector[15]
        C[3, 4] =constants_vector[16]
        C[3, 5] =constants_vector[17]
        C[4, 4] =constants_vector[18]
        C[4, 5] =constants_vector[19]
        C[5, 5] =constants_vector[20]
    else:
        ValueError('Laue class not recognized: {}\n Please use abbreviations like "CI" and "O"'.format(laue_class))
     # make the symmetric part of the matrix
    for i in range(5):
        for j in range(i + 1, 6):
            C[j, i] = C[i, j]
    return C


def get_voigt_bulk_modulus(elastic_constant_matrix):
    """
    Return Voigt bulk modulus
    :param elastic_constant_matrix:
    :return: voigt bulk modulus
    """
    matrix = elastic_constant_matrix
    return (matrix[0, 0] + matrix[1, 1] + matrix[2, 2] + 2 * (matrix[0, 1] + matrix[0, 2] + matrix[1, 2])) / 9


def get_voigt_shear_modulus(elastic_constant_matrix):
    """
    Return Voigt shear modulus
    :param elastic_constant_matrix:
    :return:
    """
    C = elastic_constant_matrix
    return ((C[0, 0] + C[1, 1] + C[2, 2]) - (C[0, 1] + C[0, 2] + C[1, 2]) + 3 * (C[3, 3] + C[4, 4] + C[5, 5])) / 15


def get_voigt_young_modulus(elastic_constant_matrix):
    """
    Return Voigt Young modulus
    :param elastic_constant_matrix:
    :return:
    """
    voigt_bulk_modulus = get_voigt_bulk_modulus(elastic_constant_matrix)
    voigt_shear_modulus = get_voigt_shear_modulus(elastic_constant_matrix)
    return (9 * voigt_bulk_modulus * voigt_shear_modulus) / (3 * voigt_bulk_modulus + voigt_shear_modulus)


def get_voigt_poisson_ratio(elastic_constant_matrix):
    """
    Return Voigt Poisson ratio
    :param elastic_constant_matrix:
    :return:
    """
    voigt_bulk_modulus = get_voigt_bulk_modulus(elastic_constant_matrix)
    voigt_shear_modulus = get_voigt_shear_modulus(elastic_constant_matrix)
    return (1.5 * voigt_bulk_modulus - voigt_shear_modulus) / (3 * voigt_bulk_modulus + voigt_shear_modulus)


def get_reuss_bulk_modulus(elastic_constant_matrix):
    """
    Return Reuss bulk modulus
    :param elastic_constant_matrix:
    :return:
    """
    S = get_compliance_matrix(elastic_constant_matrix)
    return 1 / (S[0, 0] + S[1, 1] + S[2, 2] + 2 * (S[0, 1] + S[0, 2] + S[1, 2]))


def get_reuss_shear_modulus(elastic_constant_matrix):
    """
    Return Reuss shear modulus
    :param elastic_constant_matrix:
    :return:
    """
    S = get_compliance_matrix(elastic_constant_matrix)
    return 15 / (
        4 * (S[0, 0] + S[1, 1] + S[2, 2]) - 4 * (S[0, 1] + S[0, 2] + S[1, 2]) + 3 * (S[3, 3] + S[4, 4] + S[5, 5]))


def get_reuss_young_modulus(elastic_constant_matrix):
    """
    Return Reuss Young modulus
    :param elastic_constant_matrix:
    :return:
    """
    reuss_bulk_modulus = get_reuss_bulk_modulus(elastic_constant_matrix)
    reuss_shear_modulus = get_reuss_shear_modulus(elastic_constant_matrix)
    return (9 * reuss_bulk_modulus * reuss_shear_modulus) / (3 * reuss_bulk_modulus + reuss_shear_modulus)


def get_reuss_poisson_ratio(elastic_constant_matrix):
    """
    Return Reuss Poisson ratio
    :param elastic_constant_matrix:
    :return:
    """
    reuss_bulk_modulus = get_reuss_bulk_modulus(elastic_constant_matrix)
    reuss_shear_modulus = get_reuss_shear_modulus(elastic_constant_matrix)
    return (1.5 * reuss_bulk_modulus - reuss_shear_modulus) / (3 * reuss_bulk_modulus + reuss_shear_modulus)


def get_hill_bulk_modulus(elastic_constant_matrix):
    """
    Return Hill bulk modulus
    :param elastic_constant_matrix:
    :return: hill bulk modulus
    """
    voigt_bulk_modulus = get_voigt_bulk_modulus(elastic_constant_matrix)
    reuss_bulk_modulus = get_reuss_bulk_modulus(elastic_constant_matrix)

    return 0.5 * (voigt_bulk_modulus + reuss_bulk_modulus)


def get_hill_shear_modulus(elastic_constant_matrix):
    """
    Return Hill shear modulus
    :param elastic_constant_matrix:
    :return:hill shear modulus
    """
    reuss_shear_modulus = get_reuss_shear_modulus(elastic_constant_matrix)
    voigt_shear_modulus = get_voigt_shear_modulus(elastic_constant_matrix)

    return 0.5 * (voigt_shear_modulus + reuss_shear_modulus)


def get_hill_young_modulus(elastic_constant_matrix):
    """
    Return Hill Young modulus
    :param elastic_constant_matrix:
    :return: hill young modulus
    """
    hill_bulk_modulus = get_hill_bulk_modulus(elastic_constant_matrix)
    hill_shear_modulus = get_hill_shear_modulus(elastic_constant_matrix)
    return (9. * hill_bulk_modulus * hill_shear_modulus) / (3. * hill_bulk_modulus + hill_shear_modulus)


def get_hill_poisson_ratio(elastic_constant_matrix):
    """
    Hill Poisson ratio
    :param elastic_constant_matrix:
    :return: hill poisson ratio
    """
    hill_bulk_modulus = get_hill_bulk_modulus(elastic_constant_matrix)
    hill_shear_modulus = get_hill_shear_modulus(elastic_constant_matrix)
    return (1.5 * hill_bulk_modulus - hill_shear_modulus) / (3. * hill_bulk_modulus + hill_shear_modulus)


def get_elastic_anisotropy(elastic_constant_matrix):
    """
    Universal elastic anisotropy index, isotropy = 0
    Source: Ranganathan SI, Ostoja-Starzewski M. Phys Rev Lett 2008:101.
    :param elastic_constant_matrix:
    :return: elastic anisotropy (dimensionless)
    """
    reuss_shear_modulus = get_reuss_shear_modulus(elastic_constant_matrix)
    voigt_shear_modulus = get_voigt_shear_modulus(elastic_constant_matrix)
    reuss_bulk_modulus = get_reuss_bulk_modulus(elastic_constant_matrix)
    voigt_bulk_modulus = get_voigt_bulk_modulus(elastic_constant_matrix)
    universal_elastic_anisotropy = 5. *voigt_shear_modulus / reuss_shear_modulus + voigt_bulk_modulus / \
                                   reuss_bulk_modulus  - 6
    return universal_elastic_anisotropy


def get_compliance_matrix(elastic_constant_matrix):
    """
    Get the inverse of the stiffness matrix (elastic constant matrix)
    :param elastic_constant_matrix:
    :return: compliance_matrix
    """
    import numpy as np
    return np.linalg.inv(elastic_constant_matrix)


def symmetric_matrix_to_voigt_vector(matrix):
    """
    Return 6x1 vector from symmetric 3x3 matrix.
    Matrix has to be symmetric.
    :param matrix:
    :return:
    """
    import numpy as np
    vector = np.array([matrix[0, 0],matrix[1,1],matrix[2, 2],matrix[1,2],matrix[0,2],matrix[0, 1]])

    return vector

def vector_to_matrix(vector):
    """
    Take a vector in voigt notation return the corresponding
    symmetric matrix
    :param vector:
    :return:
    """
    import numpy as np
    matrix = np.zeros((3, 3))

    matrix[0, 0] = vector[0]
    matrix[0, 1] = vector[5]
    matrix[0, 2] = vector[4]

    matrix[1, 0] = vector[5]
    matrix[1, 1] = vector[1]
    matrix[1, 2] = vector[3]

    matrix[2, 0] = vector[4]
    matrix[2, 1] = vector[3]
    matrix[2, 2] = vector[2]

    return matrix

def voigt_to_tensor_strain(voigt_strain_vector):
    """
    Convert a Voigt strain vector in tensor strain.
    :param voigt_strain_vector:
    :return:
    """
    tensor_strain_vector = voigt_strain_vector
    tensor_strain_vector[3] = voigt_strain_vector[3] / 2.
    tensor_strain_vector[4] = voigt_strain_vector[4] / 2.
    tensor_strain_vector[5] = voigt_strain_vector[5] / 2.
    return tensor_strain_vector


def lagrangian_eulerian_strain_transformation(lagrangian_strain_vector, normalize=False, magnitude=1.):
    """
    Lagrangian strain to physical strain (eta = eps + 0.5*eps*esp)
    :param lagrangian_strain_vector: lagrangian strain vector in voigt notation
    :return: Eulerian strain matrix
    """
    import numpy as np
    lagrangian_strain_vector = np.array(lagrangian_strain_vector)

    scaled_lagrangian_strain_vector = lagrangian_strain_vector * magnitude

    if normalize:
        matrix_norm = get_matrix_norm_from_lagrangian_vector(lagrangian_strain_vector)
        scaled_lagrangian_strain_vector = scaled_lagrangian_strain_vector / matrix_norm

    lagrangian_tensor_strain_vector = voigt_to_tensor_strain(scaled_lagrangian_strain_vector)

    lagrange_green_strain_tensor = vector_to_matrix(lagrangian_tensor_strain_vector)
    right_cauchy_green_def = 2 * lagrange_green_strain_tensor + np.eye(3)

    eigval, eigvec = np.linalg.eig(right_cauchy_green_def)
    strain_gradient_F = np.dot(np.dot(eigvec, np.diag(np.sqrt(eigval))), eigvec.T)

    almansi_green_strain_tensor = strain_gradient_F - np.eye(3)

    return almansi_green_strain_tensor


def get_matrix_norm_from_lagrangian_vector(lagrangian_strain_vector):
    """
    Return the Frobenius norm of the strain tensor corresponding
    to the lagrangian strain vector.
    :param lagrangian_strain_vector:
    :return:
    """
    import numpy as np
    lagrangian_tensor_strain_vector = voigt_to_tensor_strain(lagrangian_strain_vector)

    lagrangian_strain_tensor = vector_to_matrix(lagrangian_tensor_strain_vector)

    return np.linalg.norm(lagrangian_strain_tensor)


def get_strain_list(space_group_number,
                    method):
    """
    Get predefined strain list for space group and method.
    :param space_group_number:
    :param method:
    :return: dictionary of strain_number as keys and vectors as values
    """
    laue_classification = get_laue_classification(space_group_number)

    lagrangian_strain_list = []
    strain_numbers = []

    for strain_number in get_lagrangian_strain_list_from_laue(laue_classification, method):
        lagrangian_strain_list.append(lagrangian_strain_float_dict[strain_number])
        strain_numbers.append(strain_number)

    return lagrangian_strain_list, strain_numbers


def get_lagrangian_stress_matrix(stress_matrix, deformation_matrix):
    """
    Convert physical stress,e.g. measured by QuantumEspresso, to Lagrangian stress
    :param stress_matrix:
    :param deformation_matrix:
    :return:
    """
    import numpy as np
    inverse_deformation_matrix = np.linalg.inv(deformation_matrix)
    tau = np.linalg.det(deformation_matrix) * np.dot(
            inverse_deformation_matrix, np.dot(stress_matrix, inverse_deformation_matrix))
    return tau


class elastic_properties():

    def __init__(self, elastic_constant_matrix):
        import numpy as np

        self.elastic_constants = np.array(elastic_constant_matrix)

        self.shear_stability_limit = 2 #GPa
        self.bulk_stability_limit = 2 #GPa


        if self.elastic_constants.shape != (6,6):
            raise ValueError

    @property
    def elastic_constant_matrix(self):
        return self.elastic_constants

    @property
    def compliance_matrix(self):
        return get_compliance_matrix(self.elastic_constants)

    @property
    def voigt_bulk_modulus(self):
        return get_voigt_bulk_modulus(self.elastic_constants)

    @property
    def voigt_shear_modulus(self):
        return get_voigt_shear_modulus(self.elastic_constants)

    @property
    def voigt_young_modulus(self):
        return get_voigt_young_modulus(self.elastic_constants)

    @property
    def voigt_poisson_ratio(self):
        return get_voigt_poisson_ratio(self.elastic_constants)

    @property
    def reuss_bulk_modulus(self):
        return get_reuss_bulk_modulus(self.elastic_constants)

    @property
    def reuss_shear_modulus(self):
        return get_reuss_shear_modulus(self.elastic_constants)

    @property
    def reuss_young_modulus(self):
        return get_reuss_young_modulus(self.elastic_constants)

    @property
    def reuss_poisson_ratio(self):
        return get_reuss_poisson_ratio(self.elastic_constants)

    @property
    def hill_bulk_modulus(self):
        return get_hill_bulk_modulus(self.elastic_constants)

    @property
    def hill_shear_modulus(self):
        return get_hill_shear_modulus(self.elastic_constants)

    @property
    def hill_young_modulus(self):
        return get_hill_young_modulus(self.elastic_constants)

    @property
    def hill_poisson_ratio(self):
        return get_hill_poisson_ratio(self.elastic_constants)

    @property
    def elastic_anisotropy(self):
        return get_elastic_anisotropy(self.elastic_constants)

    @property
    def eigenvalues(self):
        import numpy as np
        eigenvalues, _ = np.linalg.eig(self.elastic_constants)
        return eigenvalues

    def test_positive_definite_criterion(self):
        """
        Return true if all eigenvalues are positive and False otherwise.
        :return:
        """
        import numpy as np
        if np.all(self.elastic_constants-self.elastic_constants.T==0) and np.all(self.eigenvalues > 0):
            return True
        else:
            return False

    def test_bulk_modulus_criterion(self):
        """
        Return True if Reuss bulk modulus is above stability limit and False otherwise.
        :return:
        """
        if self.reuss_bulk_modulus < self.bulk_stability_limit:
            return False
        else:
            return True

    def test_shear_modulus_criterion(self):
        """
        Return True  if Reuss shear modulus is above stability limit and False otherwise.
        :return:
        """
        if self.reuss_shear_modulus < self.shear_stability_limit:
            return False
        else:
            return True


# Rotation of elastic matrix:

def rotate_elastic_matrix(elastic_constants, rotation_matrix):
    """
    Rotate a 6x6 elastic constants matrix with respect to a rotation matrix.
    Because the 3x3x3x3 elastic tensor has been reduced to a 6x6 matrix.
    :param elastic_constants:
    :param rotation_matrix:
    :return: Rotated elastic constants matrix
    """
    import numpy as np

    transformation_matrix = np.zeros((6,6))
    rotation_matrix = np.array(rotation_matrix)

    upper_left_quarter = rotation_matrix * rotation_matrix # element-wise multiplication

    upper_right_quarter = np.zeros((3,3))
    upper_right_quarter[:,0] =  rotation_matrix[:,1] * rotation_matrix[:,2]* 2
    upper_right_quarter[:,1] =  rotation_matrix[:,0] * rotation_matrix[:,2]* 2
    upper_right_quarter[:,2] =  rotation_matrix[:,1] * rotation_matrix[:,0]* 2

    lower_left_quarter = np.zeros((3,3))
    lower_left_quarter[0,:] = rotation_matrix[1,:] * rotation_matrix[2,:]
    lower_left_quarter[1,:] = rotation_matrix[0,:] * rotation_matrix[2,:]
    lower_left_quarter[2,:] = rotation_matrix[1,:] * rotation_matrix[0,:]

    lower_right_quarter = np.zeros((3,3))

    lower_right_quarter[0,:] = rotation_matrix[1,[1,0,1]]* rotation_matrix[2,[2,2,0]] + rotation_matrix[1,[2,2,0]]* rotation_matrix[2,[1,0,1]]
    lower_right_quarter[1,:] = rotation_matrix[0, [1,2,0]]* rotation_matrix[2,[2,0,1]] + rotation_matrix[0,[2,0,1]]* rotation_matrix[2,[1,2,0]]
    lower_right_quarter[2,:] = rotation_matrix[0,[1,2,0]]* rotation_matrix[1, [2,0,1]] + rotation_matrix[0, [2,0,1]]* rotation_matrix[1,[1,2,0]]

    transformation_matrix[:3, :3] = upper_left_quarter
    transformation_matrix[:3, 3:] = upper_right_quarter
    transformation_matrix[3:, :3] = lower_left_quarter
    transformation_matrix[3:, 3:] = lower_right_quarter

    new_elastic_constants = np.dot(np.dot(transformation_matrix, elastic_constants), transformation_matrix.T)


    return new_elastic_constants.tolist()


def get_tensor(elastic_constants):
    import numpy as np
    C6o = elastic_constants
    C9o = np.zeros((3,3,3,3))
    #%!%!%--- Making the C9o Matrix ---%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!
    C9o[0,0,0,0] = C6o[0,0]; C9o[0,0,0,1] = C6o[0,5]; C9o[0,0,0,2] = C6o[0,4]
    C9o[0,0,1,0] = C6o[0,5]; C9o[0,0,1,1] = C6o[0,1]; C9o[0,0,1,2] = C6o[0,3]
    C9o[0,0,2,0] = C6o[0,4]; C9o[0,0,2,1] = C6o[0,3]; C9o[0,0,2,2] = C6o[0,2]

    C9o[0,1,0,0] = C6o[0,5]; C9o[0,1,0,1] = C6o[5,5]; C9o[0,1,0,2] = C6o[4,5]
    C9o[0,1,1,0] = C6o[5,5]; C9o[0,1,1,1] = C6o[1,5]; C9o[0,1,1,2] = C6o[3,5]
    C9o[0,1,2,0] = C6o[4,5]; C9o[0,1,2,1] = C6o[3,5]; C9o[0,1,2,2] = C6o[2,5]

    C9o[0,2,0,0] = C6o[0,4]; C9o[0,2,0,1] = C6o[4,5]; C9o[0,2,0,2] = C6o[4,4]
    C9o[0,2,1,0] = C6o[4,5]; C9o[0,2,1,1] = C6o[1,4]; C9o[0,2,1,2] = C6o[3,4]
    C9o[0,2,2,0] = C6o[4,4]; C9o[0,2,2,1] = C6o[3,4]; C9o[0,2,2,2] = C6o[2,4]
    #************************************************************************
    C9o[1,0,0,0] = C6o[0,5]; C9o[1,0,0,1] = C6o[5,5]; C9o[1,0,0,2] = C6o[4,5]
    C9o[1,0,1,0] = C6o[5,5]; C9o[1,0,1,1] = C6o[1,5]; C9o[1,0,1,2] = C6o[3,5]
    C9o[1,0,2,0] = C6o[4,5]; C9o[1,0,2,1] = C6o[3,5]; C9o[1,0,2,2] = C6o[2,5]

    C9o[1,1,0,0] = C6o[0,1]; C9o[1,1,0,1] = C6o[1,5]; C9o[1,1,0,2] = C6o[1,4]
    C9o[1,1,1,0] = C6o[1,5]; C9o[1,1,1,1] = C6o[1,1]; C9o[1,1,1,2] = C6o[1,3]
    C9o[1,1,2,0] = C6o[1,4]; C9o[1,1,2,1] = C6o[1,3]; C9o[1,1,2,2] = C6o[1,2]

    C9o[1,2,0,0] = C6o[0,3]; C9o[1,2,0,1] = C6o[3,5]; C9o[1,2,0,2] = C6o[3,4]
    C9o[1,2,1,0] = C6o[3,5]; C9o[1,2,1,1] = C6o[1,3]; C9o[1,2,1,2] = C6o[3,3]
    C9o[1,2,2,0] = C6o[3,4]; C9o[1,2,2,1] = C6o[3,3]; C9o[1,2,2,2] = C6o[2,3]
    #************************************************************************
    C9o[2,0,0,0] = C6o[0,4]; C9o[2,0,0,1] = C6o[4,5]; C9o[2,0,0,2] = C6o[4,4]
    C9o[2,0,1,0] = C6o[4,5]; C9o[2,0,1,1] = C6o[1,4]; C9o[2,0,1,2] = C6o[3,4]
    C9o[2,0,2,0] = C6o[4,4]; C9o[2,0,2,1] = C6o[3,4]; C9o[2,0,2,2] = C6o[2,4]

    C9o[2,1,0,0] = C6o[0,3]; C9o[2,1,0,1] = C6o[3,5]; C9o[2,1,0,2] = C6o[3,4]
    C9o[2,1,1,0] = C6o[3,5]; C9o[2,1,1,1] = C6o[1,3]; C9o[2,1,1,2] = C6o[3,3]
    C9o[2,1,2,0] = C6o[3,4]; C9o[2,1,2,1] = C6o[3,3]; C9o[2,1,2,2] = C6o[2,3]

    C9o[2,2,0,0] = C6o[0,2]; C9o[2,2,0,1] = C6o[2,5]; C9o[2,2,0,2] = C6o[2,4]
    C9o[2,2,1,0] = C6o[2,5]; C9o[2,2,1,1] = C6o[1,2]; C9o[2,2,1,2] = C6o[2,3]
    C9o[2,2,2,0] = C6o[2,4]; C9o[2,2,2,1] = C6o[2,3]; C9o[2,2,2,2] = C6o[2,2]

    return C9o

def rotate_elastic_matrix_exciting(elastic_constants, TM):
    import numpy as np
    import sys
    def C9nmop(m,n,o,p):
        S=0.
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        S = S + TM[m,i]*TM[n,j]*TM[o,k]*TM[p,l]*C9o[i,j,k,l]
        C9n[m,n,o,p] = S
        return C9n[m,n,o,p]


    def myabs(x):
        y=np.sqrt(x**2)
        return y

    C9o = get_tensor(elastic_constants)

    C6n = np.zeros((6,6))
    C9n = np.zeros((3,3,3,3))
    C9nmop(0,0,0,0) ;  C6n[0,0] = C9n[0,0,0,0]
    C9nmop(0,0,1,1) ;  C6n[0,1] = C9n[0,0,1,1] ; C6n[1,0] = C6n[0,1]
    C9nmop(0,0,2,2) ;  C6n[0,2] = C9n[0,0,2,2] ; C6n[2,0] = C6n[0,2]
    C9nmop(0,0,1,2) ;  C6n[0,3] = C9n[0,0,1,2] ; C6n[3,0] = C6n[0,3]
    C9nmop(0,0,0,2) ;  C6n[0,4] = C9n[0,0,0,2] ; C6n[4,0] = C6n[0,4]
    C9nmop(0,0,0,1) ;  C6n[0,5] = C9n[0,0,0,1] ; C6n[5,0] = C6n[0,5]

    C9nmop(1,1,1,1) ;  C6n[1,1] = C9n[1,1,1,1]
    C9nmop(1,1,2,2) ;  C6n[1,2] = C9n[1,1,2,2] ; C6n[2,1] = C6n[1,2]
    C9nmop(1,1,1,2) ;  C6n[1,3] = C9n[1,1,1,2] ; C6n[3,1] = C6n[1,3]
    C9nmop(1,1,0,2) ;  C6n[1,4] = C9n[1,1,0,2] ; C6n[4,1] = C6n[1,4]
    C9nmop(1,1,0,1) ;  C6n[1,5] = C9n[1,1,0,1] ; C6n[5,1] = C6n[1,5]

    C9nmop(2,2,2,2) ;  C6n[2,2] = C9n[2,2,2,2]
    C9nmop(2,2,1,2) ;  C6n[2,3] = C9n[2,2,1,2] ; C6n[3,2] = C6n[2,3]
    C9nmop(2,2,0,2) ;  C6n[2,4] = C9n[2,2,0,2] ; C6n[4,2] = C6n[2,4]
    C9nmop(2,2,0,1) ;  C6n[2,5] = C9n[2,2,0,1] ; C6n[5,2] = C6n[2,5]

    C9nmop(1,2,1,2) ;  C6n[3,3] = C9n[1,2,1,2]
    C9nmop(1,2,0,2) ;  C6n[3,4] = C9n[1,2,0,2] ; C6n[4,3] = C6n[3,4]
    C9nmop(1,2,0,1) ;  C6n[3,5] = C9n[1,2,0,1] ; C6n[5,3] = C6n[3,5]

    C9nmop(0,2,0,2) ;  C6n[4,4] = C9n[0,2,0,2]
    C9nmop(0,2,0,1) ;  C6n[4,5] = C9n[0,2,0,1] ; C6n[5,4] = C6n[4,5]

    C9nmop(0,1,0,1) ;  C6n[5,5] = C9n[0,1,0,1]

    return C6n


def get_rotation_matrix(original_cell, new_cell):
    import numpy as np
    rotation_matrix = np.linalg.solve(new_cell, original_cell)
    return rotation_matrix

def rotate_matrix_around_x(alpha):
    """
    Counterclockwise rotation of alpha around x axis
    :param alpha:
    :return:
    """
    import numpy as np

    rotation_matrix = np.zeros((3,3))

    rotation_matrix[0,0] = 1
    rotation_matrix[1,1] = np.cos(alpha)
    rotation_matrix[1,2] = np.sin(alpha)
    rotation_matrix[2,2] = np.cos(alpha)
    rotation_matrix[2,1] = -np.sin(alpha)

    return rotation_matrix

def rotate_matrix_around_y(alpha):
    """
    Counter clockwise
    :param alpha:
    :return:
    """
    import numpy as np

    rotation_matrix = np.zeros((3,3))
    rotation_matrix[0,0] = np.cos(alpha)
    rotation_matrix[1,1] = 1
    rotation_matrix[0,2] = -np.sin(alpha)
    rotation_matrix[2,2] = np.cos(alpha)
    rotation_matrix[2,0] = np.sin(alpha)

    return rotation_matrix

def rotate_matrix_around_z(alpha):
    """
    Counter clockwise
    :param alpha:
    :return:
    """
    import numpy as np

    rotation_matrix = np.zeros((3,3))

    rotation_matrix[0,0] = np.cos(alpha)
    rotation_matrix[1,1] = np.cos(alpha)
    rotation_matrix[0,1] = -np.sin(alpha)
    rotation_matrix[2,2] = 1
    rotation_matrix[1,0] = np.sin(alpha)

    return rotation_matrix

def validate_rotation_matrix(TM):
    import numpy as np
    if (np.abs(np.abs(np.linalg.det(TM))-1.) > 1e-10):
        raise ValueError('Absolute value of determinant of rotation matrix should be 1')


if __name__ == '__main__':

    # diamond_elastic_constants = [[1049.97870684728, 123.059571025402, 123.059571025402, 0.0, 0.0, 0.0], [123.059571025402, 1049.97870684728, 123.059571025402, 0.0, 0.0, 0.0], [123.059571025402, 123.059571025402, 1049.97870684728, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 560.748936040234, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 560.748936040234, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 560.748936040234]]
    # diamond_elastic_constants = [[313.094676569096, 30.2586117288053, 20.0991964067808, 0.906891631985156, -0.0239554887529643, -0.245228086536496], [30.2586117288053, 313.457836848139, 75.108883372176, -2.22011999032832, 1.05539751328943, -0.390115045323302], [20.0991964067808, 75.108883372176, 416.689326053337, -0.472577196399241, -1.51872091937483, -0.095126324448735], [0.906891631985156, -2.22011999032832, -0.472577196399241, 135.352909142889, -0.127882223818474, 1.44699209592549], [-0.0239554887529643, 1.05539751328943, -1.51872091937483, -0.127882223818474, 76.5944781295865, 0.0373839514401624], [-0.245228086536496, -0.390115045323302, -0.095126324448735, 1.44699209592549, 0.0373839514401624, 118.172905258033]]
    # diamond_elastic_constants = [[313.056001300903, 30.8099092611516, 20.219707132614, -1.63543909218785, -1.33712555756647, 0.572787450018832], [30.8099092611516, 314.135353974984, 77.6517807309798, -1.94029987307315, -0.5006598497068, -2.37119567299495], [20.219707132614, 77.6517807309798, 412.414858903638, -2.68068521380564, -1.67085310039934, -0.277814277780773], [-1.63543909218785, -1.94029987307315, -2.68068521380564, 112.0231561814, -0.308144954099176, -0.376309717159913], [-1.33712555756647, -0.5006598497068, -1.67085310039934, -0.308144954099176, 74.8155622957088, -0.832098803712641], [0.572787450018832, -2.37119567299495, -0.277814277780773, -0.376309717159913, -0.832098803712641, 116.882443724328]]
    #
    # diamond_cv_matrix =  [[-0.000570258406300864, -0.000428155789477904, -0.000428155789477904, 0.0, 0.0, 0.0], [-0.000428155789477904, -0.000570258406300864, -0.000428155789477904, 0.0, 0.0, 0.0], [-0.000428155789477904, -0.000428155789477904, -0.000570258406300864, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, -0.00231331597507201, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, -0.00231331597507201, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, -0.00231331597507201]]
    # diamond_cv_matrix =[[-9.11742595683261e-05, 3.90194536122017e-05, -2.91884804089548e-06, -6.88262599952911e-05, 0.000145591417672925, -2.35848324099706e-05], [3.90194536122017e-05, -4.18996406233988e-05, -8.24234630395702e-05, -0.000199720974757246, -0.000166596225601381, 4.4433887150001e-05], [-2.91884804089548e-06, -8.24234630395702e-05, -0.000124280591781745, -0.000424206084131606, -0.000374001194534133, -0.000151844623797955], [-6.88262599952911e-05, -0.000199720974757246, -0.000424206084131606, -0.00152157323732894, -0.00145422688009859, -0.000668401185926461], [0.000145591417672925, -0.000166596225601381, -0.000374001194534133, -0.00145422688009859, -0.00138489745525234, -0.000408471608154845], [-2.35848324099706e-05, 4.4433887150001e-05, -0.000151844623797955, -0.000668401185926461, -0.000408471608154845, 0.000128838234647335]]
    # diamond_cv_matrix =[[1.46056588550987e-05, 1.46613135282789e-05, -1.60188090449445e-05, 8.6938320369516e-05, 1.21103252186857e-05, 4.40896497957066e-05], [1.46613135282789e-05, 2.89561276862187e-05, -5.83021749287708e-05, 8.19876286985528e-05, 0.000117504617384236, 0.000106054430963638], [-1.60188090449445e-05, -5.83021749287708e-05, 0.000265334269899442, 0.00015112783164, 4.13657632016397e-05, 0.000101308652707019], [8.6938320369516e-05, 8.19876286985528e-05, 0.00015112783164, 9.21288510793024e-05, -9.13478316682703e-06, -2.21877229466836e-05], [1.21103252186857e-05, 0.000117504617384236, 4.13657632016397e-05, -9.13478316682703e-06, 1.34357501249944e-05, 4.27269689029301e-05], [4.40896497957066e-05, 0.000106054430963638, 0.000101308652707019, -2.21877229466836e-05, 4.27269689029301e-05, 1.12448584929798e-06]]
    #
    # 
    # diamond = elastic_properties(diamond_elastic_constants)
    # cv = elastic_properties(diamond_cv_matrix)
    #
    # print 'Analysing diamond properties: '
    # print 'Bulk modulus {}, {}'.format(diamond.hill_bulk_modulus, cv.hill_bulk_modulus)
    # print 'Reuss Shear modulus {}'.format(diamond.reuss_shear_modulus)
    # print 'Voigt shear modulus {}, {}'.format(diamond.voigt_shear_modulus, cv.voigt_shear_modulus)
    # print 'Young modulus {}, {}'.format(diamond.hill_young_modulus, cv.hill_young_modulus)
    # print 'Poisson ratio {}, {}'.format(diamond.hill_poisson_ratio, cv.hill_poisson_ratio)

    import numpy as np
    import math
    elastic_constants = np.array([[1073.39677300077, 200.319308828234, -4.23890836239573, 0.0, 0.0, 0.0],
        [200.319308828234, 1073.39677300077, -4.23890836239573, 0.0, 0.0, 0.0],
        [-4.23890836239573, -4.23890836239573, 43.3415551181075, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 7.07192285593431, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 7.07192285593431, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 436.538732086266]]
    )


    # elastic_constants = np.array([[ 1.5645, 0.5380, 0.5062, 0.1023, 0.1004, -0.3332],
    #     [0.5380, 1.4107, 0.5239, 0.2623, -0.0838,  -0.3209],
    #     [0.5062, 0.5239, 1.6149 ,0.3320, 0.1037,-0.0499],
    #     [0.1023, 0.2623, 0.3320, 1.0538, -0.1329 ,  -0.0401],
    #     [0.1004,-0.0838, 0.1037, -0.1329,1.0542,0.1576],
    #     [-0.3332, -0.3209, -0.0499, -0.0401,0.1576,1.0850]])





