
# -*- coding: utf-8 -*-
"""
Datary python sdk Rename Operation test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryRenameOperationTestCase(DataryTestCase):
    """
    AddOperation Test case
    """

    @mock.patch('datary.Datary.request')
    def test_rename_file(self, mock_request):
        """
        Test add_dir
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.rename_file(
            self.json_repo.get('workdir', {}).get('uuid'),
            {'path': 'test_path/path', 'basename': 'test_basename'},
            {'path': 'test_path/new_path', 'basename': 'test_new_basename'},
            )
        self.assertEqual(mock_request.call_count, 1)

        mock_request.reset_mock()

        mock_request.return_value = None
        self.datary.rename_file(
            self.json_repo.get('workdir', {}).get('uuid'),
            {'path': 'test_path/path', 'basename': 'test_basename'},
            {'path': 'test_path/new_path', 'basename': 'test_new_basename'},
            )
        self.assertEqual(mock_request.call_count, 1)
