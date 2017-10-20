# -*- coding: utf-8 -*-
"""
Datary python sdk Remove Operation test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryRemoveOperationTestCase(DataryTestCase):
    """
    RemoveOperation Test case
    """

    @mock.patch('datary.Datary.request')
    def test_delete_dir(self, mock_request):
        """
        Test operation remove delete_dir
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), "path", "dirname")
        mock_request.return_value = None
        self.datary.delete_dir(self.json_repo.get(
            'workdir', {}).get('uuid'), "path", "dirname")
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_file(self, mock_request):
        """
        Test operation remove delete_file
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.delete_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.request')
    def test_delete_inode(self, mock_request):
        """
        Test operation remove delete_inode
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.delete_inode(self.json_repo.get(
            'workdir', {}).get('uuid'), self.inode)
        mock_request.return_value = None
        self.datary.delete_inode(self.json_repo.get(
            'workdir', {}).get('uuid'), self.inode)
        self.assertEqual(mock_request.call_count, 2)

        mock_request.side_effect = Exception('Test Err exception')
        with self.assertRaises(Exception):
            self.datary.delete_inode(
                self.json_repo.get('workdir', {}).get('uuid'), self.inode)

    @mock.patch('datary.Datary.request')
    def testclear_index(self, mock_request):
        """
        Test operation remove clear_index
        """
        mock_request.return_value = MockRequestResponse("", json={})
        original = self.datary.clear_index(self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(original, True)

        mock_request.reset_mock()
        mock_request.return_value = None
        original2 = self.datary.clear_index(self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertEqual(original2, False)
