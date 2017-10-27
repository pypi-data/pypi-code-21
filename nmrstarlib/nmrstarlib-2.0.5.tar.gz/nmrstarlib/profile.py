#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import cProfile
from . import nmrstarlib


if __name__ == "__main__":
    # python3 -m nmrstarlib.profile > profile.txt 15573

    script = sys.argv.pop(0)
    source = sys.argv.pop(0)

    starfile_generator = nmrstarlib.read_files(source)
    cProfile.run("next(starfile_generator)")