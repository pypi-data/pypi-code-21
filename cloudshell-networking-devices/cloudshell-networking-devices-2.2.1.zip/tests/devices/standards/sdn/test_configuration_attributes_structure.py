import unittest

import mock

from cloudshell.devices.standards.sdn.configuration_attributes_structure import GenericSDNResource


class TestModule(unittest.TestCase):
    def test_create_networking_resource_from_context(self):
        """Check that method will create and return GenericSDNResource instance from given context"""
        shell_name = "test shell name"
        context = mock.MagicMock()
        # act
        result = GenericSDNResource.from_context(context=context,
                                                 shell_name=shell_name)
        # verify
        self.assertIsInstance(result, GenericSDNResource)


class TestGenericSDNResource(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.resource = GenericSDNResource(shell_name=self.shell_name,
                                           name=self.name)

    def test_parse_ports(self):
        """Check that method will parse ports string into the list"""
        # act
        result = self.resource._parse_ports(ports="openflow:1::eth1;openflow:2::eth2")
        # verify
        self.assertEqual(result, [("openflow:1", "eth1"), ("openflow:2", "eth2")])

    def test_parse_ports_empty_ports(self):
        """Check that method will return an empty list if ports string is empty"""
        # act
        result = self.resource._parse_ports(ports="")
        # verify
        self.assertEqual(result, [])

    def test_user(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.resource.shell_name, "User"): expected_val
        }
        # act
        result = self.resource.user
        # verify
        self.assertEqual(result, expected_val)

    def test_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.resource.shell_name, "Password"): expected_val
        }
        # act
        result = self.resource.password
        # verify
        self.assertEqual(result, expected_val)

    def test_port(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.resource.shell_name, "Controller TCP Port"): expected_val
        }
        # act
        result = self.resource.port
        # verify
        self.assertEqual(result, expected_val)

    def test_scheme(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.resource.shell_name, "Scheme"): expected_val
        }
        # act
        result = self.resource.scheme
        # verify
        self.assertEqual(result, expected_val)

    def test_add_trunk_ports(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test parsed ports"
        self.resource._parse_ports = mock.MagicMock(return_value=expected_val)
        self.resource.attributes = {
            "{}.{}".format(self.resource.shell_name, "Enable Full Trunk Ports"): "test ports"
        }
        # act
        result = self.resource.add_trunk_ports
        # verify
        self.assertEqual(result, expected_val)

    def test_remove_trunk_ports(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test parsed ports"
        self.resource._parse_ports = mock.MagicMock(return_value=expected_val)
        self.resource.attributes = {
            "{}.{}".format(self.resource.shell_name, "Disable Full Trunk Ports"): "test ports"
        }
        # act
        result = self.resource.remove_trunk_ports
        # verify
        self.assertEqual(result, expected_val)
