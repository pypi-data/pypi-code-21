import unittest

from cloudshell.devices.standards.networking.autoload_structure import AVAILABLE_SHELL_TYPES
from cloudshell.devices.standards.networking.autoload_structure import GenericResource
from cloudshell.devices.standards.networking.autoload_structure import GenericChassis
from cloudshell.devices.standards.networking.autoload_structure import GenericSubModule
from cloudshell.devices.standards.networking.autoload_structure import GenericModule
from cloudshell.devices.standards.networking.autoload_structure import GenericPort
from cloudshell.devices.standards.networking.autoload_structure import GenericPortChannel
from cloudshell.devices.standards.networking.autoload_structure import GenericPowerPort


class TestGenericResource(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.shell_type = AVAILABLE_SHELL_TYPES[-1]
        self.resource = GenericResource(shell_name=self.shell_name,
                                        name=self.name,
                                        unique_id=self.unique_id,
                                        shell_type=self.shell_type)

    def test_generic_resource_no_shell_name(self):
        name = "test name"
        unique_id = "test unique id"
        shell_type = ""
        resource = GenericResource(shell_name="",
                                   name=name,
                                   unique_id=unique_id,
                                   shell_type=shell_type)
        self.assertEqual(resource.shell_name, "")
        self.assertEqual(resource.shell_type, "")

    def test_contact_name_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Contact Name"): expected_val
        }
        # act
        result = self.resource.contact_name
        # verify
        self.assertEqual(result, expected_val)

    def test_contact_name_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.contact_name = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Contact Name")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_os_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "OS Version"): expected_val
        }
        # act
        result = self.resource.os_version
        # verify
        self.assertEqual(result, expected_val)

    def test_os_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.os_version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "OS Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_system_name_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "System Name"): expected_val
        }
        # act
        result = self.resource.system_name
        # verify
        self.assertEqual(result, expected_val)

    def test_system_name_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.system_name = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "System Name")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_vendor_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Vendor"): expected_val
        }
        # act
        result = self.resource.vendor
        # verify
        self.assertEqual(result, expected_val)

    def test_vendor_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.vendor = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Vendor")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_location_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Location"): expected_val
        }
        # act
        result = self.resource.location
        # verify
        self.assertEqual(result, expected_val)

    def test_location_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.location = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Location")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_model_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.shell_type, "Model"): expected_val
        }
        # act
        result = self.resource.model
        # verify
        self.assertEqual(result, expected_val)

    def test_model_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.shell_type, "Model")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericChassis(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericChassis(shell_name=self.shell_name,
                                       name=self.name,
                                       unique_id=self.unique_id)

    def test_model_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model"): expected_val
        }
        # act
        result = self.resource.model
        # verify
        self.assertEqual(result, expected_val)

    def test_model_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericModule(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericModule(shell_name=self.shell_name,
                                      name=self.name,
                                      unique_id=self.unique_id)

    def test_model_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model"): expected_val
        }
        # act
        result = self.resource.model
        # verify
        self.assertEqual(result, expected_val)

    def test_model_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Version"): expected_val
        }
        # act
        result = self.resource.version
        # verify
        self.assertEqual(result, expected_val)

    def test_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericSubModule(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericSubModule(shell_name=self.shell_name,
                                         name=self.name,
                                         unique_id=self.unique_id)

    def test_model_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model"): expected_val
        }
        # act
        result = self.resource.model
        # verify
        self.assertEqual(result, expected_val)

    def test_model_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Version"): expected_val
        }
        # act
        result = self.resource.version
        # verify
        self.assertEqual(result, expected_val)

    def test_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericPort(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericPort(shell_name=self.shell_name,
                                    name=self.name,
                                    unique_id=self.unique_id)

    def test_mac_address_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "MAC Address"): expected_val
        }
        # act
        result = self.resource.mac_address
        # verify
        self.assertEqual(result, expected_val)

    def test_mac_address_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.mac_address = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "MAC Address")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_l2_protocol_type_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "L2 Protocol Type"): expected_val
        }
        # act
        result = self.resource.l2_protocol_type
        # verify
        self.assertEqual(result, expected_val)

    def test_l2_protocol_type_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.l2_protocol_type = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "L2 Protocol Type")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_ipv4_address_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "IPv4 Address"): expected_val
        }
        # act
        result = self.resource.ipv4_address
        # verify
        self.assertEqual(result, expected_val)

    def test_ipv4_address_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.ipv4_address = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "IPv4 Address")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_ipv6_address_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "IPv6 Address"): expected_val
        }
        # act
        result = self.resource.ipv6_address
        # verify
        self.assertEqual(result, expected_val)

    def test_ipv6_address_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.ipv6_address = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "IPv6 Address")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_port_description_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Port Description"): attr_value
        }
        # act
        result = self.resource.port_description
        # verify
        self.assertEqual(result, attr_value)

    def test_port_description_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.port_description = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Port Description")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_bandwidth_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Bandwidth"): attr_value
        }
        # act
        result = self.resource.bandwidth
        # verify
        self.assertEqual(result, attr_value)

    def test_bandwidth_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.bandwidth = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Bandwidth")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_mtu_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "MTU"): attr_value
        }
        # act
        result = self.resource.mtu
        # verify
        self.assertEqual(result, attr_value)

    def test_mtu_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.mtu = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "MTU")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_duplex_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Duplex"): attr_value
        }
        # act
        result = self.resource.duplex
        # verify
        self.assertEqual(result, attr_value)

    def test_duplex_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.duplex = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Duplex")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_adjacent_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Adjacent"): attr_value
        }
        # act
        result = self.resource.adjacent
        # verify
        self.assertEqual(result, attr_value)

    def test_adjacent_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.adjacent = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Adjacent")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_auto_negotiation_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Auto Negotiation"): attr_value
        }
        # act
        result = self.resource.auto_negotiation
        # verify
        self.assertEqual(result, attr_value)

    def test_auto_negotiation_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.auto_negotiation = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Auto Negotiation")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericPowerPort(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericPowerPort(shell_name=self.shell_name,
                                         name=self.name,
                                         unique_id=self.unique_id)

    def test_model_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Model"): expected_val
        }
        # act
        result = self.resource.model
        # verify
        self.assertEqual(result, expected_val)

    def test_model_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.model = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Model")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_serial_number_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Serial Number"): expected_val
        }
        # act
        result = self.resource.serial_number
        # verify
        self.assertEqual(result, expected_val)

    def test_serial_number_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.serial_number = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Serial Number")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_version_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Version"): expected_val
        }
        # act
        result = self.resource.version
        # verify
        self.assertEqual(result, expected_val)

    def test_version_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.version = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Version")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_port_description_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Port Description"): attr_value
        }
        # act
        result = self.resource.port_description
        # verify
        self.assertEqual(result, attr_value)

    def test_port_description_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.port_description = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Port Description")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])


