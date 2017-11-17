# -*- coding: utf-8 -*-
"""
Datary python sdk Datasets test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryDatasetsTestCase(DataryTestCase):
    """
    DataryDatasets Test case
    """

    @mock.patch('datary.requests.requests.requests.get')
    def test_get_kern(self, mock_request):
        """
        Test Datary datasets get_kern
        """

        mock_request.return_value = MockRequestResponse(
            "", json=self.element.get('data', {}).get('kern'))
        kern = self.datary.get_kern(self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertTrue(isinstance(kern, dict))
        self.assertEqual(kern, self.element.get('data', {}).get('kern'))

        mock_request.return_value = MockRequestResponse("", status_code=500)
        kern2 = self.datary.get_kern(self.dataset_uuid, self.repo_uuid)
        self.assertTrue(isinstance(kern2, dict))
        self.assertEqual(kern2, {})

    @mock.patch('datary.requests.requests.requests.get')
    def test_get_metadata(self, mock_request):
        """
        Test Datary datasets get_metadata
        """
        mock_request.return_value = MockRequestResponse(
            "", json=self.element.get('data', {}).get('meta'))
        metadata = self.datary.get_metadata(self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertTrue(isinstance(metadata, dict))
        self.assertEqual(metadata, self.element.get('data', {}).get('meta'))

        mock_request.return_value = MockRequestResponse("", status_code=500)
        metadata2 = self.datary.get_metadata(self.dataset_uuid, self.repo_uuid)
        self.assertTrue(isinstance(metadata2, dict))
        self.assertEqual(metadata2, {})

    @mock.patch('datary.requests.requests.requests.get')
    def test_get_original(self, mock_request):
        """
        Test Datary datasets get_original
        """

        mock_request.return_value = MockRequestResponse("", json=self.original)
        original = self.datary.get_original(self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertTrue(isinstance(original, dict))
        self.assertEqual(original, self.original)
        mock_request.reset_mock()

        # not dataset_uuid, introduced
        original2 = self.datary.get_original(
            self.dataset_uuid, self.repo_uuid, self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertTrue(isinstance(original2, dict))
        self.assertEqual(original2, self.original)
        mock_request.reset_mock()

        # not dataset_uuid, introduced
        original3 = self.datary.get_original(
            self.dataset_uuid, wdir_uuid=self.wdir_uuid)
        self.assertEqual(mock_request.call_count, 1)
        self.assertTrue(isinstance(original3, dict))
        self.assertEqual(original3, self.original)
        mock_request.reset_mock()

        mock_request.side_effect = iter([
            MockRequestResponse("", status_code=500),
            MockRequestResponse("", json=self.original)
        ])

        original4 = self.datary.get_original(self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 2)
        self.assertTrue(isinstance(original4, dict))
        self.assertEqual(original4, self.original)
        mock_request.reset_mock()

        mock_request.side_effect = iter([
            MockRequestResponse("", status_code=500),
            MockRequestResponse("", status_code=500)
        ])

        original4b = self.datary.get_original(
            self.dataset_uuid, self.repo_uuid)
        self.assertEqual(mock_request.call_count, 2)
        self.assertTrue(isinstance(original4b, dict))
        self.assertEqual(original4b, {})
        mock_request.reset_mock()

        # not dataset_uuid, introduced
        original5 = self.datary.get_original(
            MockRequestResponse("", status_code=500))

        self.assertEqual(mock_request.call_count, 0)
        self.assertTrue(isinstance(original5, dict))
        self.assertEqual(original5, {})
        mock_request.reset_mock()

        # scope
        mock_request.side_effect = iter(
            [MockRequestResponse("", json=self.original),
             MockRequestResponse("", json=self.original)])
        original6 = self.datary.get_original(
            self.dataset_uuid, self.repo_uuid, scope='repo')
        self.assertEqual(mock_request.call_count, 1)
        self.assertTrue(isinstance(original6, dict))
        self.assertEqual(original6, self.original)

    @mock.patch('datary.filetrees.DataryFiletrees.get_wdir_filetree')
    @mock.patch('datary.filetrees.DataryFiletrees.get_wdir_changes')
    def test_get_dataset_uuid(self, mock_get_wdir_changes,
                              mock_get_wdir_filetree):
        """
        Test Datary datasets get_datasaet_uuid
        """
        mock_get_wdir_filetree.return_value = self.filetree
        mock_get_wdir_changes.return_value = self.changes

        path = 'b'
        basename = 'bb'

        empty_result = self.datary.get_dataset_uuid(self.wdir_uuid)
        self.assertEqual(empty_result, None)

        from_changes_result = self.datary.get_dataset_uuid(
            self.wdir_uuid, path, basename)
        self.assertEqual(from_changes_result, 'inode1_changes')
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

        mock_get_wdir_filetree.reset_mock()
        mock_get_wdir_changes.reset_mock()

        # retrive from filetree
        path = ''
        basename = 'c'

        from_commit_result = self.datary.get_dataset_uuid(
            self.wdir_uuid, path, basename)

        self.assertEqual(from_commit_result, 'c_sha1')
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

        mock_get_wdir_filetree.reset_mock()
        mock_get_wdir_changes.reset_mock()

        # NOT exists
        path = 'bb'
        basename = 'b'

        no_result = self.datary.get_dataset_uuid(
            self.wdir_uuid, path, basename)
        self.assertEqual(no_result, None)
        self.assertEqual(mock_get_wdir_filetree.call_count, 1)
        self.assertEqual(mock_get_wdir_changes.call_count, 1)

    @mock.patch('datary.requests.requests.requests.get')
    def test_get_commited_dataset_uuid(self, mock_request):
        """
        Test Datary get_commited_dataset_uuid
        """

        # no args path and basename introduced
        mock_request.return_value = MockRequestResponse(
            "", json=self.dataset_uuid)
        result_no_pathname = self.datary.get_commited_dataset_uuid(
            self.wdir_uuid)
        self.assertEqual(result_no_pathname, {})
        self.assertEqual(mock_request.call_count, 0)

        # good case
        result = self.datary.get_commited_dataset_uuid(
            self.wdir_uuid, 'path', 'basename')
        self.assertEqual(result, self.dataset_uuid)
        self.assertEqual(mock_request.call_count, 1)

        # datary request return None
        mock_request.reset_mock()
        mock_request.return_value = MockRequestResponse("", status_code=500)

        no_response_result = self.datary.get_commited_dataset_uuid(
            self.wdir_uuid, 'path', 'basename')
        self.assertEqual(no_response_result, {})
        self.assertEqual(mock_request.call_count, 1)
