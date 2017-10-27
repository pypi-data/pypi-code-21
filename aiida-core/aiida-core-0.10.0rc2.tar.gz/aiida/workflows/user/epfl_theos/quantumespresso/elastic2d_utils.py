# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller."

class NotImplementedExc(Exception):
    pass


class SpaceGroupOutOfRangeExc(Exception):
    pass


oblique_matrix = [
    [1., 1., 0., 0., 0., 1.],
    [1., 1., 0., 0., 0., 1.],
    [0., 0., 0., 0., 0., 0.],
    [0., 0., 0., 0., 0., 0.],
    [0., 0., 0., 0., 0., 0.],
    [1., 1., 0., 0., 0., 1.],
]
rectangular_matrix = [
    [1., 1., 0., 0., 0., 0.],
    [1., 1., 0., 0., 0., 0.],
    [0., 0., 0., 0., 0., 0.],
    [0., 0., 0., 0., 0., 0.],
    [0., 0., 0., 0., 0., 0.],
    [0., 0., 0., 0., 0., 1.],
]
centered_rectangular_matrix = rectangular_matrix
hexagonal_matrix = rectangular_matrix
square_matrix = rectangular_matrix
oblique_rules_dict = {
    '00': 0,
    '01': 1,
    '05': 2,
    '11': 3,
    '15': 4,
    '55': 5,
}
rectangular_rules_dict = {
    '00': 0,
    '01': 1,
    '11': 2,
    '55': 3,
}
centered_rectangular_rules_dict = {
    '00': 0,
    '01': 1,
    '11': 2,
    '55': 3,
}
hexagonal_rules_dict = {
    '00': 0,
    '01': 1,
    '11': 0,
    '55': [0, -1],
}
square_rules_dict = {
    '00': 0,
    '01': 1,
    '11': 0,
    '55': 2,
}
lagrangian_strain_energy_dict = {
    '01': [1., 0., 0., 0., 0., 0.],
    '02': [0., 1., 0., 0., 0., 0.],
    '03': [0., 0., 0., 0., 0., 2.],
    '04': [1., 1., 0., 0., 0., 0.],
    '05': [1., 0., 0., 0., 0., 2.],
    '06': [0., 1., 0., 0., 0., 2.],
    '07': [1., -1., 0., 0., 0., 2.],
}
lagrangian_strain_stress_dict ={
    '01': [1., 2., 0., 0., 0., 3.],
    '02': [-2., 1.,0., 0., 0., -3.],
    '03': [1., -3., 0., 0., 0., -2.],
    '04': [-2., -3., 0., 0., 0., 1.],
    '05': [3., 2., 0., 0., 0., -1.],
    '06': [-3., 2., 0., 0., 0., 1.],
}
bravais_classification_dict = {
    'S': 'Square',
    'H': 'Hexagonal',
    'RC': 'Centered rectangular',
    'R': 'Rectangular',
    'O': 'Oblique'

}


def get_bravais_lattice(space_group_number):
    """
    Return laue classification from space group number
    :param space_group_number:
    :return: laue classification
    """
    oblique_bravais_lattices = [1,2, 3, 6, 7, 10, 13]
    rectangular_bravais_lattices = [4, 5, 8, 11, 12, 14, 16, 17, 18, 21, 25, 26, 27, 28, 29, 30, 31, 32, 35, 38, 39,
                                      47, 49, 50, 51, 53, 54, 57, 59, 65, 67]
    square_bravais_lattices = [75, 81, 83, 85, 89, 90, 99, 100, 111,  113, 115, 117, 123,  125, 127, 129]
    hexagonal_bravais_lattices = [143, 147, 149, 150, 156, 157, 162, 164, 168, 174, 175, 177, 183, 187, 189, 191]

    if space_group_number in oblique_bravais_lattices:
        return 'O'
    elif space_group_number in rectangular_bravais_lattices:
        return 'R'
    elif space_group_number in square_bravais_lattices:
        return 'S'
    elif space_group_number in hexagonal_bravais_lattices:
        return 'H'
    else:
        return 'O'


def get_lagrangian_strain_list_from_bravais(bravais_lattice,
                                         method):
    """
    Return the list of strain numbers corresponding to strain vectors used to
    calculated the elastic constants for a specific laue class, method and order.

    :param laue_classification: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :param method: 'energy' or 'stress'
    :return: List of strain numbers
    """
    if method == 'energy':
        return _get_strain_list_2nd_order_energy(bravais_lattice)
    elif method == 'stress':
        return _get_strain_list_2nd_order_stress(bravais_lattice)
    else:
        raise NotImplementedError


