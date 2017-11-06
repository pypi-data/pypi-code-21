# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import json
import numpy as np
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from azureml.api.batch import batch_handler
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.schemaUtil import ServiceSchema
from tests.unit_tests.api.ut_common import UnitTestBase


def run(input_data, output_data='output.parquet', param=1):
    return


class BatchHandlerTests(UnitTestBase):
    int_array = np.array(range(10), dtype=np.int32)
    inputs = {'input_data': (SampleDefinition(DataTypes.NUMPY, int_array), False)}
    parser_formatted_inputs = ['--input-data']
    outputs = {'output_data': SampleDefinition(DataTypes.STANDARD, 'output.parquet')}
    parser_formatted_outputs = ['--output-data:output.parquet']
    parameters = {'param': SampleDefinition(DataTypes.STANDARD, 1)}
    parser_formatted_parameters = ['--param:1']
    dependencies = ['utils.py', 'model.csv']
    service_name = 'test_service_name'
    default_dict = {'output_data': 'output.parquet', 'param': 1}

    @patch('azureml.api.batch.batch_handler.schemaUtil.parse_batch_input', autospec=True)
    @patch('azureml.api.batch.batch_handler.schemaUtil.parse_service_input', autospec=True)
    def test_batch_parse_service_input(self, mock_parse_service_input, mock_parse_batch_input):
        parsed_args = {'input_data': 'input.csv', 'param': 3, 'output_data': 'output.parquet'}
        non_input_args = {'param': 3, 'output_data': 'output.parquet'}
        input_csv_df = [1, 2, 3]
        parsed_args_after_df_replace = {'input_data': input_csv_df, 'param': 3, 'output_data': 'output.parquet'}
        service_schema = ServiceSchema({'input_data': 'input_data_schema',
                                        'param': 'param_schema',
                                        'output_data': 'output_data_schema'}, None)
        aml_service_inputs = {'input_data': True}

        mock_parse_batch_input.return_value = input_csv_df
        mock_parse_service_input.return_value = non_input_args

        return_value = batch_handler._batch_parse_service_input(parsed_args, service_schema, aml_service_inputs, self.default_dict)

        mock_parse_batch_input.assert_called_once_with('input.csv', service_schema.input['input_data'], True)
        mock_parse_service_input.assert_called_once_with(json.dumps(non_input_args), service_schema.input)

        self.assertEqual(return_value, parsed_args_after_df_replace)

    @patch('azureml.api.batch.batch_handler.prepare_publish_setup', autospec=True)
    @patch('azureml.api.batch.batch_handler.generate_create_command', autospec=True)
    def test_prepare(self, mock_generate_create, mock_prepare_publish_setup):
        generate_create_command_result = 'test create command result'

        mock_prepare_publish_setup.return_value = self.default_dict
        mock_generate_create.return_value = generate_create_command_result

        batch_handler.prepare(run, self.inputs, self.outputs, self.parameters, self.dependencies, self.service_name)
        output = sys.stdout.getvalue().strip()

        mock_prepare_publish_setup.assert_called_once_with(run, self.inputs, self.outputs, self.parameters, self.dependencies)
        mock_generate_create.assert_called_once_with(self.service_name, self.inputs, self.outputs, self.parameters, self.dependencies, self.default_dict)
        self.assertEqual(output, generate_create_command_result)

    # @patch('azureml.api.batch.batch_handler.prepare_publish_setup', autospec=True)
    # @patch('azure.cli.command_modules.ml.service.batch.batch_service_create', autospec=True)
    # def test_publish(self, mock_batch_service_create, mock_prepare_publish_setup):
    #     mock_prepare_publish_setup.return_value = self.default_dict
    #
    #     batch_handler.publish(run, self.inputs, self.outputs, self.parameters, self.dependencies, 'service_name', 'service_title', True)
    #
    #     mock_prepare_publish_setup.assert_called_once_with(run, self.inputs, self.outputs, self.parameters, self.dependencies)
    #     mock_batch_service_create.assert_called_once_with(driver_file=_batch_sdk_utilities.BATCH_DRIVER_FILE,
    #                                                       service_name='service_name',
    #                                                       title='service_title',
    #                                                       verb=True,
    #                                                       inputs=self.parser_formatted_inputs,
    #                                                       outputs=self.parser_formatted_outputs,
    #                                                       parameters=self.parser_formatted_parameters,
    #                                                       dependencies=self.dependencies)


if __name__ == '__main__':
    assert not hasattr(sys.stdout, "getvalue")
    unittest.main(module=__name__, buffer=True, exit=False)
