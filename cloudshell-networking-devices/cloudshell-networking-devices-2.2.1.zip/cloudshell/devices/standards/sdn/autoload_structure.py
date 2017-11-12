from cloudshell.devices.standards.base import AbstractResource
from cloudshell.devices.standards.validators import attr_length_validator

AVAILABLE_SHELL_TYPES = ["CS_SDNController"]


class SDNControllerResource(AbstractResource):
    RESOURCE_MODEL = "SDN Controller"
    RELATIVE_PATH_TEMPLATE = ""

    def __init__(self, shell_name, name, unique_id, shell_type="CS_SDNController"):
        super(SDNControllerResource, self).__init__(shell_name, name, unique_id)

        if shell_name:
            self.shell_name = "{}.".format(shell_name)
            if shell_type in AVAILABLE_SHELL_TYPES:
                self.shell_type = "{}.".format(shell_type)
            else:
                raise Exception(self.__class__.__name__, "Unavailable shell type {shell_type}."
                                                         "Shell type should be one of: {avail}"
                                .format(shell_type=shell_type, avail=", ".join(AVAILABLE_SHELL_TYPES)))
        else:
            self.shell_name = ""
            self.shell_type = ""

    @property
    def model_name(self):
        """SDN Controller model name

        :rtype: str
        """
        return self.attributes.get("{}Model Name".format(self.shell_type), None)

    @model_name.setter
    @attr_length_validator
    def model_name(self, value):
        """Set SDN Controller model name"""
        self.attributes["{}Model Name".format(self.shell_type)] = value


class GenericSDNSwitch(AbstractResource):
    RESOURCE_MODEL = "Generic SDN Switch"
    RELATIVE_PATH_TEMPLATE = "OF"

    @property
    def model_name(self):
        """SDN Switch model name

        :rtype: str
        """
        return self.attributes.get("{}Model Name".format(self.namespace), None)

    @model_name.setter
    @attr_length_validator
    def model_name(self, value):
        """Set SDN Switch model name"""
        self.attributes["{}Model Name".format(self.namespace)] = value


class GenericSDNPort(AbstractResource):
    RESOURCE_MODEL = "Generic SDN Port"
    RELATIVE_PATH_TEMPLATE = "P"

    @property
    def mac_address(self):
        """

        :rtype: str
        """
        return self.attributes.get("{}MAC Address".format(self.namespace), None)

    @mac_address.setter
    @attr_length_validator
    def mac_address(self, value=""):
        """

        :type value: str
        """
        self.attributes["{}MAC Address".format(self.namespace)] = value

    @property
    def ipv4_address(self):
        """

        :rtype: str
        """
        return self.attributes.get("{}IPv4 Address".format(self.namespace), None)

    @ipv4_address.setter
    @attr_length_validator
    def ipv4_address(self, value):
        """

        :type value: str
        """
        self.attributes["{}IPv4 Address".format(self.namespace)] = value

    @property
    def ipv6_address(self):
        """

        :rtype: str
        """
        return self.attributes.get("{}IPv6 Address".format(self.namespace), None)

    @ipv6_address.setter
    @attr_length_validator
    def ipv6_address(self, value):
        """

        :type value: str
        """
        self.attributes["{}IPv6 Address".format(self.namespace)] = value

    @property
    def port_description(self):
        """

        :rtype: str
        """
        return self.attributes.get("{}Port Description".format(self.namespace), None)

    @port_description.setter
    @attr_length_validator
    def port_description(self, value):
        """The description of the port as configured in the device.

        :type value: str
        """
        self.attributes["{}Port Description".format(self.namespace)] = value

    @property
    def adjacent(self):
        """

        :rtype: str
        """
        return self.attributes.get("{}Adjacent".format(self.namespace), None)

    @adjacent.setter
    @attr_length_validator
    def adjacent(self, value):
        """The adjacent device (system name) and port, based on LLDP or CDP protocol

        :type value: str
        """
        self.attributes["{}Adjacent".format(self.namespace)] = value