class TestGenericPortChannel(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"
        self.resource = GenericPortChannel(shell_name=self.shell_name,
                                           name=self.name,
                                           unique_id=self.unique_id)

    def test_associated_ports_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Associated Ports"): expected_val
        }
        # act
        result = self.resource.associated_ports
        # verify
        self.assertEqual(result, expected_val)

    def test_associated_ports_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.associated_ports = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Associated Ports")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_ipv4_address_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "IPv4 Address"): expected_val
        }
        # act
        result = self.resource.ipv4_address
        # verify
        self.assertEqual(result, expected_val)

    def test_ipv4_address_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.ipv4_address = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "IPv4 Address")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_ipv6_address_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        expected_val = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "IPv6 Address"): expected_val
        }
        # act
        result = self.resource.ipv6_address
        # verify
        self.assertEqual(result, expected_val)

    def test_ipv6_address_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.ipv6_address = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "IPv6 Address")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])

    def test_port_description_getter(self):
        """Check that property will return needed attribute value from the internal attributes dictionary"""
        attr_value = "test value"
        self.resource.attributes = {
            "{}{}".format(self.resource.namespace, "Port Description"): attr_value
        }
        # act
        result = self.resource.port_description
        # verify
        self.assertEqual(result, attr_value)

    def test_port_description_setter(self):
        """Check that property setter will correctly add attribute value into the internal attributes dictionary"""
        attr_value = "test value"
        # act
        self.resource.port_description = attr_value
        # verify
        attr_key = "{}{}".format(self.resource.namespace, "Port Description")
        self.assertIn(attr_key, self.resource.attributes)
        self.assertEqual(attr_value, self.resource.attributes[attr_key])
