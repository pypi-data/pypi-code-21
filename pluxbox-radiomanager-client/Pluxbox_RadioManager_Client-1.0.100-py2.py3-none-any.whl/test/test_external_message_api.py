# coding: utf-8

"""
    RadioManager

    RadioManager

    OpenAPI spec version: 2.0
    Contact: support@pluxbox.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import os
import sys
import unittest

import radiomanager_sdk
from radiomanager_sdk.rest import ApiException
from radiomanager_sdk.apis.external_message_api import ExternalMessageApi


class TestExternalMessageApi(unittest.TestCase):
    """ ExternalMessageApi unit test stubs """

    def setUp(self):
        self.api = radiomanager_sdk.apis.external_message_api.ExternalMessageApi()

    def tearDown(self):
        pass

    def test_queue_external_message(self):
        """
        Test case for queue_external_message

        Queue External Message.
        """
        pass


if __name__ == '__main__':
    unittest.main()
