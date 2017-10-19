# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import pytz
import os.path
import json
import sys
import datetime as dt
from azureml.api.schema.pandasUtil import PandasUtil
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.schema.schemaUtil import save_service_schema, load_service_schema
from tests.unit_tests.api.schema_tests_common import SchemaUnitTests


class PandasUtilTests(SchemaUnitTests):
    _birthsPerName = list(zip(['Bob', 'Jessica', 'Mary', 'John', 'Mel'], [968, 155, 77, 578, 973]))
    births_df = pd.DataFrame(data=_birthsPerName, columns=['Names', 'Births'])
    test_df = pd.DataFrame(data=[[1, 3.3, "bla"], [2, -4.6, "blah"]], columns=['Idx', 'aFloat', 'aString'])

    batch_expected_data = list(zip(['John', 'Tim', 'Sally', 'Jill'], [24, 24, 21, 26]))
    batch_expected_df = pd.DataFrame(data=batch_expected_data, columns=['name', 'age'])
    batch_expected_schema = PandasUtil.extract_schema(batch_expected_df)

    def test_schema_extract(self):
        expected_swagger = self.expected_swagger_set['pandas_births']
        schema = PandasUtil.extract_schema(self.births_df)
        self._validate_pandas_extracted_schema(self.births_df, schema, expected_swagger)

    def test_schema_save_load(self):
        schema_filepath = 'pandas_saveload.schema'
        try:
            self.assertFalse(os.path.exists(schema_filepath), "Generated schema file was found prior to test run")

            # Extract & persist the service schema to disk
            input_spec = {"births": SampleDefinition(DataTypes.PANDAS, self.births_df)}
            output_spec = {"out": SampleDefinition(DataTypes.PANDAS, self.test_df)}
            save_service_schema(file_path=schema_filepath, input_schema_sample=input_spec,
                                output_schema_sample=output_spec)
            self.assertTrue(os.path.exists(schema_filepath), "Expected generated schema file was not found")

            # Load & validate the service schema from disk
            service_schema = load_service_schema(schema_filepath)
            self.assertIsNotNone(service_schema.input, "Service schema must have an input defined")
            self.assertTrue('births' in service_schema.input,
                            "Loaded input schema does not contain expected births df schema")
            self._validate_pandas_extracted_schema(self.births_df, service_schema.input['births'],
                                                   self.expected_swagger_set['pandas_births'])
            self.assertIsNotNone(service_schema.output, "Service schema must have an output defined")
            self.assertTrue('out' in service_schema.output,
                            "Loaded output schema does not contain expected tests df schema")
            self._validate_pandas_extracted_schema(self.test_df, service_schema.output['out'],
                                                   self.expected_swagger_set['test_dataframe'])
        finally:
            SchemaUnitTests._delete_test_schema_file(schema_filepath)

    def test_input_parsing(self):
        input_json = \
            '[{"Names": "Jim", "Births": 345}, {"Names": "Andrew", "Births": 121}, {"Names": "Molly", "Births": 563}]'

        # First generate the input schema
        input_schema = PandasUtil.extract_schema(self.births_df)

        # Now parse the input json into a Pandas data frame with the same schema
        parsed_input = PandasUtil.get_input_object(json.loads(input_json), input_schema)

        # Validate the result
        self._validate_parsed_input(self.births_df, (3, 2), parsed_input)

    def test_all_input_parsing(self):

        # First generate a schema with all supported types
        sample_data = [
            ["val1", True, 100, -342342.32,  dt.datetime(2017, 8, 7, 1, 2, 3, 456, pytz.utc), pd.Timedelta('1 days 2 hours'), [[1, 2], [3, 3], [10, 11]], {"key1": "bla"}],
            ["val2", False, -121, 10.3, dt.datetime(2017, 9, 7, 10, 11, 23), pd.Timedelta('-1 days 2 min 3s'), [[1, 2], [2, 3], [3, 4]], {"key1": "bla2"}],
        ]
        sample_df = pd.DataFrame(data=sample_data,
                                 columns=['aString', 'aBool', 'anInt', 'aFloat', 'aDatetime', 'aTimedelta', 'anArray', "aMap"])
        schema = PandasUtil.extract_schema(sample_df)
        self._validate_pandas_extracted_schema(sample_df, schema, self.expected_swagger_set['pandas_all_types_df'])

        # parse an input with supported types
        input_json = '[' \
                     '  {' \
                     '    "aString": "string_val_1",' \
                     '    "aBool": false,' \
                     '    "anInt": 1002, ' \
                     '    "aFloat": 11.32, ' \
                     '    "aDatetime": "2017-09-07 21:29:11.957390",' \
                     '    "aTimedelta": "2 days 10:11:02",' \
                     '    "anArray": [[1, 1], [3, 3], [10, 10]],' \
                     '    "aMap": {"key1": "test"}' \
                     '  }' \
                     ']'
        loaded_json = json.loads(input_json)
        parsed_df = PandasUtil.get_input_object(loaded_json, schema)

        # Validate the result
        self._validate_parsed_input(sample_df, (1, 8), parsed_df)
        # ensure parsed df columns are in same order as df used to generate the schema with
        original_columns = sample_df.columns.values.tolist()
        parsed_columns = parsed_df.columns.values.tolist()
        for i in range(0, len(original_columns)):
            self.assertEqual(original_columns[i], parsed_columns[i], "Columns differ at position {}: {} != {}".format(
                i, original_columns[i], parsed_columns[i]
            ))

    def test_input_from_json_file_parsing(self):
        self._run_input_from_file_test(self.sample_json)

    def test_input_from_csv_file_parsing(self):
        self._run_input_from_file_test(self.sample_csv)

    def test_input_from_tsv_file_parsing(self):
        self._run_input_from_file_test(self.sample_tsv)

    def test_input_from_arff_file_parsing(self):
        self._run_input_from_file_test(self.sample_arff)

    def test_input_from_parquet_file_parsing(self):
        # Generate the input schema
        input_schema = PandasUtil.extract_schema(self.batch_expected_df)

        with self.assertRaises(ValueError):
            PandasUtil.get_input_object_from_file(self.sample_parquet, input_schema)

    def _validate_parsed_input(self, reference_df, expected_shape, parsed_df):
        expected_columns = reference_df.columns
        expected_dtypes = reference_df.dtypes
        self.assertIsNotNone(parsed_df, "Parsed input must have a value here")
        self.assertTrue(isinstance(parsed_df, pd.core.frame.DataFrame),
                        "Parsed input must be a pandas data frame.")
        self.assertEqual(expected_shape, parsed_df.shape,
                         "Parsed data frame shape {0} different from expected {1}".format(
                             parsed_df.shape, expected_shape))
        if sys.version_info[0] == 3:
            self.assertCountEqual(parsed_df.columns.values, expected_columns.values,
                                  "Parsed data frame columns={0} are different than expected {1}".format(
                                      parsed_df.columns, expected_columns))
            self.assertCountEqual(parsed_df.dtypes, expected_dtypes,
                                  "Parsed data frame dtypes={0} are different than expected {1}".format(
                                      parsed_df.dtypes, expected_dtypes))
        else:
            self.assertItemsEqual(parsed_df.columns.values, expected_columns.values,
                                  "Parsed data frame columns={0} are different than expected {1}".format(
                                      parsed_df.columns, expected_columns))
            self.assertItemsEqual(parsed_df.dtypes, expected_dtypes,
                                  "Parsed data frame dtypes={0} are different than expected {1}".format(
                                      parsed_df.dtypes, expected_dtypes))

    def _run_input_from_file_test(self, input_file):
        # Parse the provided file into a Pandas dataframe
        parsed_input = PandasUtil.get_input_object_from_file(input_file, self.batch_expected_schema)

        # Validate result
        expected_shape = (4,2)
        expected_columns = self.batch_expected_df.columns
        expected_dtypes = self.batch_expected_df.dtypes
        self.assertIsNotNone(parsed_input, "Parsed input must have a value here")
        self.assertTrue(isinstance(parsed_input, pd.DataFrame), "Parsed input must be a pandas data frame.")
        self.assertEqual(expected_shape, parsed_input.shape, "Parsed data frame shape {0} different from expected {1}".format(parsed_input.shape, expected_shape))

        if sys.version_info[0] == 3:
            self.assertCountEqual(parsed_input.columns.values, expected_columns.values, "Parsed data frame columns={0} are different than expected {1}".format(parsed_input.columns, expected_columns))
            self.assertCountEqual(parsed_input.dtypes, expected_dtypes, "Parsed data frame dtypes={0} are different than expected {1}".format(parsed_input.dtypes, expected_dtypes))
        else:
            self.assertItemsEqual(parsed_input.columns.values, expected_columns.values, "Parsed data frame columns={0} are different than expected {1}".format(parsed_input.columns, expected_columns))
            self.assertItemsEqual(parsed_input.dtypes, expected_dtypes, "Parsed data frame dtypes={0} are different than expected {1}".format(parsed_input.dtypes, expected_dtypes))
