# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
import os
import copy
import sys
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from pyspark.sql import SQLContext
from azureml.api.schema.pythonUtil import PythonSchema
from azureml.api.schema.schemaUtil import *
from azureml.api.schema.schemaUtil import _generate_service_schema, _PUP_VERSION, _schema_version_error_format
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.schema.sparkUtil import SparkUtil
from azureml.api.schema.schemaObjects import InternalSchema
from azureml.common.utils import get_sdk_version
from tests.unit_tests.api.schema_tests_common import SchemaUnitTests


class SchemaUtilTest(SchemaUnitTests):

    _int_array = np.array(range(10), dtype=np.int32)
    _birthsPerName = list(zip(['Bob', 'Jessica', 'Mary', 'John', 'Mel'], [968, 155, 77, 578, 973]))
    _births_df = pd.DataFrame(data=_birthsPerName, columns=['Names', 'Births'])
    _sqlContext = SQLContext(SparkUtil.spark_session.sparkContext)
    _contacts_df = _sqlContext.read.json(os.path.join(SchemaUnitTests.tests_folder, 'resources/contact_data.json'))

    user_input_schema = {
        "ints": SampleDefinition(DataTypes.NUMPY, _int_array),
        "contacts": SampleDefinition(DataTypes.SPARK, _contacts_df),
        "number": SampleDefinition(DataTypes.STANDARD, 10)}
    output_schema = {"births": SampleDefinition(DataTypes.PANDAS, _births_df)}

    def setUp(self):
        expected_swagger_file = os.path.join(SchemaUnitTests.tests_folder, 'resources/test_swagger_data.json')
        with open(expected_swagger_file, 'r') as f:
            self.expected_swagger_set = json.load(f)

        schema_file_name = 'resources/schema-py3.json'
        if sys.version_info[0] == 2:
            schema_file_name = 'resources/schema-py2.json'
        self.test_schema_path = os.path.join(SchemaUnitTests.tests_folder, schema_file_name)

    def test_save_service_schema(self):
        schema_file_path = os.path.join(SchemaUtilTest.tests_folder, "save_test.json")
        try:
            save_service_schema(schema_file_path, SchemaUtilTest.user_input_schema, SchemaUtilTest.output_schema)
            self.assertTrue(os.path.exists(schema_file_path),
                            "Expected schema file was not saved at {}".format(schema_file_path))

            # make some structural validation of the saved schema
            with open(schema_file_path, 'r') as json_file:
                schema = json.load(json_file)
            self.assertTrue("input" in schema, "Schema expected to contain an input definition")
            self.assertTrue("output" in schema, "Schema expected to contain an output definition")
            self._validate_schema_structure(schema["input"], SchemaUtilTest.user_input_schema.keys(), "input")
            self._validate_schema_structure(schema["output"], SchemaUtilTest.output_schema.keys(), "output")
        finally:
            SchemaUnitTests._delete_test_schema_file(schema_file_path)

    def test_load_service_schema_happy_path(self):
        schema_file_path = os.path.join(SchemaUtilTest.tests_folder, "save_test.json")
        try:
            save_service_schema(schema_file_path, SchemaUtilTest.user_input_schema, SchemaUtilTest.output_schema)
            service_schema = load_service_schema(schema_file_path)

            # Validate the input schema
            self.assertIsNotNone(service_schema.input, "Input schema instance cannot be null")
            expected_inputs_count = len(SchemaUtilTest.user_input_schema)
            actual_inputs_count = len(service_schema.input)
            self.assertEqual(expected_inputs_count, actual_inputs_count,
                             "Loaded inputs schema items count {0} != expected count of {1}".format(
                                 expected_inputs_count, actual_inputs_count))
            for input_name in SchemaUtilTest.user_input_schema:
                self.assertTrue(input_name in service_schema.input,
                                "Missing input {} from loaded schema".format(input_name))
                self.assertEqual(service_schema.input[input_name].version, get_sdk_version())

            self._validate_numpy_extracted_schema(SchemaUtilTest._int_array, service_schema.input['ints'],
                                                  self.expected_swagger_set['int_array'])
            self._validate_spark_extracted_schema(SchemaUtilTest._contacts_df, service_schema.input['contacts'],
                                                  self.expected_swagger_set['spark_contacts_df'])
            self.assertEqual(service_schema.input['number'].internal.data_type, int,
                             "Unexpected schema for 'number' input: {}".format(service_schema.input['number']))

            # Validate the output schema
            self.assertIsNotNone(service_schema.output, "Input schema instance cannot be null")
            expected_outputs_count = len(SchemaUtilTest.output_schema)
            actual_outputs_count = len(service_schema.output)
            self.assertEqual(expected_outputs_count, actual_outputs_count,
                             "Loaded outputs schema items count {0} != expected count of {1}".format(
                                 expected_outputs_count, actual_outputs_count))
            for output_name in SchemaUtilTest.output_schema:
                self.assertTrue(output_name in service_schema.output,
                                "Missing output {} from loaded schema".format(output_name))
                self.assertEqual(service_schema.output[output_name].version, get_sdk_version())

            self._validate_pandas_extracted_schema(SchemaUtilTest._births_df, service_schema.output['births'],
                                                  self.expected_swagger_set['pandas_births'])
        finally:
            SchemaUnitTests._delete_test_schema_file(schema_file_path)

    def test_load_schema_with_no_internal_or_swagger_fails(self):
        with open(self.test_schema_path, 'r') as jsonfile:
            loaded_service_schema = json.load(jsonfile)

        schema1 = copy.deepcopy(loaded_service_schema)
        schema1["input"]["a"].pop('internal', None)
        copy_path = os.path.join(SchemaUnitTests.tests_folder, 'no_internal.json')
        SchemaUtilTest.save_json(schema1, copy_path)
        self._validate_load_error_messages(copy_path, "Invalid schema, internal schema not found for item a")

        schema2 = copy.deepcopy(loaded_service_schema)
        schema2["input"]["a"].pop('swagger', None)
        copy_path = os.path.join(SchemaUnitTests.tests_folder, 'no_swagger.json')
        SchemaUtilTest.save_json(schema2, copy_path)
        self._validate_load_error_messages(copy_path, "Invalid schema, swagger not found for item a")

    def test_load_schema_with_invalid_type_fails(self):
        with open(self.test_schema_path, 'r') as jsonfile:
            loaded_service_schema = json.load(jsonfile)
    
        schema1 = copy.deepcopy(loaded_service_schema)
        schema1["input"]["b"]["type"] = -1
        copy_path = os.path.join(SchemaUnitTests.tests_folder, 'non_type.json')
        SchemaUtilTest.save_json(schema1, copy_path)
        self._validate_load_error_messages(
            copy_path, "Invalid schema type found: -1. Only types defined in dataTypes.DataTypes are valid")

    def test_parse_input_json(self):
        service_schema = load_service_schema(self.test_schema_path)
        input_args = {"a": [i for i in range(10)], "b": 10}
        input_json = json.dumps(input_args)
        inputs = parse_service_input(input_json, service_schema.input)
        if "a" not in inputs or "b" not in inputs:
            self.fail("Parsing Input Json Failed: Not all input arguments were found")
        self.assertEqual(type(inputs["b"]), int)
        self.assertEqual(type(inputs["a"]), np.ndarray)

    def test_parse_input_json_bad_inputs(self):
        input_json = json.dumps({"a": 10, "b": 10})
        sdk_version = get_sdk_version()
        service_schema = load_service_schema(self.test_schema_path)
        self._validate_input_parsing_error_messages(input_json,
                                                    service_schema.input,
                                                    "Failed to deserialize a to type provided by input schema, "
                                                    "Error Details: Invalid input format: expected an array of items.. "
                                                    "Installed SDK version: {}. Loaded schema version: 0.1.0a11 or "
                                                    "earlier".format(sdk_version))
        input_json = json.dumps([1, 2])
        self._validate_input_parsing_error_messages(input_json,
                                                    service_schema.input,
                                                    "Input request does not respect the schema defined by the service's swagger specification.")
        int_input_json = json.dumps({"a": 10})
        string_schema = {"a": Schema(DataTypes.STANDARD, PythonSchema(str), {}, _PUP_VERSION)}
        expected_error = "Failed to deserialize a to type provided by input schema, Error Details: Invalid input data " \
                         "type to parse. Expected: {} but got {}. Installed SDK version: {}. Loaded schema " \
                         "version: 0.1.0a11 or earlier".format(str(str), str(int), sdk_version)
        self._validate_input_parsing_error_messages(int_input_json, string_schema, expected_error)

    def test_parse_input_json_mismatch_arguments(self):
        input_json = json.dumps({"g": 10})
        service_schema = load_service_schema(self.test_schema_path)
        try:
            parse_service_input(input_json, service_schema.input)
        except BadRequestException as be:
            if "Argument mismatch: Unexpected argument g" not in be.message:
                self.fail("Expected error message not found, instead got {0}".format(be.message))
        except Exception as e:
            self.fail()

    @patch('azureml.api.schema.numpyUtil.NumpyUtil.get_input_object_from_file')
    @patch('azureml.api.schema.sparkUtil.SparkUtil.get_input_object_from_file')
    @patch('azureml.api.schema.pandasUtil.PandasUtil.get_input_object_from_file')
    @patch('azureml.api.schema.pythonUtil.PythonUtil.get_input_object_from_file')
    def test_parse_batch_input(self, python_get_input_mock, pandas_get_input_mock, spark_get_input_mock, numpy_get_input_mock):
        mock_input_file = 'path_to_file'
        mock_numpy_schema = Schema(DataTypes.NUMPY, InternalSchema(), {}, self.test_schema_version)
        mock_spark_schema = Schema(DataTypes.SPARK, InternalSchema(), {}, self.test_schema_version)
        mock_pandas_schema = Schema(DataTypes.PANDAS, InternalSchema(), {}, self.test_schema_version)
        mock_python_schema = Schema(DataTypes.STANDARD, InternalSchema(), {}, self.test_schema_version)

        mock_numpy_return = 'mock_numpy_return'
        mock_spark_return = 'mock_spark_return'
        mock_pandas_return = 'mock_pandas_return'
        mock_python_return = 'mock_python_return'

        numpy_get_input_mock.return_value = mock_numpy_return
        spark_get_input_mock.return_value = mock_spark_return
        pandas_get_input_mock.return_value = mock_pandas_return
        python_get_input_mock.return_value = mock_python_return

        numpy_result = parse_batch_input(mock_input_file, mock_numpy_schema, True)
        spark_result = parse_batch_input(mock_input_file, mock_spark_schema, True)
        pandas_result = parse_batch_input(mock_input_file, mock_pandas_schema, False)
        python_result = parse_batch_input(mock_input_file, mock_python_schema, False)

        numpy_get_input_mock.assert_called_once_with(mock_input_file, mock_numpy_schema, True)
        spark_get_input_mock.assert_called_once_with(mock_input_file, mock_spark_schema, True)
        pandas_get_input_mock.assert_called_once_with(mock_input_file, mock_pandas_schema)
        python_get_input_mock.assert_called_once_with(mock_input_file, mock_python_schema)

        self.assertEqual(numpy_result, mock_numpy_return)
        self.assertEqual(spark_result, mock_spark_return)
        self.assertEqual(pandas_result, mock_pandas_return)
        self.assertEqual(python_result, mock_python_return)

    def test_load_schema_with_no_version(self):
        a11_schema_path = os.path.join(SchemaUnitTests.tests_folder, "resources/service_schema_0.1.0a11.json")
        a6_bad_schema_path = os.path.join(SchemaUnitTests.tests_folder,
                                          "resources/service_schema_0.1.0a6-with_added_version.json")
        try:
            # try to load a pre 1.0 SDK schema that would not contain version and check that we default correctly
            schema = load_service_schema(a11_schema_path)
            for name in schema.input:
                self.assertTrue(hasattr(schema.input[name], "version"))
                self.assertEqual(schema.input[name].version, _PUP_VERSION)

            # Now try to load a schema that explicitly states a version with a different major than the current SDK
            # and expect error to be thrown
            load_service_schema(a6_bad_schema_path)
            self.fail("Expected exception not thrown")
        except ValueError as ve:
            expected_msg = _schema_version_error_format.format("0.1.a6", get_sdk_version())
            self.assertEqual(str(ve), expected_msg)
        except:
            self.fail("Unexpected failure occurred: {}".format(sys.exc_info()[1]))

    def _validate_schema_structure(self, schema, expected_entries, schema_type):
        for entry_name in expected_entries:
            self.assertTrue(entry_name in schema, "Missing schema for {0} {1}".format(schema_type, entry_name))
            entry_schema = schema[entry_name]
            self.assertTrue("internal" in entry_schema,
                            "Missing internal schema definition for {0} {1}".format(schema_type, entry_name))
            self.assertTrue("swagger" in entry_schema,
                            "Missing swagger schema definition for {0} {1}".format(schema_type, entry_name))

    def _validate_input_parsing_error_messages(self, input_json, schema, message):
        try:
            parse_service_input(input_json, schema)
            self.fail("Expected exception not thrown")
        except BadRequestException as be:
            self.assertEqual(message, be.message)
        except:
            self.fail("Expected exception not found")

    def _validate_load_error_messages(self, file_name, message):
        try:
            load_service_schema(file_name)
            self.fail("Expected exception not thrown")
        except ValueError as be:
            self.assertEqual(message, str(be))
        except Exception as e:
            self.fail("Expected exception not thrown")
        finally:
            os.remove(file_name)

    def test_generate_service_schema_input_only(self):
        schema = _generate_service_schema(input_schema_sample=self.user_input_schema)
        self._validate_schema_structure(schema["input"], SchemaUtilTest.user_input_schema.keys(), "input")

    def test_generate_service_schema_empty(self):
        result = _generate_service_schema()
        expected_result = {}
        self.assertEqual(result, expected_result)

    def test_generate_service_schema_output_only(self):
        schema = _generate_service_schema(output_schema_sample=self.output_schema)
        self._validate_schema_structure(schema["output"], SchemaUtilTest.output_schema.keys(), "output")

    def test_generate_service_schema_io(self):
        schema = _generate_service_schema(input_schema_sample=self.user_input_schema,
                                          output_schema_sample=self.output_schema)
        self._validate_schema_structure(schema["input"], SchemaUtilTest.user_input_schema.keys(), "input")
        self._validate_schema_structure(schema["output"], SchemaUtilTest.output_schema.keys(), "output")

    @staticmethod
    def save_json(obj, filename):
        with open(filename, 'w') as json_file:
            json.dump(obj, json_file)
