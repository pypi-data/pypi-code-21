from unittest import mock
import shutil

from fant_sizer import fant_sizer
from fant_sizer.fant_sizer import os


def test_results_with_not_existing_files(monkeypatch):
    with mock.patch('os.walk') as mockwalk:
        mockwalk.return_value = [
            ('/some_dir', ('bar',), ('fant_sizer.py',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]
        monkeypatch.setattr('fant_sizer.fant_sizer', os)
        assert fant_sizer.get_sorted_files_by_size(path_to_root_dir='/some/path',
                                                   min_size_first=False) == []


def test_results_with_existing_files():
    dir_name = 'the_dir_for_test'
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

    with open(dir_name + '/test_file1.txt', 'w+') as test_file1, \
            open(dir_name + '/test_file2.txt', 'w+') as test_file2:
        test_file1.write('Just some text')

    assert fant_sizer.get_sorted_files_by_size(path_to_root_dir=dir_name, min_size_first=False) == \
           [('the_dir_for_test/test_file1.txt', 14), ('the_dir_for_test/test_file2.txt', 0)]
    assert fant_sizer.get_sorted_files_by_size(path_to_root_dir=dir_name, min_size_first=True) == \
           [('the_dir_for_test/test_file2.txt', 0), ('the_dir_for_test/test_file1.txt', 14)]

    shutil.rmtree(dir_name)
