# -*- coding: utf-8 -*-

import unittest
import os

from tcell_agent.config import TcellAgentConfiguration


class TcellAgentConfigurationTest(unittest.TestCase):
    def test_setting_max_data_ex_db_records_per_request(self):
        full_path = os.path.realpath(__file__)
        data_exposure_config = os.path.join(os.path.dirname(full_path), "data_exposure.config")
        configuration = TcellAgentConfiguration(data_exposure_config)

        self.assertEqual(configuration.max_data_ex_db_records_per_request, 100)

    def default_allow_payloads_test(self):
        full_path = os.path.realpath(__file__)
        simple_config = os.path.join(os.path.dirname(full_path), "simpel.config")
        configuration = TcellAgentConfiguration(simple_config)

        self.assertTrue(configuration.allow_payloads)
