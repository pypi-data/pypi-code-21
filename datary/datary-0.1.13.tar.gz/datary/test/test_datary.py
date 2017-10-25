# -*- coding: utf-8 -*-
"""
Datary Module Test
"""

import unittest
from datary import Datary, DatarySizeLimitException
from datary.test.mock_requests import MockRequestResponse


class DataryTestCase(unittest.TestCase):
    """
    Datary Test Case

    Contains DataryTestCase with all test variables who inherits and use all
    the modules.
    """

    # default params to test Datary class
    test_username = 'pepe'
    test_password = 'pass'
    test_token = '123'

    params = {'username': test_username,
              'password': test_password, 'token': test_token}
    datary = Datary(**params)

    url = 'http://datary.io/test'  # not exist, it's false
    repo_uuid = '1234-1234-21-asd-123'
    wdir_uuid = '4456-2123-55-as2-146'
    commit_sha1 = "3256-1125-23-ab3-246"
    dataset_uuid = "9132-3323-15-xs2-627"

    # old_ commit
    commit_test1 = [
        ['a', 'aa', 'data_aa', 'aa_sha1'],
        ['b', 'bb', 'data_bb', 'bb_sha1'],
        ['d', 'dd', 'data_dd', 'dd_sha1']]

    # new_ commit
    commit_test2 = [
        ['a', 'aa', 'data_aa', 'aa_sha1'],
        ['c/a', 'caa', 'data_caa', 'caa_sha1'],
        ['d', 'dd', 'data_dd', 'dd2_sha1']]

    element = {
        'path': 'a', 'basename': 'aa',
        'sha1': 'aa_sha1',
        'data': {
            'kern': {'data_aa': [[4, 5, 6]]},
            'meta': {"sha1": "d1917c11-745c-44e6-5h71-23f30ca527d3"}}}

    original = {'__kern': {'data_aa': [[1, 2, 3]]}, '__meta': {}}

    inode = 'c46ac2d596ee898fd949c0bb0bb8f114482de450'

    json_repo = {
        "owner":   "b22x2h1h-23wf-1j56-253h-21c3u5st3851",
        "creator": "b22x2h1h-23wf-1j56-253h-21c3u5st3851",
        "name": "test_repo",
        "description": "test mocking repo",
        "workdir": {
            "uuid": "s2g5311h-2416-21h2-52u6-23asw22ha2134"
        },
        "apex": {'commit': '123'},
        "visibility": "public",
        "license": {
            "name": "cc-sa"
        },
        "category": "test",
        "status": "active",
        "uuid": "47eq5s12-5el1-2hq2-2ss1-egx517b1w967"
    }

    json_repo2 = {
        "owner":   "d1917c16-741c-11e6-8b77-86f30ca893d3",
        "creator": "d1917c16-741c-11e6-8b77-86f30ca893d3",
        "name": "test_repo2",
        "description": "test mocking repo 2",
        "workdir": {
            "uuid": "d191806c-741c-11e6-8b77-86f30ca893d3"
        },
        "apex": {},
        "visibility": "private",
        "license": {
            "name": "cc-test"
        },
        "category": "test",
        "status": "active",
        "uuid": "0dc6379e-741d-11e6-8b77-86f30ca893d3"
    }

    wdir_json = {
        "tree": "e2d2bcb88032930aacae64dc5d051ed0b03b6bde",
        "changes": {
            "removedElements": [],
            "renamedElements": [],
            "modifiedElements": [],
            "addedElements": []},
        "filetree": {
            "file_test1": "3a26a47b6e7f28c77380eccc8aec23sd6dc0201e",
            "folder_test1": {
                "file_test2": "3a26a47b6e7f28c77380eccc8aec23sd6dc0201e"
            }
        }
    }

    changes = {
        "removedElements": [
            {
                "dirname": "b",
                "basename": "bb",
                "inode": "inode1_changes"
            },
            {
                "dirname": "",
                "basename": "a",
                "inode": "inode2_changes"
            }],
        "renamedElements": [],
        "modifiedElements": [{
            "dirname": "b",
            "basename": "bb",
            "inode": "inode1_changes"
        }],
        "addedElements": [{
            "dirname": "",
            "basename": "d",
            "inode": "inode3_changes"
        }]
    }

    filetree = {
        '__self': '__self_sha1',
        'a': 'a_sha1',
        'b': {
            '__self': '__self_sha1',
            'bb': 'bb_sha1'},
        'c': 'c_sha1'
    }

    categories = [{
        "id": "business",
        "name": "Business",
        "href": "api.datary.io/search/categories/business",
        "icons": {"sm": None, "md": None, "lg": None},
        "locale": {"es-ES": "Negocios"}
    }, {
        "id": "sports",
        "name": "Sports",
        "href": "api.datary.io/search/categories/sports",
        "icons": {"sm": None, "md": None, "lg": None},
        "locale": {"es-ES": "Deportes"}
    }]

    members = [
        {
            "uuid": "b71fb2a2-3b0a-452e-8479-d30f2b42f0a3",
            "username": "username1",
            "signedUpAt": "2016-04-05T19:55:45.315Z",
            "profile": {
                "displayName": "USERNAME 1",
                "avatar": {
                    "thumbnail": "test1.png",
                    "verbatim": "test1.png"
                }
            }
        },
        {
            "uuid": "b71fb2a2-3a0b-407e-9876-d7034b42f0a6",
            "username": "username2",
            "signedUpAt": "2017-02-05T19:55:45.315Z",
            "profile": {
                "displayName": "USERNAME 2",
                "avatar": {
                    "thumbnail": "test2.png",
                    "verbatim": "test2.png"
                }
            }
        },
    ]


class DatarySizeLimitExceptionTestCase(unittest.TestCase):
    """
    DatarySizeLimitException Test Case
    """

    test_msg = 'test_msg'
    path = 'test_path/folder/example'
    size = 9999

    def test_init(self):
        """
        Test init DatarySizeLimitException
        """

        test_ex = DatarySizeLimitException(
            msg=self.test_msg, src_path=self.path, size=self.size)

        self.assertEqual(test_ex.msg, self.test_msg)
        self.assertEqual(test_ex.src_path, self.path)
        self.assertEqual(test_ex.size, self.size)

        self.assertEqual(str(test_ex), ";".join(
            [self.test_msg, self.path, str(self.size)]))


class MockRequestsResponseTestCase(unittest.TestCase):
    """
    MockRequestsResponse Test Case
    """

    def test(self):
        """
        Test MockRequestsResponse
        """
        test = MockRequestResponse('aaaa', path='test_path')
        self.assertEqual(test.text, 'aaaa')
        self.assertEqual(test.path(), 'test_path')
        self.assertEqual(test.encoding(), 'utf-8')
