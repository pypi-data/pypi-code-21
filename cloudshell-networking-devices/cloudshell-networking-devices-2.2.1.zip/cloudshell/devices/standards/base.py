from collections import defaultdict

from cloudshell.devices.standards.validators import attr_length_validator


class AbstractResource(object):
    RESOURCE_MODEL = ""
    RELATIVE_PATH_TEMPLATE = ""

    def __init__(self, shell_name, name, unique_id):
        """

        :param str shell_name:
        :param str name:
        :param str unique_id:
        """
        self._name = name
        self.shell_name = shell_name
        if self.shell_name:
            self.namespace = "{shell_name}.{resource_model}.".format(shell_name=self.shell_name,
                                                                     resource_model=self.RESOURCE_MODEL
                                                                     .replace(" ", ""))
        else:
            self.namespace = ""

        self.unique_id = unique_id
        self.attributes = {}
        self.resources = {}

    def add_sub_resource(self, relative_id, sub_resource):
        """Add sub resource"""
        existing_sub_resources = self.resources.get(sub_resource.RELATIVE_PATH_TEMPLATE, defaultdict(list))
        existing_sub_resources[relative_id].append(sub_resource)
        self.resources.update({sub_resource.RELATIVE_PATH_TEMPLATE: existing_sub_resources})

    @property
    def cloudshell_model_name(self):
        """Return the name of the CloudShell model"""
        if self.shell_name:
            return "{shell_name}.{resource_model}".format(shell_name=self.shell_name,
                                                          resource_model=self.RESOURCE_MODEL.replace(" ", ""))
        else:
            return self.RESOURCE_MODEL

    @property
    def name(self):
        """Return resource name"""
        return self._name

    @name.setter
    @attr_length_validator
    def name(self, value):
        """Set resource name"""
        self._name = value

    @property
    def unique_identifier(self):
        """Return resource unique identifier"""
        return self.unique_id

    @unique_identifier.setter
    @attr_length_validator
    def unique_identifier(self, value):
        """Set resource unique identifier"""
        self.unique_id = value
