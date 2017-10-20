#!/usr/bin/env python

import re
import sys
import subprocess
import shutil
from os import makedirs, path, rename

####################################################################################################
# Temporary directory for all files
####################################################################################################
TMP_DIR = '.capy/'


####################################################################################################
# Dictionary util functions
####################################################################################################
def merge(user, default):
    if isinstance(user, dict) and isinstance(default, dict):
        for k, v in default.iteritems():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge(user[k], v)
    return user


def get(conf, prop, default):
    if not conf:
        return default

    p = conf.get(prop, None)
    if p:
        return p
    else:
        return default


####################################################################################################
# Console colors
####################################################################################################
class Color:
    ENDC = '\033[0m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    DEFAULT = '\033[39m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MANGETA = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GRAY = '\033[37m'
    DARK_GRAY = '\033[90m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MANGETA = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    WHITE = '\033[97m'


def exit_error(msg):
    print Color.LIGHT_RED + 'Error: %s' % msg + Color.ENDC
    sys.exit(1)


####################################################################################################
# Custom logger
####################################################################################################
class Logger(object):
    def __init__(self, base_file_name, pipe=None):
        if not path.exists(TMP_DIR):
            makedirs(TMP_DIR)
        self.base_file_name = base_file_name
        self.pipe = pipe
        self.file_name = None
        self.file_path = None
        self.is_used = False

    def start_for_device(self, device):
        self.file_name = '{d}_{b}'.format(d=device.name, b=self.base_file_name)
        self.file_path = path.join(TMP_DIR, self.file_name)
        self.is_used = True
        # make sure log file exists and is empty
        with open(self.file_path, 'w') as log_file:
            log_file.write('')

    def stop(self):
        self.is_used = False

    def write(self, message):
        if self.pipe:
            self.pipe.write(message)
        colorless = re.sub(r"\[[0-9]{1,2}m", "", message)
        with open(self.file_path, "a") as log_file:
            log_file.write(colorless)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass

    def fileno(self):
        if self.pipe:
            self.pipe.fileno()

    def move_to(self, dst):
        shutil.move(self.file_path, dst)
        rename(path.join(dst, self.file_name), path.join(dst, self.base_file_name))


STDOUT_LOGGER = Logger('stdout.log', sys.stdout)
STDERR_LOGGER = Logger('stderr.log', sys.stderr)


####################################################################################################
# Check if command with given name is available
####################################################################################################
def check_cmd(name):
    proc = subprocess.Popen(['which', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    stdout, stderr = proc.communicate()
    return stdout and not stderr
