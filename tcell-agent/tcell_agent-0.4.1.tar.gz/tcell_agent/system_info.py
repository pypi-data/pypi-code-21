# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function
import getpass
import pip
import os
import sys

try:
    import pwd
except ImportError:
    import getpass

    pwd = None
import errno


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def python_version_string():
    try:
        return sys.version.split("\n")[0]
    except:
        return None


def current_username():
    if pwd:  # not available on windows
        return pwd.getpwuid(os.geteuid()).pw_name
    else:
        return getpass.getuser()


def current_user_id():
    return os.getuid()


def current_process_id():
    return os.getpid()


def current_group_id():
    return str(os.getegid())  # effective group id


def get_packages(callback=None):
    installed_packages = pip.get_installed_distributions()
    for installed_package in installed_packages:
        if callback:
            callback(installed_package)
    # installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    return installed_packages