def _get_strain_list_2nd_order_energy(bravais_lattice):
    """
    Predefined strain vector list to calculate 2nd order elastic constants using the energy approach
    :param bravais_lattice: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :return: strain list
    """
    if bravais_lattice == 'S':
        return ['01', '03', '04']
    if bravais_lattice == 'H':
        return ['01', '04']
    if bravais_lattice == 'R':
        return ['01', '02', '03', '04']
    if bravais_lattice == 'RC':
        return ['01', '02', '03', '04']
    if bravais_lattice == 'O':
        return ['01', '02', '03', '04', '05', '06']


def _get_strain_list_2nd_order_stress(bravais_lattice):
    """
    Predefined strain vector list to calculate 2nd order elastic constants using the stress approach
    :param laue_classification: Abbreviation of Laue Classification, e.g. 'CI', 'HI', ...
    :return: strain_list
    """
    if bravais_lattice == 'S':
        return ['01']
    if bravais_lattice == 'H':
        return ['01']
    if bravais_lattice == 'R':
        return ['01', '02']
    if bravais_lattice == 'RC':
        return ['01', '02']
    if bravais_lattice == 'O':
        return ['01', '02']


def _get_rules_dict_from_bravais(bravais_lattice):
    """
    Return the mapping dictionary from independent constants vector to matrix elements
    :param laue_classification:
    :return: mapping rules dictionary
    """
    if bravais_lattice == 'S':
        return square_rules_dict
    if bravais_lattice == 'H':
        return hexagonal_rules_dict
    if bravais_lattice == 'R':
        return rectangular_rules_dict
    if bravais_lattice == 'RC':
        return centered_rectangular_rules_dict
    if bravais_lattice == 'O':
        return oblique_rules_dict


def _get_symmetry_matrix_from_bravais(bravais_lattice):
    """
    Return matrix with non null elastic constant elements for specific laue class
    :param laue_classification:
    :return:
    """
    if bravais_lattice == 'S':
        return square_matrix
    if bravais_lattice == 'H':
        return hexagonal_matrix
    if bravais_lattice == 'R':
        return rectangular_matrix
    if bravais_lattice == 'RC':
        return centered_rectangular_matrix
    if bravais_lattice == 'O':
        return oblique_matrix


def _get_linear_equations_matrix(method, bravais_lattice, strain_list):
    """
    Return linear equation matrix for specific method, laue classification and strain list
    :param method: 'energy' or 'stress'
    :param bravais_lattice: abbreviation of laue classification
    :param strain_list: list of strain vectors
    :return: a matrix containing the coefficients of the linear equation that has to be solved in order to compute
        the independent elastic constants
    """
    import numpy as np
    def _get_linear_matrix_row_energy(strain_vector, bravais_lattice):
        """
        Generate a matrix row for the energy method, corresponding to one deformation
        :param strain_vector:
        :param bravais_lattice:
        :return:
        """
        import numpy as np
        strain_vector = np.array(strain_vector)
        rules_dict = _get_rules_dict_from_bravais(bravais_lattice)
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

    def _get_linear_matrix_rows_stress(strain_vector, bravais_lattice):
        """
        Generate six matrix rows for the stress method, corresponding to one deformation
        :param strain_vector:
        :param bravais_lattice:
        :return:
        """
        import numpy as np
        rules_dict = _get_rules_dict_from_bravais(bravais_lattice)
        symmetry_matrix = _get_symmetry_matrix_from_bravais(bravais_lattice)

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
            row = _get_linear_matrix_row_energy(strain_vector, bravais_lattice)
            if final_matrix is None:
                final_matrix = row
            else:
                final_matrix = np.vstack((final_matrix, row))
        elif method == 'stress':
            rows = _get_linear_matrix_rows_stress(strain_vector, bravais_lattice)
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
    laue_class = get_bravais_lattice(space_group)
    variance_vector = np.array(standard_deviation_array)**2
    if custom_strain_list is None:
        strain_list, _ = get_strain_list(space_group, method)
    else:
        strain_list = custom_strain_list

    matrix = np.matrix(_get_linear_equations_matrix(method, laue_class, strain_list))

    linear_transformation_matrix = np.linalg.inv(matrix.T * matrix) * matrix.T

    absolute_linear_transformation_matrix = np.square(linear_transformation_matrix)
    variance_vector_after_absolute_linear_transformation = np.dot(absolute_linear_transformation_matrix, variance_vector)
    standard_deviation_absolute_linear_transformation = np.array(variance_vector_after_absolute_linear_transformation[0])**0.5

    # return standard_deviation_cov_diag, standard_deviation_absolute_linear_transformation
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
    bravais_lattice = get_bravais_lattice(space_group)

    if custom_strain_list is None:
        strain_list, _ = get_strain_list(space_group, method)
    else:
        strain_list = custom_strain_list

    matrix = _get_linear_equations_matrix(method, bravais_lattice, strain_list)

    polynomial_coefficients = np.array(polynomial_coeffs_array)
    ci = np.linalg.lstsq(matrix, polynomial_coefficients)

    elastic_constants_matrix = _get_matrix_from_independent_constants(ci[0], bravais_lattice)
    return elastic_constants_matrix


