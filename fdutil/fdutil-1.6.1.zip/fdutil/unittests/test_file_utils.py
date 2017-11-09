import os
import unittest

from fdutil import file_utils


def normalise_path(self,
                   path):
    return os.path.join(self.test_base_dir, os.sep.join(path.split(u'/')))


class TestGetFiles(unittest.TestCase):

    normalise_path = normalise_path

    def setUp(self):
        self.test_base_dir = os.path.dirname(os.path.realpath(__file__))
        self.output = []
        self.file_dir = self.normalise_path(u'test_data/file_utils/get_files/')

    def tearDown(self):
        pass

    def test_default_file_type(self):

        self.output = file_utils.get_files(directory=self.file_dir)
        self.output.sort()

        expected_output = [self.normalise_path(path)
                           for path in (u'test_data/file_utils/get_files/file1.json',
                                        u'test_data/file_utils/get_files/file1.txt',
                                        u'test_data/file_utils/get_files/file2.json',
                                        u'test_data/file_utils/get_files/file3.json',
                                        u'test_data/file_utils/get_files/file4.txt',
                                        u'test_data/file_utils/get_files/folder1')]

        self.assertEqual(expected_output,
                         self.output,
                         msg=u'Test get_files: Default extension: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))

    def test_default_file_type_recursive(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           recursive=True)
        self.output.sort()

        expected_output = [self.normalise_path(path)
                           for path in u'test_data/file_utils/get_files/file1.json',
                                       u'test_data/file_utils/get_files/file1.txt',
                                       u'test_data/file_utils/get_files/file2.json',
                                       u'test_data/file_utils/get_files/file3.json',
                                       u'test_data/file_utils/get_files/file4.txt',
                                       u'test_data/file_utils/get_files/folder1/file5.txt',
                                       u'test_data/file_utils/get_files/folder1/file6.json',
                                       u'test_data/file_utils/get_files/folder1/folder2/file7.txt',
                                       u'test_data/file_utils/get_files/folder1/folder2/file8.json',
        ]

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Default extension recursive: files do not match!!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))

    def test_non_default_file_type(self):

        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.txt')
        self.output.sort()

        expected_output = [self.normalise_path(path)
                           for path in (u'test_data/file_utils/get_files/file1.txt',
                                        u'test_data/file_utils/get_files/file4.txt')]

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Non default extension: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))

    def test_non_default_file_type_recursive(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.txt',
                                           recursive=True)
        self.output.sort()

        expected_output = [self.normalise_path(path)
                           for path in (u'test_data/file_utils/get_files/file1.txt',
                                        u'test_data/file_utils/get_files/file4.txt',
                                        u'test_data/file_utils/get_files/folder1/file5.txt',
                                        u'test_data/file_utils/get_files/folder1/folder2/file7.txt')]

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files: Non default extension recursive: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))

    def test_all_files(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.*')
        self.output.sort()

        expected_output = [self.normalise_path(path)
                           for path in (u'test_data/file_utils/get_files/file1.json',
                                        u'test_data/file_utils/get_files/file1.txt',
                                        u'test_data/file_utils/get_files/file2.json',
                                        u'test_data/file_utils/get_files/file3.json',
                                        u'test_data/file_utils/get_files/file4.txt')]

        self.assertEqual(expected_output,
                         self.output,
                         msg=u'Test get_files: All: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))

    def test_all_files_recursive(self):
        self.output = file_utils.get_files(directory=self.file_dir,
                                           pattern=u'*.*',
                                           recursive=True)
        self.output.sort()

        expected_output = [self.normalise_path(path)
                           for path in (u'test_data/file_utils/get_files/file1.json',
                                        u'test_data/file_utils/get_files/file1.txt',
                                        u'test_data/file_utils/get_files/file2.json',
                                        u'test_data/file_utils/get_files/file3.json',
                                        u'test_data/file_utils/get_files/file4.txt',
                                        u'test_data/file_utils/get_files/folder1/file5.txt',
                                        u'test_data/file_utils/get_files/folder1/file6.json',
                                        u'test_data/file_utils/get_files/folder1/folder2/file7.txt',
                                        u'test_data/file_utils/get_files/folder1/folder2/file8.json')]

        self.assertEqual(expected_output,
                         self.output,
                         msg=u'Test get_files: All recursive: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))


class TestGetFilesDict(unittest.TestCase):

    normalise_path = normalise_path

    def setUp(self):
        self.test_base_dir = os.path.dirname(os.path.realpath(__file__))
        self.output = {}
        self.file_dir = self.normalise_path(u'test_data/file_utils/get_files/')

    def tearDown(self):
        pass

    def test_default_file_type(self):

        file_utils.get_files_dict(directory=self.file_dir,
                                  output_dict=self.output)

        expected_output = {key: self.normalise_path(path)
                           for key, path in {u'file1': u'test_data/file_utils/get_files/file1.json',
                                             u'file2': u'test_data/file_utils/get_files/file2.json',
                                             u'file3': u'test_data/file_utils/get_files/file3.json'}.iteritems()}

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files_dict: Default extension: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))

    def test_non_default_file_type(self):

        file_utils.get_files_dict(directory=self.file_dir,
                                  output_dict=self.output,
                                  file_type=u'.txt')

        expected_output = {key: self.normalise_path(path)
                           for key, path in {u'file1': u'test_data/file_utils/get_files/file1.txt',
                                             u'file4': u'test_data/file_utils/get_files/file4.txt'}.iteritems()}

        self.assertEqual(expected_output, self.output,
                         msg=u'Test get_files_dict: Non default extension: files do not match!\n'
                             u'expected:{expected}\n'
                             u'actual:{actual}'
                             .format(expected=expected_output,
                                     actual=self.output))
