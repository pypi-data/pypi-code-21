import os
import unittest
import yaml
from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.test import TestCase

class TestLogin(TestCase):

    def test_login(self):
        logged_in_org = self.client.get_org()
        assert self.config['vcd']['org'] == logged_in_org.get('name')

if __name__ == '__main__':
    unittest.main()