def _get_matrix_from_independent_constants(constants_vector, bravais_lattice, standard_deviation=False):
    """
    Return 6x6 elastic constants matrix from vector with independent elastic constants. The upper triangle
    of the elastic constants matrix is read line by line, and the first independent element, corresponds to
    the first element in the vector, the second element of the vector to the second independent in the matrix,
    ignoring all elements, which are 0.
    :param constants_vector:
    :param bravais_lattice:
    :return: Return 6x6 elastic constants matrix
    """
    import numpy as np
    C = np.zeros((3, 3))
    if bravais_lattice == 'O':
        C[0, 0] = constants_vector[0]
        C[0, 1] = constants_vector[1]
        C[0, 2] = constants_vector[2]
        C[1, 1] = constants_vector[3]
        C[1, 2] = constants_vector[4]
        C[2, 2] = constants_vector[5]
    elif bravais_lattice == 'R':
        C[0, 0] = constants_vector[0]
        C[0, 1] = constants_vector[1]
        C[1, 1] = constants_vector[2]
        C[2, 2] = constants_vector[3]
    elif bravais_lattice == 'RC':
        C[0, 0] = constants_vector[0]
        C[0, 1] = constants_vector[1]
        C[1, 1] = constants_vector[2]
        C[2, 2] = constants_vector[3]
    elif bravais_lattice == 'H':
        C[0, 0] = constants_vector[0]
        C[0, 1] = constants_vector[1]
        C[1, 1] = constants_vector[0]
        if standard_deviation is False:
            C[2, 2] = 0.5 * (C[0, 0] - C[0, 1])
        else:
            C[2, 2] = 0.5 * (C[0, 0] + C[0, 1])
    elif bravais_lattice == 'S':
        C[0, 0] = constants_vector[0]
        C[0, 1] = constants_vector[1]
        C[2, 2] = constants_vector[2]
    else:
        ValueError('Laue class not recognized: {}\n Please use abbreviations like "CI" and "O"'.format(bravais_lattice))
     # make the symmetric part of the matrix
    for i in range(2):
        for j in range(i + 1, 3):
            C[j, i] = C[i, j]
    return C


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


def voigt_to_matrix(vector):
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


def lagrangian_eulerian_strain_transformation(lagrangian_strain_vector):
    """
    Lagrangian strain to physical strain (eta = eps + 0.5*eps*esp)
    :param lagrangian_strain_vector: lagrangian strain vector in voigt notation
    :return: Eulerian strain matrix
    """
    import numpy as np
    lagrangian_tensor_strain_vector = voigt_to_tensor_strain(lagrangian_strain_vector)

    eta_matrix = voigt_to_matrix(lagrangian_tensor_strain_vector)
    norm = 1.0

    eps_matrix = eta_matrix  # close guess for small deformations
    if np.linalg.norm(eta_matrix) > 0.7:
        print "Warning: Norm of eta_matrix larger than 0.7, might not converge"
    while norm > 1.e-10:
        x = eta_matrix - np.dot(eps_matrix, eps_matrix) / 2.
        norm = np.linalg.norm(x - eps_matrix)
        eps_matrix = x

    return eps_matrix


def get_strain_list(space_group_number,
                    method):
    """
    Get predefined strain list for space group and method.
    :param space_group_number:
    :param method:
    :return: dictionary of strain_number as keys and vectors as values
    """
    bravais_lattice = get_bravais_lattice(space_group_number)

    lagrangian_strain_list = []
    strain_numbers = []
    if method == 'stress':
        for strain_number in get_lagrangian_strain_list_from_bravais(bravais_lattice, method):
            lagrangian_strain_list.append(lagrangian_strain_stress_dict[strain_number])
            strain_numbers.append(strain_number)
    elif method == 'energy':
        for strain_number in get_lagrangian_strain_list_from_bravais(bravais_lattice, method):
            lagrangian_strain_list.append(lagrangian_strain_energy_dict[strain_number])
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


class Elastic2dProperties():

    def __init__(self, tension_coefficient_matrix):
        import numpy as np

        self.tension_coefficients = np.array(tension_coefficient_matrix)

        if self.tension_coefficients.shape != (3,3):
            raise ValueError


    @property
    def compliance_matrix(self):
        return get_compliance_matrix(self.tension_coefficients)


    @property
    def eigenvalues(self):
        import numpy as np
        eigenvalues, _ = np.linalg.eig(self.tension_coefficients)
        return eigenvalues

    def test_positive_definite_criterion(self):
        """
        Return true if all eigenvalues are positive and False otherwise.
        :return:
        """
        import numpy as np
        if np.all(self.tension_coefficients-self.tension_coefficients.T==0) and np.all(self.eigenvalues > 0):
            return True
        else:
            return False
