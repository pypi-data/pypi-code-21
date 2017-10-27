# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Philippe Schwaller."

import numpy as np
from aiida.workflows.user.epfl_theos.quantumespresso.elastic_utils import  (_get_matrix_from_independent_constants,
                                                        get_laue_classification, rotate_elastic_matrix)

class ElasticProperties():

    def __init__(self, elastic_constant_matrix, standard_deviation=None, space_group=None):
        import numpy as np

        self.elastic_constants = np.array(elastic_constant_matrix)

        self.shear_stability_limit = 2 #GPa
        self.bulk_stability_limit = 2 #GPa

        self.rotation_matrix = None

        if self.elastic_constants.shape != (6,6):
            raise ValueError("Elastic constant matrix has not a (6,6) shape")

        if standard_deviation is not None and space_group is not None:
            self.set_standard_deviation(standard_deviation, space_group)


    def set_standard_deviation(self, standard_deviation, space_group):
        import numpy as np
        laue_class = get_laue_classification(space_group)
        self.standard_deviation_matrix = _get_matrix_from_independent_constants(standard_deviation,laue_class,
                                                                                standard_deviation=True)

    def rotate_elastic_constants(self, rotation_matrix):
        import numpy as np
        if self.rotation_matrix is None:
            self.rotation_matrix = rotation_matrix
        else:
            self.rotation_matrix = np.dot(self.rotation_matrix, rotation_matrix)

        self.elastic_constants = np.array(rotate_elastic_matrix(self.elastic_constants, rotation_matrix))
        if self.standard_deviation_matrix is not None:
            self.standard_deviation_matrix = rotate_elastic_matrix(self.standard_deviation_matrix, rotation_matrix)



    @property
    def elastic_constant_matrix(self):
        return self.elastic_constants

    @property
    def compliance_matrix(self):
        return self.get_compliance_matrix()

    @property
    def voigt_bulk_modulus(self):
        return self.get_voigt_bulk_modulus()

    @property
    def voigt_shear_modulus(self):
        return self.get_voigt_shear_modulus()

    @property
    def voigt_young_modulus(self):
        return self.get_voigt_young_modulus()

    @property
    def voigt_poisson_ratio(self):
        return self.get_voigt_poisson_ratio()

    @property
    def reuss_bulk_modulus(self):
        return self.get_reuss_bulk_modulus()

    @property
    def reuss_shear_modulus(self):
        return self.get_reuss_shear_modulus()

    @property
    def reuss_young_modulus(self):
        return self.get_reuss_young_modulus()

    @property
    def reuss_poisson_ratio(self):
        return self.get_reuss_poisson_ratio()

    @property
    def hill_bulk_modulus(self):
        return self.get_hill_bulk_modulus()

    @property
    def hill_shear_modulus(self):
        return self.get_hill_shear_modulus()

    @property
    def hill_young_modulus(self):
        return self.get_hill_young_modulus()

    @property
    def hill_poisson_ratio(self):
        return self.get_hill_poisson_ratio()

    @property
    def elastic_anisotropy(self):
        return self.get_elastic_anisotropy()

    @property
    def eigenvalues(self):
        import numpy as np
        eigenvalues, _ = np.linalg.eig(self.elastic_constants)
        return eigenvalues


    # stability criteria
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


    def get_voigt_bulk_modulus(self):
        """
        Return Voigt bulk modulus
        :param elastic_constant_matrix:
        :return: voigt bulk modulus
        """
        matrix = self.elastic_constants
        return (matrix[0, 0] + matrix[1, 1] + matrix[2, 2] + 2 * (matrix[0, 1] + matrix[0, 2] + matrix[1, 2])) / 9


    def get_voigt_shear_modulus(self):
        """
        Return Voigt shear modulus
        :param elastic_constant_matrix:
        :return:
        """
        C = self.elastic_constants
        return ((C[0, 0] + C[1, 1] + C[2, 2]) - (C[0, 1] + C[0, 2] + C[1, 2]) + 3 * (C[3, 3] + C[4, 4] + C[5, 5])) / 15


    def get_voigt_young_modulus(self):
        """
        Return Voigt Young modulus
        :param elastic_constant_matrix:
        :return:
        """
        return (9 * self.voigt_bulk_modulus * self.voigt_shear_modulus) / (3 * self.voigt_bulk_modulus + self.voigt_shear_modulus)


    def get_voigt_poisson_ratio(self):
        """
        Return Voigt Poisson ratio
        :param elastic_constant_matrix:
        :return:
        """
        return (1.5 * self.voigt_bulk_modulus - self.voigt_shear_modulus) / (3 * self.voigt_bulk_modulus + self.voigt_shear_modulus)


    def get_reuss_bulk_modulus(self):
        """
        Return Reuss bulk modulus
        :param elastic_constant_matrix:
        :return:
        """
        S  = self.compliance_matrix
        return 1 / (S[0, 0] + S[1, 1] + S[2, 2] + 2 * (S[0, 1] + S[0, 2] + S[1, 2]))


    def get_reuss_shear_modulus(self):
        """
        Return Reuss shear modulus
        :param elastic_constant_matrix:
        :return:
        """
        S  = self.compliance_matrix
        return 15 / (
            4 * (S[0, 0] + S[1, 1] + S[2, 2]) - 4 * (S[0, 1] + S[0, 2] + S[1, 2]) + 3 * (S[3, 3] + S[4, 4] + S[5, 5]))


    def get_reuss_young_modulus(self):
        """
        Return Reuss Young modulus
        :param elastic_constant_matrix:
        :return:
        """
        return (9 * self.reuss_bulk_modulus * self.reuss_shear_modulus) / (3 * self.reuss_bulk_modulus + self.reuss_shear_modulus)


    def get_reuss_poisson_ratio(self):
        """
        Return Reuss Poisson ratio
        :param elastic_constant_matrix:
        :return:
        """
        return (1.5 * self.reuss_bulk_modulus - self.reuss_shear_modulus) / (3 * self.reuss_bulk_modulus + self.reuss_shear_modulus)


    def get_hill_bulk_modulus(self):
        """
        Return Hill bulk modulus
        :param elastic_constant_matrix:
        :return: hill bulk modulus
        """
        return 0.5 * (self.voigt_bulk_modulus + self.reuss_bulk_modulus)


    def get_hill_shear_modulus(self):
        """
        Return Hill shear modulus
        :param elastic_constant_matrix:
        :return:hill shear modulus
        """
        return 0.5 * (self.voigt_shear_modulus + self.reuss_shear_modulus)


    def get_hill_young_modulus(self):
        """
        Return Hill Young modulus
        :param elastic_constant_matrix:
        :return: hill young modulus
        """
        return (9. * self.hill_bulk_modulus * self.hill_shear_modulus) / (3. * self.hill_bulk_modulus + self.hill_shear_modulus)


    def get_hill_poisson_ratio(self):
        """
        Hill Poisson ratio
        :param elastic_constant_matrix:
        :return: hill poisson ratio
        """
        return (1.5 * self.hill_bulk_modulus - self.hill_shear_modulus) / (3. * self.hill_bulk_modulus + self.hill_shear_modulus)


    def get_elastic_anisotropy(self):
        """
        Universal elastic anisotropy index, isotropy = 0
        Source: Ranganathan SI, Ostoja-Starzewski M. Phys Rev Lett 2008:101.
        :param elastic_constant_matrix:
        :return: elastic anisotropy (dimensionless)
        """
        universal_elastic_anisotropy = 5. * self.voigt_shear_modulus / self.reuss_shear_modulus + self.voigt_bulk_modulus / \
                                       self.reuss_bulk_modulus  - 6
        return universal_elastic_anisotropy


    def get_compliance_matrix(self):
        """
        Get the inverse of the stiffness matrix (elastic constant matrix)
        :param elastic_constant_matrix:
        :return: compliance_matrix
        """
        import numpy as np
        return np.linalg.inv(self.elastic_constants)

    def get_info_dict(self):
        info_dict = {}

        compliance = self.compliance_matrix
        standard_deviation = self.standard_deviation_matrix

        for i in range(6):
            for j in range(i,6):
                info_dict['C{}{}'.format(i+1,j+1)] = self.elastic_constants[i][j]
                info_dict['std{}{}'.format(i+1,j+1)] = standard_deviation[i][j]
                info_dict['S{}{}'.format(i+1,j+1)] = compliance[i][j]

        info_dict['universal_anisotropy'] = self.elastic_anisotropy
        info_dict['bulk_modulus_hill'] = self.hill_bulk_modulus
        info_dict['young_modulus_hill'] = self.hill_young_modulus
        info_dict['shear_modulus_hill'] = self.hill_shear_modulus
        info_dict['poisson_ratio_hill'] = self.hill_poisson_ratio

        return info_dict
