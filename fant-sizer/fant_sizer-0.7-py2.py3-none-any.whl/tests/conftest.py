import pytest
from unittest import mock
import shutil

from fant_sizer.fant_sizer import os
from fant_sizer import fant_sizer


@pytest.fixture()
def mock_os_walk(monkeypatch):
    def _set_dirs(a_list_of_dirs: list):
        with mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = a_list_of_dirs
            monkeypatch.setattr('fant_sizer.fant_sizer', os)
    return _set_dirs


@pytest.fixture()
def create_fake_files():
    def _create_files(dir_name: str):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.mkdir(dir_name)

        with open(dir_name + '/test_file1.txt', 'w+') as test_file1, \
                open(dir_name + '/test_file2.txt', 'w+') as test_file2, \
                open(dir_name + '/test_file3.txt', 'w+') as test_file3, \
                open(dir_name + '/test_file4.txt', 'w+') as test_file4, \
                open(dir_name + '/test_file5.txt', 'w+') as test_file5:
            test_file1.write('Just some text inside')
            test_file2.write('Just')
            test_file3.write('Just some text')
            test_file4.write('Just')

    yield _create_files


@pytest.fixture()
def delete_fake_files():
    def _del_files(dir_name: str):
        shutil.rmtree(dir_name)
    yield _del_files
