from unittest import mock
import pytest

from fant_sizer import fant_sizer
from fant_sizer.fant_sizer import os


def test_results_with_not_existing_files(monkeypatch):
    fake_dir = '/some/path'
    with mock.patch('os.walk') as mockwalk:
        mockwalk.return_value = [
            ('/some_dir', ('bar',), ('fant_sizer.py',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]
        monkeypatch.setattr('fant_sizer.fant_sizer', os)
        with pytest.raises(OSError):
            fant_sizer.get_sorted_files_by_size(path_to_root_dir=fake_dir, min_size_first=False)
            fant_sizer.get_the_biggest_file(path_to_root_dir=fake_dir)
            fant_sizer.get_the_smallest_file(path_to_root_dir=fake_dir)
            fant_sizer.get_the_average_size_of_the_files(path_to_root_dir=fake_dir)
            fant_sizer.get_mode_of_the_files(path_to_root_dir=fake_dir)
            fant_sizer.get_median_of_the_files(path_to_root_dir=fake_dir)
            fant_sizer.get_range_of_the_files(path_to_root_dir=fake_dir)


def test_results_with_existing_files(create_fake_files, delete_fake_files):
    dir_name = 'the_dir_for_test'
    fake_dir_name = 'not/existing/path'

    create_fake_files(dir_name)

    # Get all files
    assert fant_sizer.get_sorted_files_by_size(path_to_root_dir=dir_name, min_size_first=False)[0] == \
           (dir_name + '/test_file1.txt', 21)
    assert fant_sizer.get_sorted_files_by_size(path_to_root_dir=dir_name, min_size_first=True)[0] == \
           (dir_name + '/test_file5.txt', 0)
    with pytest.raises(OSError):
        fant_sizer.get_sorted_files_by_size(path_to_root_dir=fake_dir_name)
    with pytest.raises(TypeError):
        fant_sizer.get_sorted_files_by_size(path_to_root_dir=12)

    # Get the smallest/biggest file
    assert fant_sizer.get_the_biggest_file(path_to_root_dir=dir_name) == (dir_name + '/test_file1.txt', 21)
    assert fant_sizer.get_the_smallest_file(path_to_root_dir=dir_name) == (dir_name + '/test_file5.txt', 0)
    with pytest.raises(OSError):
        fant_sizer.get_the_biggest_file(path_to_root_dir=fake_dir_name)
        fant_sizer.get_the_smallest_file(path_to_root_dir=fake_dir_name)

    # Get the average size of files
    assert fant_sizer.get_the_average_size_of_the_files(path_to_root_dir=dir_name) == 8.6

    # Get the median of the file sizes
    assert fant_sizer.get_median_of_the_files(path_to_root_dir=dir_name) == 4

    # Get range of the file sizes
    assert fant_sizer.get_range_of_the_files(path_to_root_dir=dir_name) == 21

    # Get mode of the file sizes
    assert fant_sizer.get_mode_of_the_files(path_to_root_dir=dir_name) == [4]

    # Catch Errors from average/median/range/mode functions
    with pytest.raises(OSError):
        fant_sizer.get_the_average_size_of_the_files(path_to_root_dir=fake_dir_name)
        fant_sizer.get_median_of_the_files(path_to_root_dir=fake_dir_name)
        fant_sizer.get_range_of_the_files(path_to_root_dir=fake_dir_name)
        fant_sizer.get_mode_of_the_files(path_to_root_dir=fake_dir_name)
    with pytest.raises(TypeError):
        fant_sizer.get_the_average_size_of_the_files(path_to_root_dir=2.5)
        fant_sizer.get_median_of_the_files(path_to_root_dir=('some', 'tuple'))
        fant_sizer.get_range_of_the_files(path_to_root_dir=[1, 2, 3])
        fant_sizer.get_mode_of_the_files(path_to_root_dir=None)

    delete_fake_files(dir_name)
