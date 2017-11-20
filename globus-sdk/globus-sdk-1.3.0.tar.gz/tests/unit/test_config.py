import os
try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk
from globus_sdk.config import GlobusConfigParser

from tests.framework import get_fixture_file_dir, CapturedIOTestCase


class ConfigParserTests(CapturedIOTestCase):

    def tearDown(self):
        super(ConfigParserTests, self).tearDown()
        globus_sdk.config._parser = None

    def _load_config_file(self, filename):
        """
        Uses patch to bypass normal _load_config to load filename instead
        """
        filename = os.path.join(
            get_fixture_file_dir(), 'sample_configs', filename)

        globus_sdk.config._parser = None

        def loadconf(cfgparser):
            cfgparser._parser.read([filename])

        with mock.patch(
                'globus_sdk.config.GlobusConfigParser._load_config', loadconf):
            globus_sdk.config._get_parser()

    def test_get_lib_config_path(self):
        """
        Gets the globus.cfg file path, confirms valid config file exists there
        """
        file_name = "globus.cfg"
        path = globus_sdk.config._get_lib_config_path()
        self.assertEqual(path[-(len(file_name)):], file_name)

        # make sure the cfg file at least has transfer and auth services
        with open(path, "r") as f:
            file_text = f.read()
            self.assertIn("transfer_service", file_text)
            self.assertIn("auth_service", file_text)

    def test_init_and_load_config(self):
        """
        Creates a GlobusConfigParser object, veriries that calling _load_config
        in __init__ gets general values for the internal ConfigParser
        """
        globus_parser = globus_sdk.config.GlobusConfigParser()
        general_items = globus_parser._parser.items("general")
        self.assertNotEqual(general_items, None)

    def test_get(self):
        """
        Confirms that get reads expected results
        Tests section, environment, failover_to_general, and check_env params
        """
        self._load_config_file("get_test.cfg")
        gcp = globus_sdk.config._get_parser()
        os.environ["GLOBUS_SDK_OPTION"] = "os_environ_value"

        # no parameters
        self.assertEqual(gcp.get("option"), "general_value")
        # section
        self.assertEqual(gcp.get("option", section="section"), "section_value")
        # environment
        self.assertEqual(gcp.get("option", environment="section"),
                         "environment_value")
        # failover_to_general
        self.assertEqual(gcp.get("option", section="nonexistant"), None)
        self.assertEqual(gcp.get("option", section="nonexistant",
                                 failover_to_general=True), "general_value")
        # check_env
        self.assertEqual(gcp.get("option", check_env=True), "os_environ_value")
        # environment > section
        self.assertEqual(gcp.get("option", section="section",
                                 environment="section"), "environment_value")
        # check_env > enviroment
        self.assertEqual(gcp.get("option", environment="section",
                                 check_env=True), "os_environ_value")

    def test_get_parser(self):
        """
        Confirms that at starting time _parser is none,
        but get_parser makes and returns a valid GlobusConfigParser
        """
        self.assertEqual(globus_sdk.config._parser, None)
        self.assertIsInstance(globus_sdk.config._get_parser(),
                              GlobusConfigParser)
        self.assertIsInstance(globus_sdk.config._parser, GlobusConfigParser)

    def test_get_service_url(self):
        """
        Confirms get_service_url returns expected results
        Tests environments, services, and missing values
        """
        self._load_config_file("url_test.cfg")

        # combinations of environments and services
        self.assertEqual(
            globus_sdk.config.get_service_url("default", "auth"),
            "https://auth.globus.org/")
        self.assertEqual(
            globus_sdk.config.get_service_url("default", "transfer"),
            "https://transfer.api.globusonline.org/")
        self.assertEqual(
            globus_sdk.config.get_service_url("beta", "auth"),
            "https://auth.beta.globus.org/")
        self.assertEqual(
            globus_sdk.config.get_service_url("beta", "transfer"),
            "https://transfer.api.beta.globus.org/")

        # missing values
        with self.assertRaises(ValueError):
            globus_sdk.config.get_service_url("nonexistent", "auth")

    def test_get_ssl_verify(self):
        """
        Confirms get_ssl_verify returns expected results
        Tests true/false, and invalid values
        """
        self._load_config_file("ssl_test.cfg")

        # true
        self.assertTrue(globus_sdk.config.get_ssl_verify("true"))
        # false
        self.assertFalse(globus_sdk.config.get_ssl_verify("false"))
        # invalid
        with self.assertRaises(ValueError):
            globus_sdk.config.get_ssl_verify("invalid")

    def test_bool_cast(self):
        """
        Confirms bool cast returns correct bools from sets off string values
        """
        true_vals = [str(1), str(True), "1", "YES", "true", "True", "ON"]
        for val in true_vals:
            self.assertTrue(globus_sdk.config._bool_cast(val))
        false_vals = [str(0), str(False), "0", "NO", "false", "False", "OFF"]
        for val in false_vals:
            self.assertFalse(globus_sdk.config._bool_cast(val))
        # invalid string
        with self.assertRaises(ValueError):
            globus_sdk.config._bool_cast("invalid")

    def test_get_default_environ(self):
        """
        Confirms returns "default", or the value of GLOBUS_SDK_ENVIRONMENT
        """
        # default if no environ value exists
        prev_setting = None
        if "GLOBUS_SDK_ENVIRONMENT" in os.environ:
            prev_setting = os.environ["GLOBUS_SDK_ENVIRONMENT"]
            del os.environ["GLOBUS_SDK_ENVIRONMENT"]
        self.assertEqual(globus_sdk.config.get_default_environ(), "default")
        # otherwise environ value
        os.environ["GLOBUS_SDK_ENVIRONMENT"] = "beta"
        self.assertEqual(globus_sdk.config.get_default_environ(), "beta")

        # cleanup for other tests
        if prev_setting:
            os.environ["GLOBUS_SDK_ENVIRONMENT"] = prev_setting
        else:
            del os.environ["GLOBUS_SDK_ENVIRONMENT"]
