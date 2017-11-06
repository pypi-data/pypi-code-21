# coding=utf-8
import logging
import random

from mali_commands.legit import BigQuerySqlHelper
from mali_commands.legit.scam import tree_to_sql_parts, parse_query
from tests.base import BaseTest

SqlHelper = BigQuerySqlHelper


class TestMetadata(BaseTest):
    def validate_sql(self, sql, params, expected_result, sql_helper_class=None):
        params = params or {}
        full_syntax = sql.format(**params)

        sql_helper_class = sql_helper_class or SqlHelper

        logging.debug('validate syntax %s with %s', full_syntax, sql_helper_class)

        actual_result = tree_to_sql_parts(parse_query(full_syntax), sql_helper_class())

        if expected_result != actual_result:
            self.assertEqual(expected_result, actual_result)

    def testSeed_only(self):
        seed = self.some_random_shit_number_int63()

        where_result = None

        self.validate_sql('seed:{seed}', dict(seed=seed), ({'seed': seed}, where_result))

    def testRange(self):
        value1 = self.some_random_shit_number_int63()
        value2 = self.some_random_shit_number_int63()
        field_name = 'field1_' + self.some_random_shit_alpha()

        where_result = '(({field_name}>={value1})AND({field_name}<={value2}))'.format(field_name=field_name, value1=value1, value2=value2)
        vars_result = None

        self.validate_sql('{field_name}:[{value1} TO {value2}]', dict(field_name=field_name, value1=value1, value2=value2), (vars_result, where_result))

    def testRange_inclusive(self):
        value1 = self.some_random_shit_number_int63()
        value2 = self.some_random_shit_number_int63()
        field_name = 'field1_' + self.some_random_shit_alpha()

        where_result = '(({field_name}>{value1})AND({field_name}<{value2}))'.format(field_name=field_name, value1=value1, value2=value2)
        vars_result = None

        self.validate_sql('{field_name}:{{{value1} TO {value2}}}', dict(field_name=field_name, value1=value1, value2=value2), (vars_result, where_result))

    def testSeed_twice(self):
        seed1 = self.some_random_shit_number_int63()
        seed2 = self.some_random_shit_number_int63()

        where_result = None

        self.validate_sql('seed:{seed1} AND seed:{seed2}', dict(seed1=seed1, seed2=seed2), ({'seed': seed2}, where_result))

    def testBuildSql_andOrOp(self):
        field_name1 = 'field1_' + self.some_random_shit_alpha()
        field_name2 = 'field2_' + self.some_random_shit_alpha()

        value1 = 'val1_' + self.some_random_shit_alpha()
        value2 = 'val2_' + self.some_random_shit_alpha()

        result_vars = None

        for op in ['AND', 'OR', 'And', 'Or', 'and', 'or']:
            result_where = '({field_name1}="{value1}"){op}({field_name2}="{value2}")'.format(
                field_name1=field_name1, field_name2=field_name2, value1=value1, value2=value2, op=op.upper())
            result_build_sql = (result_vars, result_where)

            self.validate_sql(
                '{field_name1}:{value1} {op} {field_name2}:{value2}',
                dict(field_name1=field_name1, field_name2=field_name2, value1=value1, value2=value2, op=op), result_build_sql)

    def testBuildSql_singleFieldSingleInt(self):
        value_int = self.some_random_shit_number_int63()
        field_name = 'field_' + self.some_random_shit_alpha()

        result_vars = None

        for sign in ['', '+']:
            result_where = '({field_name}={value})'.format(field_name=field_name, value=value_int)
            result_build_sql = (result_vars, result_where)

            self.validate_sql('{field_name}:{sign}{value}', dict(field_name=field_name, sign=sign, value=value_int), result_build_sql)
            self.validate_sql('{field_name}:({sign}{value})', dict(field_name=field_name, sign=sign, value=value_int), result_build_sql)

        for sign in ['-']:
            result_where = '({field_name}=-{value})'.format(field_name=field_name, value=value_int)
            result_build_sql = (result_vars, result_where)

            self.validate_sql('{field_name}:{sign}{value}', dict(field_name=field_name, sign=sign, value=value_int), result_build_sql)
            self.validate_sql('{field_name}:({sign}{value})', dict(field_name=field_name, sign=sign, value=value_int), result_build_sql)

        for op in ['=', '>', '<', '>=', '<=']:
            result_where = '({field_name}{op}{value})'.format(field_name=field_name, op=op, value=value_int)

            result_build_sql = (result_vars, result_where)

            self.validate_sql('{field_name}:{op}{value}', dict(field_name=field_name, op=op, value=value_int), result_build_sql)
            self.validate_sql('{field_name}:({op}{value})', dict(field_name=field_name, op=op, value=value_int), result_build_sql)
            self.validate_sql('{field_name}:({op}{value})', dict(field_name=field_name, op=op, value=value_int), result_build_sql)

    def testBuildSql_multiFieldInt(self):
        value_int1 = self.some_random_shit_number_int63()
        value_int2 = self.some_random_shit_number_int63()
        field_name1 = 'field1_' + self.some_random_shit_alpha()

        result_vars = None

        for sign in ['', '+']:
            result_where = '(({field_name}={value1})OR({field_name}={value2}))'.format(
                field_name=field_name1, value1=value_int1, value2=value_int2)

            result_build_sql = (result_vars, result_where)

            self.validate_sql(
                '{field_name}:({sign}{value1} {sign}{value2})',
                dict(field_name=field_name1, sign=sign, value1=value_int1, value2=value_int2), result_build_sql)

    def testBuildSql_singleFieldSingleFloat(self):
        value_float = self.some_random_shit_number_int63() / 911.0
        field_name = 'field_' + self.some_random_shit_alpha()

        result_vars = None

        for sign in ['', '+']:
            result_where = '({field_name}={value})'.format(field_name=field_name, value=value_float)
            result_build_sql = (result_vars, result_where)

            self.validate_sql('{field_name}:{sign}{value}', dict(field_name=field_name, sign=sign, value=value_float), result_build_sql)
            self.validate_sql('{field_name}:({sign}{value})', dict(field_name=field_name, sign=sign, value=value_float), result_build_sql)

        for sign in ['-']:
            result_where = '({field_name}=-{value})'.format(field_name=field_name, value=value_float)
            result_build_sql = (result_vars, result_where)

            self.validate_sql('{field_name}:{sign}{value}', dict(field_name=field_name, sign=sign, value=value_float), result_build_sql)
            self.validate_sql('{field_name}:({sign}{value})', dict(field_name=field_name, sign=sign, value=value_float), result_build_sql)

        for op in ['=', '>', '<', '>=', '<=']:
            result_where = '({field_name}{op}{value})'.format(field_name=field_name, op=op, value=value_float)

            result_build_sql = (result_vars, result_where)
            self.validate_sql('{field_name}:{op}{value}', dict(field_name=field_name, op=op, value=value_float), result_build_sql)
            self.validate_sql('{field_name}:({op}{value})', dict(field_name=field_name, op=op, value=value_float), result_build_sql)

    def testBuildSql_singleFieldSingleStringWithSpaces(self):
        value_str = '"{0}_val1 {0}_val2"'.format('val_' + self.some_random_shit_alpha())

        field_name = 'field_' + self.some_random_shit_alpha()

        result_vars = None

        result_where = '({field_name}={value})'.format(field_name=field_name, value=value_str)

        result_build_sql = (result_vars, result_where)

        self.validate_sql('{field_name}:{value}', dict(field_name=field_name, value=value_str), result_build_sql)
        self.validate_sql('{field_name}:({value})', dict(field_name=field_name, value=value_str), result_build_sql)

        self.validate_sql('{field_name}: {value}', dict(field_name=field_name, value=value_str), result_build_sql)
        self.validate_sql('{field_name}: ({value})', dict(field_name=field_name, value=value_str), result_build_sql)

    def testBuildSql_singleFieldSingleString(self):
        value_str = 'val_' + self.some_random_shit_alpha()
        field_name = 'field_' + self.some_random_shit_alpha()

        result_vars = None

        result_where = '({field_name}="{value}")'.format(field_name=field_name, value=value_str)

        result_build_sql = (result_vars, result_where)

        self.validate_sql('{field_name}:{value}', dict(field_name=field_name, value=value_str), result_build_sql)
        self.validate_sql('{field_name}:({value})', dict(field_name=field_name, value=value_str), result_build_sql)

        self.validate_sql('{field_name}: {value}', dict(field_name=field_name, value=value_str), result_build_sql)
        self.validate_sql('{field_name}: ({value})', dict(field_name=field_name, value=value_str), result_build_sql)

        self.validate_sql('{field_name}: "{value}"', dict(field_name=field_name, value=value_str), result_build_sql)
        self.validate_sql('{field_name}: ("{value}")', dict(field_name=field_name, value=value_str), result_build_sql)

        for op in ['=', '>', '<', '>=', '<=']:
            result_where = '({field_name}{op}"{value}")'.format(field_name=field_name, op=op, value=value_str)

            result_build_sql = (result_vars, result_where)
            self.validate_sql('{field_name}:{op}"{value}"', dict(field_name=field_name, op=op, value=value_str), result_build_sql)
            self.validate_sql('{field_name}:({op}"{value}")', dict(field_name=field_name, op=op, value=value_str), result_build_sql)

    def testBigQuerySample_only(self):
        sample = random.random()
        where_result = '(((FARM_FINGERPRINT(CONCAT(_sha, "$seed")) + POW(2, 63)) / POW(2, 64))>{sample:.4g})'.format(sample=1.0 - sample)
        vars_result = None

        self.validate_sql(
            'sample:{sample}',
            dict(sample=sample),
            (vars_result, where_result),
            sql_helper_class=BigQuerySqlHelper)

    def testBigQuerySample(self):
        sample = random.random()
        field_name = 'field1_' + self.some_random_shit_alpha()
        value = 'val1_' + self.some_random_shit_alpha()

        where_result = '({field_name}="{field_value}")AND(((FARM_FINGERPRINT(CONCAT(_sha, "$seed")) + POW(2, 63)) / POW(2, 64))>{sample:.4g})'.format(
            field_name=field_name, field_value=value, sample=(1.0 - sample))

        vars_result = None

        self.validate_sql(
            'sample:{sample} and {field_name}:{field_value}',
            dict(sample=sample, field_name=field_name, field_value=value), (vars_result, where_result),
            BigQuerySqlHelper)

    def testBigQuerySample_implicit(self):
        sample = random.random()
        field_name = 'field1_' + self.some_random_shit_alpha()
        value = 'val1_' + self.some_random_shit_alpha()

        where_result = '({field_name}="{field_value}")AND(((FARM_FINGERPRINT(CONCAT(_sha, "$seed")) + POW(2, 63)) / POW(2, 64))>{sample:.4g})'.format(
            field_name=field_name, field_value=value, sample=(1.0 - sample))

        vars_result = None

        self.validate_sql(
            'sample:{sample} {field_name}:{field_value}',
            dict(sample=sample, field_name=field_name, field_value=value),
            (vars_result, where_result),
            BigQuerySqlHelper)

    def testBigQuerySample_twice(self):
        sample1 = random.uniform(0., 0.5)
        sample2 = random.uniform(0.5, 1.0)
        where_result = '(((FARM_FINGERPRINT(CONCAT(_sha, "$seed")) + POW(2, 63)) / POW(2, 64))>{sample1:.4g})AND(((FARM_FINGERPRINT(CONCAT(_sha, "$seed")) + POW(2, 63)) / POW(2, 64))>{sample2:.4g})'.format(
            sample1=1.0 - sample1, sample2=1.0 - sample2)
        vars_result = None

        self.validate_sql('sample:{sample1} AND sample:{sample2}', dict(sample1=sample1, sample2=sample2), (vars_result, where_result))
