# -*- coding: utf-8 -*-
"""
Datary python sdk Repos test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryReposTestCase(DataryTestCase):
    """
    DataryRepos Test case
    """

    @mock.patch('datary.requests.requests.requests')
    @mock.patch('datary.repos.DataryRepos.get_describerepo')
    def test_create_repo(self, mock_describerepo, mock_request):
        """
        Test create_repo
        """
        mock_describerepo.return_value = MockRequestResponse(
            "", json=self.json_repo)
        mock_request.post.return_value = MockRequestResponse(
            "aaa", json=self.json_repo)
        repo = self.datary.create_repo('repo_name', 'category_test', amount=1)
        repo2 = self.datary.create_repo(
            'repo_nane', 'category_test', repo_uuid='123', amount=1)

        mock_request.post.side_effect = Exception('Amount not introduced')
        mock_describerepo.return_value = {}
        repo4 = self.datary.create_repo(
            'repo_nane', 'category_test', repo_uuid='123')

        self.assertEqual(repo.json().get('uuid'),
                         '47eq5s12-5el1-2hq2-2ss1-egx517b1w967')
        self.assertEqual(repo2.json().get('uuid'),
                         '47eq5s12-5el1-2hq2-2ss1-egx517b1w967')
        self.assertEqual(mock_request.post.call_count, 1)
        self.assertEqual(mock_describerepo.call_count, 3)
        self.assertEqual(repo4, {})

    @mock.patch('datary.requests.requests.requests')
    def test_describerepo(self, mock_request):
        """
        Test describerepo
        """
        mock_request.get.return_value = MockRequestResponse(
            "aaa", json=self.json_repo)
        repo = self.datary.get_describerepo(self.repo_uuid)
        self.assertEqual(mock_request.get.call_count, 1)
        assert isinstance(repo, dict)
        self.assertEqual(repo.get('name'), 'test_repo')

        mock_request.get.return_value = MockRequestResponse(
            "", status_code=204, json=self.json_repo)
        repo2 = self.datary.get_describerepo(self.repo_uuid)
        assert isinstance(repo, dict)
        self.assertEqual(repo2.get('name'), 'test_repo')

        mock_request.get.return_value = MockRequestResponse(
            "aaa", json=[self.json_repo, self.json_repo2])
        repo3 = self.datary.get_describerepo(
            '0dc6379e-741d-11e6-8b77-86f30ca893d3')
        assert isinstance(repo, dict)
        self.assertEqual(repo3.get('name'), 'test_repo2')

        repo4 = self.datary.get_describerepo(repo_name='test_repo2')
        assert isinstance(repo, dict)
        self.assertEqual(repo4.get('name'), 'test_repo2')

        mock_request.get.return_value = MockRequestResponse("a", json=[])
        repo5 = self.datary.get_describerepo(repo_name='test_repo2')
        self.assertEqual(repo5, {})

        # check fail requests returns None
        mock_request.get.return_value = MockRequestResponse(
            "Break test", status_code=500)
        repo6 = self.datary.get_describerepo(repo_name='test_repo2')
        self.assertEqual(repo6, {})

    @mock.patch('datary.requests.requests.requests')
    def test_deleterepo(self, mock_request):
        """
        Test deleterepo
        """
        mock_request.delete.return_value = MockRequestResponse(
            "Repo {} deleted".format('123'))
        result = self.datary.delete_repo(repo_uuid='123')
        self.assertEqual(result, 'Repo 123 deleted')

        with self.assertRaises(Exception):
            self.datary.delete_repo()
