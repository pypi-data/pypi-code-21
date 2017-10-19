# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
EncodingType

Overview
========

The mapping between MLServer data-types and Python.
"""

from enum import Enum
import numpy as np
import pandas as pd
from collections import OrderedDict


class EncodingType(Enum):
    """
    The mapping between MLServer data-types and Python.
    """
    # --- Defines the Encoding Type mapping on MLServer --   
    integer = 'integer'
    numeric = 'numeric'
    character = 'character'
    logical = 'logical'
    vector = 'vector'
    matrix = 'matrix'
    dataframe = 'data.frame'

    @classmethod
    def from_python(cls, py_type):

        # Python type by <class>,
        # .inputs(x=float) --vs-- .inputs(x='float') both are equivalent
        if hasattr(py_type, '__name__'):
            py_type = py_type.__name__

        return {
            'int': cls.integer.value,
            'float': cls.numeric.value,
            'str': cls.character.value,
            'bool': cls.logical.value,
            'numpy.array': cls.vector.value,
            'array': cls.vector.value,
            'numpy.matrix': cls.matrix.value,
            'matrix': cls.matrix.value,
            'pandas.DataFrame': cls.dataframe.value,
            'DataFrame': cls.dataframe.value,
            'list': cls.vector.value
        }.pop(py_type, None)

    @classmethod
    def to_python(cls, server_type):
        return {
            cls.integer.value: 'int',
            cls.numeric.value: 'float',
            cls.character.value: 'str',
            cls.logical.value: 'bool',
            cls.vector.value: 'numpy.array',
            cls.matrix.value: 'numpy.matrix',
            cls.dataframe.value: 'pandas.DataFrame'
        }.pop(server_type, None)

    @classmethod
    def cast_from_python(cls, server_type, value):
        """
        Cast from python to server request format.

        :param server_type: The server encoding type.
        :param value: The value to be cast.
        :return: The cast valued based on server encoding type.
        """

        if value is None:
            return None

        return {
            cls.integer.value: lambda x: int(x),
            cls.numeric.value: lambda x: float(x),
            cls.character.value: lambda x: x,
            cls.logical.value: lambda x: bool(x),
            cls.vector.value: lambda x: x.tolist(),
            cls.matrix.value: lambda x: x.tolist(),
            cls.dataframe.value: lambda x: OrderedDict([(k, x[k].tolist())
                                                        for k in x.columns])
        }[server_type](value)

    @classmethod
    def cast_to_python(cls, server_type, value):
        """
        Cast from server response format back to python.

        :param server_type: The server encoding type.
        :param value: The value to be cast.
        :return: The cast valued based on server encoding type.
        """

        if value is None:
            return None

        return {
            cls.integer.value: lambda x: int(x),
            cls.numeric.value: lambda x: float(x),
            cls.character.value: lambda x: x,
            cls.logical.value: lambda x: bool(x),
            cls.vector.value: lambda x: np.array(x),
            cls.matrix.value: lambda x: np.matrix(x),
            cls.dataframe.value: lambda x: pd.DataFrame(x)
        }[server_type](value)

    def describe(self):
        return self.name, self.value
    
    def __str__(self):
        return '<EncodingType> {0}'.format(self.value)
