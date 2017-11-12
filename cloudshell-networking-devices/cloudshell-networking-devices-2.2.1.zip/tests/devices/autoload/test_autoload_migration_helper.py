import unittest
from collections import defaultdict

import mock

from cloudshell.devices.autoload.autoload_migration_helper import migrate_autoload_details
from cloudshell.devices.autoload.autoload_migration_helper import LegacyUtils


class TestLegacyUtils(unittest.TestCase):
    def setUp(self):
        self.utils = LegacyUtils()

    def test_migrate_autoload_details(self):
        """Check that method calls internal methods for building autoload details"""
        autoload_details = mock.MagicMock()
        context = mock.MagicMock()
        root = mock.MagicMock()
        attrs = mock.MagicMock()
        self.utils._LegacyUtils__create_resource_from_datamodel = mock.MagicMock(return_value=root)
        self.utils._LegacyUtils__create_attributes_dict = mock.MagicMock(return_value=attrs)
        self.utils._LegacyUtils__attach_attributes_to_resource = mock.MagicMock()
        self.utils._LegacyUtils__build_sub_resoruces_hierarchy = mock.MagicMock()
        # act
        result = self.utils.migrate_autoload_details(autoload_details=autoload_details, context=context)
        # verify
        self.assertEqual(result, root)
        self.utils._LegacyUtils__create_resource_from_datamodel.assert_called_once_with(context.resource.model,
                                                                                        context.resource.name)

        self.utils._LegacyUtils__create_attributes_dict.assert_called_once_with(autoload_details.attributes)

        self.utils._LegacyUtils__attach_attributes_to_resource.assert_called_once_with(attrs, '', root)
        self.utils._LegacyUtils__build_sub_resoruces_hierarchy.assert_called_once_with(root,
                                                                                       autoload_details.resources,
                                                                                       attrs)

    def test__create_resource_from_datamodel(self):
        """Check that method will return created resource instance by its model name"""
        model_name = "test model name"
        res_name = "test res name"
        resource = mock.MagicMock()
        ex_class = mock.MagicMock(return_value=resource)
        self.utils._datamodel_clss_dict = {
            model_name: ex_class
        }
        # act
        result = self.utils._LegacyUtils__create_resource_from_datamodel(model_name=model_name, res_name=res_name)
        # verify
        self.assertEqual(result, resource)
        ex_class.assert_called_once_with(res_name)

    def test__create_attributes_dict(self):
        """Check that method will create dict-like object with attributes"""
        attr = mock.MagicMock(relative_address="relative_addr")
        expected_res = defaultdict(list)
        expected_res["relative_addr"].append(attr)
        # act
        result = self.utils._LegacyUtils__create_attributes_dict(attributes_lst=[attr])
        # verify
        self.assertEqual(result, expected_res)

    def test__build_sub_resoruces_hierarchy(self):
        """Check that method will call __set_models_hierarchy_recursively method for building resources hierarchy"""
        root = mock.MagicMock()
        sub_resource = mock.MagicMock(relative_address="path1/path2")
        attrs = mock.MagicMock()
        res_dict = defaultdict(list)
        res_dict[2] = [("path1", sub_resource)]

        self.utils._LegacyUtils__set_models_hierarchy_recursively = mock.MagicMock()
        # act
        self.utils._LegacyUtils__build_sub_resoruces_hierarchy(root=root,
                                                               sub_resources=[sub_resource],
                                                               attributes=attrs)
        # verify
        self.utils._LegacyUtils__set_models_hierarchy_recursively.assert_called_once_with(res_dict,
                                                                                          1,
                                                                                          root,
                                                                                          '',
                                                                                          attrs)


class TestAutoloadMigrationHelper(unittest.TestCase):

    def test_migrate_autoload_details(self):
        """Check that method will update attribute names on the autoload_details instance"""
        attr = mock.MagicMock(relative_address="relative_addr",
                              attribute_name="attr_name")

        root_attr = mock.MagicMock(relative_address=None,
                                   attribute_name="root_attr_name")

        resource = mock.MagicMock(relative_address="relative_addr",
                                  model="model")

        autoload_details = mock.MagicMock(resources=[resource],
                                          attributes=[root_attr, attr])
        shell_name = "shell_name"
        shell_type = "shell_type"
        # act
        result = migrate_autoload_details(autoload_details, shell_name, shell_type)
        # verify
        self.assertEqual(result, autoload_details)
        self.assertEqual(resource.model, "shell_name.model")
        self.assertEqual(root_attr.attribute_name, "shell_type.root_attr_name")
        self.assertEqual(attr.attribute_name, "shell_name.model.attr_name")
