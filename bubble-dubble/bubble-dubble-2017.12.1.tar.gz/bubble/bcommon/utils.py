#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
try:
    from bubble import frozen
except ImportError:
    frozen = False


def get_hg_hash():
    if not get_hg_hash.hash:
        # noinspection PyUnresolvedReferences
        if hasattr(sys, 'frozen') or frozen:
            get_hg_hash.hash = frozen.hg_hash
        else:
            path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            try:
                pipe = subprocess.Popen(['hg', 'id', '-i', '-R', path], stdout=subprocess.PIPE)
                get_hg_hash.hash = pipe.stdout.read().decode()
            except OSError:
                get_hg_hash.hash = 'unknown'
        get_hg_hash.hash = get_hg_hash.hash.strip()
    return get_hg_hash.hash


get_hg_hash.hash = ''


def get_version():
    if not get_version.version:
        if hasattr(sys, 'frozen') or frozen:
            get_version.version = frozen.version
        else:
            get_version.version = '0.0.0'
    return get_version.version


get_version.version = ''
