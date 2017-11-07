import logging
import unittest

from velenxc.errors import ExtractorError
from velenxc.parsers import JSONPathParser
from velenxc.preprocessing.extract import FeatureFromJsonExtractor

logging.basicConfig(level=logging.INFO)

data = {
    'users': [
        {'name': 'zs', 'age': '23'},
        {'name': 'ls', 'age': '40'},
        {'name': 'ls2', 'age': '30'},
        {'name': 'ls3', 'age': '20'},
        {'name': 'ls4', 'age': 50},
    ]
}


class FeatureFromJsonExtractorTestCase(unittest.TestCase):
    def test_transform_one_feature(self):
        config = {
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
                '$.users[*].age'
            ],
            'func_chains': 'm_str_to_int->r_sum_with_average'
        }

        extractor = FeatureFromJsonExtractor()
        feature_value = extractor.transform_one_feature(data, config)

        self.assertEqual(32.6, feature_value)

    def test_transform_one_feature_None(self):
        config = {
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
                '$.users[*].age2'
            ],
            'func_chains': ''
        }

        extractor = FeatureFromJsonExtractor()
        feature_value = extractor.transform_one_feature(data, config)

        self.assertEqual(None, feature_value)

    def test_transform(self):
        configs = [{
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
                '$.users[*].age'
            ],
            'func_chains': 'm_str_to_int->r_sum_with_average'
        }]

        extractor = FeatureFromJsonExtractor(json_parser_cls=JSONPathParser, func_pipeline_separator='->')
        feature_vector = extractor.transform(data, configs)

        logging.info(feature_vector)
        self.assertEqual(32.6, feature_vector['age_average'])

    def test_transform_to_int_constant(self):
        configs = [{
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
                '$.users[*].age'
            ],
            'func_chains': 'm_to_value(20)->r_sum_with_average'
        }]

        extractor = FeatureFromJsonExtractor(json_parser_cls=JSONPathParser, func_pipeline_separator='->')
        feature_vector = extractor.transform(data, configs)

        self.assertEqual(20, feature_vector['age_average'])

    def test_transform_to_float_constant(self):
        configs = [{
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
                '$.users[*].age'
            ],
            'func_chains': 'm_to_value(20.5)->r_sum_with_average'
        }]

        extractor = FeatureFromJsonExtractor(json_parser_cls=JSONPathParser, func_pipeline_separator='->')
        feature_vector = extractor.transform(data, configs)

        self.assertEqual(20.5, feature_vector['age_average'])

    def test_transform_to_str_constant(self):
        configs = [{
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
                '$.users[*].age'
            ],
            'func_chains': 'm_to_value(\'21\')->m_str_to_int->r_sum_average'
        }]

        extractor = FeatureFromJsonExtractor(json_parser_cls=JSONPathParser, func_pipeline_separator='->')
        feature_vector = extractor.transform(data, configs)

        self.assertEqual(21, feature_vector['age_average'])

    def test_should_detect_bad_configs(self):
        extractor = FeatureFromJsonExtractor()
        with self.failUnlessRaises(ExtractorError):
            extractor.schema_valid([{'feature_name': 'age_average'}], extractor.config_schema)

    def test_transform_one_feature_return_none(self):
        configs = [{
            'feature_name': 'feature_exception',
            'cn_name': 'feature_exception',
            'jsonpath': [
                '$中国$.users[*].age'
            ],
            'func_chains': 'm_divided_by'
        }]

        extractor = FeatureFromJsonExtractor(json_parser_cls=JSONPathParser, func_pipeline_separator='->')
        feature_vector = extractor.transform(data, configs)

        self.assertEqual(None, feature_vector['feature_exception'])

    def test_transform_one_feature_none_list(self):
        config = {
            'feature_name': 'age_average',
            'cn_name': 'age average',
            'jsonpath': [
            ],
            'func_chains': ''
        }

        extractor = FeatureFromJsonExtractor()
        feature_value = extractor.transform_one_feature(data, config)

        self.assertEqual(None, feature_value)

    def test_transform_one_feature_exception(self):
        configs = [{
            'feature_name': 'feature_exception',
            'cn_name': 'feature_exception',
            'jsonpath': [
                '$.users[*].age'
            ],
            'func_chains': 'r_sum_of_list'
        }]

        extractor = FeatureFromJsonExtractor(json_parser_cls=JSONPathParser, func_pipeline_separator='->')
        feature_vector = extractor.transform(data, configs)

        self.assertEqual('ERROR', feature_vector['feature_exception'])
