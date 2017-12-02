#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import os


def make_dir(abspath):
    """Make an empty directory.
    """
    try:
        os.mkdir(abspath)
        print("Made: %s" % abspath)
    except:  # pragma: no cover
        pass


def make_file(abspath, text):
    """Make a file with utf-8 text.
    """
    try:
        with open(abspath, "wb") as f:
            f.write(text.encode("utf-8"))
        print("Made: %s" % abspath)
    except:  # pragma: no cover
        pass
