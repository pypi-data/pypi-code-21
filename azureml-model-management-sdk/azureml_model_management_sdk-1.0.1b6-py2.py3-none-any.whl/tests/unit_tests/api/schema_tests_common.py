# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os.path
import json
import os
import numpy as np
from tests.unit_tests.api.ut_common import UnitTestBase


class SchemaUnitTests(UnitTestBase):
    test_schema_version = "1.0.1"

    sample_json = os.path.join(UnitTestBase.tests_folder, 'resources', 'sample_json.json')
    sample_csv = os.path.join(UnitTestBase.tests_folder, 'resources', 'sample_csv.csv')
    sample_tsv = os.path.join(UnitTestBase.tests_folder, 'resources', 'sample_tsv.tsv')
    sample_arff = os.path.join(UnitTestBase.tests_folder, 'resources', 'sample_arff.arff')
    sample_parquet = os.path.join(UnitTestBase.tests_folder, 'resources', 'sample_parquet.parquet')

    def setUp(self):
        expected_swagger_file = os.path.join(UnitTestBase.tests_folder, 'resources/test_swagger_data.json')
        with open(expected_swagger_file, 'r') as f:
            self.expected_swagger_set = json.load(f)

    def _validate_extracted_schema_is_specified(self, schema):
        self.assertIsNotNone(schema.internal, "Expected internal schema is None")
        self.assertIsNotNone(schema.swagger, "Expected swagger schema is None")

    def _validate_swagger_schemas(self, expected_schema, generated_schema):

        # Compare the example sections separately due to issues with Python's float representation
        self.assertTrue('example' in generated_schema,
                        "Generated swagger schema must contain example section")
        generated_example = generated_schema['example']
        fixed_floats_example = self._make_floats_great_strings_again(generated_example)
        expected_example = expected_schema['example']
        if isinstance(expected_example, list) or isinstance(expected_example, dict):
            self.compareCollection(expected_example, fixed_floats_example)
        else:
            self.assertEqual(fixed_floats_example, expected_example)

        # Now compare the swagger for the data contract
        generated_schema['example'] = None
        expected_schema['example'] = None
        self.assertDictEqual(expected_schema, generated_schema)

    def _validate_numpy_extracted_schema(self, array, array_schema, expected_swagger):
        self._validate_extracted_schema_is_specified(array_schema)

        internal_schema = array_schema.internal
        self.assertEqual(internal_schema.data_type, array.dtype,
                         "Internal schema has different dtype than expected: {0}".format(internal_schema.data_type))
        self.assertEqual(internal_schema.shape, array.shape,
                         "Internal schema has different shape than expected: {0}".format(internal_schema.shape))

        self._validate_swagger_schemas(expected_swagger, array_schema.swagger)

    def _validate_pandas_extracted_schema(self, df, schema, expected_swagger):
        self._validate_extracted_schema_is_specified(schema)

        schema_columns = schema.internal.column_names
        expected_columns = df.columns.values.tolist()
        self.assertIsNotNone(schema_columns, "Internal schema must have a 'column_names' property")
        self.assertSequenceEqual(schema_columns, expected_columns,
                                 "Internal schema has different columns than expected: {0}".format(schema_columns))
        schema_dtypes = schema.internal.column_types
        expected_dtypes = df.dtypes.tolist()
        self.assertIsNotNone(schema_dtypes, "Internal schema must have a 'column_names' property")
        self.assertSequenceEqual(schema_dtypes, expected_dtypes,
                                 "Internal schema has different dtypes than expected: {0}".format(schema_dtypes))
        schema_shape = schema.internal.shape
        self.assertIsNotNone(schema_shape, "Internal schema must have a 'shape' property")
        self.assertEqual(schema_shape, df.shape,
                         "Internal schema has different shape than expected: {0}".format(schema_shape))

        self._validate_swagger_schemas(expected_swagger, schema.swagger)

    def _validate_spark_extracted_schema(self, data_frame, schema, expected_swagger):
        self._validate_extracted_schema_is_specified(schema)
        self.assertEqual(schema.internal.schema, data_frame.schema,
                         "Extracted internal schema {0} does not match expected one {1}".format(
                             schema.internal.schema, data_frame.schema))
        self._validate_swagger_schemas(expected_swagger, schema.swagger)

    @staticmethod
    def _delete_test_schema_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def _make_floats_great_strings_again(self, generated):
        if type(generated) is list:
            for i in range(len(generated)):
                generated[i] = self._make_floats_great_strings_again(generated[i])
        elif type(generated) is dict:
            for key in generated:
                generated[key] = self._make_floats_great_strings_again(generated[key])
        elif type(generated) is float or \
                type(generated) is np.float32 or \
                type(generated) is np.float16:
            generated = str(round(generated, 3))
        return generated
