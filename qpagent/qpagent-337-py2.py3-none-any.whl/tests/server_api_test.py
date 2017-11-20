#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import agent.qualityplatform.api as server_api


class TestServerApi(unittest.TestCase):
    def test_add_jira_issue(self):
        self.assertIsNotNone(server_api.add_jira_issue('UTMT', 'Monkey Error Log', 'test'))


if __name__ == '__main__':
    unittest.main()
