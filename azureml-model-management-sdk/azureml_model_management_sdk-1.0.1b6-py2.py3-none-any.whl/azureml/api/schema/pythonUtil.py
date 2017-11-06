# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import base64
import datetime
from dateutil import parser

import azureml.api.schema.constants as cst
from azureml.api.schema.baseUtil import BaseUtil
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.schemaObjects import Schema, InternalSchema
from azureml.api.schema.swaggerFromPython import Python2Swagger
from azureml.api.schema.constants import ERR_FILE_NOT_SUPPORTED_FOR_PYTHON
from azureml.common.utils import get_sdk_version


class PythonSchema(InternalSchema):
    def __init__(self, data_type):
        if not isinstance(data_type, type):
            raise TypeError("Invalid data_type parameter: must be a valid python type")
        self.data_type = data_type


class PythonUtil(BaseUtil):

    type = DataTypes.STANDARD

    @classmethod
    def extract_schema(cls, data):
        internal_schema = PythonSchema(type(data))
        swagger_schema = Python2Swagger.get_swagger_from_python_sample(data)
        return Schema(PythonUtil.type, internal_schema, swagger_schema, get_sdk_version())

    @classmethod
    def get_input_object(cls, parsed_input, schema):
        # Some types require special handling
        if schema.internal.data_type is datetime.date:
            parsed_input = datetime.date.strptime(parsed_input, cst.DATE_FORMAT)
        elif schema.internal.data_type is datetime.datetime:
            parsed_input = parser.parse(parsed_input)
        elif schema.internal.data_type is datetime.time:
            parsed_input = parser.parse(parsed_input).timetz()
        elif schema.internal.data_type is bytearray or \
                (sys.version_info[0] == 3 and schema.internal.data_type is bytes):
                    parsed_input = base64.b64decode(parsed_input.encode('utf-8'))

        if not isinstance(parsed_input, schema.internal.data_type):
            raise ValueError("Invalid input data type to parse. Expected: {0} but got {1}".format(
                schema.internal.data_type, type(parsed_input)))

        return parsed_input

    @classmethod
    def get_input_object_from_file(cls, input_file, schema):
        if schema.internal.data_type is list:
            filename, file_extension = os.path.splitext(input_file)

            if file_extension == '.parquet':
                raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_PYTHON.format(file_extension))

            with open(input_file, 'r') as input:
                if file_extension == '.json':
                    import json
                    data = json.load(input)
                    return data
                elif file_extension == '.csv':
                    import csv
                    csv_reader = csv.reader(input)
                    data = list(csv_reader)
                    return data
                elif file_extension == '.tsv':
                    import csv
                    csv_reader = csv.reader(input, delimiter='\t')
                    data = list(csv_reader)
                    return data
                elif file_extension == '.arff':
                    import arff
                    dataset = arff.load(input)
                    return dataset['data']
                else:
                    raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_PYTHON.format(file_extension))
        else:
            raise ValueError("Unable to parse input file {0} into {1}".format(input_file, schema.internal.data_type))

    @classmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        internal_schema = PythonSchema.deserialize_from_string(serialized_internal_schema)
        if internal_schema.data_type is None:
            raise ValueError("Invalid python type schema: the data_type property must be specified")
        if not isinstance(internal_schema.data_type, type):
            raise ValueError("Invalid python type schema: the data type must be an valid python type. Got: {}".format(
                internal_schema.data_type))
        return internal_schema
