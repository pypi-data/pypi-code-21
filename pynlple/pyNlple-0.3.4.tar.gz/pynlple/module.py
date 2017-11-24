# -*- coding: utf-8 -*-

import os.path


def abs_path(prefix_path=__file__, object_path=''):
    """
    Get the absolute path to the `object_path` using the `prefix_path`.

    Pass the __file__ variable to form absolute paths senseless to execution environment.
    If no source_path is set, then build absolute to the project folder (module.py).

    :param str prefix_path: path to be used as the full prefix. Default: path to module.py
    :param str object_path: path to the object in your project. Default: ''
    :return: absolute path to the object using `prefix_path`
    :rtype: str
    """
    return os.path.abspath(os.path.join(os.path.dirname(prefix_path), object_path))


def append_paths(*parts):
    """
    Append `parts` of the paths to form correct path. Wraps os.path.join method.

    :param str parts: elements of the future path
    :return: correctly-formed path
    :rtype: str
    """
    return os.path.join(*parts)


def file_name(file_path):
    """
    Get the name of the file from the `file_path` preserving extension
    (assumed as the last component of the path).

    :param str file_path: string path to the file
    :return: file name without extension
    :rtype: str
    """
    components = os.path.split(file_path)
    return components[-1]


def strip_extension(file_name_):
    """
    Strips the `file_name_` by cutting of the assumed extension of the file (the last suffix separated by '.').

    :param str file_name_: the name of the file with extension
    :return: the stripped name of the file without extension
    :rtype: str
    """
    pos = file_name_.rfind('.')
    if pos > 0:
        return file_name_[:pos]
    else:
        return file_name_


def stripped_file_name(file_path):
    """
    Get the stripped name of the file from the `file_path` (assumed as the last component of the path).
    Stripping includes cutting of the assumed extension of the file (the last suffix separated by dot)

    :param str file_path: the path to the file
    :return: file name without extension (last dot-separated suffix)
    :rtype: str
    """
    file_name_ = file_name(file_path)
    return strip_extension(file_name_)


def list_dir(path_):
    return os.listdir(path_)


def is_file(path_):
    return os.path.isfile(path_)


def is_folder(path_):
    return os.path.isdir(path_)


def exists(path_):
    return os.path.exists(path_)
