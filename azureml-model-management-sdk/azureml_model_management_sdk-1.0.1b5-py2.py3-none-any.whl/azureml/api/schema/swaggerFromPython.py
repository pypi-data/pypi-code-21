# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------------

import sys
import json
import base64
import datetime
import pytz
import azureml.api.schema.constants as cst
from azureml.api.schema.baseUtil import BaseUtil


class Python2Swagger:

    @staticmethod
    def get_swagger_from_python_sample(python_data):
        """
        Generate swagger schema definition for the give python primitive object.
          
        Args:
            python_data (object): JSON serializable python object of the 
                                   supported types below:
                  Supported types: 
                    -- All: int, float, bool, str, list, dict, bytearray      
                    -- Python 2 only: long, bytes (as alias for str)
                    -- Python 3 only: bytes (as actual set of bytes)
        Returns:
            dict: Swagger representation of the passed in object, along with 
                  sample data.

        """

        if python_data is None:
            raise ValueError("Python data cannot be None")

        schema = None

        # Python 2 specific type handling
        if sys.version_info[0] == 2:
            if type(python_data) is int:
                schema = {"type": "integer", "format": "int32", "example": python_data}
            elif type(python_data) is long:
                schema = {"type": "integer", "format": "int64", "example": python_data}
            elif type(python_data) is bytes:
                schema = {"type": "string", "example": python_data}

        # Python 3 specific type handling
        else:
            if type(python_data) is int:
                schema = {"type": "integer", "format": "int64", "example": python_data}
            elif type(python_data) is bytes:
                # Bytes type is not json serializable so will convert to a base 64 string for the sample
                sample = base64.b64encode(python_data).decode('utf-8')
                schema = {"type": "string", "format": "byte", "example": sample}
            elif type(python_data) is range:
                schema = Python2Swagger._get_swagger_for_list(python_data, {"type": "integer", "format": "int64"})

        # All Python versions handling
        if type(python_data) is str:
            schema = {"type": "string", "example": python_data}
        elif type(python_data) is float:
            schema = {"type": "number", "format": "double", "example": python_data}
        elif type(python_data) is bool:
            schema = {"type": "boolean", "example": python_data}
        elif type(python_data) is datetime.date:
            sample = python_data.strftime(cst.DATE_FORMAT)
            schema = {"type": "string", "format": "date", "example": sample}
        elif type(python_data) is datetime.datetime:
            date_time_with_zone = python_data
            if python_data.tzinfo is None:
                # If no timezone data is passed in, consider UTC
                date_time_with_zone = datetime.datetime(python_data.year, python_data.month, python_data.day,
                                                        python_data.hour, python_data.minute, python_data.second,
                                                        python_data.microsecond, pytz.utc)
            sample = date_time_with_zone.strftime(cst.DATETIME_FORMAT)
            schema = {"type": "string", "format": "date-time", "example": sample}
        elif type(python_data) is datetime.time:
            time_with_zone = python_data
            if python_data.tzinfo is None:
                # If no timezone data is passed in, consider UTC
                time_with_zone = datetime.time(python_data.hour, python_data.minute, python_data.second,
                                               python_data.microsecond, pytz.utc)
            sample = time_with_zone.strftime(cst.TIME_FORMAT)
            schema = {"type": "string", "format": "time", "example": sample}
        elif isinstance(python_data, bytearray):
            # Bytes type is not json serializable so will convert to a base 64 string for the sample
            sample = base64.b64encode(python_data).decode('utf-8')
            schema = {"type": "string", "format": "byte", "example": sample}
        elif type(python_data) is list or type(python_data) is tuple:
            schema = Python2Swagger._get_swagger_for_list(python_data)
        elif type(python_data) is dict:
            schema = {"type": "object", "additionalProperties": {"type": "object"}, "example": python_data}

        # If we didn't match any type yet, try out best to fit this to an object
        if schema is None:
            schema = {"type": "object", "example": python_data}

        # ensure the schema is JSON serializable
        try:
            json.dumps(schema)
        except TypeError as te:
            raise TypeError(cst.ERR_PYTHON_DATA_NOT_JSON_SERIALIZABLE.format(str(te)))

        return schema

    @staticmethod
    def _get_swagger_for_list(python_data, item_swagger_type={"type": "object"}):
        sample_size = min(len(python_data), BaseUtil.MAX_RECORDS_FOR_SAMPLE_SCHEMA)
        sample = []
        for i in range(sample_size):
            sample.append(python_data[i])
        return {"type": "array", "items": item_swagger_type, "example": sample}
