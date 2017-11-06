# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Utilities to save and load schema information for Pandas DataFrames.
"""

import os
import pandas as pd
import numpy as np
import datetime as dt
from collections import OrderedDict
from dateutil import parser
from azureml.api.schema.baseUtil import BaseUtil
from azureml.api.schema.schemaObjects import Schema, InternalSchema
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.swaggerFromDtype import Dtype2Swagger
from azureml.api.schema.constants import ERR_FILE_NOT_SUPPORTED_FOR_PANDAS
from azureml.common.utils import get_sdk_version


class PandasSchema(InternalSchema):

    def __init__(self, shape, column_names, column_types):
        if not isinstance(shape, tuple):
            raise TypeError("Invalid shape parameter: must be a tuple with array dimensions")
        if not isinstance(column_names, list):
            raise TypeError("Invalid column_names parameter: must be a valid list of strings")
        if not isinstance(column_types, list):
            raise TypeError("Invalid column_types parameter: must be a valid list of numpy.dtype")
        self.shape = shape
        self.column_names = column_names
        self.column_types = column_types

        self.schema_map = OrderedDict()
        for i in range(0, len(self.column_names)):
            self.schema_map[self.column_names[i]] = self.column_types[i]


class PandasUtil(BaseUtil):
    type = DataTypes.PANDAS

    @classmethod
    def extract_schema(cls, data_frame):
        if not isinstance(data_frame, pd.core.frame.DataFrame):
            raise TypeError('Only valid pandas data frames can be passed in to extract schema from.')

        # Construct internal schema
        shape = data_frame.shape
        columns = data_frame.columns.values.tolist()
        types = data_frame.dtypes.tolist()
        internal_schema = PandasSchema(shape, columns, types)

        # Generate swagger schema
        col_count = len(columns)
        df_record_swagger = Dtype2Swagger.get_swagger_object_schema()
        for i in range(col_count):
            """
            For string columns, Pandas tries to keep a uniform item size
            for the support ndarray, and such it stores references to strings
            instead of the string's bytes themselves, which have variable size.
            Because of this, even if the data is a string, the column's dtype is
            marked as 'object' since the reference is an object.

            We try to be smart about this here and if the column type is reported as
            object, we will also check the actual data in the column to see if its not
            actually a string, such that we can generate a better swagger schema later on.
            """
            col_name = columns[i]
            col_dtype = types[i]
            if col_dtype.name == 'object' and type(data_frame[columns[i]][0]) is str:
                col_dtype = np.dtype('str')
            col_swagger_type = Dtype2Swagger.convert_dtype_to_swagger(col_dtype)
            df_record_swagger['properties'][col_name] = col_swagger_type

        # Also extract some sample values for the schema from the first few items of the array
        items_count = min(len(data_frame), BaseUtil.MAX_RECORDS_FOR_SAMPLE_SCHEMA)
        sample_swagger = cls.get_swagger_sample(data_frame.iloc, items_count, df_record_swagger)

        swagger_schema = {'type': 'array', 'items': df_record_swagger, 'example': sample_swagger}
        return Schema(PandasUtil.type, internal_schema, swagger_schema, get_sdk_version())

    @classmethod
    def get_input_object(cls, raw_input_value, schema):
        if not isinstance(raw_input_value, list):
            raise ValueError("Invalid input format: expected an array of items.")

        for i in range(0, len(raw_input_value)):
            raw_input_value[i] = cls._preprocess_json_input(raw_input_value[i], schema.internal.schema_map)
        data_frame = pd.DataFrame(data=raw_input_value, columns=schema.internal.column_names)

        # Validate the schema of the parsed data against the known one
        df_cols = data_frame.columns.values.tolist()
        schema_cols = schema.internal.column_names
        if len(df_cols) != len(schema_cols) or len(schema_cols) != len(list(set(df_cols) & set(schema_cols))):
            raise ValueError(
                "Column mismatch between input data frame and expected schema\n\t"
                "Passed in columns: {0}\n\tExpected columns: {1}".format(df_cols, schema_cols))

        expected_shape = schema.internal.shape
        parsed_data_dims = len(data_frame.shape)
        expected_dims = len(expected_shape)
        if parsed_data_dims != expected_dims:
            raise ValueError(
                "Invalid input data frame: a data frame with {0} dimensions is expected; "
                "input has {1} [shape {2}]".format(expected_dims, parsed_data_dims, data_frame.shape))

        for dim in range(1, len(expected_shape)):
            if data_frame.shape[dim] != expected_shape[dim]:
                raise ValueError(
                    "Invalid input data frame: data frame has size {0} on dimension #{1}, "
                    "while expected value is {2}".format(
                        data_frame.shape[dim], dim, expected_shape[dim]))

        return data_frame

    @classmethod
    def get_input_object_from_file(cls, input_file, schema):
        filename, file_extension = os.path.splitext(input_file)

        if file_extension == '.parquet':
            raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_PANDAS.format(file_extension))

        with open(input_file, 'r') as input:
            if file_extension == '.json':
                import json
                data = json.load(input)
                return PandasUtil.get_input_object(data, schema)
            elif file_extension == '.csv':
                return pd.read_csv(input_file)
            elif file_extension == '.tsv':
                return pd.read_table(input_file)
            elif file_extension == '.arff':
                import arff
                dataset = arff.load(input)
                data = pd.DataFrame(dataset['data'], columns=schema.internal.column_names)
                return data
            else:
                raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_PANDAS.format(file_extension))

    @classmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        internal_schema = PandasSchema.deserialize_from_string(serialized_internal_schema)
        if internal_schema.column_names is None:
            raise ValueError("Invalid data frame schema: the column_names property must be specified")
        if internal_schema.column_types is None:
            raise ValueError("Invalid data frame schema: the column_types property must be specified")
        if internal_schema.shape is None:
            raise ValueError("Invalid data frame schema: the shape property must be specified")

        return internal_schema


    @classmethod
    def _date_item_to_string(cls, date_item):
        return date_item.astype(dt.datetime).strftime("%Y-%m-%d")

    @classmethod
    def _timestamp_item_to_string(cls, date_item):
        return pd.Timestamp(date_item).to_pydatetime().strftime("%Y-%m-%d %H:%M:%S,%f")

    @classmethod
    def _preprocess_json_input(cls, json_input, item_schema):
        if len(item_schema) == 0:
            if item_schema.subdtype is None:
                # Simple scalar type
                return cls._handle_simple_type_preprocessing(json_input, item_schema)
            else:
                # Sub-array type
                return cls._handle_array_preprocessing(json_input, item_schema.subdtype[0])
        else:
            if isinstance(item_schema, OrderedDict) or isinstance(item_schema, dict):
                for field_name in item_schema:
                    json_input[field_name] = cls._preprocess_json_input(json_input[field_name], item_schema[field_name])
            else:
                # Structured data type
                for field_name in item_schema.names:
                    json_input[field_name] = cls._preprocess_json_input(json_input[field_name], item_schema[field_name])
            return json_input

    @classmethod
    def _handle_array_preprocessing(cls, json_input, item_type):
        if isinstance(json_input, list):
            for i in range(0, len(json_input)):
                json_input[i] = cls._handle_array_preprocessing(json_input[i], item_type)
            return json_input

        return cls._handle_simple_type_preprocessing(json_input, item_type)

    @classmethod
    def _handle_simple_type_preprocessing(cls, simple_type_json, item_type):
        simple_type_name = item_type.name.lower()
        if simple_type_name.startswith('datetime'):
            return parser.parse(simple_type_json)
        elif simple_type_name.startswith('timedelta'):
            return pd.Timedelta(simple_type_json)
        else:
            return simple_type_json
