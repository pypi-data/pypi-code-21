# -*- coding: utf-8 -*-
"""
Datary python sdk Clean Operation test file
"""
import mock
from datary.test.test_datary import DataryTestCase


class DataryCleanOperationTestCase(DataryTestCase):
    """
    Datary CleanOperation Test Case

    """
    @mock.patch('datary.operations.DataryRemoveOperation.delete_file')
    @mock.patch('datary.filetrees.DataryFiletrees.get_wdir_filetree')
    @mock.patch('datary.operations.DataryRemoveOperation.clear_index')
    @mock.patch('datary.repos.DataryRepos.get_describerepo')
    def test_clean_repo(self, mock_get_describerepo, mockclear_index,
                        mock_get_wdir_filetree, mock_delete_file):
        """
        Test operation remove clean_repo
        """
        mock_get_describerepo.return_value = self.json_repo
        mock_get_wdir_filetree.return_value = self.filetree

        self.datary.clean_repo(self.repo_uuid)

        self.assertEqual(mock_delete_file.call_count, 3)
        self.assertEqual(mockclear_index.call_count, 1)
        self.assertEqual(mock_get_describerepo.call_count, 1)
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)

        # reset mocks
        mock_get_describerepo.reset_mock()
        mockclear_index.reset_mock()
        mock_get_wdir_filetree.reset_mock()
        mock_delete_file.reset_mock()

        # describe repo retrieve None
        mock_get_wdir_filetree.return_value = self.filetree
        mock_get_describerepo.return_value = None

        self.datary.clean_repo(self.repo_uuid)

        self.assertEqual(mock_delete_file.call_count, 0)
        self.assertEqual(mockclear_index.call_count, 0)
        self.assertEqual(mock_get_describerepo.call_count, 1)
        self.assertEqual(mock_get_wdir_filetree.call_count, 0)
