# -*- coding: utf-8 -*-
"""
Datary python sdk Commits test file
"""
from unittest.mock import patch
from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse

import mock


class DataryCommitsTestCase(DataryTestCase):
    """
    Test DataryCommits Test Case
    """

    @mock.patch('datary.requests.requests.requests.post')
    def test_commit(self, mock_request):
        """
        Test Datary commit
        """

        mock_request.return_value = MockRequestResponse("a")
        self.datary.commit(self.repo_uuid, "test commit msg")

        mock_request.return_value = MockRequestResponse("ERR", status_code=500)
        self.datary.commit(self.repo_uuid, "test commit msg")

        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.repos.DataryRepos.get_describerepo')
    @mock.patch('datary.filetrees.DataryFiletrees.get_commit_filetree')
    @mock.patch('datary.datasets.DataryDatasets.get_metadata')
    def test_recollect_last_commit(self, mock_metadata, mock_filetree,
                                   mock_get_describerepo):
        """
        Test datary commits recollect_last_commit
        """
        result_zero = self.datary.recollect_last_commit()
        self.assertEqual(result_zero, [])

        result_zero2 = self.datary.get_last_commit_filetree()
        self.assertEqual(result_zero2, {})

        mock_filetree.return_value = self.filetree
        mock_get_describerepo.return_value = self.json_repo
        mock_metadata.return_value.json.return_value = \
            self.element.get('data', {}).get('meta')
        result = self.datary.recollect_last_commit({'uuid': self.repo_uuid})
        self.assertTrue(mock_filetree.called)
        self.assertTrue(mock_get_describerepo.called)

        mock_get_describerepo.return_value = None
        result2 = self.datary.recollect_last_commit({'uuid': self.repo_uuid})

        mock_filetree.return_value = None
        mock_get_describerepo.return_value = self.json_repo
        result3 = self.datary.recollect_last_commit({'uuid': self.repo_uuid})

        mock_get_describerepo.return_value = {}
        result4 = self.datary.recollect_last_commit({})

        mock_get_describerepo.return_value = {'apex': {}}
        result5 = self.datary.recollect_last_commit({})

        mock_get_describerepo.return_value = {'apex': {}}
        result6 = self.datary.recollect_last_commit({'apex': {}})

        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 3)

        for partial_result in result:
            self.assertEqual(len(partial_result), 4)

        self.assertTrue(isinstance(result2, list))
        self.assertTrue(isinstance(result3, list))
        self.assertTrue(isinstance(result4, list))
        self.assertTrue(isinstance(result5, list))
        self.assertTrue(isinstance(result6, list))
        self.assertEqual(result4, [])
        self.assertEqual(result5, [])
        self.assertEqual(result6, [])

    def test_make_index(self):
        """
        Test Datary make_index
        """
        lista = self.commit_test1
        result = self.datary.make_index(lista)
        expected_values = ['aa_sha1', 'caa_sha1', 'bb_sha1', 'dd_sha1']

        self.assertTrue(isinstance(result, dict))
        for element in result.values():
            self.assertTrue(element.get('sha1') in expected_values)

    def test_compare_commits(self):
        """
        Test Datary compare_commits
        """
        expected = {
            'add': ['caa_sha1'],
            'delete': ['bb_sha1'],
            'update': ['dd2_sha1']
        }

        result = self.datary.compare_commits(
            self.commit_test1, self.commit_test2)

        self.assertEqual(len(result.get('add')), 1)
        self.assertEqual(len(result.get('update')), 1)
        self.assertEqual(len(result.get('delete')), 1)

        for key, value in expected.items():
            elements_sha1 = [
                element.get('sha1') for element in result.get(key)]
            for sha1 in value:
                self.assertTrue(sha1 in elements_sha1)

        with patch('datary.Datary.make_index') as mock_makeindex:
            mock_makeindex.side_effect = Exception('Test Exception')
            result2 = self.datary.compare_commits(
                self.commit_test1, self.commit_test2)

            self.assertTrue(isinstance(result2, dict))
            self.assertEqual(result2, {'update': [], 'delete': [], 'add': []})

    @mock.patch('datary.operations.DataryRemoveOperation.delete_file')
    @mock.patch('datary.operations.DataryAddOperation.add_file')
    @mock.patch('datary.operations.DataryModifyOperation.modify_file')
    def test_operation_commit(self, mock_modify, mock_add, mock_delete):
        """
        Test datary  operation_commit
        """
        self.datary.operation_commit(
            wdir_uuid=self.json_repo.get('workdir').get('uuid'),
            last_commit=self.commit_test1,
            actual_commit=self.commit_test2,
            strict=True)

        self.assertEqual(mock_add.call_count, 1)
        self.assertEqual(mock_delete.call_count, 1)
        self.assertEqual(mock_modify.call_count, 1)

        mock_add.reset_mock()
        mock_modify.reset_mock()
        mock_delete.reset_mock()

        self.datary.operation_commit(
            wdir_uuid=self.json_repo.get('workdir').get('uuid'),
            last_commit=self.commit_test1,
            actual_commit=self.commit_test2,
            strict=False)

        self.assertEqual(mock_add.call_count, 1)
        self.assertEqual(mock_delete.call_count, 0)
        self.assertEqual(mock_modify.call_count, 1)

    @mock.patch('datary.commits.commits.datetime')
    def test_commit_diff_tostring(self, mock_datetime):
        """
        Test Datary commits commit_diff_tostring
        """
        datetime_value = "12/03/1990-12:04"
        mock_datetime.now().strftime.return_value = datetime_value

        test_diff = {'add': [{'path': 'path1', 'basename': 'basename1'}, {
            'path': 'path2', 'basename': 'basename2'}]}
        test_diff_result = (
            'Changes at {}\nADD\n*****************\n+  path1/basename1\n+  '
            'path2/basename2\nDELETE\n*****************\nUPDATE\n***********'
            '******\n'.format(datetime_value))

        # Empty diff
        result = self.datary.commit_diff_tostring([])
        self.assertEqual(result, "")

        result2 = self.datary.commit_diff_tostring(test_diff)
        self.assertEqual(result2, test_diff_result)

        ex = Exception('test exception in datetime')
        mock_datetime.now().strftime.side_effect = ex
        result3 = self.datary.commit_diff_tostring(test_diff)
        self.assertEqual(result3, '')
