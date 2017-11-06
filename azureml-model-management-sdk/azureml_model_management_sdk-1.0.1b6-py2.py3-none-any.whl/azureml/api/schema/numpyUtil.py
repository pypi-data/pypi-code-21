# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Utilities to extract schema information for Numpy Arrays.
"""

import os
import numpy as np
import datetime as dt
from azureml.api.schema.baseUtil import BaseUtil
from azureml.api.schema.schemaObjects import Schema, InternalSchema
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.swaggerFromDtype import Dtype2Swagger
from azureml.api.schema.constants import ERR_FILE_NOT_SUPPORTED_FOR_NUMPY
from azureml.common.utils import get_sdk_version


class NumpySchema(InternalSchema):

    def __init__(self, shape, data_type):
        if not isinstance(shape, tuple):
            raise TypeError("Invalid shape parameter: must be a tuple with array dimensions")
        if not isinstance(data_type, np.dtype):
            raise TypeError("Invalid data_type parameter: must be a valid numpy.dtype")
        self.shape = shape
        self.data_type = data_type


class NumpyUtil(BaseUtil):
    type = DataTypes.NUMPY

    timestamp_symbols = {
        "years": "Y",
        "months": "M",
        "weeks": "W",
        "days": "D",
        "hours": "h",
        "minutes": "m",
        "seconds": "s",
        "milliseconds": "ms",
        "microseconds": "us",
        "nanoseconds": "ns",
        "picoseconds": "ps",
        "femtoseconds": "fs",
        "attoseconds": "as",
    }

    @classmethod
    def extract_schema(cls, array):
        if not isinstance(array, np.ndarray):
            raise TypeError('Only valid numpy array can be passed in to extract schema from.')
        schema = NumpySchema(array.shape, array.dtype)

        # Create the swagger schema for the data type of the array
        swagger_item_type = Dtype2Swagger.convert_dtype_to_swagger(schema.data_type)
        swagger_schema = Dtype2Swagger.handle_swagger_array(swagger_item_type, schema.shape)

        # Also extract some sample values for the schema from the first few items of the array
        items_count = min(len(array), BaseUtil.MAX_RECORDS_FOR_SAMPLE_SCHEMA)
        swagger_schema['example'] = cls.get_swagger_sample(array, items_count, swagger_schema['items'])

        return Schema(NumpyUtil.type, schema, swagger_schema, get_sdk_version())

    @classmethod
    def get_input_object(cls, raw_input_value, schema):
        if not isinstance(raw_input_value, list):
            raise ValueError("Invalid input format: expected an array of items.")

        for i in range(len(raw_input_value)):
            raw_input_value[i] = cls._preprocess_json_input(raw_input_value[i], schema.internal.data_type)
        numpy_array = np.array(object=raw_input_value, dtype=schema.internal.data_type, copy=False)

        # Validate the schema of the parsed data against the known one
        expected_shape = schema.internal.shape
        parsed_dims = len(numpy_array.shape)
        expected_dims = len(expected_shape)
        if parsed_dims != expected_dims:
            raise ValueError(
                "Invalid input array: an array with {0} dimensions is expected; "
                "input has {1} [shape {2}]".format(expected_dims, parsed_dims, numpy_array.shape))
        for dim in range(1, len(expected_shape)):
            if numpy_array.shape[dim] != expected_shape[dim]:
                raise ValueError(
                    'Invalid input array: array has size {0} on dimension #{1}, '
                    'while expected value is {2}'.format(numpy_array.shape[dim], dim, expected_shape[dim]))

        return numpy_array

    @classmethod
    def get_input_object_from_file(cls, input_file, schema, has_header):
        filename, file_extension = os.path.splitext(input_file)

        if file_extension == '.parquet':
            raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_NUMPY.format(file_extension))

        with open(input_file, 'r') as input:
            if file_extension == '.json':
                import json
                raw_data = json.load(input)
                return NumpyUtil.get_input_object(raw_data, schema)
            elif file_extension == '.csv':
                data = np.genfromtxt(input_file, delimiter=",", dtype=schema.internal.data_type, skip_header=1 if has_header else 0)
                return data
            elif file_extension == '.tsv':
                data = np.genfromtxt(input_file, delimiter="\t", dtype=schema.internal.data_type, skip_header=1 if has_header else 0)
                return data
            elif file_extension == '.arff':
                import arff
                dataset = arff.load(input)['data']
                for i in range(len(dataset)):
                    dataset[i] = tuple(dataset[i])
                data = np.array(dataset, dtype=schema.internal.data_type)
                return data
            else:
                raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_NUMPY.format(file_extension))

    @classmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        internal_schema = NumpySchema.deserialize_from_string(serialized_internal_schema)
        if internal_schema.data_type is None:
            raise ValueError("Invalid array schema: the data_type property must be specified")
        if internal_schema.shape is None:
            raise ValueError("Invalid array schema: the shape property must be specified")

        return internal_schema

    @classmethod
    def _date_item_to_string(cls, date_item):
        return date_item.astype(dt.datetime).strftime("%Y-%m-%d")

    @classmethod
    def _timestamp_item_to_string(cls, date_item):
        return date_item.astype(dt.datetime).strftime("%Y-%m-%d %H:%M:%S,%f")

    @classmethod
    def _preprocess_json_input(cls, json_input, item_schema):
        if len(item_schema) > 0:
            converted_item = []
            for field_name in item_schema.names:
                new_item_field = cls._preprocess_json_input(json_input[field_name], item_schema[field_name])
                converted_item.append(new_item_field)
            return tuple(converted_item)
        else:
            simple_type_name = item_schema.name.lower()
            if simple_type_name.startswith('datetime'):
                return np.datetime64(json_input)
            elif simple_type_name.startswith('timedelta'):
                return cls._parse_timedelta(json_input)
            else:
                return json_input

    @classmethod
    def _parse_timedelta(cls, timedelta_str):
        item_split = timedelta_str.split(None, 1)
        if len(item_split) != 2:
            raise ValueError("Invalid numpy.timestamp64 value specified: {0}. Format should be <value> <time_unit_code>".format(timedelta_str))
        unit_value = int(item_split[0])
        unit_type = item_split[1].lower()
        if unit_type not in NumpyUtil.timestamp_symbols:
            raise ValueError("Invalid numpy.timestamp64 value specified: {0}. Unrecognized time unit code".format(timedelta_str))
        return np.timedelta64(unit_value, NumpyUtil.timestamp_symbols[unit_type])
