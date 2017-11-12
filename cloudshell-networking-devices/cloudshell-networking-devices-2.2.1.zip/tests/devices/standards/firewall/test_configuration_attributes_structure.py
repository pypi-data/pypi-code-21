import unittest

import mock

from cloudshell.devices.standards.firewall.configuration_attributes_structure import GenericFirewallResource
from cloudshell.devices.standards.firewall.configuration_attributes_structure import create_firewall_resource_from_context


class TestModule(unittest.TestCase):
    def test_create_networking_resource_from_context(self):
        """Check that method will create and return GenericNetworkingResource instance from given context"""
        shell_name = "test shell name"
        supported_os = "test OS"
        context = mock.MagicMock()
        # act
        result = create_firewall_resource_from_context(shell_name=shell_name,
                                                       supported_os=supported_os,
                                                       context=context)
        # verify
        self.assertIsInstance(result, GenericFirewallResource)


class TestGenericFirewallResource(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.supported_os = ["test OS"]
        self.resource = GenericFirewallResource(shell_name=self.shell_name,
                                                name=self.name,
                                                supported_os=self.supported_os)

    def test_backup_location(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Backup Location"): expected_val
        }
        # act
        result = self.resource.backup_location
        # verify
        self.assertEqual(result, expected_val)

    def test_backup_type(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Backup Type"): expected_val
        }
        # act
        result = self.resource.backup_type
        # verify
        self.assertEqual(result, expected_val)

    def test_backup_user(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Backup User"): expected_val
        }
        # act
        result = self.resource.backup_user
        # verify
        self.assertEqual(result, expected_val)

    def test_backup_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Backup Password"): expected_val
        }
        # act
        result = self.resource.backup_password
        # verify
        self.assertEqual(result, expected_val)

    def test_user(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "User"): expected_val
        }
        # act
        result = self.resource.user
        # verify
        self.assertEqual(result, expected_val)

    def test_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Password"): expected_val
        }
        # act
        result = self.resource.password
        # verify
        self.assertEqual(result, expected_val)

    def test_enable_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Enable Password"): expected_val
        }
        # act
        result = self.resource.enable_password
        # verify
        self.assertEqual(result, expected_val)

    def test_power_management(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Power Management"): expected_val
        }
        # act
        result = self.resource.power_management
        # verify
        self.assertEqual(result, expected_val)

    def test_sessions_concurrency_limit(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Sessions Concurrency Limit"): expected_val
        }
        # act
        result = self.resource.sessions_concurrency_limit
        # verify
        self.assertEqual(result, expected_val)

    def test_snmp_read_community(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "SNMP Read Community"): expected_val
        }
        # act
        result = self.resource.snmp_read_community
        # verify
        self.assertEqual(result, expected_val)

    def test_snmp_write_community(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "SNMP Write Community"): expected_val
        }
        # act
        result = self.resource.snmp_write_community
        # verify
        self.assertEqual(result, expected_val)

    def test_snmp_v3_user(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "SNMP V3 User"): expected_val
        }
        # act
        result = self.resource.snmp_v3_user
        # verify
        self.assertEqual(result, expected_val)

    def test_snmp_v3_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "SNMP V3 Password"): expected_val
        }
        # act
        result = self.resource.snmp_v3_password
        # verify
        self.assertEqual(result, expected_val)

    def test_snmp_v3_private_key(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "SNMP V3 Private Key"): expected_val
        }
        # act
        result = self.resource.snmp_v3_private_key
        # verify
        self.assertEqual(result, expected_val)

    def test_snmp_version(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "SNMP Version"): expected_val
        }
        # act
        result = self.resource.snmp_version
        # verify
        self.assertEqual(result, expected_val)

    def test_enable_snmp(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Enable SNMP"): expected_val
        }
        # act
        result = self.resource.enable_snmp
        # verify
        self.assertEqual(result, expected_val)

    def test_disable_snmp(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Disable SNMP"): expected_val
        }
        # act
        result = self.resource.disable_snmp
        # verify
        self.assertEqual(result, expected_val)

    def test_console_server_ip_address(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Console Server IP Address"): expected_val
        }
        # act
        result = self.resource.console_server_ip_address
        # verify
        self.assertEqual(result, expected_val)

    def test_console_user(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Console User"): expected_val
        }
        # act
        result = self.resource.console_user
        # verify
        self.assertEqual(result, expected_val)

    def test_console_port(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Console Port"): expected_val
        }
        # act
        result = self.resource.console_port
        # verify
        self.assertEqual(result, expected_val)

    def test_console_password(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "Console Password"): expected_val
        }
        # act
        result = self.resource.console_password
        # verify
        self.assertEqual(result, expected_val)

    def test_cli_connection_type(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "CLI Connection Type"): expected_val
        }
        # act
        result = self.resource.cli_connection_type
        # verify
        self.assertEqual(result, expected_val)

    def test_cli_tcp_port(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "CLI TCP Port"): expected_val
        }
        # act
        result = self.resource.cli_tcp_port
        # verify
        self.assertEqual(result, expected_val)

    def test_vrf_management_name(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}.{}".format(self.shell_name, "VRF Management Name"): expected_val
        }
        # act
        result = self.resource.vrf_management_name
        # verify
        self.assertEqual(result, expected_val)
