# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import os, shutil
import numpy as np
import pandas as pd
from pyspark.sql import SQLContext

from azureml.api.realtime import services
from azureml.api.schema.schemaUtil import *
from azureml.api.schema.sparkUtil import SparkUtil
from tests.unit_tests.api.ut_common import UnitTestBase
from azureml.api.schema.schemaUtil import _schema_version_error_format


class ServicesTests(UnitTestBase):
    int_array = np.array(range(10), dtype=np.int32)
    input_types = {'a': SampleDefinition(DataTypes.NUMPY, int_array),
                   'b': SampleDefinition(DataTypes.STANDARD, 10)}
    output_types = {'output1': SampleDefinition(DataTypes.STANDARD, "Adf")}
    output_type = {"sdf": "Sdf"}

    _int_array = np.array(range(10), dtype=np.int32)
    _birthsPerName = list(
        zip(['Bob', 'Jessica', 'Mary', 'John', 'Mel'], [968, 155, 77, 578, 973]))
    _births_df = pd.DataFrame(data=_birthsPerName, columns=['Names', 'Births'])
    _sqlContext = SQLContext(SparkUtil.spark_session.sparkContext)
    _contacts_df = _sqlContext.read.json(
        os.path.join(UnitTestBase.tests_folder, 'resources/contact_data.json'))

    user_input_schema = {
        "ints": SampleDefinition(DataTypes.NUMPY, _int_array),
        "contacts": SampleDefinition(DataTypes.SPARK, _contacts_df),
        "number": SampleDefinition(DataTypes.STANDARD, 10)}
    output_schema = {"births": SampleDefinition(DataTypes.PANDAS, _births_df)}

    def test_validate_run_func_no_schema(self):
        self.validate_run_func_base(sample_run, None,
                                    expected_msg="Provided run function has arguments")

    def test_validate_run_func_no_args_no_schema(self):
        self.validate_run_func_base(sample_run_no_args, None, num_args=0, num_defaults=0)

    def test_validate_run_func_happy(self):
        self.validate_run_func_base(sample_run_2, self.user_input_schema,
                                    num_args=3, num_defaults=1)

    def test_validate_run_func_kwargs_happy(self):
        self.validate_run_func_base(sample_run, {'a': None,
                                                 'b': None},
                                    num_args=2, num_defaults=0)

    def test_validate_run_func_bad_missing_arg_in_schema(self):
        self.validate_run_func_base(sample_run, {'a': None},
                                    expected_msg='Argument mismatch: Provided run')

    def test_validate_run_func_bad_extra_arg_in_schema(self):
        self.validate_run_func_base(sample_run, {'a': None,
                                                 'b': None,
                                                 'c': None},
                                    expected_msg='Argument mismatch: Provided run')

    def validate_run_func_base(self, fn, schema, num_args=0, num_defaults=0,
                               expected_msg=None):
        try:
            args, defaults = services._validate_run_func_args(fn, schema)
            # fail if expected message is not None and we don't throw
            self.assertEqual(expected_msg, None)
            self.assertEqual(len(args), num_args)
            self.assertEqual(len(defaults), num_defaults)
        except ValueError as exc:
            if not str(exc).startswith(expected_msg):
                self.fail('Threw ValueError with incorrect message. '
                          'Expected: "{}" and got "{}"'.format(expected_msg, str(exc)))

    @patch('azureml.api.realtime.services._validate_run_func_args')
    @patch('azureml.api.realtime.services._generate_service_schema')
    def test_generate_schema_no_write(self, generate_schema_mock, validate_run_func_mock):
        expected_schema = 'an awesome schema'
        generate_schema_mock.return_value = expected_schema
        schema = services.generate_schema(sample_run)
        self.assertEqual(schema, expected_schema)
        self.assertTrue(generate_schema_mock.call_count == 1)
        self.assertTrue(validate_run_func_mock.call_count == 1)

    @patch('azureml.api.realtime.services.json.dump')
    @patch('azureml.api.realtime.services.open')
    @patch('azureml.api.realtime.services._validate_run_func_args')
    @patch('azureml.api.realtime.services._generate_service_schema')
    def test_generate_schema_with_write(self, generate_schema_mock, validate_run_func_mock, open_mock, dump_mock):
        expected_schema = 'an awesome schema'
        generate_schema_mock.return_value = expected_schema
        path = os.path.join(UnitTestBase.tests_folder, 'my/awesome/filepath')
        schema = services.generate_schema(sample_run, filepath=path)
        self.assertEqual(schema, expected_schema)
        self.assertTrue(generate_schema_mock.call_count == 1)
        self.assertTrue(validate_run_func_mock.call_count == 1)
        self.assertTrue(open_mock.call_count == 1)
        self.assertTrue(dump_mock.call_count == 1)

    def test_generate_schema_with_folder_create(self):
        path = os.path.join(self.tests_folder, "folder1/folder2/schema.json")
        self.assertFalse(os.path.exists(path))
        services.generate_schema(sample_run_2, self.user_input_schema, self.output_schema, filepath=path)
        self.assertTrue(os.path.exists(path))
        shutil.rmtree(os.path.join(self.tests_folder, "folder1"), True)

    def test_generate_main(self):
        driver_path = os.path.join(self.tests_folder, "resources/sample_driver.py")
        current_schema_path = os.path.join(self.tests_folder, "resources/service_schema.json")
        no_version_schema_path = os.path.join(self.tests_folder, "resources/service_schema_0.1.0a11.json")
        old_schema_path = os.path.join(self.tests_folder, "resources/service_schema_0.1.0a6-with_added_version.json")
        generated_main_path = "test_generated_main.py"

        # First call generate main on a schema with no version (old PUP style)
        # and validate that version check passes and file gets generated
        self._test_generate_main_happy_path(generated_main_path, driver_path, no_version_schema_path)

        # Then call generate main on a schema version compatible with the current SDK
        # and validate that version check passes and file gets generated
        self._test_generate_main_happy_path(generated_main_path, driver_path, current_schema_path)

        # Now validate schema validation error is thrown when using incompatible schema
        try:
            self._test_generate_main_happy_path(generated_main_path, driver_path, old_schema_path)
            self.fail("Expected error was not thrown")
        except ValueError as vex:
            expected_msg = _schema_version_error_format.format("0.1.a6", get_sdk_version())
            self.assertEqual(str(vex), expected_msg)
        except:
            self.fail("Unexpected failure occurred: {}".format(sys.exc_info()[1]))

    def test_generate_main_runs(self):

        driver_path = os.path.join(self.tests_folder, "resources/simple-driver.py")
        generated_main_path = "test_generated_main.py"

        self.assertFalse(os.path.exists(generated_main_path))
        services.generate_main(driver_path, '', generated_main_path)
        self.assertTrue(os.path.exists(generated_main_path))

        # Now test that the code in the generated main file actually works
        from test_generated_main import init as generated_init
        from test_generated_main import run as generated_run
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            generated_init()
        out = f.getvalue().strip()
        self.assertEqual(out, "driver init run successfully.")
        # test that the swagger was generated as a result of running init
        self.assertTrue(os.path.exists('swagger.json'))
        os.remove('swagger.json')
        f.close()

        f = io.StringIO()
        with redirect_stdout(f):
            generated_run("test")
        out = f.getvalue().strip()
        self.assertEqual(out, "driver run with body: 'test'")
        f.close()

        os.remove(generated_main_path)

    def _test_generate_main_happy_path(self, generated_main_path, driver_path, schema_path):
        self.assertFalse(os.path.exists(generated_main_path))
        services.generate_main(driver_path, schema_path, generated_main_path)
        self.assertTrue(os.path.exists(generated_main_path))

        expected_generated_main_path = os.path.join(self.tests_folder, "resources/expected_generated_main.py")
        with open(expected_generated_main_path, 'r') as f:
            expected_lines = f.readlines()
        with open(generated_main_path, 'r') as f:
            generated_lines = f.readlines()

        self.assertEqual(len(expected_lines), len(generated_lines))
        for i in range(0, len(expected_lines)):
            if "schema_file =" in expected_lines[i] or "driver_module_spec =" in expected_lines[i]:
                continue
            else:
                self.assertEqual(expected_lines[i], generated_lines[i])

        os.remove(generated_main_path)


def sample_run_2(ints, contacts, number=10):
    return ServicesTests._births_df


def sample_run(a, **b):
    print(a)
    return b


def sample_run_no_args():
    return "asdf"


def sample_run_default(a, b=[2, 3, 4]):
    print(a)
    return b


def sample_run_no_args_no_output():
    print(10)
