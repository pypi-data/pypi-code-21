# -*- coding: utf8 -*-
import os

import shutil

from mali_commands.data_volume import update_config_file
from tests_data_management.base import BaseTest
from mali_commands.utilities.os_utils import flatten_dir, remove_dir


class TestDataManagement(BaseTest):
    def testUpload(self):
        self.populate_data([
            'foo.txt',
        ])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        self.add_file(volume_id, ['foo.txt'])

    def testUploadSingleProcess(self):
        self.populate_data([
            'foo.txt',
        ])

        params = {
            'object_store': {
                'use_multiprocess': False,
            }
        }

        volume_id = self.create_data_volume()

        update_config_file(volume_id, params)

        self.add_file(volume_id, ['foo.txt'])
        self.add_file(volume_id, ['foo.txt'])

    # def testUploadDirectBucket(self):
    #     self.populate_data([
    #         'foo.txt',
    #     ])
    #
    #     volume_id = self.create_data_volume()
    #     params = {
    #         'object_store': {
    #             'bucket_name': 'staging_data_volumes',
    #         }
    #     }
    #
    #     update_config_file(volume_id, params)
    #
    #     self.add_file(volume_id, ['foo.txt'])
    #     self.add_file(volume_id, ['foo.txt'])

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
        self.clone(volume_id, clone_path, 'name:foo @version:%s' % commit_id)
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
        self.clone(volume_id, clone_path, '@version:%s' % commit_id)
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

    def testNoMetadata(self):
        self.populate_data(['foo.txt'])

        volume_id = self.create_data_volume()

        self.add_file(volume_id, ['foo.txt'])

        query_result_staging = self.query(volume_id, '@version:staging')

        self.assertIsNotNone(query_result_staging[0]['id'])
        self.assertEqual(query_result_staging[0]['path'], 'foo.txt')
        self.assertEqual(query_result_staging[0]['size'], '4096')
        self.assertIsNotNone(query_result_staging[0]['url'])
        self.assertEqual(query_result_staging[0]['version'], 'staging')

        commit_result1 = self.commit(volume_id)

        query_result_after_commit = self.query(volume_id, '@version:%s' % commit_result1['commit_id'])

        self.assertIsNotNone(query_result_after_commit[0]['id'])
        self.assertEqual(query_result_after_commit[0]['path'], 'foo.txt')
        self.assertEqual(query_result_after_commit[0]['size'], '4096')
        self.assertIsNotNone(query_result_after_commit[0]['url'])
        self.assertEqual(query_result_after_commit[0]['version'], commit_result1['commit_id'])

    def testModifyMeta(self):
        self.populate_data(['foo.txt'])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'state': 'ca'})
        commit_result1 = self.commit(volume_id)

        query_result1 = self.query(volume_id, '@version:%s state:ca' % commit_result1['commit_id'])

        self.assertEqual(1, len(query_result1))
        self.assertEqual('ca', query_result1[0]['meta']['state'])

        self.add_metadata(volume_id, ['foo.txt'], {'state': 'il'})
        commit_result2 = self.commit(volume_id)

        query_result2 = self.query(volume_id, '@version:%s state:il' % commit_result2['commit_id'])
        self.assertEqual(1, len(query_result2))
        self.assertEqual('il', query_result2[0]['meta']['state'])

        query_result2 = self.query(volume_id, '@version:%s state:ca' % commit_result2['commit_id'])
        self.assertEqual(0, len(query_result2))

    def testDuplicateMetaQueryStaging(self):
        self.populate_data(['foo.txt', 'bar.txt'])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt', 'bar.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'state': 'ca'})
        self.add_metadata(volume_id, ['foo.txt'], {'state': 'ca'})
        self.add_metadata(volume_id, ['bar.txt'], {'state': 'ca'})
        query_result1 = self.query(volume_id, '@version:staging state:ca')
        self.assertEqual(2, len(query_result1))
        self.assertEqual('ca', query_result1[0]['meta']['state'])
        self.assertEqual('ca', query_result1[1]['meta']['state'])

        self.assertEqual(sorted([item['path'] for item in query_result1]), ['bar.txt', 'foo.txt'])

    def testClone_metadataFromAPreviousCommit(self):
        self.populate_data(['foo.txt', 'bar.txt'])

        volume_id = self.create_data_volume()

        self.add_file(volume_id, ['foo.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'name': 'foo'})
        commit_result1 = self.commit(volume_id)
        commit_id1 = commit_result1['commit_id']

        self.add_file(volume_id, ['bar.txt'])
        self.add_metadata(volume_id, ['bar.txt'], {'name': 'bar'})
        result = self.commit(volume_id)
        commit_id2 = result['commit_id']

        query_result = self.query(volume_id, '@version:%s name:foo' % commit_id1)
        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0]['path'], 'foo.txt')

        query_result = self.query(volume_id, '@version:%s name:foo' % commit_id2)
        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0]['path'], 'foo.txt')

    def testGroup(self):
        files = [
            '1.txt', '2.txt', '3.txt', '4.txt',
        ]
        self.populate_data(files)

        volume_id = self.create_data_volume()
        self.add_file(volume_id, files)
        self.add_metadata(volume_id, files, {'name': 'foo'})
        result = self.commit(volume_id)

        commit_id = result['commit_id']
        self.query(volume_id, 'name:foo @group:name @version:%s' % commit_id)

    def testClonedFilesWithNewMetadata(self):
        files = [
            '1.txt', '2.txt',
        ]

        self.populate_data(files)

        volume_id = self.create_data_volume()
        self.add_file(volume_id, files)
        self.add_metadata(volume_id, files, {'first': '1'})
        first_staging_query_result = self.query(volume_id, '@version:staging')

        self.assertEqual(2, len(first_staging_query_result))
        self.assertIsNotNone(first_staging_query_result[0]['id'])
        self.assertIsNotNone(first_staging_query_result[1]['id'])

        self.assertEqual(first_staging_query_result[0]['path'], '1.txt')
        self.assertEqual(first_staging_query_result[1]['path'], '2.txt')

        self.assertIsNotNone(first_staging_query_result[0]['url'])
        self.assertIsNotNone(first_staging_query_result[1]['url'])

        self.assertEqual(first_staging_query_result[0]['meta'], {'first': '1'})
        self.assertEqual(first_staging_query_result[1]['meta'], {'first': '1'})

        self.assertEqual(first_staging_query_result[0]['version'], 'staging')
        self.assertEqual(first_staging_query_result[1]['version'], 'staging')

        first_commit_result = self.commit(volume_id)

        self.assertEqual(first_commit_result['version_total_data_points'], '2')
        self.assertEqual(first_commit_result['version_total_meta_data'], '2')
        self.assertEqual(first_commit_result['total_meta_data'], '2')
        self.assertEqual(first_commit_result['total_data_points'], '2')

        first_version_query_result = self.query(volume_id, '@version:%s' % first_commit_result['commit_id'])

        self.assertEqual(2, len(first_version_query_result))

        cloned_files = []

        for filename in files:
            cloned_file = 'dup_' + filename

            cloned_files.append(cloned_file)
            shutil.copy(os.path.join(self.data_dir, filename), os.path.join(self.data_dir, cloned_file))

        self.add_file(volume_id, cloned_files)
        self.add_metadata(volume_id, cloned_files, {'second': '2'})

        second_staging_query_result = self.query(volume_id, '@version:staging')

        self.assertEqual(2, len(second_staging_query_result))
        self.assertIsNotNone(second_staging_query_result[0]['id'])
        self.assertIsNotNone(second_staging_query_result[1]['id'])

        self.assertEqual(second_staging_query_result[0]['path'], 'dup_1.txt')
        self.assertEqual(second_staging_query_result[1]['path'], 'dup_2.txt')

        self.assertIsNotNone(second_staging_query_result[0]['url'])
        self.assertIsNotNone(second_staging_query_result[1]['url'])

        self.assertEqual(second_staging_query_result[0]['meta'], {'first': None, 'second': '2'})
        self.assertEqual(second_staging_query_result[1]['meta'], {'first': None, 'second': '2'})

        self.assertEqual(second_staging_query_result[0]['version'], 'staging')
        self.assertEqual(second_staging_query_result[1]['version'], 'staging')

        second_commit_result = self.commit(volume_id)

        self.assertEqual(second_commit_result['version_total_data_points'], '2')
        self.assertEqual(second_commit_result['version_total_meta_data'], '2')
        self.assertEqual(second_commit_result['total_meta_data'], '4')
        self.assertEqual(second_commit_result['total_data_points'], '4')

        second_version_query_result = self.query(volume_id, '@version:%s' % second_commit_result['commit_id'])

        self.assertEqual(4, len(second_version_query_result))

    def testClone_changeFileContent_getLatestContent(self):
        volume_id = self.create_data_volume()
        filename = 'foo.txt'
        first_content = self.some_random_shit()
        print('First string:', first_content)
        second_content = self.some_random_shit()
        print('Second string:', second_content)
        clone_path = os.path.join(self.clone_dir, '$phase/$name')

        # First commit
        self.populate_data([filename], [first_content])
        self.add_file(volume_id, [filename])
        self.add_metadata(volume_id, [filename], {'name': filename})
        result = self.commit(volume_id)

        self.clone(volume_id, clone_path, '@version:%s' % result['commit_id'])
        flatten_dir(self.clone_dir)
        self.assertEqualDir(self.data_dir, self.clone_dir)
        remove_dir(self.clone_dir)

        # Second commit, change the file content
        self.populate_data([filename], [second_content])
        self.add_file(volume_id, [filename])
        result = self.commit(volume_id)

        self.clone(volume_id, clone_path, '@version:%s' % result['commit_id'])
        flatten_dir(self.clone_dir)
        self.assertEqualDir(self.data_dir, self.clone_dir)
        remove_dir(self.clone_dir)

        # Third commit, change the file content back to the original
        self.populate_data([filename], [first_content])
        self.add_file(volume_id, [filename])
        result = self.commit(volume_id)

        self.clone(volume_id, clone_path, '@version:%s' % result['commit_id'])
        flatten_dir(self.clone_dir)
        self.assertEqualDir(self.data_dir, self.clone_dir)
        remove_dir(self.clone_dir)
