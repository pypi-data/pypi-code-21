import os
from tests import utils


TEST_CASES = {}
def setup():
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'good')
    for directory_name in utils.list_subdirs_in_dir(data_dir):
        TEST_CASES[directory_name] = utils.list_files_in_dir(
            os.path.join(data_dir, directory_name)
        ) 

def test_preconditions():
    for directory_name in TEST_CASES:
            yield check_preconditions, directory_name

def check_preconditions(directory_name):
    num_files = len(TEST_CASES[directory_name])
    assert num_files == 2, "Found %d file(s), expected 2" % num_files

def test_sanity():
    for directory_name in TEST_CASES:
        yield check_sanity, directory_name

def check_sanity(directory_name):
    for file_name in TEST_CASES[directory_name]:
        assert utils.default_mdm_compare(file_name, file_name)

def test_different_platforms():
    for directory_name in TEST_CASES:
        yield check_different_platforms, directory_name

def check_different_platforms(directory_name):
    assert utils.default_mdm_compare(*TEST_CASES[directory_name])
