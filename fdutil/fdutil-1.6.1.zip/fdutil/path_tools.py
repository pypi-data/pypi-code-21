
import os
import sys
import subprocess

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


def open_folder(path):
    if sys.platform == 'darwin':
        subprocess.check_call(['open', '--', path])
    elif sys.platform == 'linux2':
        subprocess.check_call(['xdg-open', '--', path])
    elif sys.platform == 'win32':
        subprocess.check_call(['explorer', path])


def expand_path(path):

    if path.startswith(u'./'):
        path = u'{p}{s}{f}'.format(p=os.getcwd(),
                                   s=os.sep,
                                   f=path[2:])

    if u'/' in path and u'/' != os.sep:
        path = path.replace(u'/', os.sep)

    return path


def ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def pop_path(path):

    """ Pops current folder / file from filepath and returns

    :param path: string:    Path to update
    :return: string:        new path
    """

    pth = path.split(os.sep)
    pth.pop()

    return os.sep.join(pth)


def generate_relative_html_link(src_dir,
                                linked_file):

    """

    :param src_dir:     The directory where the html file is
    :param linked_file: The file path to be referenced in the html file.
    :return:            Relative path valid in src_dir to the file.
    """

    # Validate src_dir is a directory
    if not os.path.isdir(src_dir):
        raise ValueError(u'src_dir should be a directory path!')

    if src_dir.endswith(os.sep):
        src_dir = src_dir[:-1]

    # Find common base of both paths
    common_pth = os.path.commonprefix([
        src_dir,
        os.path.dirname(linked_file)
    ])

    # update paths to remove the common base
    src_dir = src_dir.replace(common_pth, u'')
    linked_file = linked_file.replace(common_pth, u'')

    if linked_file.startswith(os.sep):
        # Remove the leading / from the output
        linked_file = linked_file[1:]

    # Work out how many levels we have to rise (if any) and create the prefix
    num_parts = len(src_dir.split(os.sep)) if src_dir != u'' else 0
    prefix = u'../' * num_parts if num_parts >= 1 else u'./'  # TODO: This is still not quite right!

    # create the relative path
    new_link_path = prefix + linked_file

    return new_link_path


def find_files(root_dir,
               extension=u'.html'):

    """ Finds all files with specified extension recursively under the root directory specified

    :param root_dir:    Directory to search
    :param extension:   File extension to search for
    :return:            List of file paths that match the search
    """

    matched_files = []

    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(extension):
                matched_files.append(os.path.join(root, f))

    return matched_files
