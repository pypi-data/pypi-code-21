# coding: utf-8

"""
Copyright 2016 SmartBear Software

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   ref: https://github.com/swagger-api/swagger-codegen
"""

from __future__ import absolute_import

import os
import sys
import unittest

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.healthcheck_api import HealthcheckApi


class TestHealthcheckApi(unittest.TestCase):
    """ HealthcheckApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.healthcheck_api.HealthcheckApi()

    def tearDown(self):
        pass

    def test_create_healthcheck_evaluation(self):
        """
        Test case for create_healthcheck_evaluation

        
        """
        pass

    def test_create_healthcheck_parameter(self):
        """
        Test case for create_healthcheck_parameter

        
        """
        pass

    def test_get_healthcheck_checklist(self):
        """
        Test case for get_healthcheck_checklist

        
        """
        pass

    def test_get_healthcheck_checklists(self):
        """
        Test case for get_healthcheck_checklists

        
        """
        pass

    def test_get_healthcheck_evaluation(self):
        """
        Test case for get_healthcheck_evaluation

        
        """
        pass

    def test_get_healthcheck_item(self):
        """
        Test case for get_healthcheck_item

        
        """
        pass

    def test_get_healthcheck_items(self):
        """
        Test case for get_healthcheck_items

        
        """
        pass

    def test_get_healthcheck_parameter(self):
        """
        Test case for get_healthcheck_parameter

        
        """
        pass

    def test_list_healthcheck_evaluations(self):
        """
        Test case for list_healthcheck_evaluations

        
        """
        pass

    def test_list_healthcheck_parameters(self):
        """
        Test case for list_healthcheck_parameters

        
        """
        pass

    def test_update_healthcheck_evaluation(self):
        """
        Test case for update_healthcheck_evaluation

        
        """
        pass

    def test_update_healthcheck_parameter(self):
        """
        Test case for update_healthcheck_parameter

        
        """
        pass


if __name__ == '__main__':
    unittest.main()