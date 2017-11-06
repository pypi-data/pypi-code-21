#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import shlex
import platform
import ConfigParser


Linux = True if platform.system() == 'Linux' else False
CONFIG = ConfigParser.ConfigParser()
CONFIG_FILE = os.path.join(os.environ['USERPROFILE'], 'easylog.ini') if Linux else os.path.join(os.environ['HOME'], 'easylog.ini')

COLOR_MAP = {
    'blue': '\033[1;36m%s\033[0m',
    'green': '\033[1;32m%s\033[0m',
    'yellow': '\033[1;33m%s\033[0m',
    'red': '\033[1;31m%s\033[0m',
    'title': '\033[30;42m%s\033[0m',
    'info': '\033[32m%s\033[0m'
}


def bash(cmd):
    """ run a bash shell command

    :param cmd: linux shell cmd
    """
    return shlex.os.system(cmd)


def check_file_path(path, auto=False):
    """ check if the file path is correct. if it is correct and exists no file to create it

    :param path: the file path
    :param auto: if need to create file automatically. Default False
    :return: normpath(path)
    """
    path = os.path.normpath(path)
    if path[-1] == '/':
        raise LogPathError('This path is not regular file path: %s' % path)

    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        raise LogPathError('Not exist this directory: %s' % dir_path)

    if os.path.isdir(path):
        raise LogPathError('This path is not regular file path: %s' % path)

    if not os.path.exists(path):
        if auto:
            with open(path, 'a'):
                pass
        else:
            raise LogPathError('Not exist the file: %s' % path)

    return os.path.abspath(path)


def init_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w'):
            pass

    CONFIG.read(CONFIG_FILE)
    if not CONFIG.has_section('dump'):
        CONFIG.add_section('dump')


def get_log_path(path):
    """ get log path. if cmd arg exists to use it, else use config.LOGFILE

    :param path: the log file path
    :return: normpath(path)
    """
    if path:
        CONFIG.set('dump', 'logfile', path)
        CONFIG.write(open(CONFIG_FILE, 'w'))
        return path
    elif CONFIG.has_option('dump', 'logfile'):
        return CONFIG.get('dump', 'logfile')
    else:
        raise LogParaError("must take the para 'logfile' !")


def color_print(msg, color='green', exit=False):
    """ Print colorful string """
    if Linux:
        msg = COLOR_MAP.get(color, 'green') % msg
    print msg
    if exit:
        time.sleep(2)
        sys.exit()


def color_input(msg, color='green'):
    """ Input colorful string """
    if Linux:
        msg = COLOR_MAP.get(color, 'green') % msg
    return raw_input(msg).strip()


def list_remove_duplicate(lst):
    new_lst = []
    for x in lst[::-1]:
        if x not in new_lst:
            new_lst.append(x)
    return reversed(new_lst)


def tail(filename, num=10):
    """ implement tail function in windows

    :param filename: logfile path to monitor
    :param num: number for print log lines
    :return: None
    """
    check_file_path(filename)

    with open(filename) as rf:
        last = []
        for line in reversed(rf.read().split('\n')):
            if num == 0:
                break
            if not line:
                continue
            last.insert(0, line)
            num -= 1
        for line in last:
            print line.decode('utf-8')

        while True:
            try:
                line = rf.readline()
            except KeyboardInterrupt:
                break
            if line:
                sys.stdout.write(line.decode('utf-8'))


class LogPathError(Exception):
    pass

class LogLevelError(Exception):
    pass

class LogParaError(Exception):
    pass