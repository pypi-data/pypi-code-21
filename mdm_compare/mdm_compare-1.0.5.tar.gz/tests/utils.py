import os
from mdm_compare import mdm_compare
from tests import DECIMAL_PRECISION


def default_mdm_compare(mdm_file1, mdm_file2):
    return mdm_compare(mdm_file1, mdm_file2, DECIMAL_PRECISION)

def list_files_in_dir(path):
    """"
    Return a list containing the full paths of the files in the directory, while
    ignoring hidden files and directories.
    """
    return map(
        lambda x: os.path.join(path, x),
        filter(
            lambda x: x[0] != '.' and os.path.isfile(os.path.join(path, x)),
            os.listdir(path)
        )
    )

def list_subdirs_in_dir(path):
    """"
    Return a list containing the names of the subdirectories in the directory,
    while ignoring hidden files and directories.
    """
    return filter(
        lambda x: x[0] != '.' and os.path.isdir(os.path.join(path, x)),
        os.listdir(path)
    )
