import yaml
import os
import shutil
import unittest

from fdutil import parse_yaml


class TestParseJson(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = os.path.dirname(os.path.realpath(__file__))
        test_data_file = open(u'{base}{s}test_data{s}parse_yaml{s}test_data.yaml'.format(base=self.test_base_dir,
                                                                                         s=os.sep))
        self.example_yaml = yaml.load(test_data_file)
        self.out_dir = u'{base}{s}test_data{s}parse_yaml{s}output{s}'.format(base=self.test_base_dir,
                                                                             s=os.sep)

        os.makedirs(self.out_dir)

    def tearDown(self):
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)


class TestWriteJsonToFile(TestParseJson):

    def test_write_yaml_to_file_defaults(self):

        parse_yaml.write_yaml_to_file(content=self.example_yaml,
                                      output_dir=self.out_dir,
                                      filename=u'example_output')

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.yaml')))

    def test_write_yaml_to_file_backup(self):

        backup_dir = os.path.join(self.out_dir, u'backup')
        os.makedirs(backup_dir)

        parse_yaml.write_yaml_to_file(content=self.example_yaml,
                                      output_dir=self.out_dir,
                                      filename=u'example_output',
                                      backup_dir=None,
                                      file_ext=u'yaml')

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.yaml')))

        parse_yaml.write_yaml_to_file(content=self.example_yaml,
                                      output_dir=self.out_dir,
                                      filename=u'example_output',
                                      backup_dir=backup_dir,
                                      file_ext=u'yaml')

        self.assertTrue(os.path.exists(os.path.join(backup_dir, u'example_output.yaml')))

    def test_write_yaml_to_file_ext_other(self):

        parse_yaml.write_yaml_to_file(content=self.example_yaml,
                                      output_dir=self.out_dir,
                                      filename=u'example_output',
                                      backup_dir=None,
                                      file_ext=u'txt')

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.txt')))
