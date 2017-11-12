import unittest

import mock

from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder


class TestAutoloadDetailsBuilder(unittest.TestCase):
    def setUp(self):
        self.autoload_data = mock.MagicMock()
        self.builder = AutoloadDetailsBuilder(autoload_data=self.autoload_data)

    def test_autoload_details(self):
        self.builder._build_autoload_details = mock.MagicMock()
        # act
        result = self.builder.autoload_details()
        # verify
        self.assertEqual(result, self.builder._autoload_details)
        self.builder._build_autoload_details.assert_called_once_with(self.autoload_data)

    def test_validate_build_resource_structure(self):
        """Check that method will return dictionary with correct prefixes"""
        autoload_resource = {
            "resource_prefix":
                {
                    "1": ["resource_1", "resource_2"],
                    "2": ["resource_3", "resource_4"]
                }
        }
        # act
        result = AutoloadDetailsBuilder._validate_build_resource_structure(autoload_resource=autoload_resource)
        # verify
        self.assertEqual(result, {
            'resource_prefix1': 'resource_1',
            'resource_prefix2': 'resource_3',
            'resource_prefix3': 'resource_2',
            'resource_prefix4': 'resource_4'
        })

    @mock.patch("cloudshell.devices.autoload.autoload_builder.AutoLoadResource")
    @mock.patch("cloudshell.devices.autoload.autoload_builder.AutoLoadAttribute")
    def test_build_autoload_details(self, autoload_attribute_class, autoload_resource_class):
        """Check that method will add attributes and resources to the _autoload_details property"""
        autoload_data = mock.MagicMock(attributes={"test_attr": "test_val"})
        autoload_attr = mock.MagicMock()
        autoload_attribute_class.return_value = autoload_attr
        autoload_resource = mock.MagicMock()
        autoload_resource_class.return_value = autoload_resource
        resource = mock.MagicMock()
        self.builder._autoload_details = mock.MagicMock()
        self.builder._validate_build_resource_structure = mock.MagicMock(return_value={
            "resource_relative_path": resource
        })
        # need to copy func to prevent recursion
        tested_func = self.builder._build_autoload_details
        self.builder._build_autoload_details = mock.MagicMock()

        # act
        tested_func(autoload_data=autoload_data, relative_path="relative_path")
        # verify
        self.builder._autoload_details.attributes.extend.assert_called_once_with([autoload_attr])
        autoload_attribute_class.assert_called_once_with(relative_address="relative_path",
                                                         attribute_name="test_attr",
                                                         attribute_value="test_val")

        self.builder._autoload_details.resources.append.assert_called_once_with(autoload_resource)
        autoload_resource_class.assert_called_once_with(model=resource.cloudshell_model_name,
                                                        name=resource.name,
                                                        relative_address='relative_path/resource_relative_path',
                                                        unique_identifier=resource.unique_identifier)

        self.builder._build_autoload_details.assert_called_once_with(
            autoload_data=resource,
            relative_path="relative_path/resource_relative_path")
