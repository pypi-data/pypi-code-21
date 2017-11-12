# Copyright 2012-2014 Ravello Systems, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, print_function

import os
import sys
import logging
import base64

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

if sys.version_info[:2] >= (2,7):
    import unittest
else:
    import unittest2 as unittest

SkipTest = unittest.SkipTest

from ravello_sdk import RavelloClient

__all__ = ['UnitTest', 'IntegrationTest', 'SkipTest', 'unittest']


def setup_logging():
    """Configure a logger to output to stdout."""
    logger = logging.getLogger()
    if logger.handlers:
        return
    logger.setLevel(logging.DEBUG if '-v' in sys.argv else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    template = '%(levelname)s %(message)s'
    handler.setFormatter(logging.Formatter(template))
    logger.addHandler(handler)


class UnitTest(unittest.TestCase):
    """Base class for unit tests."""

    @classmethod
    def setUpClass(cls):
        setup_logging()
        fname = os.path.abspath(__file__)
        cfgname = os.environ.get('TEST_CONFIG')
        if cfgname is None:
            topdir = os.path.split(os.path.split(fname)[0])[0]
            cfgname = os.path.join(topdir, 'test.conf')
        cls.config = ConfigParser()
        cls.config.read(cfgname)

    def random_name(self):
        return base64.b64encode(os.urandom(6)).decode('ascii').rstrip()

    def assertRaises(self, exc, func, *args, **kwargs):
        # Like unittest.assertRaises, but returns the exception.
        try:
            func(*args, **kwargs)
        except exc as e:
            exc = e
        except Exception as e:
            self.fail('Wrong exception raised: {0!s}'.format(e))
        else:
            self.fail('Exception not raised: {0!s}'.format(exc))
        return exc


class IntegrationTest(UnitTest):
    """Base class for integration tests.

    Integration tests run with a connected client to the API, which is
    available under the "client" property.
    """

    pubkey = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDi3GUFtZA4WxysevYPPrp3G4' \
             'W3sehLJOyEp4vf5G/rLfoKwz1JXd3gqq8snoSwYefQSAW0PKPff6lxyaraFqq4' \
             '+vzNg4rAHJSdBhAHLWlcNWSh8UZOGD11vgGdOLrDBPZ8/jKJIZgcFiXjzulMzU' \
             'RKLGx0ZFbUZDfHYIqEpCscnlfG6kenrtWAdCrTkl4CP56xcOY91qx4s9Ll0Yvz' \
             'hyF2GiqgCe0eJqNflJkqX+d9e0A3BdIzM//UfYplzmUGimWgGN4vFFa4sspUzq' \
             'gwHV7yZYI7W+Ey5oOOiSpTt1PpkPHIBaUEmg37/7Pq6PuQxfs18QLPK1DuJz6g' \
             'UsCjFRFl testkey'

    def setUp(self):
        url = self.config.get('integration', 'url') or None
        username = self.config.get('integration', 'username')
        password = self.config.get('integration', 'password')
        self.client = RavelloClient()
        self.client.connect(url)
        self.client.login(username, password)

    def tearDown(self):
        self.client.logout()
        self.client.close()
