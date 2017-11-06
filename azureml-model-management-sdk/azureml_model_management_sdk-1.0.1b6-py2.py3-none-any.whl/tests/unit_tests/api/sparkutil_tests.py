# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os.path
import json
import pandas as pd
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame

from azureml.api.schema.sparkUtil import SparkUtil, SparkSchema
from azureml.api.schema.schemaObjects import Schema
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.schema.schemaUtil import save_service_schema, load_service_schema
from tests.unit_tests.api.schema_tests_common import SchemaUnitTests
from azureml.common.utils import get_sdk_version


class SparkUtilTests(SchemaUnitTests):

    test_data_schema = StructType([
        StructField('string', StringType(), True),
        StructField('array', ArrayType(StructType([
            StructField('f1', LongType(), True),
            StructField('f2', BooleanType(), True),
            StructField('f3', StringType(), True)]), False)),
        StructField('map', MapType(StringType(), FloatType(), False), True)])

    supported_types_schema = StructType([
        StructField('aString', StringType(), False),
        StructField('aByte', ByteType(), False),
        StructField('aShort', ShortType(), False),
        StructField('anInt', IntegerType(), False),
        StructField('aLong', LongType(), False),
        StructField('aDecimal', DecimalType(10, 3), False),
        StructField('aFloat', FloatType(), False),
        StructField('aDouble', DoubleType(), False),
        StructField('aBool', BooleanType(), False),
        StructField('aDate', DateType(), False),
        StructField('aTimestamp', TimestampType(), False),
        StructField('anArray', ArrayType(IntegerType(), False)),
        StructField('aMap', MapType(StringType(), DateType(), False), True),
        StructField('aBinary', BinaryType(), False)
    ])

    batch_expected_data = list(zip(['John', 'Tim', 'Sally', 'Jill'], [24, 24, 21, 26]))
    batch_expected_df = SparkUtil.spark_session.createDataFrame(pd.DataFrame(data=batch_expected_data, columns=['name', 'age']))

    def setUp(self):
        super(SparkUtilTests, self).setUp()
        self.sqlContext = SQLContext(SparkUtil.spark_session.sparkContext)
        contact_df_file = os.path.join(SchemaUnitTests.tests_folder, 'resources/contact_data.json')
        self.contacts_df = self.sqlContext.read.json(contact_df_file)
        test_data_df_file = os.path.join(SchemaUnitTests.tests_folder, 'resources/test_data.json')
        self.test_df = self.sqlContext.read.json(test_data_df_file, self.test_data_schema)

    def test_schema_extract(self):
        # Test against a contacts data frame
        self._run_schema_extract_test(self.contacts_df, 'spark_contacts_df')
        # Test against a DataFrame with more diverse fields
        self._run_schema_extract_test(self.test_df, 'spark_test_df')

    def test_schema_save_load(self):
        schema_filepath = 'sparksaveload.schema'
        try:
            self.assertFalse(os.path.exists(schema_filepath), "Generated schema file was found prior to test run")

            # Extract & persist the service's schema on disk
            input_spec = {"contacts": SampleDefinition(DataTypes.SPARK, self.contacts_df)}
            output_spec = {"out": SampleDefinition(DataTypes.SPARK, self.test_df)}
            save_service_schema(file_path=schema_filepath, input_schema_sample=input_spec,
                                output_schema_sample=output_spec)
            self.assertTrue(os.path.exists(schema_filepath), "Expected generated schema file was not found")

            # Load & validate service schema from disk
            service_schema = load_service_schema(schema_filepath)
            self.assertIsNotNone(service_schema.input, "Service schema must have an input defined")
            self.assertTrue('contacts' in service_schema.input,
                            "Loaded output schema does not contain expected contacts df schema")
            self._validate_spark_extracted_schema(self.contacts_df, service_schema.input["contacts"],
                                                  self.expected_swagger_set['spark_contacts_df'])
            self.assertIsNotNone(service_schema.output, "Service schema must have an output defined")
            self.assertTrue('out' in service_schema.output,
                            "Loaded output schema does not contain expected tests df schema")
            self._validate_spark_extracted_schema(self.test_df, service_schema.output["out"],
                                                  self.expected_swagger_set['spark_test_df'])
        finally:
            SchemaUnitTests._delete_test_schema_file(schema_filepath)

    def test_input_parsing(self):
        input_json = '['\
                       '{"string" : "test1", "map": {"AA": 5.3, "BB": -343.32}, "array": [{"f1": 121, "f2": false, "f3": "yada"}]},' \
                       '{"string" : "test2", "map": {"AA": 2.42, "BB": -0.25, "CC": 22.0}, "array": [{"f1": 10, "f2": true, "f3": "blah"}]},' \
                       '{"string" : "test3", "map": {"AA": 10.0, "BB": 99.12, "FF": 14.39}, "array": [{"f1": 3, "f2": false, "f3": "more blah"}]},' \
                       '{"string" : "test4", "map": {"AA": 1.3}, "array": [{"f1": 121, "f2": false, "f3": "yada"}, {"f1": 10, "f2": true, "f3": "blah"}]}' \
                     ']'
        schema = Schema(DataTypes.SPARK, SparkSchema(self.test_df.schema), {}, get_sdk_version())
        self._run_input_parsing_test(json.loads(input_json), schema, 4)

        input_json = '['\
                       '{"fname": "Michael", "lname": "Brown", "age": 58, "address": { "street": "112 Main Ave", "city": "Redmond", "state": "WA" }, "phone": "425 123 4567"},' \
                       '{"fname": "Mary", "lname": "Smith", "age": 45, "address": { "street": "34 Blue St.", "city": "Portland", "state": "OR" }, "phone": "425 111 2222"}' \
                     ']'
        schema = Schema(DataTypes.SPARK, SparkSchema(self.contacts_df.schema), {}, get_sdk_version())
        self._run_input_parsing_test(json.loads(input_json), schema, 2)

    def test_all_types_input_parsing(self):
        # Read the sample data frame from file
        all_types_data_file = os.path.join(SchemaUnitTests.tests_folder, 'resources/spark_all_types_data.json')
        sample_data = self.sqlContext.read.format("json").schema(self.supported_types_schema).load(all_types_data_file)

        # generate the schema for this data frame and validate is as expected
        data_schema = self._run_schema_extract_test(sample_data, 'spark_all_types_df')

        # parse a json input data based on this schema
        input_json = '['\
                     '  {' \
                     '    "aString": "string_val_1",'\
                     '    "aByte": 7,' \
                     '    "aShort": 300, ' \
                     '    "anInt": -80000, ' \
                     '    "aLong": 3424234234232323, ' \
                     '    "aDecimal": -10.532, ' \
                     '    "aFloat": 11.32, ' \
                     '    "aDouble": 1.27,' \
                     '    "aBool": false,' \
                     '    "aDate": "2017-11-10",' \
                     '    "aTimestamp": "2011-10-02T12:30:00",' \
                     '    "anArray": [10, 11],' \
                     '    "aMap": {"key1": "2017-03-20", "key2": "2017-05-12"},' \
                     '    "aBinary": "xJbjB54thQ6kiPAhdoF+FysJSDyrBpeX4AyPbHLrPW80j2zbW6NoChQrAnS1oYJ+bUBP1xFZH7TeHzLy2AGHbGEbQxLgQTDDnIR8LkWSqiBpWRSeN+0+es4HzOM8OZmpF9xmSqA="' \
                     '  }' \
                     ']'
        json_data = json.loads(input_json)
        self._run_input_parsing_test(json_data, data_schema, 1)

    def test_input_from_json_file_parsing(self):
        self._run_input_from_file_test(self.sample_json)

    def test_input_from_csv_file_parsing(self):
        self._run_input_from_file_test(self.sample_csv)

    def test_input_from_tsv_file_parsing(self):
        self._run_input_from_file_test(self.sample_tsv)

    def test_input_from_arff_file_parsing(self):
        # Generate the input schema
        input_schema = SparkUtil.extract_schema(self.batch_expected_df)

        with self.assertRaises(ValueError):
            SparkUtil.get_input_object_from_file(self.sample_arff, input_schema, True)

    def test_input_from_parquet_file_parsing(self):
        self._run_input_from_file_test(self.sample_parquet)

    def _run_schema_extract_test(self, df, expected_swagger_key):
        schema = SparkUtil.extract_schema(df)
        expected_swagger = self.expected_swagger_set[expected_swagger_key]
        self._validate_spark_extracted_schema(df, schema, expected_swagger)
        return schema

    def _run_input_parsing_test(self, input_json_string, input_schema, expected_rows_count):
        input_df = SparkUtil.get_input_object(input_json_string, input_schema)

        self.assertIsNotNone(input_df, "Parsed input must have a value here")
        self.assertTrue(isinstance(input_df, DataFrame), "Parsed input must be a Spark data frame.")
        self._check_SparkSchema_Equal(input_schema.internal.schema, input_df.schema)
        rows_count = input_df.count()
        self.assertEqual(rows_count, expected_rows_count,
                         "Parsed input row count of {0} is different than expected {1}".format(
                             rows_count, expected_rows_count))

    def _run_input_from_file_test(self, input_file):
        # Generate the input schema
        input_schema = SparkUtil.extract_schema(self.batch_expected_df)

        parsed_input = SparkUtil.get_input_object_from_file(input_file, input_schema, True)

        self.assertIsNotNone(parsed_input, "Parsed input must have a value here")
        self.assertTrue(isinstance(parsed_input, DataFrame), "Parsed input must be a Spark data frame.")
        self._check_SparkSchema_Equal(input_schema.internal.schema, parsed_input.schema)
        expected_rows_count = 4
        rows_count = parsed_input.count()
        self.assertEqual(rows_count, expected_rows_count, "Parsed input row count of {0} is different than expected {1}".format(rows_count, expected_rows_count))

        # Disabling this for now since its failing transiently
        #self.assertEqual(parsed_input.subtract(self.batch_expected_df).count(), 0, "Parsed input\n{0}\n is different than expected\n{1}".format(parsed_input.show(), self.batch_expected_df.show()))

    def _check_SparkSchema_Equal(self, reference_schema, data_schema):
        if type(reference_schema) != type(data_schema):
            self.fail("Spark schema type mismatch: {} vs {}".format(reference_schema, data_schema))

        if type(reference_schema) is StructType:
            for col in reference_schema.names:
                if col not in data_schema.names:
                    self.fail("Spark schema type mismatch: {} does not contain expected column {} as in {}".format(data_schema, col, reference_schema))
                self._check_SparkSchema_Equal(reference_schema[col].dataType, data_schema[col].dataType)
        else:
            self.assertEqual(reference_schema, data_schema, "Spark schema mismatch: {} vs {}".format(reference_schema, data_schema))
