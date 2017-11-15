
import itertools
import os


def filter_files(skip, seq):
    filtered = itertools.filterfalse(
        lambda x: x not in skip,
        seq
    )
    return filtered


def normalize_file_name(files):
    return map(lambda x: os.path.basename(x), files)


def read_txt(root, file):
    file_path = os.path.join(root, file)
    return open(file_path, 'r')


def file_name(file):
    name = os.path.basename(file).replace(".", "_")
    return name


def read_txt(file):
    with open(file, "r") as fd:
        return fd.read()
