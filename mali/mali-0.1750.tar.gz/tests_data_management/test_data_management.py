# coding=utf-8
import os

from tests_data_management.base import BaseTest
from mali_commands.utilities.os_utils import flatten_dir


class TestDataManagement(BaseTest):

    def testBasicFlow(self):
        """Test basic flow
        - Create a data volume
        - Add a file
        - Add a metadata
        - Commit
        - Clone
        """

        self.populate_data([
            'foo.txt',
        ])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'name': 'foo'})
        result = self.commit(volume_id)

        self.assertEqual(result['version_total_data_points'], '1')
        self.assertEqual(result['version_total_meta_data'], '1')
        self.assertEqual(result['total_meta_data'], '1')
        self.assertEqual(result['total_data_points'], '1')

        commit_id = result['commit_id']
        clone_path = os.path.join(self.clone_dir, '$phase/$name')
        self.clone(volume_id, clone_path, 'name:foo version:%s' % commit_id)
        flatten_dir(self.clone_dir)

        self.assertEqualDir(self.data_dir, self.clone_dir)

    def testMultipleCommits(self):
        self.populate_data([
            'foo.txt',
            'bar.txt'
        ])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'name': 'foo'})
        result = self.commit(volume_id)

        self.assertEqual(result['version_total_data_points'], '1')
        self.assertEqual(result['version_total_meta_data'], '1')
        self.assertEqual(result['total_meta_data'], '1')
        self.assertEqual(result['total_data_points'], '1')

        self.add_file(volume_id, ['bar.txt'])
        self.add_metadata(volume_id, ['bar.txt'], {'name': 'foo'})
        result = self.commit(volume_id)

        self.assertEqual(result['version_total_data_points'], '1')
        self.assertEqual(result['version_total_meta_data'], '1')
        self.assertEqual(result['total_meta_data'], '2')
        self.assertEqual(result['total_data_points'], '2')

        commit_id = result['commit_id']

        clone_path = os.path.join(self.clone_dir, '$phase/$name')
        self.clone(volume_id, clone_path, 'version:%s' % commit_id)
        flatten_dir(self.clone_dir)

        self.assertEqualDir(self.data_dir, self.clone_dir)

    def testMultipleCommitsNoMetadata(self):
        self.populate_data([
            'foo.txt',
            'bar.txt'
        ])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        result = self.commit(volume_id)

        self.assertEqual(result['version_total_data_points'], '1')
        self.assertEqual(result['version_total_meta_data'], '0')
        self.assertEqual(result['total_meta_data'], '0')
        self.assertEqual(result['total_data_points'], '1')

        self.add_file(volume_id, ['bar.txt'])
        result = self.commit(volume_id)

        self.assertEqual(result['version_total_data_points'], '1')
        self.assertEqual(result['version_total_meta_data'], '0')
        self.assertEqual(result['total_meta_data'], '0')
        self.assertEqual(result['total_data_points'], '2')

    def testModifyMeta(self):
        self.populate_data(['foo.txt'])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'state': 'ca'})
        commit_result1 = self.commit(volume_id)

        query_result1 = self.query(volume_id, 'version:%s state:ca' % commit_result1['commit_id'])

        self.assertEqual(1, len(query_result1))
        self.assertEqual('ca', query_result1[0]['state'])

        self.add_metadata(volume_id, ['foo.txt'], {'state': 'il'})
        commit_result2 = self.commit(volume_id)

        query_result2 = self.query(volume_id, 'version:%s state:il' % commit_result2['commit_id'])
        self.assertEqual(1, len(query_result2))
        self.assertEqual('il', query_result2[0]['state'])

        query_result2 = self.query(volume_id, 'version:%s state:ca' % commit_result2['commit_id'])
        self.assertEqual(0, len(query_result2))
