from collections import defaultdict
import unittest

import mock

from cloudshell.devices.standards.firewall.autoload_structure import AbstractResource


class TestAbstractResource(unittest.TestCase):
    def setUp(self):
        self.shell_name = "test shell name"
        self.name = "test name"
        self.unique_id = "test unique id"

        class TestedClass(AbstractResource):
            pass

        self.resource = TestedClass(shell_name=self.shell_name,
                                    name=self.name,
                                    unique_id=self.unique_id)

    def test_add_sub_resource(self):
        relative_id = "test relative id"
        sub_resource = mock.MagicMock()
        expected_sub_resources = defaultdict(list)
        expected_sub_resources[relative_id].append(sub_resource)
        # self.resource.resources = mock.MagicMock()
        # act
        self.resource.add_sub_resource(relative_id=relative_id,
                                       sub_resource=sub_resource)
        # verify
        self.assertEqual(self.resource.resources, {sub_resource.RELATIVE_PATH_TEMPLATE: expected_sub_resources})

    def test_cloudshell_model_name_getter(self):
        """Check that property will return correct name if shell name is not empty"""
        # act
        result = self.resource.cloudshell_model_name
        # verify
        self.assertEqual(result, "{}.{}".format(self.resource.shell_name,
                                                self.resource.RESOURCE_MODEL))

    def test_cloudshell_model_name_getter_shell_name_is_empty(self):
        """Check that property will return only resource model name if shell name is empty"""
        self.resource.shell_name = ""
        self.resource.RESOURCE_MODEL = "some resource modle"
        # act
        result = self.resource.cloudshell_model_name
        # verify
        self.assertEqual(result, self.resource.RESOURCE_MODEL)

    def test_name_getter(self):
        # act
        result = self.resource.name
        # verify
        self.assertEqual(result, self.resource._name)

    def test_name_setter(self):
        expected_val = "test value"
        # act
        self.resource.name = expected_val
        # verify
        self.assertEqual(self.resource._name, expected_val)

    def test_unique_identifier_getter(self):
        # act
        result = self.resource.unique_identifier
        # verify
        self.assertEqual(result, self.resource.unique_id)

    def test_unique_identifier_setter(self):
        expected_val = "test value"
        # act
        self.resource.unique_identifier = expected_val
        # verify
        self.assertEqual(self.resource.unique_id, expected_val)
