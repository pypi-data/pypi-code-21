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
        self.clone(volume_id, self.clone_dir, 'name:foo version:%s' % commit_id)

        train_dir = os.path.join(self.clone_dir, 'train')
        self.assertEqualDir(self.data_dir, train_dir)
