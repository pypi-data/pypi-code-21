import json
import os
import shutil
import unittest

from fdutil import parse_json


class TestParseJson(unittest.TestCase):

    def setUp(self):
        self.test_base_dir = os.path.dirname(os.path.realpath(__file__))
        test_data_file = open(u'{base}{s}test_data{s}parse_json{s}test_data.json'.format(base=self.test_base_dir,
                                                                                         s=os.sep))
        self.example_json = json.load(test_data_file)
        self.out_dir = u'{base}{s}test_data{s}parse_json{s}output{s}'.format(base=self.test_base_dir,
                                                                             s=os.sep)

        os.makedirs(self.out_dir)

    def tearDown(self):
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)


class TestSortJsonObject(TestParseJson):

    def check_sort(self, json_obj):

        prev_item = None

        for item in json_obj:

            if isinstance(item, tuple):
                if prev_item is not None:
                    self.assertTrue(item[0] > prev_item)

                prev_item = item[0]
                self.check_sort(item[1])

            elif isinstance(item, list):
                for i in item:
                    if isinstance(i, list):
                        self.check_sort(i)

                    else:
                        if prev_item is not None:
                            self.assertTrue(i > prev_item)

                        prev_item = i

    def test_sort(self):
        json_sorted = parse_json.sort_json_object(self.example_json.copy())
        self.check_sort(json_sorted)

    def test_sort_comparison(self):

        json_a = parse_json.sort_json_object(self.example_json.copy())
        json_b = parse_json.sort_json_object(self.example_json.copy())

        self.assertNotEqual(self.example_json, json_a)
        self.assertNotEqual(self.example_json, json_b)
        self.assertEqual(json_a, json_b)


class TestWriteJsonToFile(TestParseJson):

    def test_write_json_to_file_defaults(self):

        parse_json.write_json_to_file(content=self.example_json,
                                      output_dir=self.out_dir,
                                      filename=u'example_output')

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.json')))

    def test_write_json_to_file_backup(self):

        backup_dir = os.path.join(self.out_dir, u'backup')
        os.makedirs(backup_dir)

        parse_json.write_json_to_file(content=self.example_json,
                                      output_dir=self.out_dir,
                                      filename=u'example_output',
                                      backup_dir=None,
                                      file_ext=u'json')

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.json')))

        parse_json.write_json_to_file(content=self.example_json,
                                      output_dir=self.out_dir,
                                      filename=u'example_output',
                                      backup_dir=backup_dir,
                                      file_ext=u'json')

        self.assertTrue(os.path.exists(os.path.join(backup_dir, u'example_output.json')))

    def test_write_json_to_file_ext_other(self):

        parse_json.write_json_to_file(content=self.example_json,
                                      output_dir=self.out_dir,
                                      filename=u'example_output',
                                      backup_dir=None,
                                      file_ext=u'txt')

        self.assertTrue(os.path.exists(os.path.join(self.out_dir, u'example_output.txt')))
