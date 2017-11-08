#!/usr/bin/env python

import math
import unittest

from mock import Mock  # type: ignore
from pandas import DataFrame  # type: ignore
from pandas.util.testing import assert_frame_equal  # type: ignore

from edpanalyst import (PopulationSchema, Population, PopulationModel,
                        PopulationModelExperimental)

# The population model you use if you don't care about it in your test
PM = {
    'id': 'pm-17',
    'parent_id': 'p-14',
    'name': 'dontcare',
    'creation_time': 1234,
    'build_progress': {
        'status': 'built'
    },
    'user_metadata': {}
}
WXYZ_SCHEMA = PopulationSchema.from_json({
    'columns': [
        {
            'name': 'w',
            'stat_type': 'realAdditive'
        },
        {
            'name': 'x',
            'stat_type': 'realAdditive'
        },
        {
            'name': 'y',
            'stat_type': 'realAdditive'
        },
        {
            'name': 'z',
            'stat_type': 'realAdditive'
        },
    ]
})
XYZ_NAME_SCHEMA = PopulationSchema.from_json({
    'identifying_columns': ['name'],
    'columns': [
        {
            'name': 'name',
            'stat_type': 'void'
        },
        {
            'name': 'x',
            'stat_type': 'realAdditive'
        },
        {
            'name': 'y',
            'stat_type': 'realAdditive'
        },
        {
            'name': 'z',
            'stat_type': 'realAdditive'
        },
    ]
})


def _mock_popmod(desc, schema=None):
    mock_endpoint = Mock()
    mock_desc = Mock()
    mock_desc.json.return_value = desc
    mock_endpoint.get.return_value = mock_desc
    real_pm = PopulationModel(desc['id'], client=None, endpoint=mock_endpoint)
    real_pm._parent = Population(desc['parent_id'], client=None,
                                 endpoint=mock_endpoint, time_fn=lambda: 42)
    real_pm._parent._schema = schema
    real_pm._parent._schema_fetch_time = 41
    popmod = Mock(wraps=real_pm)
    popmod.schema = schema
    return popmod


class TestUnlikelyValues(unittest.TestCase):

    def test_unlikely_values(self):
        schema = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'Name',
                    'stat_type': 'void'
                },
                {
                    'name': 'foo',
                    'stat_type': 'realAdditive'
                },
                {
                    'name': 'x',
                    'stat_type': 'realAdditive'
                },
                {
                    'name': 'y',
                    'stat_type': 'realAdditive'
                },
            ]
        })
        mock_pm = _mock_popmod(PM, schema)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.select.return_value = DataFrame({
            'foo': [2, 3, 4, 5, 6],
            'Name': ['a', 'b', 'c', 'd', 'e']
        }, index=[str(i) for i in range(5)])
        mock_pm.row_probability.return_value = DataFrame({
            'foo': [2, 3, 4, 5, 6],
            'pr': [.025, .04, .03, .01, .05],
            'Name': ['a', 'b', 'c', 'd', 'e']
        })

        results = popmod.unlikely_values(
            'foo', num_outliers=3, select=['Name'], probability_column='pr')

        expected = DataFrame({
            'Name': ['d', 'a', 'c'],
            'foo': [5, 2, 4],
            'pr': [.01, .025, .03]
        }, columns=['Name', 'foo', 'pr'], index=[3, 0, 2])
        assert_frame_equal(results, expected)

        # `row_probability` uses all non-target columns if
        # `given_columns=None`
        mock_pm.row_probability.assert_called_once_with(
            targets=['foo'], given_columns=None, rowids=None, select=['Name'],
            probability_column='pr')

    def test_unlikely_values_with_givens(self):
        schema = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'Name',
                    'stat_type': 'void'
                },
                {
                    'name': 'foo',
                    'stat_type': 'realAdditive'
                },
                {
                    'name': 'x',
                    'stat_type': 'realAdditive'
                },
                {
                    'name': 'y',
                    'stat_type': 'realAdditive'
                },
            ]
        })
        mock_pm = _mock_popmod(PM, schema)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.select.return_value = DataFrame({
            'foo': [2, 3, 4, 5, 6],
            'Name': ['a', 'b', 'c', 'd', 'e']
        }, index=[str(i) for i in range(5)])
        mock_pm.row_probability.return_value = DataFrame({
            'foo': [2, 3, 4, 5, 6],
            'pr': [.025, .04, .03, .01, .05],
            'Name': ['a', 'b', 'c', 'd', 'e']
        })

        popmod.unlikely_values('foo', given_columns=['y'], num_outliers=3,
                               select=['Name'], probability_column='pr')

        mock_pm.row_probability.assert_called_once_with(
            targets=['foo'], given_columns=['y'], rowids=None, select=['Name'],
            probability_column='pr')


