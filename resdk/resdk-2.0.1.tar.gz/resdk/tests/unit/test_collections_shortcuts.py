"""
Unit tests for resdk/resources/collection.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

from mock import MagicMock

from resdk.resources.collection import Collection


class TestCollection(unittest.TestCase):

    def test_create_group(self):
        collection = Collection(id=1, resolwe=MagicMock())
        collection.id = 1  # this is overriden when initialized

        # only samples
        collection.create_group_relation(samples=[1, 2, 3])
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='group',
            entities=[
                {'entity': 1},
                {'entity': 2},
                {'entity': 3},
            ],
        )

        collection.resolwe.relation.create.reset_mock()

        # samples with positions
        collection.create_group_relation(samples=[1, 2, 3], positions=['first', 'second', 'third'])
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='group',
            entities=[
                {'position': 'first', 'entity': 1},
                {'position': 'second', 'entity': 2},
                {'position': 'third', 'entity': 3},
            ],
        )

        collection.resolwe.relation.create.reset_mock()

        # samples with positions - length mismatch
        with self.assertRaises(ValueError):
            collection.create_group_relation(samples=[1, 2, 3], positions=['first'])
        self.assertEqual(collection.resolwe.relation.create.call_count, 0)

        collection.resolwe.relation.create.reset_mock()

        # with label
        collection.create_group_relation(samples=[1, 2, 3], label='my_group')
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='group',
            label='my_group',
            entities=[
                {'entity': 1},
                {'entity': 2},
                {'entity': 3},
            ],
        )

    def test_create_compare(self):
        collection = Collection(id=1, resolwe=MagicMock())
        collection.id = 1  # this is overriden when initialized

        # only samples
        collection.create_compare_relation(samples=[1, 2])
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='compare',
            entities=[
                {'entity': 1},
                {'entity': 2},
            ],
        )

        collection.resolwe.relation.create.reset_mock()

        # samples with positions
        collection.create_compare_relation(samples=[1, 2], positions=['case', 'control'])
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='compare',
            entities=[
                {'position': 'case', 'entity': 1},
                {'position': 'control', 'entity': 2},
            ],
        )

        collection.resolwe.relation.create.reset_mock()

        # samples with positions - length mismatch
        with self.assertRaises(ValueError):
            collection.create_compare_relation(samples=[1, 2], positions=['case'])
        self.assertEqual(collection.resolwe.relation.create.call_count, 0)

        collection.resolwe.relation.create.reset_mock()

        # with label
        collection.create_compare_relation(samples=[1, 2], label='case-control')
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='compare',
            label='case-control',
            entities=[
                {'entity': 1},
                {'entity': 2},
            ],
        )

    def test_create_series(self):
        collection = Collection(id=1, resolwe=MagicMock())
        collection.id = 1  # this is overriden when initialized

        # only samples
        collection.create_series_relation(samples=[1, 2, 3])
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='series',
            entities=[
                {'entity': 1},
                {'entity': 2},
                {'entity': 3},
            ],
        )

        collection.resolwe.relation.create.reset_mock()

        # samples with positions
        collection.create_series_relation(samples=[1, 2, 3], positions=['0Hr', '2Hr', '4Hr'])
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='series',
            entities=[
                {'position': '0Hr', 'entity': 1},
                {'position': '2Hr', 'entity': 2},
                {'position': '4Hr', 'entity': 3},
            ],
        )

        collection.resolwe.relation.create.reset_mock()

        # samples with positions - length mismatch
        with self.assertRaises(ValueError):
            collection.create_series_relation(samples=[1, 2], positions=['0Hr'])
        self.assertEqual(collection.resolwe.relation.create.call_count, 0)

        collection.resolwe.relation.create.reset_mock()

        # with label
        collection.create_series_relation(samples=[1, 2], label='time-series')
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='series',
            label='time-series',
            entities=[
                {'entity': 1},
                {'entity': 2},
            ],
        )

    def test_create_background(self):
        collection = Collection(id=1, resolwe=MagicMock())
        collection.id = 1  # this is overriden when initialized

        # only samples
        collection.create_background_relation('sample_1', 'sample_2')
        collection.resolwe.relation.create.assert_called_with(
            collection=1,
            type='compare',
            label='background',
            entities=[
                {'position': 'sample', 'entity': 'sample_1'},
                {'position': 'background', 'entity': 'sample_2'},
            ],
        )


if __name__ == '__main__':
    unittest.main()
