from __future__ import print_function

import os
import hashlib
from time import sleep
# import random
import requests
import sys
import json
from pathlib2 import PurePath

import russell
from russell.constants import LOADING_MESSAGES
from russell.log import logger as russell_logger
from russell.manager.russell_ignore import RussellIgnoreManager


def get_task_url(id,gpu):
    """
    Return the url to proxy to a running task
    """
    if gpu:
        return "{}/{}".format(russell.russell_gpu_host, id)
    else:
        return "{}/{}".format(russell.russell_cpu_host, id)


def get_module_task_instance_id(task_instances):
    """
    Return the first task instance that is a module node.
    """
    for id in task_instances:
        if task_instances[id] == 'module_node':
            return id
    return None


def get_mode_parameter(mode):
    """
    Map the mode parameter to the server parameter
    """
    if mode == 'job':
        return 'cli'
    elif mode == 'serve':
        return 'serving'
    else:
        return mode


def wait_for_url(url, status_code=200, sleep_duration_seconds=1, iterations=120, message_frequency=15):
    """
    Wait for the url to become available
    """
    for iteration in range(iterations):
        # if(iteration % message_frequency == 0):
        #     print("\n{}".format(random.choice(LOADING_MESSAGES)), end='', flush=True)

        # print(".", end='', flush=True)
        # print (url)
        try:
            response = requests.get(url)
        except:
            return False
        if response.status_code == status_code:
            # print(".", flush=True)
            return True
        sleep(sleep_duration_seconds)
    # print(".", flush=True)
    return False

def getPythonVersion():
    if sys.version_info < (3, 0):
        return 2
    else:
        return 3


def force_unicode(s, encoding='UTF-8'):
    if getPythonVersion() == 2:
        try:
            return unicode(s)
        except UnicodeDecodeError:
            return str(s).decode(encoding, 'replace')
    else:
        return str(s)


def py2code():
    if getPythonVersion() == 2:
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')


def get_size(path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_md5_checksum(filename):
    if not os.path.isfile(filename):
        raise Exception("No such file found: {}".format(filename))
    with open(filename, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(2**20)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def sizeof_fmt(num, suffix='B'):
    """
    Print in human friendly format
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_files_in_directory(path, file_type):
    """
    Gets the list of files in the directory and subdirectories
    Respects .russellignore file if present
    """
    local_files = []
    separator = os.path.sep
    ignore_list = RussellIgnoreManager.get_list()

    # make sure that subdirectories are also excluded
    ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
    russell_logger.debug("Ignoring list : {}".format(ignore_list))
    total_file_size = 0

    for root, dirs, files in os.walk(path):
        russell_logger.debug("Root:{}, Dirs:{}".format(root, dirs))
        ignore_dir = False
        normalized_path = normalize_path(path, root)
        for item in ignore_list_expanded:
            if PurePath(normalized_path).match(item):
                ignore_dir = True
                break

        if ignore_dir:
            # Reset dirs to avoid going further down this directory
            dirs[:] = []
            russell_logger.debug("Ignoring directory : {}".format(root))
            continue

        for file_name in files:
            ignore_file = False
            normalized_path = normalize_path(path, os.path.join(root, file_name))
            for item in ignore_list_expanded:
                if PurePath(normalized_path).match(item):
                    ignore_file = True
                    break

            if ignore_file:
                russell_logger.debug("Ignoring file : {}".format(normalized_path))
                continue

            file_relative_path = os.path.join(root, file_name)
            if separator != '/':  # convert relative paths to Unix style
                file_relative_path = file_relative_path.replace(os.path.sep, '/')
            file_full_path = os.path.join(os.getcwd(), root, file_name)

            local_files.append((file_type, (file_relative_path, open(file_full_path, 'rb'), 'text/plain')))
            total_file_size += os.path.getsize(file_full_path)

    return (local_files, sizeof_fmt(total_file_size), total_file_size)


def normalize_path(project_root, path):
    """
    Convert `path` to a UNIX style path, where `project_root` becomes the root
    of an imaginery file system (i.e. becomes just an initial "/").
    """
    if os.path.sep != '/':
        path = path.replace(os.path.sep, '/')
        project_root = project_root.replace(os.path.sep, '/')

    path = path[len(project_root):] if path.startswith(project_root) else path
    path = '/' + path if not path.startswith('/') else path

    return path