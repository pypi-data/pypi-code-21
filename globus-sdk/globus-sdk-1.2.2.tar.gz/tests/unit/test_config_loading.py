"""
Test Config Loading produces expected results.
"""

import os

try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk.config

from tests.framework import get_fixture_file_dir, CapturedIOTestCase


class ConfigLoaderTests(CapturedIOTestCase):
    def tearDown(self):
        globus_sdk.config._parser = None

    def _load_config_file(self, filename):
        filename = os.path.join(
            get_fixture_file_dir(), 'sample_configs', filename)

        globus_sdk.config._parser = None

        def loadconf(cfgparser):
            cfgparser._parser.read([filename])

        with mock.patch(
                'globus_sdk.config.GlobusConfigParser._load_config', loadconf):
            globus_sdk.config._get_parser()

    def test_verify_ssl_true(self):
        self._load_config_file('verify_ssl_true.cfg')

        assert globus_sdk.config.get_ssl_verify('default') is True

    def test_verify_ssl_false(self):
        self._load_config_file('verify_ssl_false.cfg')

        assert globus_sdk.config.get_ssl_verify('default') is False

    def test_verify_ssl_invalid(self):
        self._load_config_file('verify_ssl_invalid.cfg')

        with self.assertRaises(ValueError):
            globus_sdk.config.get_ssl_verify('default')
