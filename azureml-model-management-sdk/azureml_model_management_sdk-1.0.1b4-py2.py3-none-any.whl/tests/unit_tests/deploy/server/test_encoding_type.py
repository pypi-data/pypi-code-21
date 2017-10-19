# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest
import numpy as np
import pandas as pd

from azureml.deploy.server import EncodingType


class TestEncodingType:

    @pytest.mark.parametrize(
        'input_type, input_value, expected', [
            ('int', int(5), int(5)),
            ('float', float(5.12345), float(5.12345)),
            ('str', str('MLServer'), str('MLServer')),
            ('bool', bool(True), bool(True)),
            ('numpy.array',  np.array([1, 2]), [1, 2]),
            ('numpy.matrix', np.matrix(np.arange(12).reshape((3,4))),
             [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]),
            ('pandas.DataFrame',
             pd.DataFrame({
                 'n': [2.0, 3.0, 5.0],
                 's': ['aa', 'bb', 'cc'],
                 'b': [True, False, True]
             })[['n', 's', 'b']], {
                 'n': [2.0, 3.0, 5.0],
                 's': ['aa', 'bb', 'cc'],
                 'b': [True, False, True]
             })
        ])
    def test_cast_from_python(self, input_type, input_value, expected):
        input_type = EncodingType.from_python(input_type)

        assert EncodingType.cast_from_python(input_type, input_value) == \
            expected

    @pytest.mark.parametrize(
        'output_type, output_value, expected', [
            (EncodingType.integer.value, 5, int(5)),
            (EncodingType.numeric.value, 5.12345, float(5.12345)),
            (EncodingType.character.value, 'MLServer', str('MLServer')),
            (EncodingType.logical.value, True, bool(True))
        ])
    def test_cast_to_python_primitives(self, output_type, output_value,
                                       expected):
        assert EncodingType.cast_to_python(output_type, output_value) == \
            expected

    @pytest.mark.parametrize(
        'output_type, output_value, expected', [
            (EncodingType.vector.value, [1, 2], np.array([1, 2])),
            (EncodingType.matrix.value,
             [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]],
             np.matrix(np.arange(12).reshape((3,4)))),
            (EncodingType.dataframe.value, {
                 'n': [2.0, 3.0, 5.0],
                 's': ['aa', 'bb', 'cc'],
                 'b': [True, False, True]
             },
             pd.DataFrame({
                 'n': [2.0, 3.0, 5.0],
                 's': ['aa', 'bb', 'cc'],
                 'b': [True, False, True]
             }))
        ])
    def test_cast_to_python_non_primitives(self, output_type, output_value,
                                           expected):
        assert np.all(EncodingType.cast_to_python(output_type, output_value)
                      == expected)

    @pytest.mark.parametrize(
        'input_type, expected', [
            ('int', EncodingType.integer.value),
            ('float', EncodingType.numeric.value),
            ('str', EncodingType.character.value),
            ('bool', EncodingType.logical.value),
            ('numpy.array', EncodingType.vector.value),
            ('numpy.matrix', EncodingType.matrix.value),
            ('pandas.DataFrame', EncodingType.dataframe.value)
        ])
    def test_from_python(self, input_type, expected):
        assert EncodingType.from_python(input_type) == expected

    @pytest.mark.parametrize(
        'input_type, expected', [
            (int, EncodingType.integer.value),
            (float, EncodingType.numeric.value),
            (str, EncodingType.character.value),
            (bool, EncodingType.logical.value),
            (np.array, EncodingType.vector.value),
            (np.matrix, EncodingType.matrix.value),
            (pd.DataFrame, EncodingType.dataframe.value)
        ])
    def test_from_python_as_class_types(self, input_type, expected):
        assert EncodingType.from_python(input_type) == expected

    @pytest.mark.parametrize(
        'input_type, expected', [
            (EncodingType.integer.value, 'int'),
            (EncodingType.numeric.value, 'float'),
            (EncodingType.character.value, 'str'),
            (EncodingType.logical.value, 'bool'),
            (EncodingType.vector.value, 'numpy.array'),
            (EncodingType.matrix.value, 'numpy.matrix'),
            (EncodingType.dataframe.value, 'pandas.DataFrame')
        ])
    def test_to_python(self, input_type, expected):
        assert EncodingType.to_python(input_type) == expected