class TestColumnValueProbabilities(unittest.TestCase):

    def test_basic(self):
        schema_2d = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'x',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': 'a'},
                        {'value': 'b'},
                    ]
                },
                {
                    'name': 'y',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '1'},
                        {'value': '2'},
                    ]
                },
            ]
        })  # yapf: disable
        mock_pm = _mock_popmod(PM, schema_2d)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.joint_probability.return_value = DataFrame({
            'x': ['a', 'b'],
            'p': [.2, .8]
        })

        expected = DataFrame({'x': ['b', 'a'], 'p': [.8, .2]})
        actual = popmod.column_value_probabilities('x')
        assert_frame_equal(actual.reset_index(drop=True), expected)

        mock_pm.joint_probability.assert_called_once_with(
            targets={'x': ['a', 'b']}, given=None, probability_column='p')

    def test_givens(self):
        schema_2d = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'x',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': 'a'},
                        {'value': 'b'},
                    ]
                },
                {
                    'name': 'y',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '1'},
                        {'value': '2'},
                    ]
                },
            ]
        })  # yapf: disable
        mock_pm = _mock_popmod(PM, schema_2d)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.joint_probability.return_value = DataFrame({
            'x': ['a', 'b'],
            'p': [.2, .8]
        })

        expected = DataFrame({'x': ['b', 'a'], 'p': [.8, .2]})
        actual = popmod.column_value_probabilities('x', given={'y': '1'})
        assert_frame_equal(actual.reset_index(drop=True), expected)

        mock_pm.joint_probability.assert_called_once_with(
            targets={'x': ['a', 'b']}, given={'y': '1'},
            probability_column='p')

    def test_raises_on_non_categorical_for_now(self):
        mock_pm = _mock_popmod(PM,
                               PopulationSchema.from_json({
                                   'columns': [{
                                       'name': 'x',
                                       'stat_type': 'realAdditive'
                                   }]
                               }))
        popmod = PopulationModelExperimental(mock_pm)

        with self.assertRaises(ValueError):
            popmod.column_value_probabilities('x')


class TestWheresTheColumnAssociation(unittest.TestCase):

    def test_helper_functions(self):
        schema_2d = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'x',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': 'a'},
                        {'value': 'b'},
                    ]
                },
                {
                    'name': 'y',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '1'},
                        {'value': '2'},
                    ]
                },
            ]
        })  # yapf: disable
        mock_pm = _mock_popmod(PM, schema_2d)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.joint_probability.return_value = DataFrame({
            'x': ['a', 'a', 'b', 'b'],
            'y': ['1', '2', '1', '2'],
            'p': [.1, .2, .3, .4]
        })
        pt = popmod._joint_probability_table('x', 'y')
        mock_pm.joint_probability.assert_called_once_with(
            targets={'x': ['a', 'a', 'b', 'b'],
                     'y': ['1', '2', '1', '2']})
        expected_pt = DataFrame({
            '1': [.1, .3],
            '2': [.2, .4]
        }, columns=['1', '2'], index=['a', 'b'])
        assert_frame_equal(pt, expected_pt)

        jl = popmod._product_of_marginal_probabilities_table(pt)
        expected_jl = DataFrame({
            '1': [.12, .28],
            '2': [.18, .42]
        }, columns=['1', '2'], index=['a', 'b'])
        assert_frame_equal(jl, expected_jl)

    def test_r2_two_categoricals(self):
        schema_2d = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'x',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': 'a'},
                        {'value': 'b'},
                        {'value': 'c'},
                    ]
                },
                {
                    'name': 'y',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '1'},
                        {'value': '2'},
                        {'value': '3'},
                    ]
                },
            ]
        })  # yapf: disable
        mock_pm = _mock_popmod(PM, schema_2d)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.joint_probability.return_value = DataFrame({
            'x': ['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'c'],
            'y': ['1', '2', '3', '1', '2', '3', '1', '2', '3'],
            'p': [.05, .1, .2, .1, .3, .05, .025, .05, .125]
        })

        results = popmod.wheres_the_r2('x', 'y')
        mock_pm.joint_probability.assert_called_once_with(
            targets={
                'x': ['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'c'],
                'y': ['1', '2', '3', '1', '2', '3', '1', '2', '3']
            })

        # Round the results for easier testing
        results = [(c1, c2, round(chi, 10)) for (c1, c2, chi) in results]
        expected = [('b', '3', -.11875), ('b', '2', .0975), ('a', '3', .06875),
                    ('a', '2', -.0575), ('c', '3', .05)]
        self.assertEqual(results, expected)

    def test_mi_two_categoricals(self):
        schema_2d = PopulationSchema.from_json({
            'columns': [
                {
                    'name': 'x',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': 'a'},
                        {'value': 'b'},
                    ]
                },
                {
                    'name': 'y',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '1'},
                        {'value': '2'},
                    ]
                },
            ]
        })  # yapf: disable
        mock_pm = _mock_popmod(PM, schema_2d)
        popmod = PopulationModelExperimental(mock_pm)

        mock_pm.joint_probability.return_value = DataFrame({
            'x': ['a', 'a', 'b', 'b'],
            'y': ['1', '2', '1', '2'],
            'p': [.1, .2, .3, .4]
        })

        results = popmod.wheres_the_info('x', 'y')
        mock_pm.joint_probability.assert_called_once_with(
            targets={'x': ['a', 'a', 'b', 'b'],
                     'y': ['1', '2', '1', '2']})

        # Round the results for easier testing
        prec = 10
        results = [(c1, c2, round(chi, prec)) for (c1, c2, chi) in results]
        expected = [
            ('a', '2', round(.2 * math.log(.2 / .18, 2), prec)),
            ('b', '1', round(.3 * math.log(.3 / .28, 2), prec)),
            ('b', '2', round(.4 * math.log(.4 / .42, 2), prec)),
            ('a', '1', round(.1 * math.log(.1 / .12, 2), prec)),
        ]
        self.assertEqual(results, expected)


if __name__ == '__main__':
    unittest.main()
