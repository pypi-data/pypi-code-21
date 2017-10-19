# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import datetime
import pytz
import json
import azureml.api.schema.constants as cst
import numpy as np

from azureml.api.schema.pythonUtil import PythonUtil, PythonSchema
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.schema.schemaUtil import save_service_schema, load_service_schema
from azureml.api.schema.schemaObjects import Schema
from tests.unit_tests.api.schema_tests_common import SchemaUnitTests


class PythonUtilTest(SchemaUnitTests):

    def test_schema_extract(self):
        # float
        self._run_schema_extract_test(6.4, "python_float")
        # bool
        self._run_schema_extract_test(True, "python_bool")
        # string
        self._run_schema_extract_test("some string here", "python_string")
        # bytearray
        self._run_schema_extract_test(bytearray.fromhex('f0 f1f2  '), "python_bytearray")
        # datetime.date
        self._run_schema_extract_test(datetime.date(2017, 5, 4), "python_date")
        # datetime.datetime
        some_datetime = datetime.datetime(2017, 5, 4, 10, 26, 0, 0, pytz.utc)
        self._run_schema_extract_test(some_datetime, "python_datetime")
        # datetime.time
        self._run_schema_extract_test(some_datetime.timetz(), "python_time")
        # list, tuple
        self._run_schema_extract_test([1, "blah", False], "python_list")
        self._run_schema_extract_test((1, "blah", False), "python_tuple")
        # dict
        self._run_schema_extract_test({"key1": 10, "key2": "bla"}, "python_dict")

        # Python 2 only
        if sys.version_info[0] == 2:
            # int
            self._run_schema_extract_test(10, "python2_int")
            # long
            self._run_schema_extract_test(12312321321312231231231, 'python2_long')
            # bytes
            self._run_schema_extract_test(bytes([65, 66, 67]), 'python2_bytes')
        else:
            # int
            self._run_schema_extract_test(10, "python3_int")
            # bytes
            self._run_schema_extract_test(bytes([65, 66, 67]), 'python3_bytes')
            # range
            self._run_schema_extract_test(range(1, 10), "python_range")

    def test_schema_extract_invalid_type(self):
        try:
            PythonUtil.extract_schema(np.array([10, 11, 12, 12], dtype=np.dtype('int32')))
            self.fail("Expected exception was not thrown")
        except TypeError as te:
            self.assertTrue(str(te).startswith(cst.ERR_PYTHON_DATA_NOT_JSON_SERIALIZABLE.rstrip("{}")))
        except Exception as ex:
            self.fail("Caught unexpected exception: {}".format(ex))

    def test_schema_save_load(self):
        schema_filepath = 'saveload.schema'
        try:
            self.assertFalse(os.path.exists(schema_filepath), "Generated schema file was found prior to test run")

            some_bytearray = bytearray.fromhex('f0 f1f2  ')
            some_dict = {"key1": 1, "key2": [1, 2, 3], "key3": False}
            some_date = datetime.datetime(2017, 5, 4, 10, 26, 0, 0, pytz.utc)

            # Extract & persist service schema to disk
            input_spec = {
                "in1": SampleDefinition(DataTypes.STANDARD, some_bytearray),
                "in2": SampleDefinition(DataTypes.STANDARD, some_dict)
            }
            output_spec = {"out": SampleDefinition(DataTypes.STANDARD, some_date)}
            save_service_schema(schema_filepath, input_spec, output_spec)
            self.assertTrue(os.path.exists(schema_filepath), "Expected generated schema file was not found")

            # Load & validate service schema from disk
            service_schema = load_service_schema(schema_filepath)
            self.assertIsNotNone(service_schema.input, "Service schema must have an input defined")
            self.assertTrue("in1" in service_schema.input, "Expected input schema missing")
            self._validate_extracted_python_schema(some_bytearray, service_schema.input["in1"],
                                                   self.expected_swagger_set['python_bytearray'])
            self.assertTrue("in2" in service_schema.input, "Expected input schema missing")
            self._validate_extracted_python_schema(some_dict, service_schema.input["in2"],
                                                   self.expected_swagger_set['python_other_dict'])

            self.assertIsNotNone(service_schema.output, "Service schema must have an output defined")
            self.assertTrue("out" in service_schema.output, "Expected output schema missing")
            self._validate_extracted_python_schema(some_date, service_schema.output["out"],
                                                   self.expected_swagger_set['python_datetime'])
        finally:
            SchemaUnitTests._delete_test_schema_file(schema_filepath)

    def test_input_parsing(self):
        input_json_string = \
            '{"in1": true, "in2": "2017-05-04 10:26:00.000000 +0000", "in3": {"k3": false, "k2": [1, 2], "k1": 1}}'
        input_json = json.loads(input_json_string)
        input_schema = {
            'in1': PythonUtil.extract_schema(False),
            'in2': PythonUtil.extract_schema(datetime.datetime.utcnow()),
            'in3': PythonUtil.extract_schema(dict())
        }

        for input_name in input_schema:
            self._run_input_parsing_test(input_json[input_name], input_schema[input_name])

    def _run_schema_extract_test(self, python_data, swagger_key):
        expected_swagger = self.expected_swagger_set[swagger_key]
        schema = PythonUtil.extract_schema(python_data)
        self._validate_extracted_python_schema(python_data, schema, expected_swagger)

    def _run_input_parsing_test(self, json_input, schema):
        input_data = PythonUtil.get_input_object(json_input, schema)

        # Validate the result
        self.assertIsNotNone(input_data, "Parsed input must have a value here")
        self.assertTrue(type(input_data) is schema.internal.data_type,
                        "Parsed input must be of same type {0} as described by schema. Got {1}".format(
                            type(input_data), schema.internal.data_type
                        ))

    def test_input_from_json_file_parsing(self):
        list_schema = Schema(DataTypes.STANDARD, PythonSchema(list), {}, self.test_schema_version)
        expected_result = [{'age': 24, 'name': 'John'}, {'age': 24, 'name': 'Tim'}, {'age': 21, 'name': 'Sally'}, {'age': 26, 'name': 'Jill'}]

        result = PythonUtil.get_input_object_from_file(self.sample_json, list_schema)

        self.assertEqual(result, expected_result)

    def test_input_from_csv_file_parsing(self):
        list_schema = Schema(DataTypes.STANDARD, PythonSchema(list), {}, self.test_schema_version)
        expected_result = [['name', 'age'], ['John', '24'], ['Tim', '24'], ['Sally', '21'], ['Jill', '26']]

        result = PythonUtil.get_input_object_from_file(self.sample_csv, list_schema)

        self.assertEqual(result, expected_result)

    def test_input_from_tsv_file_parsing(self):
        list_schema = Schema(DataTypes.STANDARD, PythonSchema(list), {}, self.test_schema_version)
        expected_result = [['name', 'age'], ['John', '24'], ['Tim', '24'], ['Sally', '21'], ['Jill', '26']]

        result = PythonUtil.get_input_object_from_file(self.sample_tsv, list_schema)

        self.assertEqual(result, expected_result)

    def test_input_from_arff_file_parsing(self):
        list_schema = Schema(DataTypes.STANDARD, PythonSchema(list), {}, self.test_schema_version)
        expected_result = [['John', 24], ['Tim', 24], ['Sally', 21], ['Jill', 26]]

        result = PythonUtil.get_input_object_from_file(self.sample_arff, list_schema)

        self.assertEqual(result, expected_result)

    def test_input_from_parquet_file_parsing(self):
        list_schema = Schema(DataTypes.STANDARD, PythonSchema(list), {}, self.test_schema_version)

        with self.assertRaises(ValueError):
            PythonUtil.get_input_object_from_file(self.sample_parquet, list_schema)

    def _validate_extracted_python_schema(self, python_data, extracted_schema, expected_swagger):
        self._validate_extracted_schema_is_specified(extracted_schema)

        self.assertIsNotNone(extracted_schema.internal, "Extracted schema does not have the internal part defined")
        self.assertTrue(isinstance(extracted_schema.internal, PythonSchema),
                        "Internal schema must be of type PythonSchema")
        internal_type = extracted_schema.internal.data_type
        self.assertIsNotNone(internal_type, "Internal schema must have a data type defined")
        self.assertIs(type(python_data), internal_type, "Expected internal schema of type {0}, instead got {1}".format(
            type(python_data), internal_type))
        self._validate_swagger_schemas(expected_swagger, extracted_schema.swagger)
