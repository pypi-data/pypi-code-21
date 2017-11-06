# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
try:
    from unittest import mock
    from unittest.mock import patch
except ImportError:
    import mock
    from mock import patch
import numpy as np
from azureml.api.batch import _batch_sdk_utilities
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.schema.sampleDefinition import DataTypes
from tests.unit_tests.api.ut_common import UnitTestBase


def run(input_data, output_data='output.parquet', param=1):
    return


class BatchSdkUtilitiesTests(UnitTestBase):
    int_array = np.array(range(10), dtype=np.int32)

    sample_input = (SampleDefinition(DataTypes.NUMPY, int_array))
    inputs = {'input_data': (sample_input, True)}
    schema_inputs = {'input_data': sample_input}
    service_inputs = {'input_data': True}
    outputs = {'output_data': SampleDefinition(DataTypes.STANDARD, 'output.parquet')}
    parameters = {'param': SampleDefinition(DataTypes.STANDARD, 1)}
    dependencies = ['utils.py', 'model.csv']
    schema_file = "batch_schema_test_timestamp.json"
    run_args = ['input_data', 'output_data', 'param']
    run_defaults = ('output.parquet', 1)
    default_dict = {'output_data': 'output.parquet', 'param': 1}

    expected_arg_parser_lines = ['import argparse',
                                 'parser = argparse.ArgumentParser()',
                                 'parser.add_argument("--input-data", dest="input_data")',
                                 'parser.add_argument("--output-data", dest="output_data")',
                                 'parser.add_argument("--param", dest="param", type=int)',
                                 'parsed_args = vars(parser.parse_args())']

    expected_schema_handling_lines = ['service_schema = schemaUtil.load_service_schema("{}")'.format(schema_file),
                                      'aml_service_inputs = {}'.format(service_inputs),
                                      'defaults = {}'.format(default_dict),
                                      'arguments = batch_handler._batch_parse_service_input(parsed_args, service_schema, aml_service_inputs, defaults)']

    expected_create_command = 'az ml service create batch -f service_driver.py -n service_name --in=--input-data --out=--output-data:output.parquet --param=--param:1 -d utils.py -d model.csv -d batch_schema_test_timestamp.json'

    @classmethod
    def setUpClass(cls):
        cls.run_func_args = {}
        cls.run_func_args.update(cls.schema_inputs)
        cls.run_func_args.update(cls.outputs)
        cls.run_func_args.update(cls.parameters)

        cls.expected_main = list(cls.expected_arg_parser_lines)
        cls.expected_main.extend(cls.expected_schema_handling_lines)
        cls.expected_main.append('{}(**arguments)'.format(run.__name__))

    @patch('azureml.api.schema.schemaUtil.save_service_schema', autospec=True)
    def test_generate_schema_file(self, mock_save_service_schema):
        _batch_sdk_utilities.generate_schema_file(self.inputs, self.outputs, self.parameters, self.schema_file)

        mock_save_service_schema.assert_called_once_with(self.schema_file, self.run_func_args)

    def test_add_argument_parser_to_main(self):
        result = _batch_sdk_utilities._add_argument_parser_to_main(self.inputs, self.outputs, self.parameters)

        self.compareCollection(result, self.expected_arg_parser_lines)

    def test_add_schema_handling_to_main(self):
        result = _batch_sdk_utilities._add_schema_handling_to_main(self.inputs, self.default_dict, self.schema_file)

        self.compareCollection(result, self.expected_schema_handling_lines)

    @patch('azureml.api.batch._batch_sdk_utilities._add_argument_parser_to_main', autospec=True)
    @patch('azureml.api.batch._batch_sdk_utilities._add_schema_handling_to_main', autospec=True)
    def test_generate_main(self, mock_add_schema_handling, mock_add_argument_parser):
        mock_add_schema_handling.return_value = self.expected_schema_handling_lines
        mock_add_argument_parser.return_value = self.expected_arg_parser_lines

        result_main = _batch_sdk_utilities.generate_main(run.__name__, self.inputs, self.outputs, self.parameters, self.default_dict, self.schema_file)

        self.assertEqual(result_main, self.expected_main)

    @patch('azureml.api.batch._batch_sdk_utilities.generate_main')
    def test_generate_driver_file(self, mock_generate_main):
        mock_generate_main.return_value = self.expected_main

        test_result_driver_path = os.path.join(UnitTestBase.tests_folder, 'resources/test_result_driver_file.txt')
        test_expected_driver_path = os.path.join(UnitTestBase.tests_folder, 'resources/test_expected_driver_file.txt')

        _batch_sdk_utilities.BATCH_DRIVER_FILE = test_result_driver_path

        try:
            _batch_sdk_utilities.generate_driver_file(run, self.inputs, self.outputs, self.parameters, self.default_dict, self.schema_file)

            mock_generate_main.assert_called_once_with(run.__name__, self.inputs, self.outputs, self.parameters, self.default_dict, self.schema_file)

            with open(test_result_driver_path, 'r') as test_result_driver_file, open(test_expected_driver_path, 'r') as test_expected_driver_file:
                # This line is done to avoid testing the lines that add the sdk to the path, as these will differ on
                # different computers. Once that logic is no longer needed, this will be removed
                sdk_import_lines = [next(test_result_driver_file) for x in range(3)]

                for result_line, expected_line in zip(test_result_driver_file, test_expected_driver_file):
                    self.compareCollection(result_line, expected_line)
        finally:
            if os.path.exists(test_result_driver_path):
                os.remove(test_result_driver_path)

    def test_parse_func_defaults(self):
        result = _batch_sdk_utilities.parse_func_defaults(run)
        self.compareCollection(result, self.default_dict)

    @patch('azureml.api.batch._batch_sdk_utilities.generate_schema_file', autospec=True)
    @patch('azureml.api.batch._batch_sdk_utilities.generate_driver_file', autospec=True)
    @patch('azureml.api.batch._batch_sdk_utilities.parse_func_defaults', autospec=True)
    def test_prepare_publish_setup(self, mock_parse_func_defaults, mock_generate_driver_file, mock_generate_schema_file):
        mock_parse_func_defaults.return_value = self.default_dict

        result = _batch_sdk_utilities.prepare_publish_setup(run, self.inputs, self.outputs, self.parameters, self.dependencies)

        mock_generate_schema_file.assert_called_once_with(self.inputs, self.outputs, self.parameters, mock.ANY)
        mock_generate_driver_file.assert_called_once_with(run, self.inputs, self.outputs, self.parameters, self.default_dict, mock.ANY)
        mock_parse_func_defaults.assert_called_once_with(run)

        self.compareCollection(result, self.default_dict)

    def test_generate_create_command(self):
        create_command_dependencies = list(self.dependencies)
        create_command_dependencies.append(self.schema_file)

        result_create_command = _batch_sdk_utilities.generate_create_command('service_name', self.inputs, self.outputs, self.parameters, create_command_dependencies, self.default_dict)

        self.assertEqual(self.expected_create_command, result_create_command)
