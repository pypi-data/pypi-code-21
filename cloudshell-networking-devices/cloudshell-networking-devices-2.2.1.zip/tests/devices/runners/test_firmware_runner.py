import unittest

import mock

from cloudshell.devices.runners.firmware_runner import FirmwareRunner


class TestFirmwareRunner(unittest.TestCase):
    def setUp(self):
        class TestedClass(FirmwareRunner):
            @property
            def cli_handler(self):
                pass

            @property
            def load_firmware_flow(self):
                pass

        self.logger = mock.MagicMock()
        self.tested_class = TestedClass
        self.runner = TestedClass(logger=self.logger)

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        class TestedClass(FirmwareRunner):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods cli_handler, load_firmware_flow"):
            TestedClass(logger=self.logger)

    @mock.patch("cloudshell.devices.runners.firmware_runner.UrlParser")
    def test_load_firmware(self, url_parser_class):
        """Check that method will execute load_firmware_flow"""
        url = mock.MagicMock(__contains__=mock.MagicMock(return_value=True))
        url_parser_class.parse_url.return_value = url
        path = "test path"
        vrf_mmgmt_name = "test vrf mgmt name"
        # act
        with mock.patch.object(self.tested_class, "load_firmware_flow") as load_firmware_flow:
            self.runner.load_firmware(path=path, vrf_management_name=vrf_mmgmt_name)
            load_firmware_flow.execute_flow.assert_called_once_with(path,
                                                                    vrf_mmgmt_name,
                                                                    self.runner._timeout)

    @mock.patch("cloudshell.devices.runners.firmware_runner.UrlParser")
    def test_load_firmware_path_with_invalid_path(self, url_parser_class):
        """Check that method will raise exception if path is invalid"""
        url = mock.MagicMock(__contains__=mock.MagicMock(return_value=False))
        url_parser_class.parse_url.return_value = url
        path = "test path"
        vrf_mmgmt_name = "test vrf mgmt name"
        # act
        with self.assertRaisesRegexp(Exception, "Path is wrong or empty"):
            self.runner.load_firmware(path=path, vrf_management_name=vrf_mmgmt_name)
