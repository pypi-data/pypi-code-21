import unittest

from .population_schema import ColumnDefinition, PopulationSchema


class PopulationSchemaTest(unittest.TestCase):

    def test_column_definition_eq(self):  # type: () -> None
        self.assertEqual(
            ColumnDefinition('a', 'sequence', length=4),
            ColumnDefinition('a', 'sequence', length=4, transform='identity'))
        self.assertNotEqual(
            ColumnDefinition('a', 'sequence', length=4),
            ColumnDefinition('a', 'sequence', length=3))

    def test_population_schema_eq(self):  # type: () -> None
        s1 = PopulationSchema({'a': ColumnDefinition('a', 'realAdditive')}),
        s2 = PopulationSchema({'a': ColumnDefinition('a', 'realAdditive')}),
        s3 = PopulationSchema({'b': ColumnDefinition('b', 'realAdditive')})
        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)

    def test_precise_column_definitions(self):  # type: () -> None
        cd_2_1 = ColumnDefinition('m', 'magnitude', precision=(2, 1))
        self.assertEqual((2, 1), cd_2_1.precision)

        cd_1_10 = ColumnDefinition('m', 'magnitude', precision=(1, 10))
        self.assertEqual((1, 10), cd_1_10.precision)

        self.assertEqual(cd_1_10.to_json(), {
            'name': 'm',
            'stat_type': 'magnitude',
            'precision': [1, 10]
        })

    def test_imprecise_column_definition(self):  # type: () -> None
        cd = ColumnDefinition('m', 'magnitude')
        self.assertIsNone(cd.precision)
        self.assertEqual(cd.to_json(), {'name': 'm', 'stat_type': 'magnitude'})

    def test_precision_on_non_real(self):  # type: () -> None
        with self.assertRaises(AttributeError):
            ColumnDefinition('c', 'categorical', values=['H', 'T']).precision

    def test_invalid_precisions(self):  # type: () -> None
        with self.assertRaises(ValueError):
            ColumnDefinition('m', 'magnitude', precision=(3, 6))
        with self.assertRaises(ValueError):
            ColumnDefinition('m', 'magnitude', precision=(2, 3))
        with self.assertRaises(ValueError):
            ColumnDefinition('m', 'magnitude', precision=(0, 0))

    def test_schema_from_json(self):  # type: () -> None
        schema_json = {
            'identifying_columns': ['id'],
            'columns': [
                {
                    'name': 'id',
                    'stat_type': 'void',
                },
                {
                    'name': 'val',
                    'stat_type': 'magnitude',
                    'precision': [16, 1],
                },
            ],
            'derived_columns': [],
        }
        roundtripped_json = PopulationSchema.from_json(schema_json).to_json()
        self.assertEqual(schema_json, roundtripped_json)


if __name__ == '__main__':
    unittest.main()
