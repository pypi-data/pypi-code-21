# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import os
import subprocess
import sys
from bgionline.utils import OSTYPE



if sys.stdout.isatty():
    try:
        tty_rows, tty_cols = map(int, subprocess.check_output(['stty', 'size'], stderr=open(os.devnull, 'w')).split())
        std_width = min(tty_cols - 2, 100)
    except:
        tty_rows, tty_cols = 24, 80
        std_width = 78
    color_state = True
else:
    tty_rows, tty_cols = 24, 80
    std_width = 78
    color_state = False

delimiter = None


def CYAN(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[36m' if color_state else ''
    else:
        return CYAN() + message + ENDC()


def LIGHTBLUE(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[1;34m' if color_state else ''
    else:
        return LIGHTBLUE() + message + ENDC()


def BLUE(message=None):
    if OSTYPE == 'windows':
        return message
    
    if message is None:
        return '\033[34m' if color_state else ''
    else:
        return BLUE() + message + ENDC()


def YELLOW(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[33m' if color_state else ''
    else:
        return YELLOW() + message + ENDC()


def GREEN(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[32m' if color_state else ''
    else:
        return GREEN() + message + ENDC()


def RED(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[31m' if color_state else ''
    else:
        return RED() + message + ENDC()


def WHITE(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[37m' if color_state else ''
    else:
        return WHITE() + message + ENDC()


def UNDERLINE(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[4m' if color_state else ''
    else:
        return UNDERLINE() + message + ENDC()


def BOLD(message=None):
    if OSTYPE == 'windows':
        return message
    if message is None:
        return '\033[1m' if color_state else ''
    else:
        return BOLD() + message + ENDC()


def ENDC():
    return '\033[0m' if color_state else ''
