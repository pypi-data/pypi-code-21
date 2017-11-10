from __future__ import absolute_import

import os
from pkg_resources import resource_string, resource_filename


def get_package_file_content(module_name, filename):
    return resource_string(module_name, filename)


def get_package_file_full_path(module_name, filename):
    return os.path.abspath(resource_filename(module_name, filename))
