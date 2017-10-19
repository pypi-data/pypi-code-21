# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Utilities to save and load schema information for Spark DataFrames.
"""

import os
import base64
from dateutil import parser
from decimal import Decimal
from pyspark.sql import SQLContext
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *

from azureml.api.schema.baseUtil import BaseUtil
from azureml.api.schema.schemaObjects import Schema, InternalSchema
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.swaggerFromSpark import Spark2Swagger
from azureml.api.schema.constants import ERR_FILE_NOT_SUPPORTED_FOR_SPARK
from azureml.common.utils import get_sdk_version


class SparkSchema(InternalSchema):

    def __init__(self, df_schema):
        if not isinstance(df_schema, StructType):
            raise TypeError("Invalid data fme schema parameter: must be a valid StructType object")
        self.schema = df_schema

    def serialize_to_string(self):
        return self.schema.jsonValue()

    @classmethod
    def deserialize_from_string(cls, serialized_schema_string):
        df_schema = StructType.fromJson(serialized_schema_string)
        return SparkSchema(df_schema)


class SparkUtil(BaseUtil):
    type = DataTypes.SPARK

    spark_session = SparkSession.builder.getOrCreate()
    sqlContext = SQLContext(spark_session.sparkContext)

    @classmethod
    def extract_schema(cls, data_frame):
        if not isinstance(data_frame, DataFrame):
            raise TypeError('Invalid data type: expected a Spark data frame.')

        internal_schema = SparkSchema(data_frame.schema)
        swagger_schema = Spark2Swagger.convert_spark_dataframe_schema_to_swagger(data_frame.schema)

        # Also extract some sample values for the schema from the first few items of the array
        items_to_sample = data_frame.take(BaseUtil.MAX_RECORDS_FOR_SAMPLE_SCHEMA)
        items_count = len(items_to_sample)
        df_record_swagger = swagger_schema['items']
        swagger_schema['example'] = cls.get_swagger_sample(items_to_sample, items_count, df_record_swagger)

        return Schema(SparkUtil.type, internal_schema, swagger_schema, get_sdk_version())

    @classmethod
    def get_input_object(cls, raw_input_value, schema):
        if not isinstance(raw_input_value, list):
            raise ValueError("Invalid input format: expected an array of items.")

        """
        Because the transform from Spark format to Swagger format is not perfect, (e.g. Spark timestamp can only 
        be represented as a formatted string in Swagger, but the string is not directly convertible by Spark back to 
        a timestamp type, even when presented with this hint), we first process the incoming payload and fix some of 
        these inconsistencies
        """
        for i in range(0, len(raw_input_value)):
            raw_input_value[i] = cls._preprocess_json_input(raw_input_value[i], schema.internal.schema)
        data_frame = SparkUtil.sqlContext.createDataFrame(data=raw_input_value, schema=schema.internal.schema, verifySchema=True)

        return data_frame

    @classmethod
    def get_input_object_from_file(cls, input_file, schema, has_header):
        filename, file_extension = os.path.splitext(input_file)

        if file_extension == '.json':
            import json
            with open(input_file, 'r') as input:
                return SparkUtil.get_input_object(json.load(input), schema)
        elif file_extension == '.csv':
            return SparkUtil.spark_session.read.csv(input_file, schema=schema.internal.schema, header=has_header)
        elif file_extension == '.tsv':
            return SparkUtil.spark_session.read.csv(input_file, schema=schema.internal.schema, header=has_header, sep='\t')
        elif file_extension == '.arff':
            raise ValueError("Unable to parse .arff file {} into spark dataframe.".format(input_file))
        elif file_extension == '.parquet':
            return SparkUtil.spark_session.read.parquet(input_file)
        else:
            raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_SPARK.format(file_extension))

    @classmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        internal_schema = SparkSchema.deserialize_from_string(serialized_internal_schema)
        return internal_schema

    @classmethod
    def _date_item_to_string(cls, date_item):
        return str(date_item)

    @classmethod
    def _timestamp_item_to_string(cls, date_item):
        return date_item.strftime("%Y-%m-%d %H:%M:%S,%f")

    @classmethod
    def _preprocess_json_input(cls, json_input, item_schema):
        if type(item_schema) is StructType:
            for field_name in item_schema.names:
                json_input[field_name] = cls._preprocess_json_input(json_input[field_name],
                                                                    item_schema[field_name].dataType)
            return json_input

        if type(item_schema) is StructField:
            return cls._preprocess_json_input(json_input, item_schema.dataType)

        type_name = item_schema.typeName()
        if type_name == 'date':
            return parser.parse(json_input).date()
        if type_name == 'timestamp':
            return parser.parse(json_input)
        if type_name == 'decimal':
            return Decimal(json_input)
        if type_name == 'binary':
            bytes = base64.b64decode(json_input.encode('utf-8'))
            return bytearray(bytes)

        if type_name == 'array':
            for i in range(0, len(json_input)):
                json_input[i] = cls._preprocess_json_input(json_input[i], item_schema.elementType)
        elif type_name == 'map':
            for key in json_input:
                json_input[key] = cls._preprocess_json_input(json_input[key], item_schema.valueType)

        return json_input
