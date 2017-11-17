# -*- coding: utf-8 -*-
"""
Datary python sdk Members test file
"""
import mock

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryMembersTestCase(DataryTestCase):
    """
    Datary Members Test Case
    """

    @mock.patch('datary.requests.requests.requests.get')
    def test_get_members(self, mock_request):
        """
        Test get_members
        =============   =============   ===================================
        Parameter       Type            Description
        =============   =============   ===================================
        mock_request    mock            Mock datary.Datary.request function
        =============   =============   ===================================
        """

        mock_request.return_value = MockRequestResponse(
            "aaa", json=self.members)
        member = self.datary.get_members(member_name='username1')
        self.assertEqual(member, self.members[0])

        member2 = self.datary.get_members(
            member_uuid=self.members[1].get('uuid'))
        self.assertEqual(member2, self.members[1])

        members_fail = self.datary.get_members(member_name='username3')
        self.assertEqual(members_fail, {})

        members_limit = self.datary.get_members()
        assert isinstance(members_limit, list)

    @mock.patch('datary.members.DataryMembers.get_members')
    @mock.patch('datary.requests.requests.requests.get')
    def test_get_member_repos(self, mock_request, mock_get_members):
        """
        Test get_members
        ===============   ======  =============================================
        Parameter         Type      Description
        ===============   ======  =============================================
        mock_request      mock    Mock datary.Datary.request function
        mock_get_members  mock    Mock datary.DataryMember.get_members function
        ================  ======  =============================================
        """
        mock_get_members.return_value = {'uuid': 123, 'name': "test_member"}
        mock_request.return_value = MockRequestResponse(
            'aaa',
            json=[self.json_repo, self.json_repo2])

        # retrieve repos using member_uuid
        repos1 = self.datary.get_member_repos(member_uuid="123")

        self.assertEqual(repos1, [self.json_repo, self.json_repo2])
        self.assertEqual(mock_get_members.call_count, 0)
        self.assertEqual(mock_request.call_count, 1)

        mock_request.reset_mock()
        mock_get_members.reset_mock()

        # retrieve repos using member_name
        repos2 = self.datary.get_member_repos(member_name='test_member')

        self.assertEqual(repos2, [self.json_repo, self.json_repo2])
        self.assertEqual(mock_get_members.call_count, 1)
        self.assertEqual(mock_request.call_count, 1)

        mock_request.reset_mock()
        mock_get_members.reset_mock()

        # fail retrieve repos without passing args
        with self.assertRaises(Exception):
            self.datary.get_member_repos()

        self.assertEqual(mock_get_members.call_count, 0)
        self.assertEqual(mock_request.call_count, 0)

        mock_get_members.return_value = {}
        mock_request.return_value = MockRequestResponse(
            'aaa',
            json=[self.json_repo, self.json_repo2],
            status_code=500)

        # fail retrieve member
        repos3 = self.datary.get_member_repos(member_name='pepe')
        self.assertEqual(repos3, None)
        self.assertEqual(mock_get_members.call_count, 1)
        self.assertEqual(mock_request.call_count, 1)
