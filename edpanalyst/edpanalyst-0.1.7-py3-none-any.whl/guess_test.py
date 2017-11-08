import unittest

from typing import Any, List  # NOQA

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from edpanalyst.guess import (guess_schema, _is_like_list_of_numbers,
                              _guess_precision)


class TestGuess(unittest.TestCase):

    def test_basic_schema(self):  # type: () -> None
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame.from_items([
            ('few_numbers', [rs.randint(0, 10) for _ in range(100)]),
            ('more_numbers', [rs.randint(0, 100) for _ in range(100)]),
            ('all_distinct_numbers', [i for i in range(100)]),
            ('all_distinct_strings', [('val' + str(i)) for i in range(100)]),
            ('constant', [1 for _ in range(100)]),
        ])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'few_numbers',
                    'stat_type': 'categorical',
                    'values': [{'value': str(x)} for x in range(10)],
                    'stat_type_reason': 'Only 10 distinct values'
                },
                {
                    'name': 'more_numbers',
                    'stat_type': 'realAdditive',
                    'stat_type_reason':
                    'Contains only numbers (68 of them, uniform cor. 0.999, '
                    'log-uniform cor. 0.891)',
                    'precision': [1, 1],
                },
                {
                    'name': 'all_distinct_numbers',
                    'stat_type': 'realAdditive',
                    'stat_type_reason':
                    'Contains only numbers (100 of them, not all values '
                    'are positive)',
                    'precision': [1, 1],
                },
                {
                    'name': 'all_distinct_strings',
                    'stat_type': 'void',
                    'stat_type_reason': 'Non-numeric and all values unique'
                },
                {
                    'name': 'constant',
                    'stat_type': 'void',
                    'stat_type_reason': 'Column is constant'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_void_hint(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([('foo', ['total', 1, 'junk'])])
        hints = {'foo': {'stat_type': 'void'}}
        guessed = guess_schema(test_frame, hints=hints).to_json()

        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason': 'Hinted',
                },
            ],
            'derived_columns': [],
        }  # yapf: disable

        self.assertEqual(guessed, expected)

    def test_sequence_hint(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([('foo', [0, 1, 2])])
        with self.assertRaises(ValueError):
            guess_schema(test_frame, hints={'foo': {'stat_type': 'sequence'}})

    def test_categorical_hints(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([
            ('actually_categorical', [1, 2, 3]),
        ])

        hints = {'actually_categorical': {'stat_type': 'categorical'}}

        guessed = guess_schema(test_frame, hints=hints).to_json()

        expected = {
            'columns': [
                {
                    'name': 'actually_categorical',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '1'},
                        {'value': '2'},
                        {'value': '3'},
                    ],
                    'stat_type_reason': 'Hinted',
                },
            ],
            'derived_columns': [],
        }  # yapf: disable

        self.assertEqual(guessed, expected)

    def test_numeric_hints(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([('actually_numeric', [0, 0, 1])])
        hints = {'actually_numeric': {'stat_type': 'realAdditive'}}
        guessed = guess_schema(test_frame, hints=hints).to_json()

        expected = {
            'columns': [
                {
                    'name': 'actually_numeric',
                    'stat_type': 'realAdditive',
                    'stat_type_reason': 'Hinted',
                    'precision': [1, 1],
                },
            ],
            'derived_columns': [],
        }  # yapf: disable

        self.assertEqual(guessed, expected)

    def test_general_numeric_hint(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([('actually_numeric', [0, 0, 1])])
        hints = {'actually_numeric': {'stat_type': 'real'}}
        guessed = guess_schema(test_frame, hints=hints).to_json()

        expected = {
            'columns': [
                {
                    'name': 'actually_numeric',
                    'stat_type': 'realAdditive',
                    'stat_type_reason': 'Hinted',
                    'precision': [1, 1],
                },
            ],
            'derived_columns': [],
        }  # yapf: disable

        self.assertEqual(guessed, expected)

    def test_numeric_hint_problem(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items([('not_numeric', [0, 'a', 1])])
        hints = {'not_numeric': {'stat_type': 'realMultiplicative'}}
        with self.assertRaises(ValueError):
            guess_schema(test_frame, hints=hints)

    def test_tricky_categoricals(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', [.1, 1.000000002, float('nan'), ""])])
        guessed = guess_schema(test_frame).to_json()
        # NaN doesn't count, but empty string does
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': ''},
                        {'value': '0.1'},
                        {'value': '1.000000002'},
                    ],
                    'stat_type_reason': 'Only 3 distinct values'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_numeric_categorical_sorting(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', [0, 1, 'A', 'C', 2, 100, 'B', 20, 'IMASTRING', 'AA',
                      10])])
        guessed = guess_schema(test_frame).to_json()
        # NaN doesn't count, but empty string does
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'categorical',
                    'values': [
                        {'value': '0'},
                        {'value': '1'},
                        {'value': '2'},
                        {'value': '10'},
                        {'value': '20'},
                        {'value': '100'},
                        {'value': 'A'},
                        {'value': 'AA'},
                        {'value': 'B'},
                        {'value': 'C'},
                        {'value': 'IMASTRING'},
                    ],
                    'stat_type_reason': 'Only 11 distinct values'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_too_sparse_categorical(self):  # type: () -> None
        test_frame = pd.DataFrame.from_items(
            [('foo', ["f{}".format(x) for x in range(100)] * 2)])
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason': '100 distinct values. 100 are '
                                        'non-numeric (f0, f1, f2, ...)'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_one_non_number_and_null(self):  # type: () -> None
        vals = list(range(30))  # type: List[Any]
        vals = vals + ['-', np.nan]
        test_frame = pd.DataFrame.from_dict({'foo': vals})
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason':
                        '31 distinct values. 1 are non-numeric (-)'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_poorly_covered_categorical(self):  # type: () -> None
        vals = [('s' + str(x)) for x in list(range(30))]  # type: List[Any]
        vals = [None] + vals
        test_frame = pd.DataFrame.from_dict({'foo': vals})
        guessed = guess_schema(test_frame).to_json()
        expected = {
            'columns': [
                {
                    'name': 'foo',
                    'stat_type': 'void',
                    'stat_type_reason': '30 distinct values. 30 are '
                                        'non-numeric (s0, s1, s2, ...)'
                },
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_normal_transformation(self):  # type: () -> None
        # Check that normal and lognormal data with the same mean and variance
        # get classified as realAdditive and realMultiplicative, respectively.
        # This isn't a great test; Madeleine doesn't think you can really ever
        # find a normal distribution with the same mean and variance as a
        # lognormal distribution where both don't fit about as well as each
        # other unless the normal distribution has negative numbers.

        # Generate some random data.
        n = 1000
        rs = np.random.RandomState(17)
        lognormal_data = rs.lognormal(1.2, 0.8, size=n)
        normal_data = rs.normal(
            np.mean(lognormal_data), np.std(lognormal_data), size=n)
        test_frame = pd.DataFrame.from_items([('normal', normal_data),
                                              ('log_normal', lognormal_data)])

        # Check that `guess_schema` guesses correctly.
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [
                {'name': 'normal', 'stat_type': 'realAdditive'},
                {'name': 'log_normal', 'stat_type': 'realMultiplicative'},
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_log_normal_with_single_negative_value(self):  # type: () -> None
        rs = np.random.RandomState(17)
        data = rs.lognormal(0, 1, 10000)
        data = np.append(data, -.01)
        test_frame = pd.DataFrame({'almost_log_normal': data})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        # It's not actually for sure true that this should be realAdditive and
        # not realMultiplicative. See the discussion in guess.py.
        expected = {
            'columns': [{
                'name': 'almost_log_normal',
                'stat_type': 'realAdditive'
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_numeric_column_full_of_strings(self):  # type: () -> None
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame({
            'str_numbers': [str(rs.randint(0, 100)) for _ in range(100)]
        })
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'str_numbers',
                'stat_type': 'realAdditive',
                'precision': [1, 1],
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_numeric_column_of_thousands(self):  # type: () -> None
        rs = np.random.RandomState(17)
        test_frame = pd.DataFrame({
            'th': [1000 * rs.randint(-50, 50) for _ in range(100)]
        })
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'th',
                'stat_type': 'realAdditive',
                'precision': [1000, 1],
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_multiplicative_column_of_tenths(self):  # type: () -> None
        rs = np.random.RandomState(17)
        tenths = np.round(np.exp(rs.normal(2, 1, size=100)), decimals=1)
        test_frame = pd.DataFrame({'tenths': tenths})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'tenths',
                'stat_type': 'realMultiplicative',
                'precision': [1, 10],
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_is_like_list_of_numbers(self):  # type: () -> None
        self.assertTrue(_is_like_list_of_numbers(list()))
        self.assertTrue(_is_like_list_of_numbers(tuple()))
        self.assertTrue(_is_like_list_of_numbers(np.array([1, 2])))
        self.assertTrue(_is_like_list_of_numbers([None]))
        self.assertFalse(_is_like_list_of_numbers(np.array(['foo', 'bar'])))
        self.assertFalse(_is_like_list_of_numbers(['foo']))
        self.assertFalse(_is_like_list_of_numbers(3))
        self.assertFalse(_is_like_list_of_numbers(b'foo'))
        self.assertFalse(_is_like_list_of_numbers(u'foo'))
        self.assertFalse(_is_like_list_of_numbers({}))
        self.assertFalse(_is_like_list_of_numbers({0: 1, 2: 3}))

    def test_sequences_with_normal_noise(self):  # type: () -> None
        # Generate a list of six sequences, the longest of which are length
        # ten, with one missing value, with normal noise.
        length = 10
        rs = np.random.RandomState(17)
        sequences = [np.cumsum(rs.normal(size=length)) for _ in range(6)]
        sequences[2] = None  # add a missing sequence
        sequences[3].resize(length - 2)  # chop off some values
        sequences[4][7] = None  # make a sequence element missing

        # Check that the column is guessed to be of type "sequence", with an
        # identity transform, with length equal to the length of the longest
        # sequence.
        test_frame = pd.DataFrame({'x': sequences})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'x',
                'stat_type': 'sequence',
                'length': length,
                'transform': 'identity',
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_sequences_with_lognormal_noise(self):  # type: () -> None
        # Generate a list of six sequences with lognormal increments.
        length = 10
        rs = np.random.RandomState(17)
        sequences = [np.cumprod(rs.lognormal(size=length)) for _ in range(6)]

        # Check that the column is guessed to be of type "sequence", with a log
        # transform.
        test_frame = pd.DataFrame({'x': sequences})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'x',
                'stat_type': 'sequence',
                'length': length,
                'transform': 'log',
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_sequences_with_no_numbers(self):  # type: () -> None
        test_frame = pd.DataFrame({
            'w': [[], []],
            'x': [['two', 'three'], ['five', 'six']],
            'y': [[None, None], [None, None]],
            'z': [None, None],
        })
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [
                {'name': 'w', 'stat_type': 'void'},
                {'name': 'x', 'stat_type': 'void'},
                {'name': 'y', 'stat_type': 'void'},
                {'name': 'z', 'stat_type': 'void'},
            ],
            'derived_columns': [],
        }  # yapf: disable
        self.assertEqual(guessed, expected)

    def test_constant_sequences(self):  # type: () -> None
        length = 10
        sequences = [[17] * length for _ in range(7)]
        test_frame = pd.DataFrame({'x': sequences})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'x',
                'stat_type': 'void',
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_sequences_with_constant_first_element(self):  # type: () -> None
        sequences = [[1, 2, 3, 2], [1, 7, 0, 5], [None, 1, -9, 1]]
        test_frame = pd.DataFrame({'x': sequences})
        guessed = guess_schema(test_frame).to_json(drop_reasons=True)
        expected = {
            'columns': [{
                'name': 'x',
                'stat_type': 'void',
            }],
            'derived_columns': [],
        }
        self.assertEqual(guessed, expected)

    def test_guess_precision(self):  # type: () -> None
        # Try units of 1000, 100, ..., 0.01 and confirm they're guessed. We
        # can't use subTest in this test because it's python3-only.
        rng = np.random.RandomState(17)
        for places in range(-3, 3):
            x = rng.randint(-1e6, 1e6, size=1000) / 10**places
            prec = _guess_precision(x)
            if places <= 0:
                self.assertEqual((10**-places, 1), prec)
            else:
                self.assertEqual((1, 10**places), prec)

    def test_precision_when_all_bits_are_used(self):  # type: () -> None
        rng = np.random.RandomState(17)
        self.assertIsNone(_guess_precision(rng.normal(0, 1, size=100)))

    def test_precision_on_very_large_integers(self):  # type: () -> None
        rng = np.random.RandomState(17)
        self.assertIsNone(_guess_precision(rng.randint(1e15, size=100)))

    def test_precision_on_very_small_fractions(self):  # type: () -> None
        self.assertIsNone(_guess_precision(np.array([1e-30, 3e-30, 2e-30])))


if __name__ == '__main__':
    unittest.main()
