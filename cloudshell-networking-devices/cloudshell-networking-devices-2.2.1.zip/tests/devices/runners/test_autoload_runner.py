import unittest

import mock

from cloudshell.devices.runners.autoload_runner import AutoloadRunner


class TestAutoloadRunner(unittest.TestCase):
    def setUp(self):
        class TestedClass(AutoloadRunner):
            @property
            def autoload_flow(self):
                pass

        self.tested_class = TestedClass
        self.resource_conf = mock.MagicMock()
        self.runner = TestedClass(resource_config=self.resource_conf)

    def test_autoload_flow(self):
        """Check that instance can't be instantiated without implementation of the "autoload_flow" method"""
        class TestedClass(AutoloadRunner):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods autoload_flow"):
            TestedClass(resource_config=self.resource_conf)

    def test_discover(self):
        """Check that method will use execute autoload_flow"""
        expected_res = mock.MagicMock()
        # act
        with mock.patch.object(self.tested_class, "autoload_flow") as autoload_flow:
            autoload_flow.execute_flow.return_value = expected_res
            result = self.runner.discover()

            # verify
            self.assertEqual(result, expected_res)
            autoload_flow.execute_flow.assert_called_once_with(self.resource_conf.supported_os,
                                                               self.resource_conf.shell_name,
                                                               self.resource_conf.family,
                                                               self.resource_conf.name)
