# coding=utf-8
import os

from tests_data_management.base import BaseTest


class TestDataManagement(BaseTest):

    def testBasicFlow(self):
        """Test basic flow:
        - Create a data volume
        - Add a file
        - Add a metadata
        - Commit
        - Clone
        """
        print('Testing basic flow')

        self.populate_data([
            'foo.txt',
        ])

        volume_id = self.create_data_volume()
        self.add_file(volume_id, ['foo.txt'])
        self.add_metadata(volume_id, ['foo.txt'], {'name': 'foo'})
        commit_id = self.commit(volume_id)

        clone_path = os.path.join(self.clone_dir, '$phase/$name')
        self.clone(volume_id, clone_path, 'name:foo version:%s' % commit_id)

        test_path = os.path.join(self.clone_dir, 'test')
        self.assertEqualDir(self.data_dir, test_path)
