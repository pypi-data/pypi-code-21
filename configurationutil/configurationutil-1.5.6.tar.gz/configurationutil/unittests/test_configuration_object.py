
import os
import unittest

from configurationutil.cfg_providers import base_provider
from fdutil.path_tools import pop_path

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


class TestConfigurationObject(unittest.TestCase):

    def setUp(self):
        self.cfg_file = os.path.join(pop_path(__file__), u'test_config_object.json')
        self.template = os.path.join(pop_path(__file__), u'resources', u'upgrade_template.json')
        self.missing_template = os.path.join(pop_path(__file__), u'test_config_object_template.json')

    def tearDown(self):
        pass

    def test_instantiation(self):

        base_provider.ConfigObject.DEFAULT_TEMPLATE = self.template

        with self.assertRaises(NotImplementedError):
            self.cfg = base_provider.ConfigObject(config_file=self.cfg_file,
                                                  create=True)

        del base_provider.ConfigObject.DEFAULT_TEMPLATE

    def test_instantiation_missing_default_template(self):
        with self.assertRaises(NotImplementedError):
            self.cfg = base_provider.ConfigObject(config_file=self.cfg_file,
                                                  create=True)

    def test_instantiation_missing_default_file(self):

        base_provider.ConfigObject.DEFAULT_TEMPLATE = self.missing_template

        with self.assertRaises(IOError):
            self.cfg = base_provider.ConfigObject(config_file=self.cfg_file,
                                                  create=True)

        del base_provider.ConfigObject.DEFAULT_TEMPLATE

if __name__ == u'__main__':
    unittest.main()
